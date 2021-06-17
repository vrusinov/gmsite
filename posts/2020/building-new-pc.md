As Ireland went into second lockdown of 2020, I've decided to upgrade my home personal computer.

I use my PC for gaming, hacking around with Linux and general wasting time in the Internet.

Previously I used PC with Intel i5-3550. After an SSD, GPU and memory upgrades it was still a very capable machine. It is actually still in use today to play some less demanding games co-op with my spouse. However I was not 100% happy with how some CPU-heavy games behaved (city/transport simulators), and compile times were getting annoyingly long while hacking. Another thing I was not happy about is fan management - the old PC had proprietary Lenovo motherboard which would spin case and CPU fans too much.

## Desires

Given above I wanted:

*   Quietness. Ideally I wanted it to be semi-passive so that all fans will stop completely under light load.
*   Good single-core performance for games which don't do multi-threading too well.
*   8 or more cores for compiling stuff (also, it's fun to have many bars in `htop`).

<!-- TEASER_END -->

## Components

Here's what I ended up with:

[PCPartPicker Part List](https://ie.pcpartpicker.com/list/QZNmF8)

| Type                                                                            | Item                                                                                                                                                                                                          | Price               |
| ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- |
| **CPU**                                                                         | [AMD Ryzen 7 3800X 3.9 GHz 8-Core Processor](https://ie.pcpartpicker.com/product/qryV3C/amd-ryzen-7-3800x-39-ghz-8-core-processor-100-100000025box)                                                           | €433.91 @ Custompc  |
| **CPU Cooler**                                                                  | [Noctua NH-U12S 55 CFM CPU Cooler](https://ie.pcpartpicker.com/product/wjmLrH/noctua-cpu-cooler-nhu12s)                                                                                                       | €69.94 @ Komplett   |
| **Motherboard**                                                                 | [Asus ROG STRIX B450-F GAMING ATX AM4 Motherboard](https://ie.pcpartpicker.com/product/XQgzK8/asus-rog-strix-b450-f-gaming-atx-am4-motherboard-strix-b450-f-gaming)                                           | €116.08             |
| **Memory**                                                                      | [Crucial Ballistix 32 GB (2 x 16 GB) DDR4-3200 CL16 Memory](https://ie.pcpartpicker.com/product/gCCFf7/crucial-ballistix-32-gb-2-x-16-gb-ddr4-3200-memory-bl2k16g32c16u4b)                                    | €143.98             |
| **Storage**                                                                     | [Crucial P5 1 TB M.2-2280 NVME Solid State Drive](https://ie.pcpartpicker.com/product/yTTzK8/crucial-p5-1-tb-m2-2280-nvme-solid-state-drive-ct1000p5ssd8)                                                     | €154.87             |
| **Video Card**                                                                  | [EVGA GeForce RTX 2060 SUPER 8 GB SC ULTRA GAMING Video Card](https://ie.pcpartpicker.com/product/9wPgXL/evga-geforce-rtx-2060-super-8-gb-sc-ultra-gaming-video-card-08g-p4-3067-kr)                          | €415.45             |
| **Case**                                                                        | [GameMax Silent ATX Mid Tower Case](https://ie.pcpartpicker.com/product/Tx6qqs/gamemax-silent-atx-mid-tower-case-gmx-silent)                                                                                  | Purchased For €0.00 |
| **Power Supply**                                                                | [Corsair RMx (2018) 650 W 80+ Gold Certified Fully Modular ATX Power Supply](https://ie.pcpartpicker.com/product/2HbwrH/corsair-rmx-2018-650w-80-gold-certified-fully-modular-atx-power-supply-cp-9020178-na) | €138.95 @ Komplett  |
| **Operating System**                                                            | [Microsoft Windows 10 Home OEM 64-bit](https://ie.pcpartpicker.com/product/wtgPxr/microsoft-os-kw900140)                                                                                                      | Purchased For €0.00 |
| **Case Fan**                                                                    | [Noctua A14 PWM 82.5 CFM 140 mm Fan](https://ie.pcpartpicker.com/product/dwR48d/noctua-case-fan-nfa14pwm)                                                                                                     | €37.94 @ Komplett   |
| **Monitor**                                                                     | [HP Z24i 24.0" 1920x1200 60 Hz Monitor](https://ie.pcpartpicker.com/product/qwR48d/hp-monitor-d7p53a4aba)                                                                                                     | Purchased For €0.00 |
| *Prices include shipping, taxes, rebates, and discounts*                        |                                                                                                                                                                                                               |                     |
| **Total**                                                                       | **€1511.12**                                                                                                                                                                                                  |                     |
| Generated by [PCPartPicker](https://pcpartpicker.com) 2020-12-10 13:42 GMT+0000 |                                                                                                                                                                                                               |                     |

### Case

<img src="/posts/2020/gamemax_silent_mid_tower_case.png" alt="GameMax Silent Mid-Tower PC Gaming Case" width="20%" style="float: right;">
I used [GameMax Silent Mid-Tower PC Gaming Case](http://www.gamemax.uk/index.php/products/cases/silent-mid-tower-gaming-pc-case/), just because I already had it.

**Pros**:

*   Although is says "gaming case", it looks neutral - like a big black box. No extra lights, windows, etc.
*   Some decent sound dampening - it has some rubber-y stuff inside of panels.

**Cons**

*   It's huge. Works for me right now, but who knows if it will change in the future. I may be forced to change the case if we move or re-arrange something in current apartment.
*   It has a lot of parts, compartments which I don't use: 3.5" and 2.5" SSD/HDD enclosures, separate compartment for PSU, 5.25" bays for optical drives, etc.

**Alternatives**:

If I was getting something new I probably would have chosen something smaller and simpler, like one of the [CoolerMaster Q series](https://www.coolermaster.com/catalog/cases/mini-tower/masterbox-q300l/), or maybe a small mini-ITX case.

### CPU

<img src="/posts/2020/amd_3800x.jpg" alt="AMD 3800X" width="20%" style="float: right;">

AMD 3800X performs very well, and majority of my workloads don't stress it enough. Originally I wanted to go with 3700X as however there was a discount for 3800X and it was just ~15 EUR more expensive. The price from PCPartPicker above is incorrect - I got it for about 320 EUR.

Note I got it well before 5000 series were released.

**Pros**

*   8 cores / 16 threads.
*   Cores are reasonably fast - it easily gets 4.5 boost GHz on single-thread tests.
*   Was only ~15 EUR more expensive than 3700X
*   It's on the same socket as all AMD Ryzen so far (up to most recent Ryzen 3), and there is a lot of different motherboards with forward and backward compatibility. I may upgrade to 5000 series later without too much hassle.

**Cons**

*   It's hot: 105 W TDP.
*   Not as fast in single thread as 3800XT, which boosts up to 4.7 GHz.
*   Comes with a cooler which I had no use for. Throwing away perfectly good cooler is bad for environment. Anyone wants free prism cooler?

**Alternatives**

*   AMD 3600XT has less cores, but also less expensive, have same single-thread performance and lower TDP.
*   3800XT is a bit more expensive and faster in single thread.
*   Intel i9 9900K has similar performance, a bit lower TDP but was more expensive at the time (seems similar price now though).

### CPU cooler

<img src="/posts/2020/noctua_nh_u12s.jpg" alt="Noctua NH-U12S" width="20%" style="float: right;">

[Noctua NH-U12S](https://noctua.at/en/nh-u12s)

As I mentioned above, the CPU is hot! It is listed at 105 W TDP, and I suspect my motherboard may be giving it even more. It goes up to 75-ish C under full load forcing Noctua NH-U12S to spin at full speed. And although this is a very good cooler and it's not audible whatsoever up until about 50% RPM, it is very noticeable at 100%.

I use it in one-fan configuration. I may try attaching 2nd fan in a pull
configuration - maybe the two fans will be able to cool the CPU at a lower
speed.

**Alternatives**

I probably should have went with larger [NH-D15](https://noctua.at/en/nh-d15).

### Motherboard

<img src="/posts/2020/asus_rog_b450f.jpg" alt="Asus ROG STRIX B450-F" width="20%" style="float: right;">


I went for [Asus ROG STRIX B450-F GAMING
](https://rog.asus.com/Motherboards/ROG-Strix/ROG-STRIX-B450-F-GAMING-Model/) as I had good experience with Asus motherboards previously. However, this model was rather disappointing, and the main reason my intention of having semi-passively cooled PC failed. Turns out although Asus has fancy setup program with a lot of control over how fans work, it is unable to turn PWM fans off. And for CPU fan it insists to have 100% RPM at above 75 C. I would have been more comfortable running my CPU up to 80-85 C and would have preferred something like 80% RPM at 75 C.

**Pros**

*   4+ fan headers
*   4 slots for RAM
*   Integrated IO shield is a blessing - no more forgetting or getting stabbed by it. End result looks better too

**Cons**

*   Can't turn PWM fans off, limited flexibility it setting fan curves
*   B450 chipset does not support PCI-express 4.0 (though it does not matter for me)
*   Takes a long time to initialize - long enough that my monitor decides to turn off or (more annoyingly) switch to another video input if there's a work laptop connected to it.
*   No integrated beeper. I tried turning it on with no monitor connected and thought it didn't post.

**Alternatives**

Dunno? I suspect many "gamer" motherboard may have similar problems, and non-gamer ones seem to be much more expensive. I'd probably still look into server/workstation segment. I would be also cool to have open-source firmware on board so that I can modify it to my liking. There was some news about Coreboot support for AMD processors.

### Memory

<img src="/posts/2020/crucial-ballistix.png" alt="Crucial Ballistix 32 GiB Kit" width="20%" style="float: right;">

[Crucial Ballistix 32 GiB Kit (2 x 16 GiB) DDR4-3200 Desktop Gaming Memory](https://eu.crucial.com/memory/ddr4/bl2k16g32c16u4b) does the job. I debated about having ECC but it wasn't clear if consumer motherboard will support it well, so I decided against it. I went for DDR4-3200 as AMD website listed it as fastest supported by AMD 3800X. It turns out it's more complicated and I may have went for faster one.

For some reason it was detected as 2600, not 3200 and I had to manually adjust it in BIOS settings.

### SSD

<img src="/posts/2020/crucial_p5.jpg" alt="Crucial P5 1 TB PCIe M.2 2280SS SSD" width="20%" style="float: right;">

[Crucial P5 1 TB](https://eu.crucial.com/ssd/p5/ct1000p5ssd8) just works. This is my first M.2 SSD, and it was amusing see 1 TiB of fast storage can be now squeezed into such a small form-factor.

### Video Card

<img src="/posts/2020/evga_rtx2060.webp" alt="EVGA GeForce RTX 2060 SUPER" width="20%" style="float: right;">

I've got [EVGA GeForce RTX 2060 SUPER](https://www.evga.com/products/product.aspx?pn=08G-P4-3161-KR) because I was willing to spend at most 500 EUR on video card, and everything else felt like a potential downgrade from 1070 I previously used (all 16* and 2050 had less than 8 GiB of memory). I did not look into AMD cards since I had bad experience with their drivers before (both in Linux and Windows), and did not hear enough positive news about them improving.

**Pros**

*   Semi-passive: stops fans under light load.
*   Can run most current games at 60 fps / 1080p on ultra settings.

**Cons**

*   For ~500 EUR it does not feel like a big update from 1070.
*   Still struggles with some games on highest settings. Turns out most demanding game I have right now is Borderlands 3 and it can't quite run it on ultra at 60 fps.
*   Eats a lot of power, and produces a lot of heat. It feels like 10-series card with higher power budget.

**Alternatives**

Recently released GeForce RTX 3070 would definitely be a better choice at similar price.

### PSU

<img src="/posts/2020/corsair_rm650x.jpeg" alt="Corsair RM650x" width="20%" style="float: right;">

[Corsair RM650x](https://www.corsair.com/us/en/Categories/Products/Power-Supply-Units/Power-Supply-Units-Advanced/RMx-Series/p/CP-9020178-NA) works well and have some margin. I think my systems would have worked well with 550 W or maybe even 450 W PSU.

**Pros**

*   Semi-passive - turns off fans completely under low power draw.
*   Modular - since my PC does not have any SATA drives, or any extra devices I only needed a few cables coming from PSU.

**Cons**

*   Fan speed depends on power draw, not temperature. It will spin fans under load even if it's not hot.
*   80+ GOLD certified, which is not highest rating available. 80+ Platinum are available now.

## End result

Overall, it's a decent upgrade, and may last me another 8 years with minimal modifications.

I failed at goal of making it semi-passive, as stupid motherboard will spin fans even at idle. However as I'm writing this post all fans are at 15% of their max RPM, and I can't hear them at all. Things get loud if I ran CPU at 100% for over a minute, or when I play demanding games. Former could have been improved if Motherboard will let me run CPU hotter, or maybe with different CPU fan configuration. For latter not much can be done - 1060 eats up to 175 W, dumping all this heat back into the case, so things get hot. In such workloads my computer becomes a heater, and I don't need any extra heating during Irish winter in my small room while playing demanding games.

### What I would have changed

*   Different motherboard which gives me more control over fans.
*   Different / more efficient CPU cooler.

### Upgradability

It should be easy to upgrade the following:

*   RAM to 64 GiB as there are two more slots available, and motherboard supports that
*   CPU to Ryzen 5000 series, and B450 chipset should still support them
*   Video card to Nvidia 30 or later series

So overall decent.
