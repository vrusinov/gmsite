For further experimentation with Kubernetes I've decided to add one more node to my [home cluster](/en/posts/2020/setting-up-single-node-kubernetes-cluster/). This time the node was running Gentoo and I used containerd CRI.

<!-- TEASER_END -->

# Installing kubelet in Gentoo

This was easy enough to do:

```bash
emerge -av sys-cluster/kubelet sys-cluster/kubeadm
```

Make sure to install kubeadm of the same major version. E.g. if your server is running 1.23, do `emerge -av '=sys-cluster/kubeadm-1.23.13'`. Kubelet can be one major version above or below, so if you are running Kubernetes 1.23 you can do anything between 1.22.0 and 1.24.x. You can mask other versions in [`/etc/portage/package.mask`](https://wiki.gentoo.org/wiki//etc/portage/package.mask).

Once installed, enable it with:

```bash
sudo systemctl daemon-reload

sudo systemctl enable kubelet
sudo systemctl start kubelet
```

# Installing and configuring containerd

Installation is simple:

```bash
sudo emerge -av app-containers/containerd

sudo systemctl start containerd
sudo systemctl enable containerd
```

Next edit `/var/lib/kubelet/kubeadm-flags.env` and make sure `KUBELET_KUBEADM_ARGS` variable contains `--container-runtime=remote` and `--container-runtime-endpoint=unix:///run/containerd/containerd.sock`.

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

After a while we have I had my node:

```shell
$ kubectl get nodes -o wide
NAME                         STATUS     ROLES                  AGE      VERSION   INTERNAL-IP     EXTERNAL-IP   OS-IMAGE                 KERNEL-VERSION            CONTAINER-RUNTIME
<...>
homer.greenmice.info         Ready      <none>                 2y24d    v1.24.7   192.168.0.244   <none>        Gentoo Linux             5.15.74-gentoo-x86_64     containerd://1.6.8
<...>
```

# Links

*   [Container runtimes](https://kubernetes.io/docs/setup/production-environment/container-runtimes/)
*   [Gentoo forum topic](https://forums.gentoo.org/viewtopic-t-1111252-start-0.html)
*   [Changing the Container Runtime on a Node from Docker Engine to containerd](https://kubernetes.io/docs/tasks/administer-cluster/migrating-from-dockershim/change-runtime-containerd/)
