---
layout: post
title:  "Showing the Language Chooser screen after reinstalling macOS"
comments: true
---

When a Mac comes fresh out of the box and is started up, the first setup screen should be the one where you choose the language in which the setup will proceed.

![img-1]

However, this choice appears to be remembered if you reinstall the OS, meaning the first screen you see is the "country choice" screen, in whichever language was initially chosen.

![img-2]

If you work in a multilingual environment, this could be problematic when repurposing Macs, especially using DEP/zero-touch workflows.

Thanks to [an article on the Jamf discussion boards][1] I was able to figure out how to bring the screen back. The process is as follows:

* Install the operating system from the recovery partition or from internet recovery.
* After the computer reboots and gives you the "country choice" screen, force-shutdown the Mac and boot back into the recovery partition.
* Open `Utilities` > `Terminal`
* Enter the following, replacing the volume name if your system volume is not named `Macintosh HD`:

```bash
mount -uw /
touch /Volumes/Macintosh\ HD/var/db/.RunLanguageChooserToo
```

* Now, quit Terminal and reboot back into the newly-installed system volume, and you should see the "language chooser" screen.

[1]: https://www.jamf.com/jamf-nation/discussions/7217/making-language-chooser-run-at-first-boot
[img-1]: /assets/images/mac-install-start.jpg
[img-2]: /assets/images/mac-install-welcome.jpg

{% include urls.md %}
