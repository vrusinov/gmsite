<img src="/posts/2022/flag_of_ukraine.svg" width="50%" align="right" style="margin: 0.3em;">

I condone Russian invasion to Ukraine. I hope the war ends soon. I wish Ukrainians can take their country back and start rebuilding. I wish there was no more suffering.

There is another, less bloody but still important war happening right now. The informational war between Putin and regular residents of Russia. It's been going on for a really long time but escalated dramatically in the last few weeks. [Thousands of people were arrested](https://www.bbc.com/news/world-europe-60640204) for participating in anti-war protests. Many, if not all independent news sources [were blocked](https://www.nytimes.com/2022/03/07/technology/russia-ukraine-internet-isolation.html) so that Putin can continue spreading lies through the government-controlled channels without facing any criticism. And the sad part is that Putin appears to be winning this war. Many Russians are now brainwashed. I've been watching for years how many of my acquaintances become angrier and more and more radicalized. Thanfully my close friends (those few who are still in Russia) were spared and still have their critical thinking intact. But for how long?

So I've decided to help them and set up a VPN service which will help them to get access to free information.

<!-- TEASER_END -->

# OpenVPN

I've decided to do it using [OpenVPN](https://openvpn.net/). Primarily because I've used it before and was somewhat familiar with it. But also because it can work over https on tcp port 443 which should hopefully make it a bit harder to detect & block.

And, since I already had a ~~hammer~~ [Kubernetes cluster](/en/posts/2020/setting-up-single-node-kubernetes-cluster/), I've decided to run it there.

# Docker image

I could not find an up-to-date and supported image for OpenVPN so I've built my own [here](https://hub.docker.com/r/vrusinov/openvpn). It is based on Gentoo and the Dockerfile is in [my sundry repo](https://github.com/google/copr-sundry/blob/master/docker/openvpn/Dockerfile).

# Server setup

## CA and keys

While OpenVPN supports several authorization/authentication methods, I've decided to use a fairly simple way of setting up PKI (public key infrastructure). It is possible to set PKI via unsecure channel, but I had a secure one so I've decided to just generate certificate authority along with server and client keys in one place and then just distribute generated files as appropriate.

I've used [easy-rsa](https://github.com/OpenVPN/easy-rsa) for this:

```sh
alias easyrsa=/usr/share/easy-rsa/easyrsa
easyrsa init-pki
easyrsa build-ca nopass

# Put your server name instead of example.com
easyrsa build-server-full example.com nopass
# Place distinguishable client name instead of 'username1'
easyrsa build-client-full username1 nopass
easyrsa build-client-full username2 nopass

easyrsa gen-dh
```

The set of command created CA (with public and private keys), server key and two pairs of private/public keys for two clients. OpenVPN server would need server key, clients will need their private/public pair, and everyone will need CA public certificate. All of these are placed into not-so-trivial folder hierarchy under `pki/`.

The following script took care of packaging necessary for server files in a flat directory and storing it as Kubernetes secret:

```sh
#!/bin/bash

mkdir -p etc-openvpn
cp pki/ca.crt etc-openvpn
cp pki/issued/example.com.crt etc-openvpn
cp pki/private/example.com.key etc-openvpn
cp pki/dh.pem etc-openvpn

kubectl -n vpn create secret generic etc-openvpn --dry-run=client --from-file=etc-openvpn -o yaml > openvpn-config.yaml

kubectl apply -f openvpn-config.yaml

kubectl -n vpn rollout restart deployment openvpn-tcp
```

## Server config

For now I've just set OpenVPN via TCP on port 30749. It had to be in range 30000-31000 so I can use `NodePort` service later on. It does not use TLS auth so may be vulnerable to DOS, and does [not provide adequate protection](http://openvpn.net/howto.html#mitm) from MITM. The goal of the service is to circumvent censorship, not to provide perfect security. I expect my clients to use https and other secure protocols, though DNS may be still vulnerable.

I've used following server config:

```conf
proto tcp
port 30749
dev tun

ca /etc/openvpn/ca.crt
cert /etc/openvpn/example.com.crt
key /etc/openvpn/example.com.key
dh /etc/openvpn/dh.pem

topology subnet

# Give clients IP in 10.185.162.0/24
server 10.185.162.0 255.255.255.0

# Set default gateway through VPN
push "redirect-gateway def1 bypass-dhcp"
push "dhcp-option DNS 8.8.8.8"

# Allows same client to connect more than once.
duplicate-cn

keepalive 10 120
max-clients 10

# Enable compression
compress lz4-v2
push "compress lz4-v2"
allow-compression yes

user openvpn
group openvpn

persist-key
persist-tun

log         /dev/stdout

# Logging settings
verb 4
mute 20

# run /etc/openvpn/up.sh when the connection is set up. This will set up NAT.
script-security 2
up "/bin/sh /etc/openvpn/up.sh"
```

`up.sh` script sets up NAT so that clients have Internet connectivity:

```sh
#!/bin/sh

set -e

echo "1" > /proc/sys/net/ipv4/ip_forward
iptables -t nat -A POSTROUTING -s 10.185.162.0/24 -o eth0 -j MASQUERADE
```

The config and `up.sh` are put into `etc-openvpn` folder and therefore put into `etc-openvpn` Secret by the above script.

In order for `iptables` command in `up.sh` to work, `ip_tables` module needs to be loaded on the *host*. I did this by running `modprobe ip_tables` on all of my Kubernetes hosts, and by putting "ip_tables" to `/etc/modules-load.d/iptables.conf`.

## Kubernetes deployment

Here's how my deployment currently looks like:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openvpn-tcp
  namespace: vpn
  labels:
    app: openvpn-tcp
spec:
  replicas: 1
  selector:
    matchLabels:
      app: openvpn-tcp
  strategy:
    type: Recreate
  template:
    metadata:
      labels:
        app: openvpn-tcp
    spec:
      containers:
        - name: openvpn-tcp
          image: vrusinov/openvpn:2.5.2-r1
          command: ["/bin/openvpn"]
          args:
            - "/etc/openvpn/openvpn.conf"
          ports:
          - name: ovpn
            containerPort: 30749
            protocol: TCP
          resources:
            requests:
              cpu: "0.01"
              memory: "16Mi"
            limits:
              cpu: "1"
              memory: "32Mi"
          volumeMounts:
            - name: openvpn-config-volume
              mountPath: /etc/openvpn/
          securityContext:
            capabilities:
              add:
              - NET_ADMIN
              - SYS_ADMIN
            privileged: true
      securityContext:
        runAsUser: 0
        runAsGroup: 0
        # 394 is the ID of the `openvpn` user in my image.
        fsGroup: 394
      volumes:
        - name: openvpn-config-volume
          secret:
            defaultMode: 420
            secretName: etc-openvpn
```

The main downside is that since OpenVPN needs to create new network interfaces, it had to run in privileged mode with some dangerous capabilities. In theory it should have been possible to run in non-privileged mode just with capabilities but I didn't manage to figure it out yet.

## Kubernetes service

I've used `NodePort` service so that clients can connect to the server:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: openvpn-tcp
  namespace: vpn
spec:
  selector:
    app: openvpn-tcp
  ports:
    - name: ovpn-tcp
      protocol: TCP
      port: 30749
      targetPort: 30749
      nodePort: 30749
  type: NodePort
```

# Client setup

I've created following template for the client config:

```conf
client

dev tun
proto tcp4
nobind
resolv-retry infinite

remote example.com 30749

# Try to preserve some state across restarts.
persist-key
persist-tun

comp-lzo

verb 3
```

It's only the template because it's missing certificates. I've created `make-ovpn.sh` script to create per-user .ovpn file which can be then shared with clients and used by either Linux or Windows clients:

```sh
#!/bin/bash
# Creates ovpn file with bundled keys

client_name=$1
F="${client_name}.ovpn"
cp openvpn-client.conf $F

if [[ ! -f pki/private/${client_name}.key ]]
then
    easyrsa build-client-full $client_name nopass
fi

echo "<ca>" >> $F
cat pki/ca.crt | sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' >> $F
echo "</ca>" >> $F

echo "<cert>" >> $F
cat pki/issued/${client_name}.crt | sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' >> $F
echo "</cert>" >> $F

echo "<key>" >> $F
cat pki/private/${client_name}.key >> $F
echo "</key>" >> $F
```

Now, I could create all necessary keys and client-specific config by running `./make-ovpn test`. This would create `test.ovpn` file which can be later used by clients like so: `openvpn test.ovpn`.

# Future work

This was set up in a relatively quick and dirty way. There are many possible incremental improvements, especially for security and hardening:

* Set up server [certificate verification](http://openvpn.net/howto.html#mitm) to prevent MITM.
* Set up [tls-auth](https://openvpn.net/community-resources/hardening-openvpn-security/).
* Limit egress from OpenVPN using `NetworkPolicy`.
* Set up UDP server.
* Set up server working through Ingress on port 443.
* Remove dangerous privileges from OpenVPN container and [try to run it as a regular user](https://community.openvpn.net/openvpn/wiki/UnprivilegedUser).
* Set up IPv6.
* Create `down.sh` script to clean up NAT properly.
* Tighten up OpenVPN deployment - set up probes, run more than one instance, etc.

# Links

* [OpenVPN howto](https://openvpn.net/community-resources/how-to/)
* [Easy-RSA howto](https://community.openvpn.net/openvpn/wiki/EasyRSA3-OpenVPN-Howto)
* [How To Set Up and Configure an OpenVPN Server on Ubuntu](https://www.digitalocean.com/community/tutorials/how-to-set-up-and-configure-an-openvpn-server-on-ubuntu-20-04)
* [Running OpenVPN as unprivileged user](https://community.openvpn.net/openvpn/wiki/UnprivilegedUser)
* [Another OpenVPN image](https://hub.docker.com/r/kylemanna/openvpn/)
* [How to hide OpenVPN traffic](https://proprivacy.com/vpn/guides/how-to-hide-openvpn-traffic-an-introduction)
* [Hardening OpenVPN Security](https://openvpn.net/community-resources/hardening-openvpn-security/)