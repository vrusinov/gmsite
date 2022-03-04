Write your post here.

# Generating keys

```sh
mkdir openvpn-conf
cd openvpn-conf
cp /usr/share/easy-rsa/vars.example vars
$EDITOR vars  # Modify a few non-critical things

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

# Links

* https://openvpn.net/community-resources/how-to/
* https://community.openvpn.net/openvpn/wiki/EasyRSA3-OpenVPN-Howto
* https://www.digitalocean.com/community/tutorials/how-to-set-up-and-configure-an-openvpn-server-on-ubuntu-20-04
* https://community.openvpn.net/openvpn/wiki/UnprivilegedUser
* https://hub.docker.com/r/kylemanna/openvpn/
* https://proprivacy.com/vpn/guides/how-to-hide-openvpn-traffic-an-introduction
* https://community.openvpn.net/openvpn/wiki/EasyRSA3-OpenVPN-Howto