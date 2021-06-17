**Author**: Vladimir Rusinov - [vladimir.rusinov@gmail.com](mailto:vladimir.rusinov@gmail.com) - [www.rusinov.ie](www.rusinov.ie)

**Proposed**: 2021-06-17

**Last update**: 2021-06-17

**Status**: proposed

View this document in: [Google docs](https://docs.google.com/document/d/1Psn_2Bw1UF9GNp8OXK4T_qts37gpqnKJjDSGpJUyfMw/edit#) | [www.rusinov.ie website](https://www.rusinov.ie/en/pages/design-proposal-cloud-service-backups-using-restic/) | Github

[TOC]

# Problem statement

Restic is a modern backup program that can backup your files. Individuals and SMBs may solve their file backup problem using restic.

However there is still a lot of data in cloud services, and it’s often more important than local files. E-mail, social network profile data, online documents and spreadsheets are often more important than data on one’s HDD or SSD. And while the majority of online/cloud providers do a good job at keeping the data safe and taking care of durability, mistakes still happen.

It is possible to be locked out of a cloud account (especially if it's a free one) or remove data accidentally. Sometimes services get it wrong and lose your data, or even just shut down.

The cloud data needs to be backed up too.

Some services make it possible (e.g. Google lets you get a copy of your data via Google Takeout), but almost none make it easy and convenient. Wouldn’t it be great if cloud data could be backed up just as easily as the local files using restic?

# Design proposal

## Summary

Restic already has an [‘FS’](https://github.com/restic/restic/blob/master/internal/fs/interface.go) interface which abstracts away filesystem access. There are implementations for local Windows and Unix filesystems. We can add ‘cloud’ filesystem implementations which will represent various objects as files. Depending on the backup target the corresponding ‘FS’ implementation will be chosen and the rest of the restic code will be unaware whether it is working with local filesystem or some virtual one representing some cloud service.

This idea is partially implemented by YoshieraHuang in pull request #[2995](https://github.com/restic/restic/pull/2995) (for sftp) and by  KrustyHack in pull request #[2223](https://github.com/restic/restic/issues/2223) (for Google Cloud Storage).

## UX

Pull requests #[2995](https://github.com/restic/restic/pull/2995) and #[2223](https://github.com/restic/restic/issues/2223) referenced above introduce a large number of additional flags to handle authentication. If we were to implement a dozen different backup sources, we’d have to add even more different flags (or environment variables), and it may quickly become messy.

It is also not clear how to choose the correct ‘FS’ implementation.

I propose to solve this via turning the backup source argument to be url-like and implementing authentication via configuration files. Examples:

*   `restic -r <repo> backup /home/user/` - will do a backup of local /home/user/ files.

*   `restic -r <repo> backup file:/home/user/` - same as above

*   `restic -r <repo> backup sftp:user@host/home/user/` - will log in as user@host via sftp and do a backup of /home/user/.

*   `restic -r <repo> backup gmail:/home/user/.config/restic/gmail-auth.conf` - will do a backup using ‘gmail’ ‘FS’ implementation and will use authentication from `/home/user/.config/restic/gmail-auth.conf` file.

And so on, with the general structure being <fs_implementation>:<path>.

It will be the responsibility of each fs implementation to interpret a path. For `file` FS implementation it will be a local directory. `gmail` may open and parse settings from a local file, etc.

Where possible different ‘FS’ implementations will share similar config format and behaviour.

## Restore

Restoring cloud backups may not be straightforward. It is easy to restore filesystem-like ‘sftp’ or ‘gcs’ data by copying/uploading files to corresponding service. However ‘facebook’ or ‘strava’ may not provide the ability to restore data in an automated way, if at all.

restic will provide tools to convert mounted (e.g. via fuse) backup to something usable. Having social network post history in some human- and machine-readable formats may be still worthwhile even if it’s not possible to re-import it back.

## Hostname and path handling

By default restic uses local hostname and path to identify snapshots.

This may not work well for cloud services, especially for hostname. Using local hostname and path can easily lead to mess, e.g. if backups of the same cloud service account are taken from different hosts.

Different ‘FS’ implementations may override hostname (unless one is explicitly provided via --host flag). It will be recommended to use <account>@<service> format as default hostname and avoid using local hostname for non-local ‘FS’ implementations. Examples could be:

[vladimir.rusinov@gmail.com](mailto:vladimir.rusinov@gmail.com)@google_mail

zuck@facebookinov@gmail.com](mailto:vladimir.rusinov@gmail.com)@google_calendar

bill@msn_mail

etc.

## rdiff-backup "frontend"

Similarly to rdiff-backup backend, rdiff-backup "frontend" may be integrated to provide support for a bunch of storage/cloud services. One integration may unlock support backups of a large number of filesystem-like services, but will not allow backups of less file-like services. E.g. it may help backup Dropbox but may not help with Google Calendar backups. Also, it’ll be likely more awkward to use than "native" service support.

More research and more specific design may be needed.

## Advantages of this design

*   One restic repository can be used for all backups - local and cloud

*   All benefits of restic snapshot management

*   Some deduplication possible, e.g. for when some subset of data is synced to local filesystems

## Downsides

*   One restic repository can be used for all backups - local and cloud - can be dangerous if backup repository is compromised

*   Increased restic binary size. Since it’s in Go and statically-typed, adding more ‘FS’ implementations may pull more dependencies and increase ‘restic’ binary size for everyone.

*   UX is not perfect - we mix paths and config files.

# Next steps / Milestones

1. Write design proposal  - **done**

2. Send proposal to review

3. In parallel to (2), start implementing cloud backup for one provider as a proof of concept. Having actual code will help refine design and may help discussion.

4. Iterate on design comments, adjust the code from (3) accordingly.

5. Finalize design and code of the first cloud backup source, send PR, merge it into the upcoming version of restic.

6. Implement support for popular cloud service providers: SFTP and GCS as there are already pull requests which may need a small number of changes, Gmail, Facebook, Github, Hotmail, Dropbox, Google Drive, etc.

# Alternatives

## Do nothing

Too late, I already wrote this design.

Also, I still need my backups.

## Keep restic for local backups only

One can simply have a service-specific backup/dump program and save backups as local files, to be picked up by restic backups. This is approach currently used by the author of this document and it has several downsides:

*   Requires managing different tools and different backup schedules

*   Makes it difficult to see which services were backed up when

*   Requires enough local storage to store a copy of all cloud data

## Use stdin source + 3rd party binaries

Backup source can be implemented as a separate binary that simply dumps backup into stdout (e.g. in tar format if the source is file-based). Restic will then consume backup from stdin.

Such an approach is possible today, and no code changes are required. Restic may provide better documentation with specific examples of how to do this at least for popular services.

Advantages:

*   No code changes are required

*   No restic binary size bloat and no additional code to maintain

Disadvantages:

*   Worse UX

*   Worse deduplication (tar may add its own headers or realign blocks in a way that makes deduplication impossible).

*   Impossible to recover from partial failures - the whole backup/export will have to be started from scratch

*   No advantage from restic cache.
