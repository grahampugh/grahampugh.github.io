---
layout: post
title:  "Use AutoPkg to install applications into the User Applications folder"
comments: true
---

When setting up my own machine, I often like to install some applications into my own User Applications folder (`/Users/$currentuser/Applications`). This folder does not exist by default, but is recognised as an Applications folder by macOS when created, and items within appear in Spotlight just like any app installed in `/Applications`. Installing them in the user space keeps them separate from apps installed by my management system, MDM or from the App Store.

I also pretty much always install AutoPkg on my Mac, since I write a lot of recipes as part of my job.

> Check out my [AutoPkgSetup](https://github.com/grahampugh/AutoPkgSetup) script for an easy way to install AutoPkg on a new Mac.

AutoPkg offers the use of `.install` recipes, intended to be run interactively on your own machine. However, these all install applications into the `/Applications` folder and set the app bundle ownership to `root`. But some applications' update mechanisms work better when the app is owned by the user&mdash;I'm sure we've all encountered prompts to enter admin credentials to update certain apps when an update becomes available.

## Introducing User-install Recipes

With the help of a new processor, I've now started to create `.userinstall` recipes for apps that I'd like to install into my user space. 

`.userinstall` recipes are like `.install` recipes, but instead of installing the apps into `/Applications`, they install the apps into `/Users/$currentuser/Applications`. They additionally change the ownership of the apps to the current user rather than root.

So far, I've created the following recipes in my [grahampugh-recipes](https://github.com/autopkg/grahampugh-recipes/tree/main/UserInstallers) repo, to help build my own "Admin Toolkit":

* `Apparency.userinstall`
* `iMazingProfileEditor.userinstall`
* `Notion.userinstall`
* `PPPCUtility.userinstall`
* `SilentKnight.userinstall`

![User Applications Folder](/assets/images/User-Apps-Folder.png)

## Technical details

To allow installation into the user space, the current user needs to be identified. A new processor `com.github.grahampugh.recipes.commonprocessors/GetUserHome` achieves this, outputting values for the keys `current_user` and `user_home`. This processor requires no inputs and should be the first process in the `.userinstall` recipe.

Apps that come from a DMG can use the existing `InstallFromDMG` processor. Apps that come from a ZIP or other source should use the `com.github.grahampugh.recipes.commonprocessors/InstallFromFolder` processor, after whatever processors are required to extract the app from it's downloaded source into a folder, e.g. `Unarchiver`.

It should be noted that the existing `InstallFromDMG` processor has the ability to change the ownership of the installed app to the current user, so normal `.install` recipes _could_ be adapted to change the ownership.

## Caveats

Not all apps are suitable for installation into the user space. The recipes in this folder are all based on apps that are supplied within a DMG or ZIP file - these are normally self-contained app bundles that are suitable for installation in the user space. Apps that come from installer packages may not be suitable for installation into the user space. The `InstallFromFolder` would technically be able to install the app from a `.pkg` package into the user space, if an earlier processor extracted the app into a folder in the recipe cache, but each app would need to be tested.

## Conclusion

`.userinstall` recipes are probably only of niche interest, but let me know if you give it a try!

What other apps do you regularly install on your own Mac as part of your "Admin Toolkit"? Let me know and I'll see if they are suitable for a `.userinstall` or `.install` recipe!

{% include urls.md %}
