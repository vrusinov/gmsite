After setting up my shiny [single-node Kubernetes "cluster"](en/posts/2020/setting-up-single-node-kubernetes-cluster/) I wanted to do something useful with it. Many of the useful things require your useful data not to disappear, so I needed to figure out how to do that.

In Kubernetes [storage is organized](https://kubernetes.io/docs/concepts/storage/) via Volumes. These Volumes can be attached to Pods via Volume Claims. There are two types of Volumes: regular ones and Persistent Volumes. Regular Volumes are ephemeral and destroyed together with Pods (e.g. when it crashes or rescheduled). These are of course less interesting than Persistent Volumes which as the name suggest survive Pod restarts.

There are many ways to implement Persistent Volumes, the simplest is probably to use [Local Persistent Volumes](https://kubernetes.io/blog/2019/04/04/kubernetes-1.14-local-persistent-volumes-ga/). They simply bind local directory into pod. However they force pods to be always running on the same node.

This was not interesting enough for me so I went with something more complicated.

<!-- TEASER_END -->

# Choosing storage provider

As with many things in Kubernetes there are many ways to implement Persistent Volumes.

When running on top of public cloud the choice is fairly obvious: it's usually best to use the Cloud's virtual block device such as [gcePersistentDisk](https://kubernetes.io/docs/concepts/storage/volumes/#gcepersistentdisk) or [awsElasticBlockStore](https://kubernetes.io/docs/concepts/storage/volumes/#awselasticblockstore).

I only had my poor server-laptop, potential to add more hosts in the future, and no virtual block device providers. So I had to build my own virtual block devices or filesystems.

Here we have Gluster, EdgeFS and Ceph. The latter seemed to be the most interesting to me (and most familiar - I was an SRE for a [very similar system](https://www.systutorials.com/colossus-successor-to-google-file-system-gfs/)).

# Planning Ceph installation

I had the single node with 3 different devices to play with. The node is just an old laptop that I use as a home server. It has:

*   tiny 20G SSD, where the system is installed, mounted as /
*   larger (but slower) HDD
*   even larger (and even slower) USB-HDD

By default Ceph requires at least 3 different nodes with at least one storage device each. However it is possible to configure Ceph's [CRUSH](https://docs.ceph.com/docs/jewel/rados/operations/crush-map/) to accept a single node.

Thus I decided I'd use replicated bucket with min_size of 2. So each piece of data will be stored at least 2 times on two different devices. This way I won't lose any data if one of the storage devices fails. And of course I'd lose everything if the whole laptop dies. This is OK for a home system, and I may add more hardware in the future.

# Deploying Ceph

There seems to be two ways of deploying Ceph:

1.  Manually outside of Kubernetes (installing via OS packages)
2.  On top of Kubernetes.

Setting Ceph manually seemed to be a lot of hassle. There's just too many components.

For option 2 [Rook](https://rook.io/) is the most popular solution. Rook is a Kubernetes Operator - essentially a set of tools which make it easier to deploy and manage Ceph and other storage systems on top of Kubernetes. That's what I decided to use.

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

Make sure we have the resources:

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

## Defining and creating a cluster

Modern versions of Ceph use ["Bluestore"](https://ceph.io/community/new-luminous-bluestore/) as a storage engine. Bluestore works on top of raw block devices, so for this installation I'd leave small SSD for a system, will use part of the second HDD, and will use entire USB-HDD for Ceph.

LVM2 must be still installed:

```bash
sudo dnf install lvm2
```

Next, it was necessary to deploy manifests to create a basic Ceph cluster. These run components of Ceph: manager, monitor, OSD and several others. OSDs are probably the most interesting component - they do the actual interaction with storage devices, and there will be one per device.

Since I used non-standard Ceph setup with just two devices I had to tweak sample manifests quite a bit. Here's `cluster.yaml`:

```yaml
#################################################################################################################
# Define the settings for the rook-ceph cluster with common settings for a production cluster.
# All nodes with available raw devices will be used for the Ceph cluster. At least three nodes are required
# in this example. See the documentation for more details on storage settings available.

# For example, to create the cluster:
#   kubectl create -f common.yaml
#   kubectl create -f operator.yaml
#   kubectl create -f cluster.yaml
#################################################################################################################

kind: ConfigMap
apiVersion: v1
metadata:
  name: rook-config-override
  namespace: rook-ceph
data:
  config: |
    [global]
    osd_pool_default_size = 1
---
apiVersion: ceph.rook.io/v1
kind: CephCluster
metadata:
  name: rook-ceph
  namespace: rook-ceph
spec:
  cephVersion:
    image: ceph/ceph:v14.2.10
    allowUnsupported: false
  dataDirHostPath: /var/lib/rook
  skipUpgradeChecks: false
  continueUpgradeAfterChecksEvenIfNotHealthy: false
  mon:
    # This is one of the tweaks - normally you'd want more than one monitor and
    # you'd want to spread them out
    count: 1
    allowMultiplePerNode: true
  mgr:
    modules:
    - name: pg_autoscaler
      enabled: true
  dashboard:
    enabled: true
    ssl: true
  monitoring:
    # requires Prometheus to be pre-installed
    enabled: false
    rulesNamespace: rook-ceph
  network:
    # Enable host networking. This is useful if we want to mount ceph outside of
    # Kubernetes virtual network.
    provider: host
  rbdMirroring:
    workers: 0
  crashCollector:
    disable: false
  cleanupPolicy:
    confirmation: ""
  annotations:
  resources:
  removeOSDsIfOutAndSafeToRemove: false
  # This is an interesting section - it determines which devices will be
  # considered to be part of bluestore. Devices must be empty. Use wipefs to
  # clean them up.
  storage:
    useAllNodes: true
    useAllDevices: false
    devices:
    #
    # HDD:
    - name: "/dev/disk/by-id/ata-Hitachi_HTS545050A7E380_TE85113Q0J4S5R-part2"
    # USB-HDD:
    # by-id does not work due to a bug
    #- name: "/dev/disk/by-id/usb-WD_Elements_1042_57584C314139313237333936-0:0"
    - name: "sdc"
    config:
      osdsPerDevice: "1"
      storeType: bluestore
  disruptionManagement:
    managePodBudgets: false
    osdMaintenanceTimeout: 30
    manageMachineDisruptionBudgets: false
    machineDisruptionBudgetNamespace: openshift-machine-api
```

Another useful this to have is a toolbox - will help me maintain Ceph without
having to install Ceph tools on my hosts. Here's toolbox.yaml:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: rook-ceph-tools
  namespace: rook-ceph
  labels:
    app: rook-ceph-tools
spec:
  dnsPolicy: ClusterFirstWithHostNet
  containers:
  - name: rook-ceph-tools
    image: rook/ceph:v1.3.8
    command: ["/tini"]
    args: ["-g", "--", "/usr/local/bin/toolbox.sh"]
    imagePullPolicy: IfNotPresent
    env:
      - name: ROOK_ADMIN_SECRET
        valueFrom:
          secretKeyRef:
            name: rook-ceph-mon
            key: admin-secret
    securityContext:
      privileged: true
    volumeMounts:
      - mountPath: /etc/ceph
        name: ceph-config
      - name: mon-endpoint-volume
        mountPath: /etc/rook
  hostNetwork: true
  volumes:
    - name: mon-endpoint-volume
      configMap:
        name: rook-ceph-mon-endpoints
        items:
        - key: data
          path: mon-endpoints
    - name: ceph-config
      emptyDir: {}
```

Let's apply these two and see them in action:

```bash
kubectl apply -f cluster.yaml
# Let us also deploy a toolbox - will help us monitor cluster status.
kubectl apply -f toolbox.yaml
```

Check pods:

```
$ kubectl get pod -n rook-ceph
NAME                                                              READY   STATUS        RESTARTS   AGE
csi-cephfsplugin-provisioner-7469b99d4b-6wwdk                     5/5     Running       1          3d16h
csi-cephfsplugin-provisioner-7469b99d4b-mj2zc                     5/5     Running       2          3d16h
csi-cephfsplugin-rl2zf                                            3/3     Running       0          3d16h
csi-rbdplugin-hw8fh                                               3/3     Running       0          3d16h
csi-rbdplugin-provisioner-865f4d8d-dp5d9                          6/6     Running       4          3d16h
csi-rbdplugin-provisioner-865f4d8d-r2wlf                          6/6     Running       0          3d16h
rook-ceph-crashcollector-krusty.home.greenmice.info-75fdd66f7q2   1/1     Running       0          137m
rook-ceph-mgr-a-64fd77c8fd-fhc4n                                  1/1     Running       4          4d14h
rook-ceph-mon-a-cb5b84f5c-wjqjb                                   1/1     Running       5          4d14h
rook-ceph-operator-6cc9c67b48-ltvxm                               1/1     Running       1          3d16h
rook-ceph-operator-6cc9c67b48-m875j                               0/1     Terminating   8          4d14h
rook-ceph-osd-0-7cd6975767-swtgr                                  1/1     Running       0          137m
rook-ceph-osd-1-7b87f564fc-mcbd5                                  1/1     Running       0          137m
rook-ceph-osd-prepare-krusty.home.greenmice.info-zsjd2            0/1     Completed     0          129m
rook-ceph-tools                                                   1/1     Running       0          100s
rook-discover-htxkp                                               1/1     Running       0          3d16h

$ kubectl -n rook-ceph exec -it rook-ceph-tools -- ceph status
  cluster:
    id:     6ab148e7-fd6e-4132-bdaf-e5ce7934d2cb
    health: HEALTH_OK

  services:
    mon: 1 daemons, quorum a (age 17h)
    mgr: a(active, since 2h)
    osd: 2 osds: 2 up (since 2h), 2 in (since 2h)

  data:
    pools:   0 pools, 0 pgs
    objects: 0 objects, 0 B
    usage:   2.0 GiB used, 1.3 TiB / 1.3 TiB avail
    pgs:
```

## Using Ceph - test filesystem

The above does not create any Ceph 'pools' - we have Ceph components but no
storage is actually usable. I've created one for test and mounted to my
workstation outside of the Kubernetes cluster.

To do this slightly modified `filesystem-test.yaml` from examples directory. I
changed name and flipped `activeStandby` to false. Note this pool has replica
size of 1 so it does not provide any redundancy.

```yaml
apiVersion: ceph.rook.io/v1
kind: CephFilesystem
metadata:
  name: test-fs
  namespace: rook-ceph
spec:
  metadataPool:
    replicated:
      size: 1
      requireSafeReplicaSize: false
  dataPools:
    - failureDomain: osd
      replicated:
        size: 1
        requireSafeReplicaSize: false
      compressionMode: none
  preservePoolsOnDelete: false
  metadataServer:
    activeCount: 1
    activeStandby: false
```

Applied via:

```bash
kubectl apply -f filesystem-test.yaml
```

After this I could see my test-fs in the `ceph status` output:

```shell
$ kubectl -n rook-ceph exec -it rook-ceph-tools -- ceph status
  cluster:
    id:     6ab148e7-fd6e-4132-bdaf-e5ce7934d2cb
    health: HEALTH_WARN
            2 pool(s) have no replicas configured

  services:
    mon: 1 daemons, quorum a (age 20h)
    mgr: a(active, since 4h)
    mds: test-fs:1 {0=test-fs-b=up:active} 1 up:standby-replay
    osd: 2 osds: 2 up (since 5h), 2 in (since 5h)

  task status:
    scrub status:
        mds.test-fs-a: idle
        mds.test-fs-b: idle

  data:
    pools:   2 pools, 64 pgs
    objects: 22 objects, 2.2 KiB
    usage:   2.0 GiB used, 1.3 TiB / 1.3 TiB avail
    pgs:     64 active+clean

  io:
    client:   1.2 KiB/s rd, 2 op/s rd, 0 op/s wr
```

Now, in order to mount it I needed to know address of the monitor service and a
secret. There are probably better ways to do this but for test this can be
obtained via these two commands:

``` shell
$ kubectl -n rook-ceph exec -it rook-ceph-tools -- grep mon_host /etc/ceph/ceph.conf
mon_host = 192.168.0.54:6789
$ kubectl -n rook-ceph exec -it rook-ceph-tools -- grep key /etc/ceph/keyring
key = A<xxx>g==
```

Or, to save in variables:

```bash
mon_host=$(kubectl -n rook-ceph exec -it rook-ceph-tools -- grep mon_host /etc/ceph/ceph.conf | cut -d " " -f 3 | tr -d '\r')
ceph_secret=$(kubectl -n rook-ceph exec -it rook-ceph-tools -- grep key /etc/ceph/keyring | cut -d " " -f 3 | tr -d '\r')
```

In order to mount it the kernel needs to be compiled with Ceph support, and Ceph tools must be installed. My client was Gentoo and I was able to install Ceph tools via following command:

```bash
sudo emerge -av sys-cluster/ceph
```

And mount:

```bash
sudo mkdir -p /mnt/ceph-test
sudo mount -t ceph -o mds_namespace=test,name=admin,secret=$ceph_secret $mon_host:/ /mnt/ceph-test

# By default permissions set to be only writable by root
sudo touch /mnt/ceph-test/test
sudo rm /mnt/ceph-test/test
```

## Using Ceph - "prod" filesystem

Filesystem with redundancy of 1 would obviously have terrible durability. Ceph recommends replication factor of 3 or using Reed-Solomon encoding.

I used replication of 2 instead. It still has poor durability. Not only because 2 device failures may result in data loss, but also if there is some form of corruption (e.g. due to bitrot or sudden crash), Ceph may not be able to determine which one of the two replicas is correct. Still, it's good enough for my purpose.

I removed test filesystem created earlier and created a proper one:

```yaml
# https://github.com/rook/rook/blob/master/Documentation/ceph-filesystem.md
apiVersion: ceph.rook.io/v1
kind: CephFilesystem
metadata:
  name: replicated2
  namespace: rook-ceph
spec:
  metadataPool:
    replicated:
      size: 2
      requireSafeReplicaSize: true
  dataPools:
    #  'failureDomain: osd' protects from a single osd crash or single device
    # failure but not from the whole node failure.
    - failureDomain: osd
      replicated:
        size: 2
        requireSafeReplicaSize: true
      compressionMode: aggressive
  preservePoolsOnDelete: false
  metadataServer:
    activeCount: 1
    activeStandby: false
```

Another thing that is required is a StorageClass. Without it, the filesystem
would be created but it won't be possible to reference it via
PersistentVolumeClaim.

```yaml
# https://github.com/rook/rook/blob/master/Documentation/ceph-filesystem.md
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: rook-cephfs
# Change "rook-ceph" provisioner prefix to match the operator namespace if needed
provisioner: rook-ceph.cephfs.csi.ceph.com
allowVolumeExpansion: true
parameters:
  # clusterID is the namespace where operator is deployed.
  clusterID: rook-ceph

  # CephFS filesystem name into which the volume shall be created
  fsName: replicated2

  # Ceph pool into which the volume shall be created
  # Required for provisionVolume: "true"
  pool: replicated2-data0

  # The secrets contain Ceph admin credentials. These are generated automatically by the operator
  # in the same namespace as the cluster.
  csi.storage.k8s.io/provisioner-secret-name: rook-csi-cephfs-provisioner
  csi.storage.k8s.io/provisioner-secret-namespace: rook-ceph
  csi.storage.k8s.io/controller-expand-secret-name: rook-csi-cephfs-provisioner
  csi.storage.k8s.io/controller-expand-secret-namespace: rook-ceph
  csi.storage.k8s.io/node-stage-secret-name: rook-csi-cephfs-node
  csi.storage.k8s.io/node-stage-secret-namespace: rook-ceph

reclaimPolicy: Delete
```

And that was enough to be able to use CephFS as persistent volumes for my Kubernetes Pods, e.g. for [Jellyfin](https://jellyfin.org/):

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: jellyfin-config
  namespace: media
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: rook-cephfs
  resources:
    requests:
      storage: 1Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: media
  namespace: media
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: rook-cephfs
  resources:
    requests:
      storage: 100Gi
---
# Jellyfin deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jellyfin-deployment
  labels:
    app: jellyfin
  namespace: media
spec:
  replicas: 1
  strategy:
    type: Recreate
  selector:
    matchLabels:
      app: jellyfin
  template:
    metadata:
      labels:
        app: jellyfin
    spec:
      containers:
      - name: jellyfin
        image: linuxserver/jellyfin:version-10.7.5-1
        ports:
        - containerPort: 8096
        env:
        - name: TZ
          value: "Europe/Dublin"
        - name: UMASK
          value: "000"
        - name: PUID
          value: "1000"
        - name: PGID
          value: "1000"
        volumeMounts:
        - name: media
          mountPath: /data
        - name: jellyfin-config
          mountPath: /config
        resources:
          limits:
            cpu: "4"
            memory: "1Gi"
          requests:
            cpu: "10m"
            memory: "512Mi"
      securityContext:
        fsGroup: 1000
        fsGroupChangePolicy: "OnRootMismatch"
      volumes:
        - name: media
          persistentVolumeClaim:
            claimName: media
        - name: jellyfin-config
          persistentVolumeClaim:
            claimName: jellyfin-config
```

# Conclusion

Open-source cluster filesystems are here and available for hobbyists. Learning about them and setting everything up took many evenings (I did not mention many mistakes I did in this article), but now I have my own cluster filesystem.

I did not actually use it for anything yet. Per documentation it should be a matter of creating non-test CephFilesystem and referencing it in Persistent Volume Claim of deployments. I may write about it in the future.

# Future work

*   Add more nodes, and increase number of monitors to 3.
*   Upgrade to Ceph 15.

# Links

*   Overview:
    -   [Rook website](https://rook.io)
    -   [To Rook, or not to Rook, that's Kubernetes](https://medium.com/flant-com/to-rook-in-kubernetes-df13465ff553)
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
