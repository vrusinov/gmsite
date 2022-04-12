Monit is a simple, lightweight, but useful and powerful enough monitoring solution for your servers.

Monit can monitor:

*   OS processes (presence, resources)
*   files, directories and file system for changes (mtime, size and checksum
    changes)
*   network hosts (ping, TCP connections)

Monit can notify administrator via configurable e-mail messages. It also can
automatically restart failed service.

Monit has an embedded web-server which allows to view state on monitoring objects and disable or enable them.

<!-- TEASER_END -->

Of course, enterprise-class monitoring systems have much more features, but they are quite a bit more complex.
BTW, there is product named M/Monit. It can control multiple Monit instances.
Unfortunately, M/Monit is only available under commercial license.

Let's try to install and configure Monit:

```bash
emerge -av monit
```

And here are some config examples:

/etc/monitrc:

```
set daemon  120 # check every 2 minutes
set logfile syslog facility log_daemon

set mailserver localhost
set eventqueue # use event queue is case mail server is unreachable
    basedir /var/monit
    slots 10
set mail-format { from: monit@ myserver.com }
set alert admin1 admin2 # list of alert revievers

# internal httpd configuration
set httpd port 2812 and
    use address 0.0.0.0
    allow 1.2.3.4
    allow admin:password

include /etc/monit.d/*
```

/etc/monit.d/system

```perl
# overall OS resources checking
check system myserver
    if loadavg (1min) > 30 then alert
    if loadavg (5min) > 20 then alert
    if memory usage > 75% then alert
    if cpu usage (user) > 70% then alert
```

/etc/monit.d/apache2:

```perl
check process apache with pidfile /var/run/apache2.pid
    start program = "/etc/init.d/apache2 start"
    stop program  = "/etc/init.d/apache2 stop"
    if totalmem > 500.0 MB for 5 cycles then restart
    if children > 250 then restart
    if loadavg(5min) greater than 30 for 8 cycles then stop
    if failed host myserver.com port 80 protocol http
       and request "/index.html"
       then restart
    if failed port 443 type tcpssl protocol http
       with timeout 15 seconds
       then restart
    if 3 restarts within 5 cycles then timeout
```

/etc/monit.d/fs:

```perl
# file system:
check device data with path /dev/sdb1
    start program  = "/bin/mount /data"
    stop program  = "/bin/umount /data"
    if space usage > 80% for 5 times within 15 cycles then alert
    if inode usage > 80% then alert
    group server
```

# Links

*   <a href="http://mmonit.com/monit/">Monit official site</a>
*   <a href="http://mmonit.com/">M/Monit</a>
