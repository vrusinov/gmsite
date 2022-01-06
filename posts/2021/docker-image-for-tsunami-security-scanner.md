I've built unofficial image for the [Tsunami security scanner](https://github.com/google/tsunami-security-scanner).

Pull it from [Docker Hub](https://hub.docker.com/repository/docker/vrusinov/tsunami-security-scanner).

<!-- TEASER_END -->

Tsunami is a general purpose network security scanner with an extensible plugin system for detecting high severity vulnerabilities with high confidence.

It is not very mature yet but may still be useful.

The image I've built is experimental and based on Gentoo. It's probably too large and may have many problems. But it works for me.

I run it as Kubernetes jobs using manifests like this:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: tsunami-scan-localhost
  namespace: tsunami
spec:
  template:
    spec:
      containers:
      - name: tsunami
        image: vrusinov/tsunami-security-scanner:latest
        env:
          - name: IP_V4_TARGET
            value: "127.0.0.1"
      restartPolicy: Never
```

Dockerfile is based on the example provided in
[tsunami's repo](https://github.com/google/tsunami-security-scanner) and lives
in my
['sundry' repository](https://github.com/google/copr-sundry/tree/master/docker/tsunami-security-scanner).
