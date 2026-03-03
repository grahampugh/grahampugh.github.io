---
layout: post
title:  "Create custom profiles using JamfUploader without a template file"
comments: true
---

## Introduction

[JamfUploader] contains AutoPkg processors for performing actions that affect a Jamf Pro server, such as uploading a package, creating a policy, updating a configuration profile, and much more. This post concerns creating custom macOS configuration profiles.

Traditionally, if you're using the [JamfUploader] processor `JamfComputerProfileUploader` to create a custom profile, you first have to make a PLIST file, save that in your recipe repo or overrides folder, and reference that file in the recipe. An example PLIST would be something like this one for the VLC App:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>SUEnableAutomaticChecks</key>
    <false/>
    <key>SUHasLaunchedBefore</key>
    <true/>
    <key>SUSendProfileInfo</key>
    <false/>
</dict>
</plist>
```

## Now you can do away with the PLIST files

I've created a new, simple AutoPkg processor, `CreatePlist`, which will take an input dictionary from the recipe itself, and create a PLIST file in the recipe's cache directory. This can then be used in a subsequent `JamfComputerProfileUploader` process (or any other process that requires a PLIST file as an input). The recipe can be in PLIST or YAML format.

Here's an example recipe:

```yaml
Identifier: com.github.grahampugh.recipes.tests.CreatePlist
MinimumVersion: "2.3"

Input: {}

Process:
  - Processor: com.github.grahampugh.recipes.commonprocessors/CreatePlist
    Arguments:
      output_file_name: VLC
      plist_content:
        SUEnableAutomaticChecks: False
        kSUHasLaunchedBefore2: True
        SUSendProfileInfo: False

  - Processor: com.github.grahampugh.jamf-upload.processors/JamfComputerProfileUploader
    Arguments:
      identifier: org.videolan.vlc
      profile_name: "%output_file_name%"
      payload: "%plist_path%"
      profile_category: Applications
      profile_template: Profile-single-group.xml
      profile_computergroup: All Managed Clients
      replace_profile: "True"
```

Note that the `plist_content` value can contain strings, integers, dictionaries and arrays:

```yaml
      plist_content:
        key1: value1
        key2: True
        key3: 0
        key4:
          dict1: "0.0"
          dict2: "%substituted_value%"
        key5:
         - example
         - example2
```

Incidentally, it is possible to also manufacture a `.mobileconfig` file using this method. However, safe to say that this method is more suited to simple custom profile, the type you might upload to the "Application & Custom Settings" section of a configuration profile in Jamf Pro.

The new processor is available in the `grahampugh-recipes` AutoPkg repo.

## Other recent updates to JamfUploader

JamfUploader is heavily used by my current team, so I've been busy extending its capabilities and keeping it up to date:

- The legacy `dbfileupload` endpoint has now been removed from `JamfPackageUploader`, since we're now 20 point releases in to its removal and the introduction of the `/api/v1/packages` endpoint. The `/api/v1/jcds` endpoint has also been removed from the Jamf Pro API in version 11.25, making `jcds2_mode` non-functional, so I've removed this, too.

- I've updated `JamfPackageRecalculator` and `JamfPackageUploader` to use the new(ish) `/api/v1/cloud-distribution-point/refresh-inventory` endpoint to recalculate packages (replacing the now defunct `/api/v1/jcds/refresh-inventory` endpoint).

- I've also made new processors for handling Static Groups using new Jamf Pro API endpoints - `JamfComputerStaticGroupUploader` and `JamfMobileDeviceStaticGroupUploader`. These are an alternative to using the existing `JamfComputerGroupUploader` and `JamfMobileDeviceGroupUploader` for uploading a Static Group, which require an XML template. It allows you to add a description, too, which is not possible using the older Classic API `computergroups` and `mobiledevicegroups` endpoints. These new processors require no template file.

- Smart Groups can also be uploaded using the new API, giving the ability to add a description to these, too. To do this, you use the `JamfObjectUploader` processor, adding the appropriate `object_type` key for computer- or mobile device smart groups; namely `computer_group` or `mobile_device_group`, respectively. Since the new API is JSON-based, I've provided a new processor to allow you to convert your old XML smart group templates to JSON - `ConvertGroupXMLtoJSON`.

## Conclusion

As ever, if you're using JamfUploader at all, please subscribe to the `#jamf-uploader` channel in the Mac Admins Slack to keep abreast of the changes, and to ask about any problems you're encountering!

{% include urls.md %}
