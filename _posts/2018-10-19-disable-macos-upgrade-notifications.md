---
layout: post
title:  "Disable macOS Upgrade Notifications"
comments: true
---

As is common around this time of year, Apple have begun to push out notifications to logged-in Mac users, inviting them to upgrade to the latest version of macOS. This time, of course, it's 10.14 Mojave.

![img-1]

## How is the notification pushed to users?

The notification is itself distributed by Apple's software update. It is a package named `macOSInstallerNotification_GM.pkg`.

When the package is installed, it extracts to `/Library/Bundles/OSXNotification.bundle`

The notification is then pushed as per the preferences in `/Library/Preferences/com.apple.noticeboard.plist`

## How do I stop it from showing on macOS 10.12 and 10.13 devices?

_Note: This post is not concerned with the rights and wrongs of preventing upgrade to Mojave._

If the computer has not yet received the update, you can prevent it if you manage your own software update catalog, for example with [Reposado].

You can alternatively run a command to ignore the particular update.

Note that as per the man page for `softwareupdate`:

> The identifier is the first part of the item name (before the dash and version number) that is shown by `softwareupdate --list`.

Using the `--ignore` option of `softwareupdate`, you can therefore ignore the update as follows:

```
softwareupdate --ignore macOSInstallerNotification_GM
```

If you run this as root, you should see this output:

```
Ignored updates:
(
    "macOSInstallerNotification_GM"
)
```

If you missed the chance to prevent the update and you're already seeing popups, then you can delete the installed bundle (again, as root):

```
rm -rf /Library/Bundles/OSXNotification.bundle
```

In the tests of others, this was enough to prevent the pop-up. Incidentally, the process is identical to the notifications for High Sierra a year ago.

It might also be possible to suppress the notifications by manipulating the preferences in `com.apple.noticeboard`, but you could end up suppressing unrelated notifications. There's scant reference to this method, but see [this Jamf Nation article](https://www.jamf.com/jamf-nation/discussions/26103/high-sierra-upgrade-nags) for how some people dealt with it with High Sierra. But it seems it may not be necessary.


## Have you just got a script for all this?

Sure, see this gist:

{% gist a027206e47a1e4e9f346b884dd8cfdeb %}

If you're in Jamf Pro, push this script in a policy to computers running a version of macOS less than 10.14.

If you use [Munki], then [Rick Heil](https://rickheil.com/) has a blog post just for you: [Suppress New OS Major Version Updates with Munki](https://rickheil.com/suppress-new-os-major-version-updates-with-munki/).


What about 10.11 devices?
----

Slack user `@rrenstrom` reported that the notification machanism is different on OS X 10.11:

>I saw a similar upgrade notification on a 10.11 system. Looks like Apple is using a different mechanism here, although the notification looks the same.
>
>If it installs (perhaps only on Macs with a deprecated OS <10.12), it will show up in `install.log` as `10.14NoticeboardNotification`.
>
>Unlike the other Mojave upgrade notification being distributed as a software update (the macOSInstallerNotification_GM package), this one is triggered by nbagent and from a separate updates catalog (noticeboard), so it may not be possible to block with the `--ignore` tactic, but it's worth a try (e.g. `softwareupdate --ignore 10.14NoticeboardNotification`). The package receipt `pkgutil --files com.apple.pkg.10.14NoticeboardNotification.16U1627` shows it installed at `/private/tmp/noticeboard/com.apple.noticeboard.notification.10.14fornon10.8.1.0.bundle`.
>
>It adds some entries to `/Library/Preferences/com.apple.noticeboard.plist` to keep track of how many times the notification popup has been dismissed. From the `reminderIntervals` key in the update catalog, looks like it may appear every 7 days, 24 times.

I have not yet set up an OS X 10.11 device with which I could test a mechanism for suppressing these updates. I'll update this blog if I can verify that the above steps are effective.




Acknowledgements
----

This information came from a conversation in the [#mojave](https://macadmins.slack.com/messages/CB0547P08) channel on the [MacAdmins Slack Team], particularly from the following users:

```
@tom.case
@elios
@ehemmete
@matx
@refreshingapathy
@zoocoup
@rrenstrom
```

Thanks, all!

[img-1]: /assets/images/Upgrade.png

{% include urls.md %}
