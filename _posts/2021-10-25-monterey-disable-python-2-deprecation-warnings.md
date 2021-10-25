---
layout: post
title:  "macOS Monterey - MDM custom preference to disable python 2 deprecation popups"
comments: true
---

If you run a Python script on a Mac running macOS Monterey, or even if there is a `python` command in a shell script that you run on Monterey, you will get a popup warning, something like this:

![python2 warning](/assets/images/JamfNeedsToBeUpdated.png)

Python 2 was deprecated back in January 2020, but Apple are still including it in the latest OS for "compatibility". With Monterey, they decided to add this warning, and this can prevent the scripts from running at all, for example if they are being run freom your managment system when nobody is logged into the computer.

It's also not obvious to the user that the prompt is caused by a python script. It makes it appear that the program that invokes the script is "out of date". I've also seen this when using Visual Studio Code, for example, because an extension is evaluating python 2 scripts I still have in some repos. But the warning is just telling me that Visual Studio Code is out of date and needs to be updated.

Now is the time to remove any Python 2 scripts from your management workflow. But, if you wish to prevent your users from seeing this prompt while you work through finding and removing any python scripts or commands from your workflow, you can do it easily enough with a custom MDM preference key.

The domain you need is `com.apple.python`, and the preference key is `DisablePythonAlert` - set it to `True`.

If you are using Jamf Pro, you can just copy-paste [this payload][1] into a custom profile:

```xml
<plist version="1.0">
<dict>
    <key>DisablePythonAlert</key>
    <true/>
</dict>
</plist>
```

For the crazies among you, I also have an [AutoPkg recipe to create the profile in Jamf][2].

[1]: https://github.com/eth-its/autopkg-mac-recipes-yaml/blob/main/Profiles/com.apple.python.plist
[2]: https://github.com/eth-its/autopkg-mac-recipes-yaml/blob/main/Jamf_Profile_Recipes/DisablePython2DeprecationPrompt-profile.jamf.recipe.yaml

{% include urls.md %}
