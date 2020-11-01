This post is a follow-up to
[a post where I talk about backups strategy](/en/posts/2020/backups-part-1-strategy/).

Here I describe my solution for file backups from my Linux computers, and don't
yet go into the subject of other devices and online services.

After some experimentation I decided to use [restic](https://restic.net/) for this. Restic is a modern, open-source backup program with an active community. It is written in Go. It runs on Linux (but also BSD, Mac and Windows) and can back up to local disks as well as remote/cloud services.

And as I wanted my backups to be cheap, "pay as you go" and off-site I've opted to use Backblaze for storage.

# Why restic?

<!-- TEASER_END -->

## Advantages

-   It can be distributed as a single, statically-compiled executable. It is also packaged for most of the Linux distributions.
-   It is a relatively simple client program, no server needed. The client has everything to back up your data.
-   It de-duplicates files regardless of where they come from. So if you have same files in different folders or machines, it will only store them once.
-   All backups are incremental. Obviously first backup will take a long time since there is nothing to increment against. Subsequent, and again even for different folders and machines will only copy files that don't exist in repository.
-   Supports almost any storage backend you can imagine. It is even possible to "Raid 0" several via [rclone backend](https://restic.net/blog/2018-04-01/rclone-backend/).
-   Encrypts all data.

## Disadvantages

- The fact it is has no server can be a disadvantage. In my case this means that I am forced to give Backblaze access key and restic respository password on each machine. This means each machine I own have full write permissions to Backblaze, and if it is compromised all data from all of my machines can be stolen, and all backups can be wiped. I find this an acceptable risk and have following mitigations:
  - backup script (which contains those keys and passwords) is only readable by a `root` user.
  - all of the local disks, especially on laptops are encrypted
  - I will immediately revoke and regenerate Backblaze keys if I suspect anything.
- Garbage collection may be problematic. In restic it is done in two steps. First, older backups (or "snapshots" in restic terminology) are marked for deletion. This only removes snapshot descriptors and leaves blobs of the data around. Then 'prune' operation does a garbage collection and removes unreferenced data. The prune operation is extremely slow and locks the whole respository (so no backups can take place while it's running). My repository is a little bit over 1 TiB and it's close to be impossible to prune: it's just takes too long. Thankfully there is a [very promising pull request](https://github.com/restic/restic/pull/2718) with prune re-implementation, and I hope it will be included in the next restic version.

# Why Backblaze?

Simply because it seemed to be the cheapest. There is a gotcha: downloads from Backblaze can be very expensive, so it will be expensive I ever need to restore large amount of data.

I believe all of Backblaze dataceners are in US, and I would have preferred to keep my backups closer somewhere in EU. But nothing matches their prices (not even things like Amazon Glacier).

# Using restic

## Backup script

I use the following script on my machines:

```bash
#!/bin/bash

set -e

# Change these with your own IDs and passwords.
# RESTIC_PASSWORD is something your data will be encrypted with.
export B2_ACCOUNT_ID=<...>
export B2_ACCOUNT_KEY=<...>
export RESTIC_PASSWORD=<...>
REPO="b2:<...>:restic"

DIRS="/home/* /mnt/* /media/*"
FILTERS="/etc/restic/filters"

LOG="/var/log/backup.log"
OLD_LOG="/var/log/backup.log.old"

test -e $LOG && mv $LOG $OLD_LOG

# Retries a command on failure.
# $1 - the max number of attempts
# $2... - the command to run
retry() {
    local -r -i max_attempts="$1"; shift
    local -r cmd="$@"
    local -i attempt_num=1

    until $cmd
    do
        if (( attempt_num == max_attempts ))
        then
            echo "Attempt $attempt_num failed and there are no more attempts left!"
            return 1
        else
            echo "Attempt $attempt_num failed! Trying again in $(( attempt_num*attempt_num )) seconds..."
            sleep $(( attempt_num*attempt_num++ ))
        fi
    done
}

for dir in $DIRS; do
  if [ -d "$dir" ] ; then
    cd "$dir"
    date >> $LOG
    echo "backing up $dir" >> $LOG
    retry 14 restic -r b2:${REPO?}:restic --verbose --exclude-file /etc/restic/filters backup $dir >> $LOG
  fi
done
```

This script will create restic snapshots for each of the directories in `/home` (so one snapshot per user), and each of directories in `/mnt` (if any). The backup itself will be retried for up to 14 times with increasing delays between attempts.

`/etc/restic/filters` is a file which simply contains files which don't need to be backed up. A part of it:

```
*.bak
*.log.1
*.thumb.png
/home/*/.cache/
/home/*/.cmake/
/home/*/.config/google-chrome-beta/
/home/*/.config/google-chrome/
/home/*/.config/pulse/
/home/*/.dbus/
/home/*/.kde/cache-*
/home/*/.kde/share/apps/okular/docdata/
/home/*/.kde/share/apps/RecentDocuments/
/home/*/.pulse-cookie
/home/*/.pulse/
/home/*/.xsession-errors*
/mnt/windows/*
debug.log
```

Now, I simply put this file into `cron.daily` directory on all machines I have, making sure it is only readable by root (e.g. by running `chmod 700 /etc/cron.daily/backup.sh`).

## Garbage collection

As I mentioned above, garbage collection is the painful part. Here's the script I used before:

```bash
#!/bin/bash

set -e

export B2_ACCOUNT_ID=<...>
export B2_ACCOUNT_KEY=<...>
export RESTIC_PASSWORD=<...>

LOG="/var/log/backup_clean.log"
OLD_LOG="/var/log/backup_clean.log.old"

# Retries a command on failure.
# $1 - the max number of attempts
# $2... - the command to run
retry() {
    local -r -i max_attempts="$1"; shift
    local -r cmd="$@"
    local -i attempt_num=1

    until $cmd
    do
        if (( attempt_num == max_attempts ))
        then
            echo "Attempt $attempt_num failed and there are no more attempts left!"
            return 1
        else
            echo "Attempt $attempt_num failed! Trying again in $(( attempt_num*attempt_num )) seconds..."
            sleep $(( attempt_num*attempt_num++ ))
        fi
    done
}

test -e $LOG && mv $LOG $OLD_LOG

retry 100 restic -r b2:${REPO?}:restic forget \
    --keep-last 3 \
    --keep-daily 3 \
    --keep-weekly 3 \
    --keep-monthly 3 >> ${LOG}
retry 100 restic -r b2:${REPO?}:restic prune >> ${LOG}
```

I've tried to run it weekly on one of my home machines, but my weak 20 Mbits uplink was not just fast enough. In current implementation prune may rewrite a lot of "packs", moving a lot of data around.

So I needed to run it in place with better connectivity. For this I've created another Kubernetes cluster, similarly to [what I did with my home server](/en/posts/2020/setting-up-single-node-kubernetes-cluster/) and few machines I have here. This new cluster was set up on two [Hetzner cloud machines](https://www.hetzner.com/cloud). I won't write about it as it is very similar setup to what I previously described.

On this cluster I use the following manifest to run prune once a week:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: restic-cache
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: hcloud-volumes
---
apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: prune
spec:
  # minute, hour, day of month, month, day of week
  # Chosen randomly - pelase do not copy.
  schedule: "27 15 * * 6"
  # 3 days
  startingDeadlineSeconds: 259200
  concurrencyPolicy: Forbid
  jobTemplate:
    spec:
      template:
        spec:
          # 6 days
          activeDeadlineSeconds: 518400
          restartPolicy: OnFailure
          containers:
          - name: prune
            image: restic/restic
            resources:
              requests:
                memory: "1Gi"
            command: ["/bin/sh"]
            args: ["-c", "restic --cache-dir /cache -r b2:<...>:restic unlock && restic -v --cache-dir /cache -r b2:<...>:restic forget --keep-last 3 --keep-daily 3 --keep-weekly 3 --keep-monthly 3 && restic --cache-dir /cache -r b2:<...>:restic prune"]
            env:
              - name: B2_ACCOUNT_ID
                value: "<...>"
              - name: B2_ACCOUNT_KEY
                value: "<...>"
              - name: RESTIC_PASSWORD
                value: "<...>"
            volumeMounts:
            - name: restic-cache
              mountPath: /cache
          volumes:
          - name: restic-cache
            persistentVolumeClaim:
              claimName: restic-cache
```

The `PersistentVolumeClaim` is technically not necessary but should speed things up a bit so that restic is able to re-use some of the previously downloaded data.

# Summary

So there we have it. It covers all of my local file backup needs - for now. Backups of non-Linux devices and online services is not a solved problem yet. I hope to be able to write about that in the future.

Just to remind, here's the summary of what data I have:

| Description                 | Importance | Backed up?                          |
| --------------------------- | ---------- | ----------------------------------- |
| **Files**                   |            |                                     |
| `/home`                     | High       | <span class="hl-green">Y</span>     |
| `/etc`                      | Low        | <span class="hl-green">N</span>     |
| `/var`                      | Low        | <span class="hl-green">N</span>     |
| `/root`                     | Low        | <span class="hl-green">N</span>     |
| `/media` and `/mnt`         | Medium     | <span class="hl-green">Y</span>     |
| `/mnt/windows`              | Low        | <span class="hl-green">N</span>     |
| `/bin`, `/usr`, `/lib`, etc | Low        | <span class="hl-green">N</span>     |
| **Devices**                 |            |                                     |
| Phones                      | Low        | <span style="color:green">N</span>  |
| Virgin router               | Low        | <span style="color:green">N</span>  |
| UniFi Dream Machine         | Medium     | <span style="color:orange">N</span> |
| Chromecast / Google TV      | Low        | <span style="color:green">N</span>  |
| **Online Services**         |            |                                     |
| Facebook                    | Medium     | <span style="color:orange">N</span> |
| Feedly                      | Medium     | <span style="color:orange">N</span> |
| GitHub                      | Medium     | <span style="color:orange">N</span> |
| Gmail                       | High       | <span style="color:red">N</span>    |
| Google Calendar             | High       | <span style="color:red">N</span>    |
| Google Drive                | High       | <span style="color:red">N</span>    |
| Google Keep                 | Medium     | <span style="color:orange">N</span> |
| Netatmo                     | Medium     | <span style="color:orange">N</span> |
| Password manager            | High       | <span style="color:red">N</span>    |
| ProtonMail                  | Medium     | <span style="color:orange">N</span> |
| WhatsApp                    | Low        | <span style="color:green">N</span>  |
| YouTube                     | Medium     | <span style="color:orange">N</span> |
| YouTube music               | High       | <span style="color:green">N</span>  |

# Future work

The set up is not perfect and here's what I'd like to eventually improve:

- Monitoring for successful/unsuccessful backups. Currently I only get e-mail from cron, and only if local mail is set up properly.
- Add occasional truly offline backup. I may want to copy restic respotoroty to external HDD and ship it to my friends. This may help me recover things in case of some catastrophic failure of both my machines and my repository (e.g. if they are compromised or even just do something wacky as a result of e.g. corrupt memory).
- You may have noticed I don't use Kubernetes secrets to store B2 keys properly. This needs to be fixed.
- Keep looking around for solutions that don't make all of my data accessible to all backup clients.

# Alternatives considered

There's what I used or looked at previously.

## Duplicity

[Duplicity](http://duplicity.nongnu.org/) is a mature backup program. It is similar to restic in a lot of ways: it's a client program which can upload local files to some other local or remote places. I used it before and it worked quite well.

Advantages:

- Mature software, so it's likely close to be bug-free. It feels very secure.
- No problems with garbage collection - it simply removes files.
- Different machines/directories may use different encryption keys.
- Supports compression.

Disadvantages:

- No de-duplication across hosts. Each host is essentially on its own and have its own set of backup files, which don't intersect with others.
- It follows classic full/incremental backup model. So it must have full backups once in a while, and then able to take increments based on that. Practically this means for any reasonable retention policy two full backups must co-exist pretty much all the time. So it would use 2x amount of space.

## duplicati

[Duplicati](https://www.duplicati.com/) is another program similar to restic and Duplicity. It's not client/server. It is much closer to restic than to Duplicity. I used the older version so what I write below may not be true anymore.

Advantages:

- Have fancy lock-free algorithm. This means all operations on repository can happen in parrallel. Garbage collection does not block backups!

Disadvantages:

- The newer versions appears to be written in C# and requires Mono.
- The older version (which I used) while was technically open-source, was not very open. It felt more like commertial software.
- I had problems with older version crapping itself and corrupting repository. It appears this part [was entierly rewritten](https://www.duplicati.com/articles/Storage-Engine/) so it may be better now.

## Borg

[Borg Backup](https://github.com/borgbackup) is really cool and I really wanted to use it. It's a client/server application (unlike the above), it has great documentation and acvive community.

Unfortunately, it primarily works with local directories or over ssh. It does not appear to have support for any cloud providers, and I just don't have cheap off-site storage available over ssh. It is also not clear how well will it work with intermittent connections.

## Commertial solutions

Many of these are cool, however almost all operate on subscription basis, and limit number of computers (or are very expensive).
