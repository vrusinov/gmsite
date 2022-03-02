TODO: summary

# Dovecot

[Dovecot](https://www.dovecot.org/) is the Mail Delivery Agent (MDA) of my system. It seems to be have good combination between reliability, feature set and security.

Dovecot is what allows me to access my mail via IMAP. It also "owns" the mail storage - all of the at-rest mail is stored in a single PersistentVolumeClaim associated with Dovecot deployment. Although it [supports master/master replication](https://wiki.dovecot.org/Replication), I've decided not to use it. Running on top of Hetzner's virtual disks powered by Ceph, the Dovecot's replication is unlikely to have significant difference to durability. And I can tolerate short outages of the IMAP server as it should not affect mail delivery.

I've used [the official (however still experimental)](https://hub.docker.com/r/dovecot/dovecot) image. Here's how my deployment looks like:

```yaml
TODO
```

This will set up Dovecot but it won't be accessible from the outside the cluster. There are several ways of doing so and I chose to do it via Ingress. I already had ingress-nginx set up and although Kubernetes Ingress does not technically support arbitrary TCP or UDP services, it was possible to configure ingress-nginx it to use [PROXY protocol](https://docs.nginx.com/nginx/admin-guide/load-balancer/using-proxy-protocol/) to pass IMAP and SMTP.

Following the [guide](https://kubernetes.github.io/ingress-nginx/user-guide/exposing-tcp-udp-services/) I've set ConfigMap for tcp-services which included just IMAP port for now:

```yaml
TODO
```

After this a few objects in the ingress needed to be adjusted.

First, I needed to add imap port to the nginx service:

```yaml
---
# Source: ingress-nginx/templates/controller-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: ingress-nginx-controller
  namespace: ingress-nginx
spec:
  type: NodePort
  ipFamilyPolicy: SingleStack
  externalTrafficPolicy: Local
  ipFamilies:
    - IPv4
  ports:
    - name: http
      port: 80
      protocol: TCP
      targetPort: http
      appProtocol: http
    - name: https
      port: 443
      protocol: TCP
      targetPort: https
      appProtocol: https
    - name: imap  # Proxied
      port: 143
      targetPort: 143
      protocol: TCP
  selector:
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/component: controller
```

Note `externalTrafficPolicy: Local` and `imap` port defined there.

Then flags passed to the controller needed to be adjusted. For this I modified `args` section of the ingress-nginx-controller Deployment to include `--tcp-services-configmap=ingress-nginx/tcp-services` flag, like so:

```yaml
args:
- /nginx-ingress-controller
- --election-id=ingress-controller-leader
- --controller-class=k8s.io/ingress-nginx
- --configmap=$(POD_NAMESPACE)/ingress-nginx-controller
- --validating-webhook=:8443
- --validating-webhook-certificate=/usr/local/certificates/cert
- --validating-webhook-key=/usr/local/certificates/key
- --tcp-services-configmap=ingress-nginx/tcp-services
```

Dovecot had to be configured to expect proxy protocol. This is what `haproxy_trusted_networks` and `haproxy = yes` in the imap service section of the above config do.


# Links

* https://github.com/instantlinux/docker-tools/blob/main/images/dovecot/kubernetes.yaml
* https://hub.docker.com/r/instantlinux/dovecot
* https://mailu.io/1.7/kubernetes/mailu/index.html - older version switched to helm
* https://polarathene.github.io/docker-mailserver/advanced/kubernetes/
* https://kubernetes.github.io/ingress-nginx/user-guide/exposing-tcp-udp-services/