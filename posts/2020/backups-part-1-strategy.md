There are two kinds of people in this world: people who back up their files and
people who will back up their files.

If you don't do backups, check the
[world backup day website](http://www.worldbackupday.com/en/). It lists a number
of reasons of why backups are important and provides some advice on how to start
backing your files up.

However, that advice is rather simplistic. After following it and setting up
/some/ backup, one may end up with no usable backups still and false sense of
security. Or, people who are more paranoid (or experienced?), may still have
some anxiety. There are still many open questions. Do I backup the right files?
Did I forget anything? Will these backups protect me from all data loss
situations? Do they cost me too much?

To reduce this anxiety for myself I am starting the series of posts where I will
document how I do backups. I hope these will be useful for more people as well.

Now, before I start implementing any backups, I need to understand what to back
up. So let's start with...

# Data Catalogue

Or what data do I have and how important is it?

| Description           | Importance                              | Comment                                                                                                                      |
| --------------------- | --------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **Files**             |                                         | Me & my spouse own several laptops, a desktop and a "home server" which is just an old laptop. All of them mostly run Linux. |
| /home                 | Mixed: from worthless to very important | Spread over several laptops & desktops. A lot of files are duplicate between machines                                        |
| /etc                  | Medium                                  | Can be restored after a lot of documentation reading                                                                         |
| /var                  | Low                                     | I try not to put anything important there. Need to double-check though.                                                      |
| /root                 | Low                                     | Nothing there                                                                                                                |
| /media and /mnt       | Medium                                  | Additional drives mounted there. Mostly various downloads which may be annoying to re-download                               |
| /mnt/windows          | Low                                     | Special case - dual-boot Windows installation for games. Nothing there except saves which should be synced online            |
| /bin, /usr, /lib, etc | Low                                     | Easy enough to reinstall/repair from distribution                                                                            |
|                       |                                         |                                                                                                                              |
