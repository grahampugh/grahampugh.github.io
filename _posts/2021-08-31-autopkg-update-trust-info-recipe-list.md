---
layout: post
title: "AutoPkg - verify and update trust information on all recipes in a recipe-list"
comments: true
---

I use [AutoPkg] for multiple workflows, and as a result I have developed a lot of custom shared processors. As with most code, I often have to update my shared processors as I find bugs or scale up and factor in additional edge cases. Often times these shared processors feature in many or all of my recipes, and every time I make a change to one of the processors, I have to update the trust information on every recipe.

For very legitimate reasons, the command `autopkg update-trust-info` does not include an option to go through an entire recipe list and update the trust on each one. For example, if I update my processor, but at the same time, a parent recipe from another repo is changed, and I blindly update the trust on it, then I'm defeating the object of keeping recipe overrides.

However, accepting those caveats, I needed a way to do this, as it would just not be possible to update all the trusts manually given the number of recipes I maintain.

## autopkg-update-trust-info-recipe-list.sh

Users of my [JamfUploader][jamfuploader] and/or [VersionRegexGenerator][version-regex-generator] processors are probably already familiar with this problem. To make life easier for those of you who haven't already gone ahead and written something similar, I have made a script that allows you to update all recipes in a list at once. The script is called [autopkg-update-trust-info-recipe-list.sh](https://github.com/grahampugh/osx-scripts/tree/main/autopkg-scripts) and is available [here](https://github.com/grahampugh/osx-scripts/tree/main/autopkg-scripts).

To update trust information on a recipe list, simply run the script with the path to the list as a parameter:

    /path/to/autopkg-update-trust-info-recipe-list.sh /path/to/recipe-list.txt

The script has various options, including:

- To add verbosity to the verification output, add `-v` or `-vv`. The `-vv` option is very useful, as it shows you the git diff of any changed recipe files or shared processors.

- To run through the recipe list and verify which recipes are trusted, but not actually update the trust, use the `--verify-only` parameter. This should be used as a safety net before blindly updating trust on the list. If you don't already have another system in place to monitor the trust of your recipes, then I recommend that you run this first, with `-vv` set, so that you can see the differences in each recipe and mitigate any that are unconnected to the known update of a shared processor.

- To set the format of the override, use the `--format` parameter with either the `plist` or `yaml` value. The default is `yaml`.

- To force new overrides rather than update the existing one, use the `--force` option. I would not recommend this option unless you are maintaining your own recipes and have to make changes to the `Input` lists in a whole bunch of them at the same time (because `autopkg --update-trust-info` does not update the `Input` list of your override).

> Note: If no existing override is found, it will make one. This shouldn't be common, but if you are maintaining a single recipe list that is used on multiple AutoPkg servers, it will help you stay in sync. Additionally, you can add the `--pull` parameter and any parent repos that are missing will be added to your repo list.

For a full set of options, run `/path/to/autopkg-update-trust-info-recipe-list.sh --help`.

## Conclusion

This script provides a way to update trust on all AutoPkg recipes in a recipe list after a shared processor that is in many of the recipes changes. I do not recommend that you use it as a regular tool for updating trust without first verifying what has changed, but I hope it helps [JamfUploader][jamfuploader] users handle the frequency of updates better.

> By the way, I will announce any updates to the [JamfUploader][jamfuploader] processors in the [MacAdmins Slack][macadmins slack team] `#jamf-upload` channel, and you can subscribe to notifications for any changes to GitHub AutoPkg repos that contain shared processors that you use by clicking the "Watch" button on the GitHub page for that repo.

{% include urls.md %}
