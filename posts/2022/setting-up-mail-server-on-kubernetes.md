TODO: summary

# Dovecot

[Dovecot](https://www.dovecot.org/) is the Mail Delivery Agent (MDA) of my system. It seems to be have good combination between reliability, feature set and security.

Dovecot is what allows me to access my mail via IMAP. It also "owns" the mail storage - all of the at-rest mail is stored in a single PersistentVolumeClaim associated with Dovecot deployment. Although it [supports master/master replication](https://wiki.dovecot.org/Replication), I've decided not to use it. Running on top of Hetzner's virtual disks powered by Ceph, the Dovecot's replication is unlikely to have significant difference to durability. And I can tolerate short outages of the IMAP server as it should not affect mail delivery.

I've used [the official (however still experimental)](https://hub.docker.com/r/dovecot/dovecot) image. Here's how my deployment looks like:

```yaml
TODO
```

# Links

* https://github.com/instantlinux/docker-tools/blob/main/images/dovecot/kubernetes.yaml
* https://hub.docker.com/r/instantlinux/dovecot
* https://mailu.io/1.7/kubernetes/mailu/index.html - older version switched to helm
* https://polarathene.github.io/docker-mailserver/advanced/kubernetes/