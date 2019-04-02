---
layout: post
title:  "Jamf Pro and AutoPkg"
comments: true
---

[AutoPkg] was initially designed to automate the downloading of applications and their import into [Munki].

Munki can natively import the commonly used method of distributing software, that is to say an app bundle inside a disk image. In many cases this means that just two processes are required: the `URLDownloader` processor (normally inside a parent `.download` recipe) to download the disk image, and the `MunkiImporter` processor (normally in a child `.munki` recipe) to create the required metadata and import the `dmg` into Munki.

Interestingly, this is also the case with many `.install` recipes, which are designed to install an application on the same device as AutoPkg is installed, since the `InstallFromDMG` processor can automate the copying of the app from the DMG to your `Applications` folder.

Unfortunately, there is no automated method of importing `dmg`-based applications into Jamf Pro. To use AutoPkg with Jamf Pro, you need to build `.jss` recipes which utilise the [JSSImporter] processor. `JSSImporter` can only handle installer packages (pkgs). This often means that an additional `.pkg` recipe is required to wrap the app up in a package, such as with the `AppPkgCreator` processor for basic drag-and-drop applications.

# What is an AutoPkg recipe?

An AutoPkg recipe is a PLIST file containing a list (strictly, an array) of processors, which are python scripts. Many processors are provided by the Mac Admins community, and will cover most eventualities.

The list runs sequentially, so the order of processes is essential.

This list of processes can span multiple recipes. The files are referred to in a hierarchy, using the concept of "parents". When running AutoPkg, you provide the "child" recipe in the command line. The child recipe lists the parent recipe inside. That parent recipe may also have its own parent recipe, and so on. All the links are followed by AutoPkg to provide the complete sequential list of processors that it needs to run.

## Recipe Overrides

The main benefit of AutoPkg is that it is a common and extensible framework, with recipes easy to share in the Mac Admins community, so that individual engineers are not having to write their own scripts to do the same process. A caveat to this is that trusting other people's scripts leaves you vulnerable: you need to inspect the recipes to make sure you understand what they do. To help with this, AutoPkg has the concept of "recipe overrides", which are generated locally and contain trust information, allowing AutoPkg to check whether a recipe has changed since it was last downloaded.

## Arguments

The recipe provides a set of input parameters for each processor, called "arguments". Many processors set common defaults so that arguments only have to be specified if they are different to the default.

A good example of this would be the path to which a drag-and-drop application is to be copied - since it is nearly always `/Applications`, there is no need to provide this parameter in a recipe in most circumstances.

Arguments can be set a fixed value, or they could contain a reference to an "Input" value. Input values are values that can be provided in the same recipe, in child recipes, in Recipe Override files, or directly from the command line when running AutoPkg.

The precedence of an Input value is the reverse of that order: an Input value in the command line takes precedence over that in a Recipe Override, which in turn takes precedence over a child recipe, which in turn takes precedence over the value in a parent recipe.

This order of precedence means that parent recipes can be referenced by different child recipes. For example, the processes for importing an application into Munki is very different to the process of importing into Jamf Pro, but both need to download the same installer DMG from the internet, so both can refer to the same `.download` recipe as a parent recipe.

As another example, a `.download` recipe might work for multiple versions of an application, where just changing one input parameter in a child recipe such as the download URL can result in the download of a different app, without needing a separate recipe, since the process is otherwise the same.

## download recipe

A `.download` recipe is usually the parent recipe for subsequent steps.

## pkg recipe

## jss recipe


{% include urls.md %}
