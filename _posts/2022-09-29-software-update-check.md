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

## Do we need to run the softwareupdate command at all?

If you take a look in the `install.log` log file on a Mac, `softwareupdated` appears to run pretty often. I don't have data to say exactly how often, but it appears to be several times a day, without any manual prompting. In that case, is it really worth polling the software catalogs again in your own script or tool?

We can access the data from the checks that are made by the machine by consulting the preferences file `com.apple.SoftwareUpdate.plist`. I first learned this from the people at Root3 who wrote the excellent [Support][1] app.

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

While there may be reasons to run `softwareupdate --list` in scripts, consider whether it is necessary for your tool. Consulting the existing record on the computer may give you the result you need, is less work for your tool, and a reduction in the frequency of polling Apple's software catalog servers could improve the performance of that service.


[1]: https://github.com/root3nl/supportapp

{% include urls.md %}
