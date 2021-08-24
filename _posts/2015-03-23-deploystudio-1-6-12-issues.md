---
layout: post
title: "DeployStudio 1.6.12 with Late-2012 Mac minis and Early-2015 MacBook Pros"
comments: true
---

**UPDATE: DeployStudio have now released version 1.6.13 which addresses the kernel cache issue that was present in 1.6.12.**

**UPDATE 2: OS X is no longer forked as of 10.10.3**

[DeployStudio] hasn't been updated for a while: version 1.6.12 came out 21 October 2014. Since then we've had new Mac minis and MacBook Pros released that won't boot to NetBoot images or USB boot sticks built using version 1.6.12.

What's worse, Early-2015 MacBook Pros (the ones with the new force-touch, taptic TrackPad), are using a forked version of OS X 10.10.2 (14C2513) (regular Macs are still on 14C1514).

# Late-2014 Mac minis

<h4>DeployStudio USB sticks</h4>

**UPDATE: This is no longer required if you upgrade your DeployStudio USB stick using version 1.6.13 of DeployStudio Assistant.**

You can fix your existing DeployStudio USB boot stick so that it will work on the Late-2014 Mac minis by plugging it into a fully up-to-date 10.10.2 Mac and running the following command to patch it:

```bash
$ sudo kextcache -update-volume /Volumes/DeployStudioRuntimeHD -Installer
```

[Reference][1]

<h4>NetBoot images</h4>

**UPDATE: This is no longer required if you upgrade your DeployStudio NetBoot image using version 1.6.13 of DeployStudio Assistant.**

You can also fix your NetBoot image in a similar way **(please note, I haven't tried booting to this yet as my network does not allow it)**:

-   Browse into the NetBoot image, which is normally in the folder `/Library/NetBootSP0`, and double-click `NetInstall.dmg`.
-   Run the following command to patch it:
    `$ sudo kextcache -update-volume /Volumes/DeployStudioRuntime -Installer`
-   Unmount the DMG

# Early-2015 MacBook Pros

The method for Mac minis won't fix your existing USB stick or NetBoot image to make it work on Early-2015 MacBook Pros. You must install DeployStudio on one of these new Macs, and then run DeployStudio Assistant to create your NetBoot image or DeployStudio USB boot stick. You will then have to run the commands as above to patch the images.

Bear in mind that your existing DeployStudio master images and [AutoDMG] OS X installers won't work on these Macs either. Additionally, you cannot download OS X Yosemite from the App Store on these Macs, as the forked version is not available. So if you need to rebuild one of these Macs, you will have to use Internet Recovery, or obtain `InstallESD.dmg` from the recovery partition, e.g. using [this method][2].

[1]: http://www.deploystudio.com/Forums/viewtopic.php?id=7102
[2]: http://hints.macworld.com/article.php?story=20110831105634716"

{% include urls.md %}
