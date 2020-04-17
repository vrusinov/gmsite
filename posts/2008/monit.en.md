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

Let's try to install and configure monit:<br><pre class="brush: bash">emerge -av monit<br></pre>And here are some config examples:<br><br>/etc/monitrc <br><pre class="brush: bash">set daemon  120 # check every 2 minutes<br>set logfile syslog facility log_daemon<br><br>set mailserver localhost<br>set eventqueue # use event queue is case mail server is unreachable<br>    basedir /var/monit<br>    slots 10<br>set mail-format { from: monit@ myserver.com }<br>set alert admin1 admin2 # list of alert revievers<br><br># internal httpd configuration<br>set httpd port 2812 and<br>    use address 0.0.0.0<br>    allow 1.2.3.4<br>    allow admin:password<br><br>include /etc/monit.d/*<br></pre><br>/etc/monit.d/system <br><pre class="brush: bash"># overall OS resources checking<br>check system myserver<br>    if loadavg (1min) &gt; 30 then alert<br>    if loadavg (5min) &gt; 20 then alert<br>    if memory usage &gt; 75% then alert<br>   if cpu usage (user) &gt; 70% then alert<br></pre><br><pre class="brush: bash"># apache2:<br>check process apache with pidfile /var/run/apache2.pid<br>    start program = "/etc/init.d/apache2 start"<br>    stop program  = "/etc/init.d/apache2 stop"<br>    if totalmem &gt; 500.0 MB for 5 cycles then restart<br>    if children &gt; 250 then restart<br>    if loadavg(5min) greater than 30 for 8 cycles then stop<br>    if failed host myserver.com port 80 protocol http<br>       and request "/index.html"<br>       then restart<br>    if failed port 443 type tcpssl protocol http<br>       with timeout 15 seconds<br>       then restart<br>    if 3 restarts within 5 cycles then timeout<br></pre><br><pre class="brush: bash"># file system:<br>check device data with path /dev/sdb1<br>    start program  = "/bin/mount /data"<br>    stop program  = "/bin/umount /data"<br>    if space usage &gt; 80% for 5 times within 15 cycles then alert<br>    if inode usage &gt; 80% then alert<br>    group server<br></pre><h2>Links</h2><ul><li><a href="http://mmonit.com/monit/">monit official site</a></li><li> <a href="http://mmonit.com/">M/Monit</a></li></ul>
