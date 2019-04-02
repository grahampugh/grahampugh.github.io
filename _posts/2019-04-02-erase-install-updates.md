---
layout: post
title:  "Updates to the erase-install.sh script"
comments: true
---

Back in March 2018, I wrote a [blog post][1] about `startosinstall --eraseinstall`, which had been introduced that day with macOS 10.13.4. This allows us to reinstall macOS directly on any Mac running 10.13.4 or greater and with an APFS filesystem. Since Mojave was released, all systems are running APFS, so this has become universally useful.

In the same blog post, I introduced a Bash script which I named [erase-install.sh][2], which leverages a [fork][3] of [Greg Neagle's installinstallmacos.py][4] script. `installinstallmacos.py` is an easy way to obtain a valid `Install macOS` application using Apple's `softwareupdate` catalogues.

The `erase-install.sh` script includes everything needed to download `installinstallmacos.py` to the system, use it to download the appropriate `Install macOS` application, and optionally run the `startosinstall` binary with the `--eraseinstall` parameter to wipe and reinstall the device.

There have been various iterations over the past year, with additional options such as checks for valid Build ID, and the ability to specify which version or build of macOS to download to the system.

Thanks to some excellent input from Mark Lamont and Anver Housseini, I have today added some new options.

## Specify an OS

Previously you could run `erase-install.sh --erase` to download the nearest valid version of macOS to the system and then perform the erase/install. Upgrading during the erase/install procedure was not recommended - I'm not sure if that's still the case. So if your system is running macOS 10.13.6, for example, this option will download the `Install macOS High Sierra.app` version 10.13.6, and perform the erase.

However, the script can also be used to simply download the installer, and place it in the `/Applications` folder so that users on the system can run the installer manually at a time of their choice to upgrade their system, or the installer can be linked to a management procedure such as an "Upgrade macOS to Mojave" Policy in Jamf Pro. In the previous versions of `erase-install.sh`, you had to specify the specific version of macOS you wanted to download, with the argument `--version=10.14.4` (for example). If 10.14.4 is not available in the softwareupdate catalog, the script will fail/exit.

To improve things, I've now introduced the argument `--os=10.14` into version 0.4.0 of `erase-install.sh`. This only looks for a valid installer matching the specified major version, e.g. 10.13, 10.14 etc., so we don't have to change our workflow every time a new minor version is released.

## Install additional packages

`startosinstall --eraseinstall` supports the installation of additional custom packages during the erase/install process. These packages must be [signed distribution packages][5].

`erase-install.sh` v0.4.0 now includes the option to specify a folder in which to look for packages to include in the `startosinstall` command. The default path is set in the script to `/Library/Management/erase-install/extras`, but this can be overridden with the `--extras=/path/to/folder` argument.

I haven't tested it out, but this should mean Jamf administrators could run "cache-only" policies to put the packages into the Jamf Pro Cache ready for running this policy. Feedback welcome!

Many thanks to Mark Lamont for his work on this part.

## Localisation for Jamf Pro admins

When using `erase-install.sh` to erase/install a client on a system enrolled to Jamf Pro, the Jamf Helper is used to display information to the computer user that the installer application is downloading, and that the erase/install is taking place.

Anver Housseini introduced localisation to the script. It checks the current user's system language and displays the information in that language. Just English (default) and German are available at present, but it would be easy to add additional languages - contributions welcome!

## List-only option

If you just want to run the script to check what versions of macOS installers are available for your system without downloading them, I've added the `--list` parameter, which will just perform the download of the forked `installinstallmacos.py` and then list the available installers and whether they are valid for the system or not, then stop.


[1]: 2018-03-26-reinstall-macos-from-system-volume.md
[2]: https://github.com/grahampugh/erase-install
[3]: https://github.com/grahampugh/macadmin-scripts
[4]: https://github.com/munki/macadmin-scripts
[5]: https://scriptingosx.com/2017/09/on-distribution-packages/

{% include urls.md %}
