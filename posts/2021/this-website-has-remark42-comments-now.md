Now you can tell me how wrong I am!

Comments are self-hosted using [remark42](https://github.com/umputun/remark42), there are no ads or tracking. The [privacy policy](/en/pages/privacy-policy/) was updated nonetheless.

Remark42 does not support captcha and its anti-spam is rudimentary, so I wasn't brave enough to enable anonymous posting. You'd have to log in. Currently it is possible to log in via Google or GitHub, and I plan to add more methods later.

<!-- TEASER_END -->

# Setup

remark42 runs on top of Kubernetes cluster (of course it is!) that I set up in [Hetzner Cloud](https://hetzner.com/cloud).

There is a [Helm chart](https://github.com/groundhog2k/helm-charts/tree/master/charts/remark42) to deploy remark42 on kubernetes but I used simpler deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: remark42
  namespace: gmsite
  labels:
    app: remark42
spec:
  replicas: 1
  selector:
    matchLabels:
      app: remark42
  strategy:
    type: Recreate
  template:
    metadata:
      namespace: remark42
      labels:
        app: remark42
    spec:
      containers:
      - name: remark42
        image: umputun/remark42:v1.8.1
        ports:
        - containerPort: 8080
        env:
          - name: REMARK_URL
            value: "https://comments.rusinov.ie/"
          - name: "SITE"
            value: "rusinov_ie"
          - name: SECRET
            valueFrom:
              secretKeyRef:
                name: remark42
                key: SECRET
          - name: STORE_BOLT_PATH
            value: "/srv/var/db"
          - name: BACKUP_PATH
            value: "/srv/var/backup"
          - name: DEBUG
            value: "true"
          - name: AUTH_GOOGLE_CID
            valueFrom:
              secretKeyRef:
                name: remark42
                key: AUTH_GOOGLE_CID
          - name: AUTH_GOOGLE_CSEC
            valueFrom:
              secretKeyRef:
                name: remark42
                key: AUTH_GOOGLE_CSEC
          - name: AUTH_GITHUB_CID
            valueFrom:
              secretKeyRef:
                name: remark42
                key: AUTH_GITHUB_CID
          - name: AUTH_GITHUB_CSEC
            valueFrom:
              secretKeyRef:
                name: remark42
                key: AUTH_GITHUB_CSEC
          - name: ADMIN_SHARED_ID
            value: "google_b182b5daa0004104b348d9bde762b1880ed9d98d"
          - name: TIME_ZONE
            value: "Europe/Dublin"
        volumeMounts:
        - name: srvvar
          mountPath: /srv/var
        securityContext:
          # Container writes to /web/ - can't make read-only.
          readOnlyRootFilesystem: false
        resources:
          requests:
            cpu: "100m"
            memory: "25Mi"
          limits:
            cpu: "1"
            memory: "1Gi"
      securityContext:
        # Has its own root priviledge drop
        #runAsUser: 1001
        #runAsGroup: 1001
        #fsGroup: 1001
      volumes:
       - name: srvvar
         persistentVolumeClaim:
           claimName: remark42
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: remark42
  namespace: gmsite
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: hcloud-volumes
---
apiVersion: v1
kind: Service
metadata:
  name: remark42-web
  namespace: gmsite
spec:
  selector:
    app: remark42
  ports:
    - name: http
      protocol: TCP
      port: 8080
      targetPort: 8080
---
# TODO: switch to networking.k8s.io/v1
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  name: remark42-ingress
  namespace: gmsite
  annotations:
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - comments.rusinov.ie
    secretName: comments-tls
  rules:
  - host: "comments.rusinov.ie"
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          serviceName: remark42-web
          servicePort: 8080
```

You'd also need another manifest for secrets. It can look something like this:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: remark42
  namespace: gmsite
stringData:
  SECRET: <changeme>
  AUTH_GOOGLE_CID: <changeme>.apps.googleusercontent.com
  AUTH_GOOGLE_CSEC: <changeme>
  AUTH_GITHUB_CID: <changeme>
  AUTH_GITHUB_CSEC: <changeme>
```

For https certificate I used the [guide published by Digital Ocean](https://www.digitalocean.com/community/tutorials/how-to-set-up-an-nginx-ingress-with-cert-manager-on-digitalocean-kubernetes) with minimal adjustments.

# Future work

In order to make comment system more convenient and robust I hope to improve following over time:

*   Add support for more authentication providers
*   Enable e-mail notifications
*   Set up off-site backups.

Anything else? Let me know in comments.
