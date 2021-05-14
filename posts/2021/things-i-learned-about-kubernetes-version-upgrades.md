Back what I was setting up my [home Kubernetes cluster](/en/posts/2020/setting-up-single-node-kubernetes-cluster/) the latest Kubernetes version was 1.18.6.

A lot of minor and major versions were released since then and now the latest version is 1.21.0. I didn't go all the way to 1.21.0 but I've recently performed upgrade to latest stable version in 1.20 branch.

Kubernetes has somewhat [decent upgrade instructions](https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-upgrade/). But they are far from comprehensive and I've learned a few thing things even upgrading my small home cluster with a very small number of apps. I can understand now why Kubernetes admins fear upgrades.

<!-- TEASER_END -->

# Upgrading kubernetes is more complicated than running 'dnf update'

When new versions of kubelet popped up in 'dnf update' I simply accepted them, and everything continued working.

Only later I realised it is not actually updating pods/images and the main API server pods were still running at version 1.18.6 despite kubelet being at 1.21.0. I was surprised such version skew it did not cause too many issues.

# yaml files in `/etc/kubernetes/manifests/` are not authoritative

In "Securing etcd" section of my [original post](/en/posts/2020/setting-up-single-node-kubernetes-cluster/) I simply suggested editing `/etc/kubernetes/manifests/kube-apiserver.yaml` pointing to certificate files and new etcd address. This bit me back.

Turns out `kubeadm` re-generates these manifests based on `kubeadm-config` ConfigMap. So when it needs to be updated too, e.g. via `kubectl -n kube-system edit ConfigMap/kubeadm-config`. (I've updated the post now, but you may want to modify ConfigMap/kubeadm-config if you followed it earlier).

I'm sure there are better ways of doing so (there ought to be some kubeadm sub-command) but I have not discovered them yet.
