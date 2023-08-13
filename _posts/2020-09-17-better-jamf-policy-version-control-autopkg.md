---
layout: post
title: "Better Jamf Policy Version Control with AutoPkg and Regex"
comments: true
---

One of the major limitations of [Jamf Pro] in comparison to [Munki] when it comes to software deployment is the lack of ability to compare version strings between what is installed on a Mac client and what is available in the software repository. Munki can determine whether the installed version has a "lower", "higher" or equal version string than the version in the repo, which means Munki will never try to install an older version of an app than what is currently installed. Jamf, on the other hand, can only determine whether the strings are equal or not.

When you scope an ongoing, recurring check-in Policy based on Smart Group criteria that an Application is installed and the installed Application Version is not equal to a given version, that policy will run so long as the installed version does not match the repo version. But what if the user managed to install a newer version of the app than you are currently offering via Jamf? Either the older version will overwrite the newer version or, as often happens, the installation of the older version will fail, since many package installers include checks to prevent downgrading. At next check-in, the policy will try and fail again, and this will repeat over and over...

## Patch?

Jamf Patch was supposed to address this issue, but rather than adding "greater than"/"less than" functionality to regular policies, the Patch project became an over-engineered nightmare, necessitating compiling lists of versions in a separate server not included in Jamf Pro, and creating different Patch Policy objects in Jamf Pro which can only be scoped to computers that already have some version of the app installed, meaning you still have to maintain policies for computers that don't have the app installed.

## Match Version Number Or Higher.bash

Recent versions of Jamf Pro have added the ability to do a regex match of Application Version. Though not as simple as "greater than" / "less than" options, it does open up the possibility of constructing a regex string which matches the current version plus any feasible higher version.

Back in the summer of 2020, William Smith of Jamf Professional Services shared a script which, when provided with a version string from the command line, outputs a regex string which matches the inputted version and anything higher. This complicated and impressive script is available as a gist file: [check it out here!][1].

William also gave an excellent video conference talk as part of the [2020 MacAdmins Campfire Sessions][2] about regex which touches on this script at the end: [you should watch this now if you haven't already!][3].

As an example, the regex for version `80.0.1` of Firefox is:

    ^(\d{3,}.*|9\d{1,}.*|8[1-9].*|80\.\d{2,}.*|80\.[1-9].*|80\.0\.\d{2,}.*|80\.0\.[2-9].*|80\.0\.1.*)$

The outputted version string can be pasted into a Smart Group, so that if installed Application Version does not match the regex string, the policy is in scope. Here is an example for Firefox based on an "update-smart" Smart Groups similar to that used in standard AutoPkg `.jss` recipes:

![Firefox-update-smart Smart Group]

This policy is only in scope if Firefox is either not installed, or an older version of Firefox is installed (and if the computer is in the `Testing` static group). This properly mimics Munki's criteria for installing the Firefox package.

Unfortunately, we need to recalculate the regex string each time the version is bumped for an app. Manually running this script for each application in your Jamf portfolio every time there is an update is not very scalable.

## Automation with AutoPkg - enter VersionRegexGenerator

After William's talk I started thinking about how to automate the creation of the regex strings as part of an [AutoPkg] workflow. At first I wondered about bundling the script into [JSSImporter], but so that it could be used in other recipes, I settled on creating a separate AutoPkg processor.

The [VersionRegexGenerator][4] processor is a wrapper over an amended version of William's `match-version-number-or-higher.bash` ([see it here][5]). It takes the value of `version` that is normally output from the parent `.pkg` recipe, and outputs a value for `version_regex`. The `SmartGroupTemplate.xml` used by JSSImporter or other Jamf-related Processors can be amended to use `%version_regex%` rather than `%version%`.

## How to add regex matching to a `.jss` recipe

In `.jss` recipes, you simply need to add this processor before the `JSSImporter` processor:

```xml
<dict>
    <key>Processor</key>
    <string>com.github.grahampugh.recipes.commonprocessors/VersionRegexGenerator</string>
</dict>
```

> Note that this cannot be added to a Recipe Override, since it comes _before_ the JSSImporter process, so anyone wishing to use this will need to clone the existing recipe into their own repo and add the the processor.

As examples, I have converted most of the `.jss` recipes in the `grahampugh-recipes` repo to use regex matching. [Check them out][6].

## Conclusion

Thanks to William Smith's work, and a bit of tweaking from myself, we can start to get better version control in Jamf Pro. We no longer have to manage the problem of users with admin rights updating their apps beyond what we have tested and made available in Jamf - at least from the prospective of policies running over and over, or making policies available in Self Service that may fail to run.

I'd like to hear from you if you use this processor. I envisage that the `VersionRegexGenerator` processor would be of most use to those of us who create our own recipes for deploying apps to production computers, and have started using it internally.

Let me know also if you think the processor should be included in standard `.jss` recipes. Standard `.jss` recipes create Self Service policies that are only meant for testing, so it's not a critical benefit to these recipes, and I am not the maintainer of the `jss-recipes` repo so that's not my decision, but we can ask 😀.

[firefox-update-smart smart group]: /assets/images/firefox-update-smart.png
[1]: https://gist.github.com/2cf20236e665fcd7ec41311d50c89c0e
[2]: https://www.youtube.com/playlist?list=PLRUboZUQxbyUyqkH7BFaQGAR7x51olLNt
[3]: https://www.youtube.com/watch?v=Wc8Kpw0nEww&list=PLRUboZUQxbyUyqkH7BFaQGAR7x51olLNt
[4]: https://github.com/autopkg/grahampugh-recipes/tree/master/CommonProcessors#versionregexgenerator
[5]: https://github.com/autopkg/grahampugh-recipes/blob/master/CommonProcessors/match-version-number-or-higher.bash
[6]: https://github.com/autopkg/grahampugh-recipes/tree/master/_JSS_Recipes

{% include urls.md %}
