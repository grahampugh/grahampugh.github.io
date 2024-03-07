---
layout: post
title:  "Do you need to use the softwareupdate command to discover available updates?"
comments: true
---

Many open source tools and vendor products for Mac use the `softwareupdate` command to check for software updates. Typically, they will use the folllowing argument:

    softwareupdate --list

This polls Apple's software catalogs, which normally takes a few seconds. However, many members of the Mac admin community have in recent times been reporting that running this command can cause the `softwareupdated` daemon to hang. That can cause serious problems in certain workflows, including Jamf Pro's Inventory Update (`recon`) if collection of software updates is enabled.

Many open source tools have introduced a step to kickstart the `softwareupdated` daemon before performing the `--list` argument, in an effort to clear the hanging software update process:

    /bin/launchctl kickstart -k system/com.apple.softwareupdated

Even with this workaround, there are problems with using the `softwareupdate --list` command when trying to encourage users to perform software updates themselves, because there can be inconsistencies between the command's output and what gets displayed in the Software Updates Preferences Pane.

> UPDATE, 07 March, 2024: As of macOS 14.4, it is no longer possible to run the kickstart command shown above.

## Do we need to run the softwareupdate command at all?

The `softwareupdate` command is just one of the possible ways that a Mac may check for updates.

In the Software Update settings, a user can check the box "Automatically keep my Mac up to date". Or, in the "Advanced" section, they could just check the box "Check for updates". When this is checked, a LaunchDaemon is set that checks for updates every six hours. These settings can of course also be managed via MDM.

Additionally, your MDM software may also include methods for checking for software updates via MDM commands. And, of course, users may make manual checks of their own accord.

One can imagine that if you have competing management, security and "nudging" tools all running uncoordinated software update checks, potentially simulteneuosly, this could cause the issues that have been reported. Perhaps the "Check for updates" box is enough?

We can access the data from the software update checks by consulting the preferences file `com.apple.SoftwareUpdate.plist`. I first learned this from the people at Root3 who wrote the excellent [Support][1] app.

If we consult the `RecommendedUpdates` key, we get a list of available updates. :

    % defaults read /Library/Preferences/com.apple.SoftwareUpdate.plist RecommendedUpdates
    (
            {
            "Display Name" = Safari;
            "Display Version" = "16.0";
            Identifier = "Safari16.0MontereyAuto";
            "Product Key" = "012-49737";
        },
            {
            "Display Name" = "macOS Monterey 12.6";
            "Display Version" = "12.6";
            Identifier = "MSU_UPDATE_21G115_patch_12.6";
            MobileSoftwareUpdate = 1;
            "Product Key" = "MSU_UPDATE_21G115_patch_12.6";
        },
            {
            "Display Name" = "Command Line Tools for Xcode";
            "Display Version" = "14.0";
            Identifier = "Command Line Tools for Xcode";
            "Product Key" = "012-62819";
        }
    )

If there are no updates, this array will be empty:

    % defaults read /Library/Preferences/com.apple.SoftwareUpdate.plist RecommendedUpdates
    (
    )

Another key, `LastRecommendedUpdatesAvailable`, simply shows the count of updates available. This key in the first example above therefore shows the number `3`:

    % defaults read /Library/Preferences/com.apple.SoftwareUpdate.plist LastRecommendedUpdatesAvailable
    3

If there are no updates, as in the second example above, we just get a zero:

    % defaults read /Library/Preferences/com.apple.SoftwareUpdate.plist LastRecommendedUpdatesAvailable
    0

The advantage of consulting the `com.apple.SoftwareUpdate.plist` file is that the results are instantly returned, and they do not induce a new `softwareupdate` run. Additionally, these results are more likely to be consistent with what the user sees in the Software Update pane, which is helpful if the ultimate aim is to encourage or prompt the user to run any updates themselves (although note that when the user opens the Software Update pane, another check may often be made).

## Which updates require a restart?

Notice also that the macOS update shown in the first example above is labelled with `MobileSoftwareUpdate = 1`. I believe that this indicates an OS update which requires a restart. So that's another thing you can parse to check whether any updates require user intervention such as a prompt for the password of a Volume Owner on Apple Silicon Mac and a required restart.

## Conclusion

Consider whether it is necessary to run `softwareupdate --list` in your tool, especially if you have MDM software, and can push a configuration profile to enable automatic software update checks. Consulting the existing record on the computer is likely to give you the result you need, is less work for your tool, and a reduction in the frequency of polling Apple's software catalog servers could improve the performance of that service. If you are developing a tool that you intend to share, perhaps it is worth giving the tool's users the option of whether the `softwareupdate --list` command is used, or just consulting the plist instead?

> **Amendments:** This post was updated 2022-10-10 with the information about the six hourly check that is made when the "Check for updates" box is checked.

[1]: https://github.com/root3nl/supportapp

{% include urls.md %}
