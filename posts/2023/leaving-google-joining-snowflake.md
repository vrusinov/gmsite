This Friday was my last day in [Google](https://sre.google/). Tomorrow will be my first day in [Snowflake](https://snowflake.com/). I loved my job in Google but after over 10 years it was a time for a change. It is a big change.

![Google MTV](/posts/2023/google_mtv.jpg)

<!-- TEASER_END -->

# 10 years in Google Storage SRE

I've spent all of my Google time in various Storage SRE teams in Ireland. It wasn't an intention, it sort of just happend. My Google story started in...

## May 2012 - younger me arrives to Dublin

![A warm welcome](/posts/2023/live_dublin.jpg)

I arrived to Dublin with no specific plan and no idea what will happen. I didn't even knew which team I will be joining. I was lucky to be accompanied by my spouse, who had her own big challenge ahead (she didn't speak any English at the time, and immigration laws were not allowing her to work).

I wasn't sure how long I'll manage to stay in Ireland and in Google, but I figured we'll stick for a couple of years and re-asses. Re-assessment never came and Dublin just naturally became our new home.

## BCD SRE

![2012](/posts/2023/me_2012.jpg)

My first team in Google was "BCD". I was shocked by it. Google was a dream company, working at a scale I never saw before (and may not see in the future). I expected every byte and every CPU cycle to be accounted for. I expected there would be an army of engineers and each of them to be a hair short of being a God.

What I saw instead was a team of about 20 engineers who ran pretty much all of Google storage. As simple as that. A small group of people who had a copy of the Internet and few other bits and bobs in their systems. These were exceptionally good engineers, but they were not Gods. In fact, I quickly realized I'm not too different from them. This was very surprising to me at the time.

The team was however in trouble - turns out 20 people wasn't quite enough to run all of the storage. Oncall was very noisy, there were cross-site communication issues and just in general too much stuff to do, too much chaos and not enough automation. Management was good at dealing with that, and one of the actions they took was splitting the team in two. So shortly after starting I ended up in...

## Bigtable SRE

As a legacy from BCD, the team was still under heavy pager and ticket load. This is when I was exposed to Dave's ideas like [Bad Machinery](https://www.usenix.org/conference/srecon15europe/program/presentation/oconnor) and helped with it a bit. However mostly I was focused on efficiency projects. I saved Google a lot of money and got my first promotion.

Socially, this was probably the most fun I ever had at work. Being relatively junior, I wasn't exposed to a lot of management / politics. Bad machinery helped so oncall wasn't bad either. Team was good, I did a lot of travel and made a lot of friends. My foundest memory is resolving an outage during SRE Europe offsite in Amsterdam. I was secondary oncall and together with my primary we were on treasure hunt in the city, which of course brought us to RLD, and of course this is where we got paged. So we had to quickly resolve it on a porch of a "coffee shop".

However after a while there wasn't all that much for me to do. I failed another promo and realized I need a change. I loved the team but it was time to move on to...

## Cloud SQL SRE

I had some experience running PostgreSQL at previous job which came in handy: I launched Cloud Postgres. This lead to successfull promo.

This is also where I got a chance to be part of public Cloud business and got to work with open-source stuff, and I liked it.

But then after PostgreSQL was done I felt the itch again. There was a shortage of managers at the time and I reported to someone who managed two different teams. They did a very good job, but it still wasn't fun for anyone involved. So I though this is something I can help with. So I joined ...

## Persistent Disk SRE

I joined [Persistent Disk](https://cloud.google.com/persistent-disk) to become an SRE manager. It was a strong, stable team doing a lot of high-impact things. It was full of good people and I expected to have an opportunity to take it easy and learn the new role.

I've learned the role indeed, and people tell me I was fairly good, but it wasn't easy. What should've been an easy team was not. The team was re-organized twice with USA shard changing locations, than there was explosive growth of Google Cloud, then there was a pandemic, and most recently there is another crisis to deal with.

I learned a lot and I was surrounded but a lot of great people. I'll miss them.

# Why leave Google

Despite some recent actions from leadership which I view as mistakes, Google is a great company. However I've spent over 10 years there, and I felt like on one hand, I was too comfortable, and on another I was missing out on different experience and perspectives. I wanted to know how external world works.

# Why join Snowflake

They are the "outside world", while at the same time they operate public cloud service. So it's a good mix of something new and unknown but also something familiar. Also, they pay well. :)

It is a change, and quite a big one:

* This is IC role, so after over 4 years of being a manager I'll have to get my hands a lot more dirty with technology.

* Technology will be quite new to me. Apart from a short stint in Cloud SQL and playing with my homelab, my focus has been on proprietary Google tech for a very long time.

* It is a much smaller company, so likely operate in a different way. They also don't seem to be trying to just copy Google SRE model despite a large number of ex-Googlers there.

* They sent me top of the line M1 Macbook. I've never used Mac before so it's another, albeit smaller difference.

Another good fact is that I already know a lot of people there, and they are all good. I may even have a [chance to work with my old BCD SRE peer](https://jmmv.dev/2022/10/bye-microsoft-hi-snowflake.html), whose thoughts on Snowflake are similar to mine.

![It's huge. Or my table is too small](/posts/2023/mac.jpg)
