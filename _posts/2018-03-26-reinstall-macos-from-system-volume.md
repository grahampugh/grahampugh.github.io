---
layout: post
title:  "Erase All Contents And Settings (almost) - erase and reinstall macOS in situ"
comments: true
---

Many Mac admins have been anticipating an **"Erase All Contents And Settings"** option for macOS, to emulate that available on iOS. Apple are taking a big step further towards that goal, according to a Knowledge Base article named [Upgrade or Install macOS on a Mac at your Institution][1], which was updated by Apple on 22 February, 2018.

In the briefly-available updated version of the document, a very interesting new feature was detailed, as screenshotted here:

![img-eraseinstall]

A few hours later, the article was removed and replaced with the [earlier version][1].

---

## startosinstall

The `startosinstall` command is included in the `Install macOS High Sierra.app` (and, in fact, since *El Capitan*), which can be downloaded from the Mac App Store. An existing use case for this command is to install macOS High Sierra onto a blank volume, such as in a VM, an external drive, or onto a system volume from a NetInstall image using [Imagr]. A typical command to do so would be:

```
/Applications/Install\ macOS\ High\ Sierra.app/Contents/Resources/startosinstall --applicationpath /Applications/Install\ macOS\ High\ Sierra.app --agreetolicense --nointeraction --volume /Volumes/External\ Macintosh\ HD
```

The `--nointeraction` flag is undocumented, as described in [Rich Trouton's post][2], and allows the command to be run without interaction, meaning it can be scripted.

The new part is the `--eraseinstall` flag.

Extrapolating from what was revealed in the article, the following command should erase the system disk *in situ*, without need to boot from a network drive, or Recovery Partition, or connect to another computer using Target Disk Mode:

```
/Applications/Install\ macOS\ High\ Sierra.app/Contents/Resources/startosinstall --applicationpath /Applications/Install\ macOS\ High\ Sierra.app --eraseinstall --agreetolicense --nointeraction
```

It's as near as you can get to "Erase All Contents And Settings" without some sort of built-in special APFS-snapshot-plus-software-updates mechanism. Many think that will come in the future, but I'm not so sure it would make sense for Apple to provide this. It may just be that we get a wrapper for the `startosinstall` mechanism; perhaps a new check-box in the GUI of `Install macOS High Sierra.app` that says "Erase my Boot Drive and reinstall macOS High Sierra".

---

**Note:** This feature is **not** implemented in macOS 10.13.3. I cannot comment on whether this works or not in current beta versions of macOS 10.13.4, or if there are limitations to its use. I will update this article when the new feature appears in a future official release of `Install macOS High Sierra.app`.

---

## Remotely wiping a managed Mac

Since this command requires no interaction, it will be easy to run this as a command on your management tool (e.g. [Jamf Pro]), or package the command up as a payload-free package to run in [Munki]. All you need to do is ensure the latest `Install macOS High Sierra.app` is available on the device. This is of course done normally via the Mac App Store.

### installinstallmacos.py

Greg Neagle posted a script named [installinstallmacos.py][3] which makes obtaining `Install macOS High Sierra.app` even simpler than via the Mac App Store. It is *not quite* non-interactive, because you have to choose which version of the app to download.

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
 1    091-62780    10.13.3    17D47  Install macOS High Sierra
 2    091-62779    10.13.3  17D2047  Install macOS High Sierra
 3    091-71284    10.13.4  17E160g  Install macOS High Sierra Beta

Choose a product to download (1-3):
```

At this point you select 1, 2 or 3, and the download proceeds. By default the `Install macOS High Sierra.app` is saved into a sparse disk image.

The different versions of macOS are present due to the forked build of 10.13.3, and any available public beta. It would be great to be able to run this locally and programmatically on a client in order to ensure the correct build, but there's currently no flag for that, so this script should be done on an administrator's Mac, and then uploaded to your management server in whatever form is suitable for your platform (`pkg`, `dmg`).

It will then be easy to develop a policy or workflow in which the `Install macOS High Sierra.app` is downloaded to the client (e.g. in Jamf Pro this can be pre-cached on clients), and then the `startosinstall --eraseinstall` command is run in order to set off the rebuild of the device. In a DEP environment, nothing more will be required to get the device ready for the next user.

---

## Warning!

This is a **lethal** workflow and should obviously only be made available to the correct people, and warning messages should be added before it is triggered, since it wipes the device!


[img-eraseinstall]: /assets/images/eraseinstall.png

[1]: https://support.apple.com/en-us/HT208020
[2]: https://derflounder.wordpress.com/2017/09/26/using-the-macos-high-sierra-os-installers-startosinstall-tool-to-install-additional-packages-as-post-upgrade-tasks/
[3]: https://github.com/munki/macadmin-scripts/blob/master/installinstallmacos.py
[4]: https://derflounder.wordpress.com/2018/02/27/using-installinstallmacos-py-to-download-macos-high-sierra-installers/

{% include urls.md %}
