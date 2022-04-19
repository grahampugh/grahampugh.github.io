---
layout: post
title: "JamfPackageUploader 'JCDS-mode' for a new way to upload packages to Jamf Cloud"
comments: true
---

Tools like [JSSImporter] and [JamfUploader] traditionally use an undocumented API endpoint for uploading packages to Cloud Distribution Points. Various people figured this `dbfileupload` endpoint out by reverse-engineering the package upload done by the Jamf Admin (formerly Casper Admin) application. 

For those interested, a `curl` request to this endpoint looks like this:

```bash
curl --request POST \
    --header "authorization: Basic MY-ENCRYPTED-CREDENTIALS" \
    --header 'Accept: application/xml' \
    --header 'DESTINATION: 0' \
    --header "OBJECT_ID: -1" \
    --header 'FILE_TYPE: 0' \
    --header "FILE_NAME: Some Package Name" \
    --upload-file "/path/to/some/package.pkg" \
    "https://my.jamf.instance/dbfileupload"
```

To replace an existing package, one can set the OBJECT_ID to an existing package.

This endpoint, although not supported by Jamf, works well for people using an external cloud provider for their fileshare distribution point. However, for those with a Jamf Cloud Distribution Point, it has been proving less reliable, especially recently.

## Detecting whether the package uploaded or not

The http response of a `curl` request to the `dbfileupload` endpoint is often ambiguous, so there's no good way of programmatically determining that the package upload was successful. The only way to find this out is to check the package in the Jamf Pro web console. It's not uncommon to see an "availability pending" message, which may eventually turn onto an "upload failed" message.

![availability-pending](/assets/images/jamf-pkg-availability-pending.png)

## An alternative method

A conversation between `@mosen`, `@rodgerramjet` and myself (`@grahamrpugh`) in the [MacAdmins Slack][1] led to `@rodgerramjet` figuring out the Jamf Pro admin console GUI package upload mechanism by reading the network requests being made while uploading a package in the GUI. This method is a four-stage process, which, using `curl`, looks like this:

{% gist 55b7657dbe3dbd15ac38888bf6e72bb8 %} 

## JamfPackageUploader JCDS-mode

I have now added a `jcds_mode` option to `JamfPackageUploader` processor, so that those of you who use Jamf Cloud can upload packages using this alternative method. 

`jcds_mode` is experimental, and comes with limitations:

1. It is only suitable for standard Jamf Cloud setups. It won't work if you use a different cloud service such as Amazon S3 for your cloud distribution service, or if you have multiple distribution points.
2. You cannot replace an existing package with `jcds_mode`. You first have to delete the package in the GUI, and wait a minute or so.

To set JCDS-mode for all recipes, add the key to your AutoPkg prefs:

```sh
defaults write "$HOME/Library/Preferences/com.github.autopkg.plist" jcds_mode -bool True
```

Or, to upload a specific package using AutoPkg with JamfPackageUploader and JCDS-mode, add it as an argument, for example:

```sh
autopkg run -v Firefox.pkg --post com.github.grahampugh.jamf-upload.processors/JamfPackageUploader --key jcds_mode=True
```

And the key can be added directly to the processor in a `.jamf` recipe, for example:

```yaml
  - Processor: com.github.grahampugh.jamf-upload.processors/JamfPackageUploader
    Arguments:
      category_name: "Applications"
      jcds_mode: True
```

## Conclusion

As with the existing `dbfileupload` endpoint, using this `/api/file` endpoint programmatically is **unsupported by Jamf**, and **subject to change/breakage at any time**. I have offered it as a (hopefully) temporary alternative for those of you struggling with failed package uploads to Jamf Pro using AutoPkg, but if your workflow depends on it, **please** reach out to Jamf to express your need for an officially supported and documented API endpoint for package upload.

[1]: https://macadmins.slack.com/archives/C01AVR04ES1/p1645137480263299

{% include urls.md %}
