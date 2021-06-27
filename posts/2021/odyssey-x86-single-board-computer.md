Shortly after setting-up [single-node Kubernetes cluster](/en/posts/2020/setting-up-single-node-kubernetes-cluster/), [single-node Ceph cluster](/en/posts/2020/setting-up-single-node-ceph-cluster-for-kubernetes/) I wanted an actual cluster. I've also noticed Ceph doesn't actually works all that well. Besides obvious lack of failure tolerance, it didn't seemed to work well with two devices of a very different size (internal ~300G HDD and 1T USB-HDD). So I've decided to get some more hardware. Also, I started running actual application on the cluster and the old laptop I am using as a server started running out of RAM.

I live in a small apartment and I don't really have a lot of space. All I have is a small shelf in storage area. Normal desktops and especially rack servers won't fit. They are also noisy, eat a lot of power and produce a lot of heat. Also I already had two old SATA HDDs lying idle, which I wanted to use, so the new hardware needed SATA support.

I found solution in [Odyssey X86](https://www.seeedstudio.com/ODYSSEY-X86J4105800-p-4445.html) board.

<!-- TEASER_END -->

# Hardware

ODYSSEY X86 is a single board computer (SBC), and it means what it says. It's just a small single board with CPU, memory and everything needed on it. It has:

* [Intel Celeron J4105 CPU](https://ark.intel.com/content/www/us/en/ark/products/128989/intel-celeron-j4105-processor-4m-cache-up-to-2-50-ghz.html)
* 8 GiB of DDR4 RAM (not extendable)
* two 1G Realtec network cards
* 64G eMMC - a small, slow SSD but it's handy for installing OS to it - this way all other connected storage can be used exclusively for Ceph.
* single SATA port and three SATA power connectors
* two M.2 slots (Key B SATA and Key M PCIe)

It can be powered by included power supply (with barrel connector) or via usb-c. CPU eats up to 10W, and the rest should not require much power. So it's fairly economic to run.

The board also has wifi and some sort of Ardurino with bunch of pins but that wasn't important for me.

It is sadly not cheap - about 200 EUR, but that's what happens during chip shortage.

At first I ordered and assembled just one. I ordered from www.digikey.ie but despite Irish domain, the board was sent from US and I had to pay import duty. Since I had two HDDs, and board only has one SATA port (but three power connectors), I also got [M.2 to SATA convertor](https://www.seeedstudio.com/M-2-to-SATA-Converter-2-Stacked-Ports-p-4727.html). SATA power connectors are not standard so I also got a couple of cables from seeedstudio.
At first I ordered and assembled just one. I ordered from www.digikey.ie but despite Irish domain, the board was sent from US and I had to pay import duty. Since I had two HDDs, and board only has one SATA port (but three power connectors), I also got [M.2 to SATA convertor](https://www.seeedstudio.com/M-2-to-SATA-Converter-2-Stacked-Ports-p-4727.html). SATA power connectors are not standard so I also got a couple of [cables from seeedstudio](https://www.seeedstudio.com/SATA-26AWG-200mm-p-4680.html). And to top it all up, [re_computer case](https://www.seeedstudio.com/re-computer-case-p-4465.html) with few other bits and bobs.

# Software

TODO

# Alternatives

TODO

# Conclusions

TODO

# Future work

TODO
