---
layout: post
title: "Undocumented options in the startosinstall command"
comments: true
---

Since OS X 10.11, OS X / macOS installer applications have had the `startosinstall` command line tool bundled in it. My [presentation at the Texas Apple Admins Virtual Meetup](2020-05-05-texas-apple-admins-presentation.md) last month went into the history of the command, and the available command line options.

The currently documented options are as follows:

    --license, prints the user license agreement only.
    --agreetolicense, agree to the license you printed with --license.
    --rebootdelay, how long to delay the reboot at the end of preparing. This delay is in seconds and has a maximum of 300 (5 minutes).
    --pidtosignal, Specify a PID to which to send SIGUSR1 upon completion of the prepare phase. To bypass "rebootdelay" send SIGUSR1 back to startosinstall.
    --installpackage, the path of a package (built with productbuild(1)) to install after the OS installation is complete; this option can be specified multiple times.
    --eraseinstall, (Requires APFS) Erase all volumes and install to a new one. Optionally specify the name of the new volume with --newvolumename.
    --newvolumename, the name of the volume to be created with --eraseinstall.
    --preservecontainer, preserves other volumes in your APFS container when using --eraseinstall.
    --forcequitapps, on restart applications are forcefully quit. This is the default if no users are logged in.
    --usage, prints this message.

An additional undocumented option is already well known:

    --nointeraction

This option, along with the `--agreetolicense` option, is required to run the `startosinstall` command silently, for example from a script.

## There are more options!

A problem was reported to me by my colleague Anver Housseini while running my [erase-install] tool to reinstall macOS. The `startosinstall` command quit without starting the install, with the following output:

    The files "Preboot" and "com.apple.TimeMachine.localsnapshots" are located on the root
    of Macintosh HD. If you continue installing, these files will be deleted. To continue
    anyway, add --allowremoval.

The `--allowremoval` was unknown to me, so I asked the MacAdmins Slack collective brain about it. Nobody seems to have come across it, but some digging by `@nstrauss` found this and one other additional undocumented option:

    --bridgeos-pkg

`@bp` was able to determine that both these options have been present in all public versions of macOS 10.15.

## allowremoval

As shown above, this option seems to be a way to force-clear some files on the system disk that otherwise cause the command to halt. The possible error messages are as follows:

    The file "%s" is located on the root of %s. If you continue installing, this file will
    be deleted. To continue anyway, add --allowremoval.
    The files "%s" and "%s" are located on the root of %s. If you continue installing,
    these files will be deleted. To continue anyway, add --allowremoval.
    The file "%s" and %lu others are located on the root of %s. If you continue installing,
    these files will be deleted. To continue anyway, add --allowremoval.

So, one or multiple files can cause the command to halt. I don't know what the possible files would be, but local snapshots appear to be one such object. I tried to reproduce the error by creating a local snapshot on a T1 MacBook Pro running 10.15.4, but it didn't cause the command to halt or print an error.

## bridgeos-pkg

This would appear to be an option to supply your own BridgeOS package. BridgeOS is the operating system installed on the T2 chip. These packages are normally obtained from Apple's servers during the installation of macOS. The existence of this option implies that you can override the behaviour to supply a different BridgeOS package.

It is unclear what this would be used for. For example, could it be used to bypass the need for internet during reinstallation? Is it used by Apple engineers to install unpublished/beta/forked versions of BridgeOS for testing?

It is a brave soul who tests this feature out! I would imagine that the pieces could be picked up with a DFU restore, but (what a shame) I do not have a T2 Mac in my Home Office with which to experiment 😀

Let us all know if you try it, and what happens!

Thanks again to `@nstrauss` and `@bp` for indulging in some digging to find out more about these undocumented command options.

{% include urls.md %}
