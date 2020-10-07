For further experimentation with Kubernetes I've decided to add one more node to my [home cluster](/en/posts/2020/setting-up-single-node-kubernetes-cluster/). This time the node will be running Gentoo and I'll use Docker as CRI.

<!-- TEASER_END -->

# Installing kubelet in Gentoo

This was easy enough to do:

```bash
emerge -av sys-cluster/kubernetes
```

Make sure `kubelet` USE flag is turned on.

There is a problem with Gentoo ebuild: the provided systemd file does not specify necessary arguments for `kubeadm join` to work later. I populate it manually before enabling the service:

```bash
cat <<EOF | sudo tee /etc/systemd/system/kubelet.service.d/10-kubeadm.conf
[Service]
Environment="KUBELET_KUBECONFIG_ARGS=--bootstrap-kubeconfig=/etc/kubernetes/bootstrap-kubelet.conf --kubeconfig=/etc/kubernetes/kubelet.conf"
Environment="KUBELET_CONFIG_ARGS=--config=/var/lib/kuberecommendedyaml"
# This is a file that "kubeadm init" and "kubeadm join" generates at runtime, populating the KUBELET_KUBEADM_ARGS variable dynamically
EnvironmentFile=-/var/lib/kubelet/kubeadm-flags.env
# This is a file that the user can use for overrides of the kubelet args as a last resort. Preferably, the user should use
# the .NodeRegistration.KubeletExtraArgs object in the configuration files instead. KUBELET_EXTRA_ARGS should be sourced from this file.
EnvironmentFile=-/etc/default/kubelet
ExecStart=
ExecStart=/usr/bin/kubelet $KUBELET_KUBECONFIG_ARGS $KUBELET_CONFIG_ARGS $KUBELET_KUBEADM_ARGS $KUBELET_EXTRA_ARGS
EOF

sudo systemctl daemon-reload

sudo systemctl enable kubelet
sudo systemctl start kubelet
```

# Installing and configuring Docker

Installation is simple:

```bash
sudo emerge -av app-emulation/docker
```

Some adjustments are needed before starting it - it is recommended to use systemd as cgroup driver, and use overlay2 as a storage driver. This is configured in `/etc/docker/daemon.json`:

```bash
cat <<EOF | sudo tee /etc/docker/daemon.json
{
  "exec-opts": ["native.cgroupdriver=systemd"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m"
  },
  "storage-driver": "overlay2"
}
EOF
```

Now, start and enable it:

```bash
sudo systemctl start docker
sudo systemctl enable docker
```

# Adding new node to existing cluster

In order to add a node to an existing cluster the token is needed. Token for adding node can only be used once, and expires after a while if not used (I believe in 24 hours by default).

`kubeadm` is used to create new tokens:

```bash
kubeadm token create --print-join-command
```

With `--print-join-command` kubeadm will print out a command that can be simply copy-pasted and run on a new node. It will look similar to this: `kubeadm join 192.168.0.54:6443 --token qiwv05.pn2snd5kbgheoruv     --discovery-token-ca-cert-hash sha256:3425849ab342397a0d5e359839e992821b0694f69864aba9d000b53a614da37b`.

The Gentoo ebuild creates /etc/kubernetes/manifests directory and places .keep file in it, which causes an error: `[ERROR DirAvailable--etc-kubernetes-manifests]: /etc/kubernetes/manifests is not empty`. I simply remove this directory before trying to join.

```bash
# Clean directory kubeadm complains about:
sudo rm -rf /etc/kubernetes/manifests
sudo kubeadm join 192.168.0.54:6443 --token qiwv05.pn2snd5kbgheoruv     --discovery-token-ca-cert-hash sha256:3425849ab342397a0d5e359839e992821b0694f69864aba9d000b53a614da37b
```

After a while we have our new node:

```shell
$ kubectl get nodes
NAME          STATUS   ROLES    AGE   VERSION
homer         Ready    <none>   23m   v1.18.6
krusty        Ready    master   83d   v1.18.5
```

# Links

*   [Container runtimes](https://kubernetes.io/docs/setup/production-environment/container-runtimes/)
*   [Gentoo forum topic](https://forums.gentoo.org/viewtopic-t-1111252-start-0.html)
