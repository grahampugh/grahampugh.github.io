---
layout: post
title:  "Apple Security Update mistakenly disables Ethernet ports"
comments: true
---

Apple today made an error with a security update that could have a high IT support cost.
As reported in [MacRumors Forums](http://forums.macrumors.com/threads/software-update-031-51913-will-break-your-ethernet-driver.1958521/),
"Software update 031-51913", designed to block some incompatible Kernel Extensions, 
also renders certain Mac models unable to connect to the Internet via Ethernet ports, as 
the ports become unrecognised.

Reports show that many iMacs, MacBook Pros, Mac mini and Mac Pro computers are affected.

Apple have already released a fix, which can be directly downloaded as a package:

[AppleKextExcludeList_10_11.pkg](http://swcdn.apple.com/content/downloads/47/55/031-52551/djk479pucjbs7r2ln9u3n0573nt31ifb45/AppleKextExcludeList_10_11.pkg)

As noted on Twitter by [@MikeyMikey], you can tell if the fix has been deployed in 
`/var/log/install.log`, as you will see `031-52551 | Incompatible Kernel Extension Configuration Data 3.28.2`:

![img_1]

Affected Mac computers that are connected via wi-fi will get the update and the Ethernet 
adapter will be once again detected and functional. But if wi-fi is unavailable, it won't be possible to use deployment
methods such as Munki, ARD, Casper etc, or wait for automatic updates to fix the error. 
Manual intervention is required, either connecting via external Ethernet adapter and running 
software updates, or transferring the fix manually with a Flash Drive.  That could be a 
support-time problem in organisations that have ethernet-connected Mac labs, common in education.

How to avoid this in future?
----------

After this error by Apple, IT organisations may need to consider testing Apple security updates before 
deploying them to their Mac fleets.  There are two ways you can achieve this:

*  The [Software Update service](https://support.apple.com/en-us/HT202030) in OS X Server
   allows you to cache and control the release of updates.  This requires a Mac running the OS X Server app, 
   with sufficient storage to host updates.  
*  [Reposado] is a mature, open source tool which replicates the functionality of OS X Server's 
   Software Update service, which can be hosted on a Linux server or VM. A web front end for 
   Reposado has also been created: [Margarita].

[img_1]: https://pbs.twimg.com/media/CcQi97EUEAARKJs.jpg

{% include urls.md %}

