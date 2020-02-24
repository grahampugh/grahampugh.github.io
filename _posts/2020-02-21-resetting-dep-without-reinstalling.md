---
layout: post
title:  "Resetting Device Enrollment cache without reinstalling macOS"
comments: true
---

When a freshly built or rebuilt Mac gets to the "country choice" screen as part of Setup Assistant, and is connected to a network, the device checks in with Apple to see if it is assigned to be enrolled to an MDM service using Automated Device Enrollment (what we used to call DEP). If you forget to assign the device to the correct MDM service before getting to this point, it can be difficult to get it to enroll to the service you intended without reinstalling the OS once again.

In recent times, the following command, which is supposed to reset the DEP cache, has become more reliable:

```
sudo profiles renew -type enrollment
```

The question is, how to run this command during the Setup Assistant process? You can bring up Terminal during Setup Assistant, but since there is no admin account on the device up to the point when Device Enrollment takes place, one cannot run the above command.

## Gaining root access at the Setup Assistant

To be able to run the above command, we need to gain root access. I learned this is possible from [@yohan] via MacAdmins Slack. 

First, we need to re-enable the Language Chooser Screen, which is the first screen in Setup Assistant but is not shown by default on computers more than once. To do this, we can do one of two things:

1. On Macs without a T2 chip, boot into Single User Mode using `cmd-S`.
2. On Macs with or without a T2 chip, boot into Recovery Mode using `cmd-R` and open `Utilities` > `Terminal`.

On a Mac running Catalina or greater, run the following commands:

    ```bash
    mount -uw /System/Volumes/Data
    touch /var/db/.RunLanguageChooserToo
    ```

On a Mac running Mojave or earlier, run the following commands, replacing the volume name if your system volume is not named `Macintosh HD`:

    ```bash
    mount -uw /
    touch /Volumes/Macintosh\ HD/var/db/.RunLanguageChooserToo
    ```

Now, if you are in Recovery Mode, quit Terminal, and whether in Recovery or Single-User Mode, reboot back into the system volume, and you should see the "language chooser" screen.

![img-1]

To open Terminal at this screen, click `ctrl-alt-cmd-T`. Terminal at this point is running as root. So, now you can run:

```
profiles renew -type enrollment
```

Then close Terminal and continue with Setup Assistant as normal. In my recent experience this has always been successful in resetting the DEP cache so that it will check in with Apple again and get the correct current DEP status.


[img-1]: /assets/images/mac-install-start.jpg

{% include urls.md %}
