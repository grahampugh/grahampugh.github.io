---
layout: post
title:  "Erase All Contents And Settings - erase and reinstall macOS in situ"
comments: true
---

Many Mac admins have been anticipating an **"Erase All Contents And Settings"** option for macOS, to emulate that available on iOS. Apple have taken a big step further towards that goal in macOS 10.13.4.

---

## startosinstall --eraseinstall

The `startosinstall` command is included in the `Install macOS High Sierra.app` (and, in fact, since *El Capitan*), which can be downloaded from the Mac App Store. An existing use case for this command is to install macOS High Sierra onto a blank volume, such as in a VM, an external drive, or onto a system volume from a NetInstall image using [Imagr]. A typical command to do so would be:

```
/Applications/Install\ macOS\ High\ Sierra.app/Contents/Resources/startosinstall \
  --applicationpath /Applications/Install\ macOS\ High\ Sierra.app \
  --agreetolicense --nointeraction --volume /Volumes/External\ Macintosh\ HD
```

The `--nointeraction` flag is undocumented, as described in [Rich Trouton's post][2], and allows the command to be run without interaction, meaning it can be scripted.

In the Apple Knowledge Base article [Prepare your institution for macOS High Sierra 10.13.4][5], Apple revealed a new flag for the `startosinstall` command, the `--eraseinstall` flag:

> The `startosinstall` command inside the macOS Installer app at Contents/Resources/startosinstall lets you erase your boot volume and install macOS to it using the new `--eraseinstall` flag. You can use the `--installpackage` flag to specify additional packages to apply after installing macOS.

Using the new flag, the following command erases the system disk *in situ*, without need to boot from a network drive, or Recovery Partition, or connect to another computer using Target Disk Mode:

```
/Applications/Install\ macOS\ High\ Sierra.app/Contents/Resources/startosinstall \
  --applicationpath /Applications/Install\ macOS\ High\ Sierra.app \
  --eraseinstall --agreetolicense --nointeraction
```

It's as near as you can get to "Erase All Contents And Settings" without some sort of built-in special APFS-snapshot-plus-software-updates mechanism. Many think that will come in the future, but I'm not so sure it would make sense for Apple to provide this. It may just be that we get a wrapper for the `startosinstall` mechanism; perhaps a new check-box in the GUI of `Install macOS High Sierra.app` that says "Erase my Boot Drive and reinstall macOS High Sierra".

### Notes

1. The `--eraseinstall` flag only works on APFS volumes, and only works on devices that already have macOS 10.13.4 installed. It is also only present in versions of the `Install macOS High Sierra.app` that install macOS 10.13.4 or above.

2. You cannot specify a volume with the `--volume` flag in combination with the `--eraseinstall` flag, since it is implied that the command will be run on the volume to be erased.

---

## Remotely wiping a managed Mac

Since this command requires no interaction, it is easy to run this as a command on your management tool (e.g. [Jamf Pro]), or package the command up as a payload-free package to run in [Munki]. All you need to do is ensure the latest `Install macOS High Sierra.app` is available on the device. This is of course done normally via the Mac App Store.
### installinstallmacos.py

Greg Neagle published a script named [installinstallmacos.py][3] which makes obtaining `Install macOS High Sierra.app` even simpler than via the Mac App Store. It is *not quite* non-interactive, because you have to choose which version of the app to download, but this can be circumvented - see below.

As detailed in [another blog post by Rich Trouton][4], all that is required to obtain the `Install macOS High Sierra.app` in a disk image is the following command, which requires root privileges:

```
$ sudo python installinstallmacos.py

Downloading https://swscan.apple.com/content/catalogs/others/index-10.13seed-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog...
Downloading http://swcdn.apple.com/content/downloads/16/14/091-62779/frfttxz116hdm02ajg89z3cubtiv64r39s/InstallAssistantAuto.smd...
Downloading https://swdist.apple.com/content/downloads/16/14/091-62779/frfttxz116hdm02ajg89z3cubtiv64r39s/091-62779.English.dist...
Downloading http://swcdn.apple.com/content/downloads/10/36/091-62780/objx55fn5lwnefnetcap2i0c7xg3avoor9/InstallAssistantAuto.smd...
Downloading https://swdist.apple.com/content/downloads/10/36/091-62780/objx55fn5lwnefnetcap2i0c7xg3avoor9/091-62780.English.dist...
Downloading http://swcdn.apple.com/content/downloads/45/61/091-71284/77pnhgsj5oza9h28y7vjjtby8s1binimnj/InstallAssistantAuto.smd...
Downloading https://swdist.apple.com/content/downloads/45/61/091-71284/77pnhgsj5oza9h28y7vjjtby8s1binimnj/091-71284.English.dist...
 #    ProductID    Version    Build  Title
 1    091-76233    10.13.4   17E199  Install macOS High Sierra
 2    091-62779    10.13.3  17D2047  Install macOS High Sierra
 3    091-71284    10.13.4  17E160g  Install macOS High Sierra Beta


Choose a product to download (1-3):
```

At this point you select 1, 2 or 3, and the download proceeds. At the time this post was written, option 1 gives you the latest official 10.13.4 build. By default the `Install macOS High Sierra.app` is saved into a sparse disk image. If you know in advance which value you want (in tests, it does consistently provide the list in the same order), you can supply the required value in a shell script with the following syntax, which will make the script proceed without interaction:

```
$ yes 1 | sudo python installinstallmacos.py
```

Using this command means that you don't need to host the `Install macOS High Sierra.app` on your management system, you  can just run this when required on the device itself.

With `Install macOS High Sierra.app` on the client, the `startosinstall --eraseinstall` command can be run in order to set off the rebuild of the device. In a DEP environment, nothing more will be required to get the device ready for the next user.  

---

## Automate the whole process

I have written a script that can be deployed to a client that you wish to wipe, which will, without any required interaction, download and run `installinstallmacos.py`, download the `Install macOS High Sierra.app` and place it in a `sparseimage`, mount the `sparseimage` and run the `startosinstall --eraseinstall` which creates a temporary new volume on which to place the installer, reboots the Mac and proceeds to install the vanilla image.

**The script is now available as a GitHub repository. Go to [github.com/grahampugh/erase-install][erase-install]**

***Note: to prevent duplication and stale scripts, I've removed the previous gist link for this script***

Note that if you have this script in a Jamf Pro policy, you can specify which macOS installer value you wish to feed to `installinstallmacos.py` in Parameter 4. Otherwise, add the value into the script. See the notes in the script for details.

Adding the `--installpackage` flag to the `startosinstall` command, you can add additional signed packages to the command which will be installed after installation, such as a signed client agent installer for Munki, Puppet, Chef etc. These would have to be cached on the client before the command was run.

---

## Warning!

This is a **lethal** workflow and should obviously only be made available to the correct people, and warning messages should be added before it is triggered, since it wipes the device!

[1]: https://support.apple.com/en-us/HT208020
[2]: https://derflounder.wordpress.com/2017/09/26/using-the-macos-high-sierra-os-installers-startosinstall-tool-to-install-additional-packages-as-post-upgrade-tasks/
[3]: https://github.com/munki/macadmin-scripts/blob/master/installinstallmacos.py
[4]: https://derflounder.wordpress.com/2018/02/27/using-installinstallmacos-py-to-download-macos-high-sierra-installers/
[5]: https://support.apple.com/en-us/HT208488

{% include urls.md %}
