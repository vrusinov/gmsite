There are two kinds of people in this world: people who back up their files and
people who will back up their files.

If you don't do backups, check the
[world backup day website](http://www.worldbackupday.com/en/). It lists a number
of reasons of why backups are important and provides some advice on how to start
backing your files up.

However, their advice is rather simplistic. After following it and setting up
/some/ backup, one may end up with no usable backups still and false sense of
security. Or, people who are more paranoid (or experienced?), may still have
some anxiety. There are still many open questions. Do I backup the right files?
Did I forget anything? Will these backups protect me from all data loss
situations? Do they cost me too much?

<!-- TEASER_END -->

To reduce this anxiety for myself I am starting the series of posts where I will
document how I do backups. I hope these will be useful for more people as well.

Now, before I start implementing any backups, I need to understand what to back
up. So let's start with...

# Data Catalogue

Or what data do I have and how important is it?

| Description                 | Importance | Comment                                                                                                                                         |
| --------------------------- | ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| **Files**                   |            | Me & my spouse own several laptops, a desktop and a "home server" which is just an old laptop. All of them mostly run Linux.                    |
| `/home`                     | High       | Spread over several laptops & desktops. A lot of files are duplicate between machines                                                           |
| `/etc`                      | Low        | Can be restored after some documentation reading                                                                                                |
| `/var`                      | Low        | I try not to put anything important there. Need to double-check though.                                                                         |
| `/root`                     | Low        | Nothing there                                                                                                                                   |
| `/media` and `/mnt`         | Medium     | Some additional devices may be mounted there.                                                                                                   |
| `/mnt/windows`              | Low        | Special case - dual-boot Windows installation for games. Nothing there except saves which should be synced online                               |
| `/bin`, `/usr`, `/lib`, etc | Low        | Easy enough to reinstall/repair from distribution                                                                                               |
| **Devices**                 |            | Non-computer devices                                                                                                                            |
| Phones                      | Low        | We are on Android and almost everything is backed up to Google account. There is nothing really valuable there anyway.                          |
| Virgin router               | Low        | I use internet from Virgin media and they insist on their own router. I use close to default settings there so loss of config is not a big deal |
| UniFi Dream Machine         | Medium     | Most of the home routing is done by UniFi Dream Machine, so its config is nice to preserve                                                      |
| Chromecast / Google TV      | Low        | Doesn't hold any state                                                                                                                          |
| **Online Services**         |            |                                                                                                                                                 |
| Facebook                    | Medium     |                                                                                                                                                 |
| Feedly                      | Medium     | It may be annoying to loose list of subscriptions                                                                                               |
| GitHub                      | Medium     | It's important but by the nature of git I'll have many copies naturally                                                                         |
| Gmail                       | High       |                                                                                                                                                 |
| Google Calendar             | High       |                                                                                                                                                 |
| Google Drive                | High       | A lot of important stuff there for archival                                                                                                     |
| Google Keep                 | Medium     | Some small notes there                                                                                                                          |
| Netatmo                     | Medium     |                                                                                                                                                 |
| Password manager            | High       |                                                                                                                                                 |
| ProtonMail                  | Medium     |                                                                                                                                                 |
| Reddit                      | Medium     |                                                                                                                                                 |
| WhatsApp                    | Low        |                                                                                                                                                 |
| YouTube                     | Medium     | No videos but playlists and subscriptions                                                                                                       |
| YouTube Music               | High       | My music collection is there. It would be bad to loose it along with my playlists                                                               |

That's everything I could remember at the moment.

You may have noticed I've also included online services in the list of data I
care about. I believe it's a mistake to leave them out. I expect companies to
take a good care of my data (and I know first-hand it is true in case of Google). However, I may get locked out of the account for some reason, or the service may be unavailable at some critical time, or may even shut down.

Next, I need to understand what do I need to protect from.

# Data loss scenarios

| Scenario                            | Probability       | Comment                                                                                              |
| ----------------------------------- | ----------------- | ---------------------------------------------------------------------------------------------------- |
| Storage device (HDD or SSD) failure | Medium            | Modern hardware is quite robust but can still fail                                                   |
| Human error                         | High              | My fat fingers are by far the biggest risk to my data.                                               |
| Theft or loss                       | High for laptops  |                                                                                                      |
| Natural disaster (fire, etc)        | ??? Hopefully low |                                                                                                      |
| Malice                              | Low               | I believe I am protected enough from random malicious attacks and not valuable enough to be targeted |

# Other considerations

-   I use [syncthing](https://syncthing.net/) extensively to sync files between
    my machines, so a lot of files are duplicates.
-   I don't want to spend a fortune on these backups.
-   I dislike and try to avoid subscription services and would prefer to pay for what I use approach.
-   A lot of my machines have intermittent connection to the Internet, and often do not have public IP address.
-   I have a weak Internet uplink at home (upload is capped at 20 Mbps).
-   A lot of my data does not change too frequently.

# Solution requirements

Taking all of above into consideration, here's what I would like from my backup solution:

Must-have:

-   Off-site and ideally offline backups.
-   Ability to work with clients without public IP.
-   Ability to do incremental backups.
-   I did not mention this, but all data must be encrypted in transit and at rest.

Nice to have:

-   De-duplication across different hosts.
-   Pay as you go instead of subscription.
-   Use of open-source software so I can hack and improve my backup solution.

# Next up

That's all for this post. Check [part 2](/en/posts/2020/backups-part-2-files/) where I describe my solution for files backups.
