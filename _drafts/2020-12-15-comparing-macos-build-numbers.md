---
layout: post
title: "Comparing build version from a macOS installer application with the build version of your system volume"
comments: true
---

If you need to compare the version of your system macOS with that of a downloaded installer application such as `Install macOS Big Sur.app`, you'll need to know how to obtain this information.

## System version

You can get version information for your system's macOS using the `sw_vers` command:

    % /usr/bin/sw_vers
    ProductName:	macOS
    ProductVersion:	11.1
    BuildVersion:	20C69

Sidenote, for making comparison easier in a script, use e.g. `sw_vers -buildVersion`:

    % /usr/bin/sw_vers -buildVersion
    20C69

The `ProductVersion` is too vague as there are multiple versions using the same string, so that only leaves `BuildVersion`.

## Install macOS application build version

To find an application version, we normally look inside the application's `Info.plist`. A typical application would have a `CFBundleVersion` or `CFBundleShortVersionString` key. Unfortunately, these apps do not use the build version in either of these keys:

    % /usr/libexec/PlistBuddy -c "Print :CFBundleVersion" /Applications/Install\ macOS\ Big\ Sur.app/Contents/Info.plist
    16201

    % /usr/libexec/PlistBuddy -c "Print :CFBundleShortVersionString" /Applications/Install\ macOS\ Big\ Sur.app/Contents/Info.plist
    16.2.01

These values do relate to the version, but are not useful when trying to compare with the output of `sw_vers`. We could use `DTPlatformVersion`:

    % /usr/libexec/PlistBuddy -c "Print :DTPlatformVersion" /Applications/Install\ macOS\ Big\ Sur.app/Contents/Info.plist
    11.1

But as described above, using the version number alone would not account for betas, supplemental updates etc. The Build ID is a better "unique" identifier.

Until recently I was using the `DTSDKBuild` value, but of late, this has been consistently lower than the published Build Version, so clearly represents some other build milestone:

    % /usr/libexec/PlistBuddy -c "Print :DTSDKBuild" /Applications/Install\ macOS\ Big\ Sur.app/Contents/Info.plist
    20C68

## SharedSupport

After doing some digging, I found a file that does contain the same Build version that is reported by `sw_vers`. Unfortunately, it is within the `SharedSupport` disk image inside the installer application, so we need to mount that before extracting the value:

    % hdiutil attach -quiet -noverify "$installer_app/Contents/SharedSupport/SharedSupport.dmg"
    % build_xml="/Volumes/Shared Support/com_apple_MobileAsset_MacSoftwareUpdate/com_apple_MobileAsset_MacSoftwareUpdate.xml"
    % installer_build=$(/usr/libexec/PlistBuddy -c "Print :Assets:0:Build" "$build_xml")
    % diskutil unmount force "/Volumes/Shared Support"
    % echo "$installer_build"
    20C69

## Comparing the versions

Comparing build versions in a shell language is tricky. The version string is composed of concatenated components which need to be compared individually. For example, build version `20C69` contains:

    20 : The Darwin version
    C  : The minor version in alphabet form
    69 : A build version

But what about `20C5061b`, which is the build version of macOS Big Sur 11.1 Beta? If we did a numerical comparison of `69` with `5061`, we would choose the incorrect version. But we can't do a simple text comparison of the two, because, for example `19H4` was an older version than `19H15`.

This is still a work-in-progress for my `erase-install.sh` script, but at present I'm comparing as follows:

1. Numerical comparison of the Darwin version.
2. Alphabetical comparison of the Minor version.
3. Numerical comparison of the first two figures of the build version.
4. Numberical comparison of the next two figures of the build version.
5. Alphabetical comparison of any suffix letter.

I suspect that this will prove not be correct in some future release, and will need tweaking.

## Conclusion

Build version strings are tricky to obtain and hard to compare. I'd be interested in hearing how anyone else is doing this kind of comparison. Also, if anyone knows how to get the `CFBundleShortVersionString` of the installed system, this might be a better way to proceed, as this appears to use proper semantic versioning.

{% include urls.md %}
