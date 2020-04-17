Original: [Iptables – производительность роутера](http://centos.alt.ru/?p=32) (Russian)


Incorrect iptables settings may cause poor router performance. I'll show you how can you improve iptables performance

# Disable connection tracking

The first thing you need to do (if you are not using NAT) is to disable connection tracking in nat table, PREROUTING chain:
```Bash
iptables -A PREROUTING -j NOTRACK
```
Notice that if you have rules with match module, you'll have to change them to avoid match module. Also, all rules using conntrack will stop working.

# Place 'hottest' rules to the top

<!-- TEASER_END -->

Iptables checks rules in linear order, one by one, and each network packet would go through the chain from first rule and until first condition match, That's why it's important to place most popular rules to beginning of the chain. <br>You could check what rules are hottest using following commend:<br><pre class="brush: bash">iptables -L -n -v<br></pre><b>Example:</b> We have border router with ~10 000 clients. Some of the ip addresses needs to be blocked. E.g. we have 2 000 blocked ip addresses, so we have 2 000 rules in iptables like
```Bash
iptables -A FORWARD -s 192.168.0.1 -j DROP
iptables -A FORWARD -s 192.168.0.20 -j DROP
iptables -A FORWARD -s 192.168.0.34 -j DROP
# and so on
iptables -A FORWARD -s 192.168.1.2 -j DROP
iptables -A FORWARD -s 192.168.1.15 -j DROP
iptables -A FORWARD -s 192.168.1.23 -j DROP
# and so on
iptables -A FORWARD -s 192.168.2.1 -j DROP
iptables -A FORWARD -s 192.168.2.2 -j DROP
iptables -A FORWARD -s 192.168.2.3 -j DROP
# and so on
iptables -A FORWARD -s 192.168.7.10 -j DROP
iptables -A FORWARD -s 192.168.7.18 -j DROP
iptables -A FORWARD -s 192.168.7.254 -j DROP
# and allow all other ip addresses
iptables -A FORWARD  -j ACCEPT
```


In this configuration every single packet (e.g. from non-blocked 192.168.2.123) would be checked 2 000 times. This is terrible!<br>But there is a solution: rewrite rules as follows:<br><br><pre class="brush: bash"># create chain for every subnet<br>iptables -A FORWARD -s 192.168.0.0/24 -j NET-00<br>iptables -A FORWARD -s 192.168.1.0/24 -j NET-01<br>iptables -A FORWARD -s 192.168.2.0/24 -j NET-02<br>iptables -A FORWARD -s 192.168.3.0/24 -j NET-03<br>iptables -A FORWARD -s 192.168.4.0/24 -j NET-04<br>iptables -A FORWARD -s 192.168.5.0/24 -j NET-05<br>iptables -A FORWARD -s 192.168.6.0/24 -j NET-06<br>iptables -A FORWARD -s 192.168.7.0/24 -j NET-07<br># and check blocked ip addresses in this chains<br>iptables -A NET-00 -s 192.168.0.1 -j DROP<br>iptables -A NET-00 -s 192.168.0.20 -j DROP<br>iptables -A NET-00 -s 192.168.0.34 -j DROP<br># and so on<br>iptables -A NET-01 -s 192.168.1.2 -j DROP<br>iptables -A NET-01 -s 192.168.1.25 -j DROP<br>iptables -A NET-01 -s 192.168.1.23 -j DROP<br># and so on for all other chains<br># and accept pachet in the end:<br>iptables -A FORWARD  -j ACCEPT<br></pre><br>In this case maximum 255 checks would be applied to the packet, which is much better.<br>Another way to solve bottleneck is to use <a href="http://ipset.netfilter.org/">ipset</a>.</div></body></html>
