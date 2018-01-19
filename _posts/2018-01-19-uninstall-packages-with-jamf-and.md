---
layout: post
title:  "Jamf Pro uninstaller policies with a little help from Munki"
comments: true
---

[Munki]'s' `pkginfo` files can contain information not only on how to install a package, but also how to uninstall it. When an application is installed on a client, the **Managed Software Center** can therefore offer a `Remove` button:

![img-3]

There are four main types of uninstaller action built in to Munki:

1. Deletion of applications that live entirely within `/Applications` folder.
2. Running a vendor-supplied uninstaller application, binary or script.
3. Removal of packages using information in the package receipts.
4. A self-crafted uninstaller script.

A high proportion of applications can be uninstalled using options 1 or 3.

Jamf has only a limited offering when it comes to application removal. You have two choices:

1. Manually "index" a snapshotted package using the `Jamf Admin` macOS application. Indexed policies gain a "Remove" button. This is not an option at all if you are using AutoPkg to automate the production of installer packages.
2. Create a separate policy for uninstalling a policy. This must be manually crafted (normally using a script or an uninstaller package).

You cannot really replicate the "Remove" button experience of Munki with option 2, but at least you can create Uninstaller policies, scoped only to clients with those applications installed.

![img-4]

---

## 1. Jamf Pro: Deletion of applications that live entirely within the Applications folder

It's easy to script this, so you can easily create a template script that takes care of Uninstaller policies for App Store apps and similarly contained applications. Here's a quick and very basic example:

{% gist 97cd9c3de8f4690a9dc242f74c3211a9 %}

---

## 2. Jamf Pro: Running a vendor-supplied uninstaller application, binary or script

Similarly, it's easy to write a script that will run a vendor's uninstaller that is already on the client drive. I don't even need to provide an example here, which is good as I don't have one yet.

---

## 3. Jamf Pro: Removal of packages using information in the package receipts

This is tougher. You have to analyse the package receipts for the installed files, then pass that information to a script that deletes them all. Then delete the package receipt. You can get a list of files that were installed using a particular package using the following command:

```
pkgutil --files co.pretend.ShinyApplication
```

Perhaps you could use this list and pipe it to an `rm` command. But of course, every package includes folders right up to the root folder, e.g.:

```
$ pkgutil --files jp.co.canon.CUPSPS_M.icons.SF-04.pkg
Library
Library/Printers
Library/Printers/Canon
Library/Printers/Canon/CUPSPS2
Library/Printers/Canon/CUPSPS2/Icons
Library/Printers/Canon/CUPSPS2/Icons/SF-04
Library/Printers/Canon/CUPSPS2/Icons/SF-04.bundle
Library/Printers/Canon/CUPSPS2/Icons/SF-04.bundle/Contents
Library/Printers/Canon/CUPSPS2/Icons/SF-04.bundle/Contents/Info.plist
...
```

So you can't use `rm -rf` to delete folders and their contents, as that could get very messy. You need to iterate through the list properly so that you only remove files and empty folders.

This logic has been built into the Munki client, and it provides a command-line Python script called `removepackages` to perform the removal, based on a package ID:

```
$ sudo /usr/local/munki/removepackages -l jp.co.canon.CUPSPS_M.icons.SF-04.pkg
Password:
    Gathering information on installed packages...
	0..20..40..60..80..100
	0..20..40..60..80..100
    Determining which filesystem items to remove...
/Library/Printers/Canon/CUPSPS2/Icons/SF-04
/Library/Printers/Canon/CUPSPS2/Icons/SF-04.bundle
/Library/Printers/Canon/CUPSPS2/Icons/SF-04.bundle/Contents
/Library/Printers/Canon/CUPSPS2/Icons/SF-04.bundle/Contents/Info.plist
...
```

Wouldn't it be great if Jamf Pro could utilise this tool to make package removal simple, so we don't have to write a new one?

Well, it can!

---

## Jamf And... a bit of Munki: Using removepackages with Jamf Pro

`removepackages` is not a self-contained script. It imports various modules from Munki's library of python functions. So to utilise `removepackages` on a client we need to install Munki on the client.

...but not all of Munki. We only need the `core` Munki tools.

### Installing the core munkitools

You can download Munki as a single package, but then we would have to install the entire suite of Munki tools, the Managed Software Center, and the LaunchDaemon, which requires a reboot. We don't want most of this stuff. Additionally, of course, we want to get the package into the JSS from [AutoPkg].

I only found a `munkitools3.munki` AutoPkg recipe - no `.download` or `.pkg` recipe. The `.munki` recipe is useful to us in some ways, in that it downloads the munkitools package and repackages it into five components, `core`, `admin`, `app`, `app-usage` and `launchd`. But the recipe cannot be run by Jamf Pro admins, however, as it will fail, since no Munki repository is configured. And we only want the `core` package.

Fortunately it was easy to edit the existing `.munki` recipe to create a `MunkiToolsCore.pkg` recipe and associated `MunkiToolsCore.jss` recipe to import the package into the JSS using [JSSImporter]. I've made them available on my GitHub ([github.com/grahampugh/grahampugh-autopkg-recipes](https://github.com/grahampugh/grahampugh-autopkg-recipes/tree/master/MunkiToolsCore)), but feel free to put in your own repo.

**Scope**

You can scope this policy to everyone, otherwise be sure to create a smart group of clients that have it installed.

**What gets installed?**

The `core` package installs just the following:

```
/Library/Managed Installs
/Library/Managed Installs/Cache
/Library/Managed Installs/catalogs
/Library/Managed Installs/manifests
/usr/local/munki/authrestartd
/usr/local/munki/launchapp
/usr/local/munki/logouthelper
/usr/local/munki/managedsoftwareupdate
/usr/local/munki/munkilib/*
/usr/local/munki/ptyexec
/usr/local/munki/removepackages
/usr/local/munki/supervisor
```

I think we only actually need the `/Library/Managed Installs` folder, where a small sqlite database of package receipt info is maintained, and `/usr/local/munki/removepackages` and `/usr/local/munki/munkilib/*`, but I haven't bothered trying to re-script the recipes to trim it down further, as it is lightweight and innocuous enough as it is.

### Creating a policy to uninstall a packaged application

You can add a template script to a policy which has the package ID as a parameter. If a policy installs multiple packages, just add more package IDs to the next parameters. Here's an example I made earlier:

{% gist bb065d69a5c78e0c1db5216fc09bb144 %}

This script kills the app before attempting to remove it, so I added another parameter for the app name:

![img-1]

Now, Munki has a record of every package installed , thanks to the `makepkginfo` tool. Jamf Pro does not have that information, so you have to look up the package ID using:

```
pkgutil --pkgs
```

It may not always be obvious what the package ID is (though it normally is). If in doubt, you could look at a Munki recipe...

---

## Careful Now!

![img-2]

As with Munki, `removepackages` is not suitable for all apps. There could be unintended consequences, where files required by another app get removed. So **TEST!**

It's worth looking in an equivalent `.munki` recipe/`pkginfo` file for the following keys - if you see these, you should be good to go (but, still, **TEST!**):

```xml
<key>uninstallable</key>
<true/>
<key>uninstall_method</key>
<string>removepackages</string>
```

If your uninstall policy is more complicated and requires the removal of more than 7 packages, or multiple applications even, then you will either need to duplicate the script so that you have more parameters to play with, or just adapt the script for that particular app and hard-code the package IDs into it.

If all else fails, you can of course fall back on writing a dedicated script to remove that particular application. You may even find such uninstaller scripts already written in existing `.munki` recipes. It's always worth a look.

If any of you try this out, please let me know how you get on! Or, if you think it's a crazy idea with gaping pitfalls, also let me know! I only thought of the idea a few hours ago but it seems to work so far (famous last words!).

[img-1]: https://user-images.githubusercontent.com/5802725/35166706-16cbe350-fd53-11e7-85fe-5acfe4cd309a.png
[img-2]: /assets/images/father-ted-careful-now.gif
[img-3]: /assets/images/munki_add_remove.png
[img-4]: /assets/images/self-service-uninstallers.png


{% include urls.md %}
