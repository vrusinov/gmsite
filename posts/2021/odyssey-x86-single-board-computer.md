Shortly after setting-up [single-node Kubernetes cluster](/en/posts/2020/setting-up-single-node-kubernetes-cluster/), [single-node Ceph cluster](/en/posts/2020/setting-up-single-node-ceph-cluster-for-kubernetes/) I wanted an actual cluster. I've also noticed that Ceph doesn't actually work all that well: Besides obvious lack of failure tolerance, it didn't seemed to like working on top of just two storage devices of a very different sizes (internal ~300G HDD and 1T USB-HDD). So I've decided to get some more hardware.

I live in a small apartment and I don't really have a lot of space. All I have is a small shelf in storage area. Normal desktops and especially rack servers won't fit. They are also noisy, eat a lot of power and produce a lot of heat. Another thing is that I already had two old SATA HDDs lying idle, which I wanted to use, so the new hardware needed SATA support.

I found the solution in [Odyssey X86](https://www.seeedstudio.com/ODYSSEY-X86J4105800-p-4445.html) board.

<a href="/posts/2021/odyssey.jpg"><img src="/posts/2021/odyssey_small.jpg"></a>

<!-- TEASER_END -->

# Hardware

ODYSSEY X86 is a single board computer (SBC), and it means what it says. It's just a small self-contained board with the CPU, memory and everything else needed on it. It has:

*   [Intel Celeron J4105 CPU](https://ark.intel.com/content/www/us/en/ark/products/128989/intel-celeron-j4105-processor-4m-cache-up-to-2-50-ghz.html)
*   8 GiB of DDR4 RAM (not extendable)
*   two 1G Realtek network cards
*   64G eMMC - a small, slow SSD but it's handy for installing OS to it - this way all other connected storage can be used exclusively for Ceph.
*   single SATA port and three SATA power connectors
*   two M.2 slots (Key B SATA and Key M PCIe)

It can be powered by included power supply (with barrel connector) or via usb-c. CPU eats up to 10W, and the rest should not require much power. So it's fairly economic to run.

The board also has wifi and some sort of Ardurino with bunch of pins but that wasn't important for me.

It is sadly not cheap - about 200 EUR, but that's what happens during chip shortage.

At first I ordered and assembled just one. I ordered from [www.digikey.ie](https://www.digikey.ie) but despite Irish domain, the board was sent from US and I had to pay import duty. Since I had two HDDs, and board only has one SATA port (but three power connectors), I also got [M.2 to SATA convertor](https://www.seeedstudio.com/M-2-to-SATA-Converter-2-Stacked-Ports-p-4727.html). SATA power connectors are not standard so I also got a couple of cables from seeedstudio. And to top it all up, [re_computer case](https://www.seeedstudio.com/re-computer-case-p-4465.html) with few other bits and bobs.

Once I got the first board running I was satisfied enough to get one more - this time from amazon.de. This arrived without import duty, along with 1T M.2 SSD.

# Software

The board behaves just like a normal X86 computer, the only noticeable difference is that it has UEFI-only BIOS, so it is not possible to boot in legacy mode.

I was able to easily boot from USB and install CentOS 8 to the eMMC.

# Alternatives

The best and probably better option is [ODROID H2+](https://www.hardkernel.com/shop/odroid-h2plus/). It has 2 SATA ports, 2 2.5Gbit Ethernet ports, and unlike in Odyssey RAM is not soldered in and it's possible to install up to 32 GiB. Unfortunately it was not, and still is not in stock due to chip shortage.

Another possible alternative is Intel's NUC or something similar. NUCs are expensive and can't power 3.5" drives. Other NUC-like computers are cheaper but also have problems - they usually have limited SATA suppirt, small non-exnesible enclosures, and don't have eMMC (so will need separate boot device).

Finally, there are some non-X86 boards, e.g. [ROCKPro64](https://www.pine64.org/rockpro64/) or Raspberry Pi 4. They don't seem to have native SATA support, although there are adaptors which connect via USB or M.2. Main problem was architecture: since I already had Kubernetes running on X86 I wanted to avoid mixing architectures to minimize number of possible problems.

# Conclusions

I've extended Ceph cluster on these two boards and now I have much more stable Ceph cluster. Overall configuration is this:

| Host   |             | CPU                 | RAM   | Storage                      |
| ------ | ----------- | ------------------- | ----- | ---------------------------- |
| krusty | Old laptop  | Intel Core i3-3217U | 6 GiB | 300G 2.5" HDD                |
| lisa   | Odyssey X86 | Intel Celeron J4105 | 8 GiB | 250G 2.5" HDD; 500G 3.5" HDD |
| apu    | Odyssey X86 | Intel Celeron J4105 | 8 GiB | 1T M.2 SSD                   |

And in case I need more storage, I still have one M.2 slot left in lisa, and one M.2 + one SSD slot left in apu without the need for any additional boards.

# Future work

*   I didn't extend Kubernetes cluster yet - apiserver and etcd are still singly-homed on krusty.
*   My Ceph currently uses 2x replication. Although it is not recommended and potentially unsafe, I'm reasonably satisfied with the trade-off. I may change it to 3x if the laptop fails and I replace it with Odyssey or similar board.
*   If/when HDDs fail I may switch entirely to M.2 SSDs - they take much less space and likely consume less power. I'm not a data hoarder so they don't need to be very large, thus should be relatively affordable.
*   Currently I only use one of the Ethernet ports on Odysseys so they are limited to 1 Gbps. I may try to use bond both to get 2 Gbps if I notice poor performance.
