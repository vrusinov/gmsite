I condone Russian invasion to Ukraine. The war is horrible and it's painful to see all the suffering people of Ukraine are going though. I hope the war ends soon and Ukrainians can take their country back and start rebuilding. I wish there was no more suffering.

There is another, less bloody but still important war happening right now. The informational war between Putin and regular residents of Russia. It's been going on for a really long time but escalated dramatically in the last few weeks. [Thousands of people were arrested](https://www.bbc.com/news/world-europe-60640204) for participating in anti-war protests. Many, if not all independent news sources [were blocked](https://www.nytimes.com/2022/03/07/technology/russia-ukraine-internet-isolation.html) so that Putin can continue spreading lies through the government-controlled channels without facing any criticism. And the sad part is that Putin appears to be winning this war. Many Russians are now brainwashed. I've been watching how many of my acquaintances become angrier and more and more radicalized year after year to culmination now. Thanfully my close friends (those who are still in Russia) were spared and still have their critical thinking intact. But for how long?

So I've decided to help them and set up a VPN service which will help them to get access to banned by Putin information.

<!-- TEASER_END -->

# OpenVPN

I've decided to do it using [OpenVPN](https://openvpn.net/). Mostly because I've used it before and was somewhat familiar with it. But because it can work over https on tcp port 443 which should hopefully make it a bit harder to detect & block.

And, since I had a ~~hammer~~ [Kubernetes cluster](/en/posts/2020/setting-up-single-node-kubernetes-cluster/), I've decided to run it there.

# Docker image

I could not find an up-to-date and supported image for OpenVPN so I've built my own [here](https://hub.docker.com/r/vrusinov/openvpn). It is based on Gentoo and the Dockerfile is in [my sundry repo](https://github.com/google/copr-sundry/blob/master/docker/openvpn/Dockerfile).

# OpenVPN set up

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

The above creates CA (with public and private keys), server key and two pairs of private/public keys for two clients. OpenVPN server would need server key, clients will need their private/public pair, and everyone will need CA public certificate. All of these are placed into not-so-trivial folder hierarchy under `pki/`.

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

I've used following server config:

```

```

# Links

* https://openvpn.net/community-resources/how-to/
* https://community.openvpn.net/openvpn/wiki/EasyRSA3-OpenVPN-Howto
* https://www.digitalocean.com/community/tutorials/how-to-set-up-and-configure-an-openvpn-server-on-ubuntu-20-04
* https://community.openvpn.net/openvpn/wiki/UnprivilegedUser
* https://hub.docker.com/r/kylemanna/openvpn/
* https://proprivacy.com/vpn/guides/how-to-hide-openvpn-traffic-an-introduction
* https://community.openvpn.net/openvpn/wiki/EasyRSA3-OpenVPN-Howto