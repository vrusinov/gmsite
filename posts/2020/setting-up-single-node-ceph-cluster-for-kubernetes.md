After setting up my shiny [single-node Kubernetes "cluster"](en/posts/2020/setting-up-single-node-kubernetes-cluster/) I wanted to do something useful with it. Many of the useful things require your useful data not to disappear, so I needed to figure out how to do that.

In Kubernetes [storage is organized](https://kubernetes.io/docs/concepts/storage/) via Volumes which can be attached to Pods via Volume Claims. More specifically I was interested in Persistent Volumes. Regular Volumes are ephemeral and destroyed together with Pods (e.g. when it crashes or rescheduled), so these are relatively easy. In contrast, Persistent Volumes stay around until explicitly deleted.

There are many ways to implement Persistent Volumes, the simplest is probably to use [Local Persistent Volumes](https://kubernetes.io/blog/2019/04/04/kubernetes-1.14-local-persistent-volumes-ga/). They simply bind local directory into pod. However they force pods to be running on the same node.

This was of course too simple for me. I had plans to add more nodes in the future. I was also on over-engineering crusade already and wanted to play with some open-source cluster filesystem. So I decided to create single-node "distributed" storage "cluster".

<!-- TEASER_END -->

# Choosing storage provider

When running on top of public cloud the choice is fairly obvious: it's usually best to use the Cloud's virtual block device such as [gcePersistentDisk](https://kubernetes.io/docs/concepts/storage/volumes/#gcepersistentdisk) or [awsElasticBlockStore](https://kubernetes.io/docs/concepts/storage/volumes/#awselasticblockstore).

I only had my poor server-laptop and no virtual block device providers. So I had to build my own virtual block devices or filesystems.

Here we have Gluster, EdgeFS and Ceph. The latter seemed to be the most interesting to me (and most familiar as I work with- and was even SRE for a [very similar system](https://www.systutorials.com/colossus-successor-to-google-file-system-gfs/)).

# Planning Ceph installation

I had the single node with 3 different devices to play with. The node is just an old laptop that I use as a hope server. It has:

*   tiny 20G SSD, where the system is installed, mounted as /
*   larger (but slower) HDD, mounted at /data
*   even larger (and even slower) USB-HDD, mounted at /mnt/usb-hdd/

All of this devices were already partitioned with ext4 filesystems created, and they already had some files on them (which I did not want to remove).

Normally, for Ceph we'd need at least 3 different nodes with at least one storage device on each one. However it is possible to configure Ceph's [CRUSH](https://docs.ceph.com/docs/jewel/rados/operations/crush-map/) to accept single node.

I'd use replicated bucket with min_size and max_size of 2. So each piece of data will be stored at least 2 times on two different devices. This way I won't lose any data if one of the storage devices fails. It will however won't accept new writes before I add more storage devices (as 20G SSD is likely won't be usable due to its size). And of course nothing will work if my "server" crashes.

# Deploying Ceph

There seems to be generally two ways to deploy Ceph:

1.  Deploy manually outside of Kubernetes (installing via OS packages)
2.  Deploy on top of Kubernetes.

For option 2 there are solutions like [Rook](https://rook.io/). Rook is a Kubernetes Operator and it essentially a set of tools which make it easier to deploy and manage Ceph and a few other storage systems on top of Kubernetes.

## Creating Rook manifest

```bash
git clone https://github.com/rook/rook
cd rook
git checkout v1.3.8
cd cluster/examples/kubernetes/ceph
```

## Create common resources:

```bash
kubectl create -f common.yaml
```

Make sure we have resources:

```bash
$ kubectl explain cephclusters
KIND:     CephCluster
VERSION:  ceph.rook.io/v1

DESCRIPTION:
     <empty>
```

## Create operator:

```bash
kubectl create -f operator.yaml
```

Check for its status:

```bash
$ kubectl get pod -n rook-ceph
NAME                                  READY   STATUS    RESTARTS   AGE
rook-ceph-operator-6cc9c67b48-m875j   1/1     Running   0          15s
```

## Defining and creating a cluster.

Prepare host:

```bash
sudo dnf install lvm2
```

This step will create OSD (Object Storage Daemon - a service responsible for storing chunks of data on individual disks). It won't create any pools yet, so we'll have individual disks exposed to Ceph but won't be able to actually use them yet.

I had to tweak a few things as I was not sure if Rook will discover my devices correctly.

TODO: list cluster.yaml
TODO: list toolbox.yaml

```bash
kubectl apply -f cluster.yaml
# Let us also deploy a toolbox - will help us monitor cluster status.
kubectl apply -f toolbox.yaml
```

Check pods:

```
$ kubectl get pod -n rook-ceph
NAME                                                              READY   STATUS    RESTARTS   AGE
csi-cephfsplugin-kh4r6                                            3/3     Running   0          3m21s
csi-cephfsplugin-provisioner-7469b99d4b-8b8nj                     5/5     Running   0          3m21s
csi-cephfsplugin-provisioner-7469b99d4b-mckfq                     5/5     Running   0          3m21s
csi-rbdplugin-provisioner-865f4d8d-ksrg6                          6/6     Running   0          3m21s
csi-rbdplugin-provisioner-865f4d8d-l8x6l                          6/6     Running   0          3m21s
csi-rbdplugin-qk7pk                                               3/3     Running   0          3m21s
rook-ceph-crashcollector-krusty.home.greenmice.info-757455b57jb   1/1     Running   0          119s
rook-ceph-mgr-a-cf5b85d54-kbgrg                                   1/1     Running   0          2m1s
rook-ceph-mon-a-5bf98c9d49-k6g48                                  1/1     Running   0          2m53s
rook-ceph-operator-6cc9c67b48-g8cm7                               1/1     Running   0          107m
rook-discover-xfnpw                                               1/1     Running   0          106m
$ kubectl -n rook-ceph exec -it rook-ceph-tools -- ceph status
  cluster:
    id:     54da5076-3190-4558-b60e-9aa715fa774a
    health: HEALTH_WARN
            OSD count 0 < osd_pool_default_size 3
            mon a is low on available space

  services:
    mon: 1 daemons, quorum a (age 20m)
    mgr: a(active, since 19m)
    osd: 0 osds: 0 up, 0 in

  data:
    pools:   0 pools, 0 pgs
    objects: 0 objects, 0 B
    usage:   0 B used, 0 B / 0 B avail
    pgs:
```

# Future work

*   Add more nodes, and increase number of monitors to 3.
*   Upgrade to Ceph 15.

# Links

*   Overview:
    -   [Rook website](https://rook.io)
    -   [To Rook, or not to Rook, that’s Kubernetes](https://medium.com/flant-com/to-rook-in-kubernetes-df13465ff553)
    -   [What is Rook? Ceph Storage Integration on Kubernetes with Rook](https://medium.com/faun/what-is-rook-ceph-storage-integration-on-kubernetes-with-rook-9fa3f3487b90)
    -   [Rook more than Ceph](https://the-report.cloud/rook-more-than-ceph)
*   Guides:
    -   [The Ultimate Rook and Ceph Survival Guide](https://www.cloudops.com/2019/05/the-ultimate-rook-and-ceph-survival-guide/)
    -   [Kubernetes clusters for the hobbyist](https://github.com/hobby-kube/guide)
    -   [Deploy A Ceph Cluster On Kubernetes With Rook](https://itnext.io/deploy-a-ceph-cluster-on-kubernetes-with-rook-d75a20c3f5b1)
    -   [Expose a Rook-based Ceph cluster outside of Kubernetes](https://www.adaltas.com/en/2020/04/16/expose-ceph-from-rook-kubernetes/)
    -   [Ceph in a single node cluster](https://blog.virtengine.com/ceph-in-a-single-node/)
*   Documentation:
    -   [Ceph Advanced Configuration](https://rook.io/docs/rook/v1.3/ceph-advanced-configuration.html)
    -   [Deprecate directory-based and Filestore OSDs](https://github.com/rook/rook/issues/3379)
    -   [Ceph Prerequisites](https://rook.io/docs/rook/v1.3/ceph-prerequisites.html)
