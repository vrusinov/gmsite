<img src="/posts/2020/kubernetes.png" alt="Kubernetes log" width="10%" style="float: right;"> As almost any engineer I have a small "server" at home. This server is nothing
more than an old laptop running CentOS and a few docker containers in it. At
some point I got tired of restarting and updating them manually. And of course
instead of writing a few systemd unit files I've decided to over-engineer it and
run Kubernetes on it.

This was a nice way to keep myself busy for a few evenings and get some relevant
experience.

# Choices

After small amount of reading it was quite obvious there is no single way to set
up Kubernetes. There are many ways to set Kubernetes up and it's easy to get
lost. Thus before doing everything else, let's outline what is it that I wanted:

*   Working Kubernetes "cluster" that fits on one machine with dual-code CPU and
    4 GiB of RAM.
*   It must be possible to run it on more than one machine in the future.
*   It must be close to what I'd run in production - I want to get relevant
    experience. So no Minikube or similar things.

<!-- TEASER_END -->

Based on this I chose the following components:

## Operating system

The "server" already ran CentOS 8 (or even CentOS Stream). No reason to change
that.

Decision: **CentOS 8**

## Container Runtime

Kubernetes lets you chose container runtime. Container runtime is a thing than
runs containers. The default choice here is of course Docker.

Thanks to [Open Container Initiative](https://opencontainers.org/) Docker is not
the only choice as there is a standard now and multiple projects implementing
it. So we are not limited to just Docker now.

Now, Docker does quite a lot of stuff which seems to intertwine with what
Kubernetes provide (Swarm, many networking options, etc). It seemed silly to
have all of it running together with kubelet. In addition, I've seen my share of
Docker bugs so I wanted some other bugs instead.

Looking around a bit, [cri-o](https://cri-o.io/) seemed nice. It is built
primarily for Kubernetes, so hopefully does not have unnecessary bits
implemented. It's supports all container registries and by default uses
runc/containerd to actually run containers - the same tools Docker uses. So it
will still share some of the bugs with Docker!

**Winner**: [cri-o](https://cri-o.io/)

## Networking

Kubernetes network model is fairly straightforward: each pod (a group of one or
more containers) gets its own IP address. Pods talk to each other using this IP.

How its implemented from physical network perspective is quite tricky. Kevin
Sookocheff explained this quite well in his
[blog post](https://sookocheff.com/post/kubernetes/understanding-kubernetes-networking-model/).

Implementation of the Kubernetes network can involve VLANs, virtual switches,
tunnels, routing protocols or fancy software-defined network hardware. Major
cloud providers have their own implementations of virtual networks which
integrate nicely with Kubernetes. However since I am home user and I don't have
fancy programmable hardware for software-defined networks, I needed to run a
virtual network. Good news is that Kubernetes provides a way to solve this. You
"simply" plug a network provider which supports the
[necessary APIs](https://github.com/containernetworking/cni) and this provider
will be responsible for configuring bridges, tunnels and everything involved.
The bad news is that there seems to be
[more than a dozen different network providers for Kubernetes](https://kubernetes.io/docs/concepts/cluster-administration/networking/),
and the choice seems quite overwhelming at first.

However after digging through this (did I mention I hate networking?) the choice became
obvious. I wanted Pods to be able to talk IPv6 to each other and external
network and the only popular CNI that supported it was Calico.

**Winner**: [Calico](https://www.projectcalico.org/).

# Installing Kubernetes

## cri-0

First steps is to install container runtime. Unfortunately installing cri-o on
CentOS requires adding flimsy looking third-party repositories from OpenSUSE
build system. (Maybe cri-o was not the best choice after all?).

Following [the guide](https://github.com/cri-o/cri-o#getting-started):

```bash
# Enable repositories:
sudo dnf -y module disable container-tools
sudo curl -L -o /etc/yum.repos.d/devel:kubic:libcontainers:stable.repo https://download.opensuse.org/repositories/devel:kubic:libcontainers:stable/CentOS_8_Stream/devel:kubic:libcontainers:stable.repo
sudo curl -L -o /etc/yum.repos.d/devel:kubic:libcontainers:stable:cri-o:1.18.repo https://download.opensuse.org/repositories/devel:kubic:libcontainers:stable:cri-o:1.18/CentOS_8_Stream/devel:kubic:libcontainers:stable:cri-o:1.18.repo

# Install cri-o
sudo dnf install cri-o

# Load modules necessary for cri-o:
sudo bash -c 'cat >> /etc/modules-load.d/cri-o.conf <<EOF
overlay
br_netfilter
EOF'
sudo systemctl restart systemd-modules-load.service

# Configure necessary for cri-o sysctl settings:
sudo bash -c 'cat > /etc/sysctl.d/99-kubernetes-cri.conf <<EOF
net.bridge.bridge-nf-call-iptables  = 1
net.ipv4.ip_forward                 = 1
net.bridge.bridge-navailableables = 1
EOF'
sudo sysctl --system

# Enable and start the service
sudo systemctl start cri-o
sudo systemctl enable cri-o
```

## etcd

Kubernetes stores its data in [etcd](https://etcd.io/) - a Paxos-based highly
available key-value store.

Kubernetes
[can run etcd as a static pod](https://blog.scottlowe.org/2020/04/02/setting-up-etcd-with-kubeadm-containerd-edition/),
however this did not feel right to me: etcd is probably the most critical piece
of the cluster so deserved its own systemd unit.

For CentOS etcd is available from
[Openstack repos](https://docs.openstack.org/install-guide/environment-packages-rdo.html):

```bash
sudo dnf install centos-release-openstack-ussuri
sudo dnf install etcd
```

Default settings should work for a single-node cluster. Expansion to a few more
nodes is possible via
[static clustering](https://github.com/etcd-io/etcd/blob/master/Documentation/op-guide/clustering.md#static).

However I made a few adjustments to default config to ensure it behaves a little
bit better in small cluster. So I have following /etc/etcd/etcd.conf:

```bash
#[Member]
# 192.168.0.54 is the ip address of my server.
ETCD_LISTEN_PEER_URLS="http://localhost:2380,http://192.168.0.54:2380"
ETCD_LISTEN_CLIENT_URLS="http://localhost:2379,http://192.168.0.54:2379"
ETCD_NAME="krusty"
# Do snapshots more frequently to reduce memory and disk usage.
ETCD_SNAPSHOT_COUNT="5000" # Default is 100000

# Lower heartbeat latency as we don't have a very fast hardware:
# Do heartbeats every 1s and fail if heard no response for 5 seconds
# In cluster setup this means it can take up to 6 seconds to detect machine
# failure and start doing someting about it.
ETCD_HEARTBEAT_INTERVAL="1000"
ETCD_ELECTION_TIMEOUT="5000"

#[Clustering]
ETCD_INITIAL_ADVERTISE_PEER_URLS="http://localhost:2380,http://192.168.0.54:2380"
ETCD_ADVERTISE_CLIENT_URLS="http://localhost:2379,http://192.168.0.54:2379"
ETCD_INITIAL_CLUSTER="krusty=http://192.168.0.54:2380,krusty=http://localhost:2380"
```

To start and enable etcd:

```bash
sudo systemctl start etcd
sudo systemctl enable etcd
```

After doing that I was able to run `etcdctl member list` and see single-member
etcd cluster.

## Control plane

I used
[kubeadm](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/)
for setting everything up.

First, enabling official repository and installing control plane components.
'el7' in repository baseurl is not a mistake - there is no el8 repository. 'el7'
is supposed to work for 7 and 8 (ugh).

```bash
sudo sh -c 'cat <<EOF > /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://packages.cloud.google.com/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
EOF'

# Install kubernetes components
sudo dnf install kubelet kubeadm kubectl
# And some optional dependencies:
sudo dnf install iproute-tc
```

Now, the system needs to be adjusted for running kubelet.

In /etc/sysconfig/kubelet:

```bash
KUBELET_EXTRA_ARGS=--cgroup-driver="systemd"
```

It should be possible to start kubelet now:

```bash
# Start and enable kubelet:
sudo systemctl start kubelet
sudo systemctl enable kubelet
```

Now, the most interesting part - configuring control plane.

```bash
# Configure control plane.
# Adjust "advertiseAddress: 192.168.0.54" to address of your server
# Adress etcd enpoints (http://192.168.0.54:2379) to address of your
# etcd server(s).
cat > /tmp/master-configuration.yaml <<EOF
apiVersion: kubeadm.k8s.io/v1beta2
kind: InitConfiguration
localAPIEndpoint:
  advertiseAddress: 192.168.0.54
  bindPort: 6443
---
apiVersion: kubeadm.k8s.io/v1beta2
kind: ClusterConfiguration
certificatesDir: /etc/kubernetes/pki
etcd:
  external:
    endpoints:
      - http://192.168.0.54:2379
networking:
  podSubnet: 10.42.0.0/16
EOF

# Bootstrapping the cluster:
# This will take a while and will print out token like 818d5a.8b50eb5477ba4f40.
# Write it down, may be needed later.
sudo kubeadm init --config /tmp/master-configuration.yaml

# As suggested, make it possible to run kubectl without sudo:
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

After this we should see components of the control plane running:

```bash
$ sudo crictl ps
CONTAINER ID        IMAGE                                                              CREATED             STATE               NAME                      ATTEMPT             POD ID
9532e552dab61       67da37a9a360e600e74464da48437257b00a754c77c40f60c65e4cb327c34bd5   4 minutes ago       Running             coredns                   0                   d943e42fb4830
80e385d9a3871       67da37a9a360e600e74464da48437257b00a754c77c40f60c65e4cb327c34bd5   4 minutes ago       Running             coredns                   0                   802d1551e04f4
d3964e90dced0       c3d62d6fe4120e9a9558d0ab1904667ac43b176c6b075ce06708e4476d53aa22   5 minutes ago       Running             kube-proxy                0                   5942aa65d2ed3
ca8ba34a8ff2b       0e0972b2b5d1a9fce6ab591c9cff2ab5cd23f5dc4aaa62630d52342e71420305   5 minutes ago       Running             kube-scheduler            0                   54bab995eb29e
49bb767626464       ffce5e64d9156ea4a08f30c61581a3dc52b654422948a11cf47e362a29250dd8   5 minutes ago       Running             kube-controller-manager   0                   bc9c32c7689a6
cf289823c5177       56acd67ea15a38321e93fc688824a1a74922725d5e6576c3a42794dd6925b2f1   5 minutes ago       Running             kube-apiserver            0                   99abeabc6bae9
```

## Calico

```bash
# Install the Tigera Calico operator and custom resource definitions:
kubectl create -f https://docs.projectcalico.org/manifests/tigera-operator.yaml

# Install Calico by creating the necessary custom resource:
cat > /tmp/calico-custom-resources.yaml <<EOF
# This section includes base Calico installation configuration.
# For more information, see: https://docs.projectcalico.org/v3.15/reference/installation/api#operator.tigera.io/v1.Installation
# Downloaded from https://docs.projectcalico.org/manifests/custom-resources.yaml
apiVersion: operator.tigera.io/v1
kind: Installation
metadata:
  name: default
spec:
  # Configures Calico networking.
  calicoNetwork:
    # Note: The ipPools section cannot be modified post-install.
    ipPools:
    - blockSize: 26
      cidr: 10.42.0.0/16
      encapsulation: VXLANCrossSubnet
      natOutgoing: Enabled
      nodeSelector: all()
EOF
kubectl create -f /tmp/calico-custom-resources.yaml

# Installation will take a while. We can check status by doing
kubectl get tigerastatuses

# Remove the taints on the master so that we can schedule pods on it:
kubectl taint nodes --all node-role.kubernetes.io/master-
```

## Deploying Kubernetes Dashboard

At this point we should have running cluster, but it won't be actually running anything except itself. Let's deploy Kubernetes Dashboard so that we have some non-system pods running and have a nice UI for our cluster.

I did it from desktop, now running Gentoo.

```bash
sudo emerge -av sys-cluster/kubernetes
# Copy config over:
rsync -rv 192.168.0.54:.kube $HOME

# Deploy Kubernetes Dashboard version 2.0.3:
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.0.3/aio/deploy/recommended.yaml

# Make sure it is running:
kubectl get pods -n kubernetes-dashboard
```

I was not quite ready to deal with concept of Services and with setting up
frontends. Thankfully we can still open it using Kubernetes proxy. It will
require secret to log in. Ideally a separate user should be set up for this.
However I was not quite ready to deal with users and permissions either, so I
share my bad advice of logging it as `admin-user`:

```bash
# Get bearer token:
kubectl -n kubernetes-dashboard describe secret $(kubectl -n kubernetes-dashboard get secret | grep admin-user | awk '{print $1}') | grep ^token

kubectl proxy &

google-chrome http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/ &
```

Here is how it cloud look:

![Kubernetes dashboard nodes](/posts/2020/kubernetes-nodes.png "List of nodes")

![Kubernetes dashboard workloads](/posts/2020/kubernetes-workloads.png "List of workloads")

## Securing etcd

The way I set etcd above is quite terrible - it lets anyone who has network access to it to do anything. There is no transport security or authentication. I should have done it right away, but I was too lazy and I had to [secure](https://github.com/etcd-io/etcd/blob/master/Documentation/op-guide/security.md) it later. Kubernetes only supports authentication via SSL certificates, and it's quite a hassle to generate and maintain certificate authority, server and client keys and certificates. Thankfully kubeadm can do it for us:

```bash
sudo kubeadm init phase certs etcd-ca
sudo kubeadm init phase certs etcd-server
sudo kubeadm init phase certs etcd-healthcheck-client
sudo kubeadm init phase certs etcd-peer

sudo chown etcd:etcd /etc/kubernetes/pki/etcd/peer.crt
sudo chown etcd:etcd /etc/kubernetes/pki/etcd/server.key
```

Now, modify /etc/etcd/etcd.conf`. Note 'https' in URLS.

```bash
#[Member]
ETCD_LISTEN_PEER_URLS="https://localhost:2380,https://192.168.0.54:2380"
ETCD_LISTEN_CLIENT_URLS="https://localhost:2379,https://192.168.0.54:2379"

#[Clustering]
ETCD_INITIAL_ADVERTISE_PEER_URLS="https://localhost:2380,https://192.168.0.54:2380"
ETCD_ADVERTISE_CLIENT_URLS="https://localhost:2379,https://192.168.0.54:2379"
ETCD_INITIAL_CLUSTER="krusty=https://192.168.0.54:2380,krusty=https://localhost:2380"

#[Security]
ETCD_CERT_FILE="/etc/kubernetes/pki/etcd/server.crt"
ETCD_KEY_FILE="/etc/kubernetes/pki/etcd/server.key"
ETCD_CLIENT_CERT_AUTH="true"
ETCD_TRUSTED_CA_FILE="/etc/kubernetes/pki/etcd/ca.crt"
#ETCD_AUTO_TLS="false"
ETCD_PEER_CERT_FILE="/etc/kubernetes/pki/etcd/peer.crt"
ETCD_PEER_KEY_FILE="/etc/kubernetes/pki/etcd/peer.key"
ETCD_PEER_CLIENT_CERT_AUTH="true"
ETCD_PEER_TRUSTED_CA_FILE="/etc/kubernetes/pki/etcd/ca.crt"
#ETCD_PEER_AUTO_TLS="false"
```

Let's restart it now.

```bash
sudo systemctl restart etcd
# Make sure cluster is still healthy:
sudo etcdctl -endpoints=https://127.0.0.1:2379 -ca-file=/etc/kubernetes/pki/etcd/ca.crt cluster-health
```

At this point I had etcd which requires SSL and certificate validation, and
Kubernetes clusters which still tries to use plain http. I could not find a nice
way to modify setting so I've resorted to manual modification of
`/etc/kubernetes/manifests/kube-apiserver.yaml`:

```yaml
spec:
  containers:
  - command:
    - kube-apiserver
    <...>
    - --etcd-servers=https://192.168.0.54:2379
    - --etcd-certfile=/etc/kubernetes/pki/etcd/server.crt
    - --etcd-keyfile=/etc/kubernetes/pki/etcd/server.key
    - --etcd-cafile=/etc/kubernetes/pki/etcd/ca.crt
```

Restart kubelet and check if everything sill work:

```bash
sudo systemctl restart kubelet
kubectl get nodes
```

Editing yaml file above was actually a hack. To make it permanent and to make
sure the file is not overwritten (e.g. during version upgrades) I needed to
modify corresponding ConfigMap. This can be done by running
`kubectl -n kube-system edit ConfigMap/kubeadm-config`. There I updated
`caFile`, `certFile` and `keyFile` to point to correct files, and changed
endpoint to https.

```yaml
   etcd:
     external:
       caFile: "/etc/kubernetes/pki/etcd/ca.crt"
       certFile: "/etc/kubernetes/pki/etcd/server.crt"
       endpoints:
       - https://192.168.0.54:2379
       keyFile: "/etc/kubernetes/pki/etcd/server.key"
```


# Final words

As this was the first time I played with Kubernetes all of this took quite a few
evenings of research. And I probably made a number of things wrong. I don't have
comments set up for this blog (yet?), so yell at me or ask questions via
[GitHub issues](https://github.com/vrusinov/gmsite/issues) of this site.

# Future work

*   Move etcd to IPv6
*   I did not set up IPv6 for Calico, may do it later
*   Figure out how to set up Service for Kubernetes Dashboard
*   Add more nodes

# Resources

I used and found following resources useful:

*   Guides
    -   [Kubernetes clusters for the hobbyist](https://github.com/hobby-kube/guide)
    -   [Creating a single control-plane cluster with kubeadm](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm/)
*   Container runtimes
    *   [Documentation on Container runtimes](https://kubernetes.io/docs/setup/production-environment/container-runtimes/)
*   Networking:
    *   [Understanding Kubernetes networking: pods](https://medium.com/google-cloud/understanding-kubernetes-networking-pods-7117dd28727)
    *   [Documentation on Networking in Kubernetes](https://kubernetes.io/docs/concepts/cluster-administration/networking/)
    *   [Comparing Kubernetes CNI Providers: Flannel, Calico, Canal, and Weave](https://rancher.com/blog/2019/2019-03-21-comparing-kubernetes-cni-providers-flannel-calico-canal-and-weave/)
    *   [Introduction to Calico](https://docs.projectcalico.org/introduction/)
    *   [Get Calico up and running in your Kubernetes cluster](https://docs.projectcalico.org/getting-started/kubernetes/)
    *   [Enable dual stack in Calico](https://docs.projectcalico.org/networking/dual-stack)
    *   [Enabling IPv6 support in Calico](https://docs.projectcalico.org/networking/ipv6)
    *   [Dual Stack Operation with Calico on Kubernetes](https://www.projectcalico.org/dual-stack-operation-with-calico-on-kubernetes/)
    *   [Enable IPv6 on Kubernetes with Project Calico](https://www.projectcalico.org/enable-ipv6-on-kubernetes-with-project-calico/)
*   etcd
    -   [A Guide to Kubernetes Etcd: All You Need to Know to Set up Etcd Clusters](https://superuser.openstack.org/articles/a-guide-to-kubernetes-etcd-all-you-need-to-know-to-set-up-etcd-clusters/)
    -   [Bootstrapping an etcd Cluster with TLS using Kubeadm](https://blog.scottlowe.org/2018/08/21/bootstrapping-etcd-cluster-with-tls-using-kubeadm/)
    -   [More on Setting up etcd with Kubeadm](https://blog.scottlowe.org/2018/10/29/more-on-setting-up-etcd-with-kubeadm/)
    -   [Setting up etcd with Kubeadm, containerd Edition](https://blog.scottlowe.org/2020/04/02/setting-up-etcd-with-kubeadm-containerd-edition/)
    -   [etcd transport security model](https://github.com/etcd-io/etcd/blob/master/Documentation/op-guide/security.md)
