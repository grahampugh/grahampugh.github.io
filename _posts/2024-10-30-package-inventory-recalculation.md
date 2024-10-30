---
layout: post
title:  "Jamf package inventory recalculation - GUI, API, JamfUploader"
comments: true
---

If you're a Jamf Pro cloud customer using the Jamf Cloud Distribution Service (JCDS) for packages, you may have noticed that some packages may take time to be fully available after uploading them. This can occur regardless of whether you upload the package via the web interface or using the Jamf Pro API.

<img src="/assets/images/jamf-pkg-availability-pending.png" alt="Package availability pending" width="300"/>

Since the release of Jamf Pro 11.10, it is now possible to force a recalculation of the packages list in the GUI, using the Refresh button that is displayed within any of the packages that are listed as "availability pending". This button actually recalculates all packages, not just the one that's listed as pending, so if you have a bunch of "pending" packages, this should sort them all out, so long as the package is actually present on the JCDS.

## Recalculating the package list via the API

It's also possible to recalculate the packages list via the Jamf Pro API. The new `api/v1/jcds/refresh-inventory` endpoint will instigate a recalculation of the packages in the JCDS, exactly the same as if the button in the GUI is pressed.

## JamfPackageUploader and JamfPackageRecalculator

I have added a new `recalculate` key to the `JamfPackageUploader` processor which will force a package recalculation at the end of the process if set to `True`. For example:

```yaml
- Processor: com.github.grahampugh.jamf-upload.processors/JamfPackageUploader
  Arguments:
    pkg_category: "%PKG_CATEGORY%"
    recalculate: "True"
```

However, depending on your workflow, you may not wish to force a recalculation after each package upload, but rather wait until the end of an AutoPkg run. [Munki] users will be familiar with the concept of recalculating catalogs at the end of a recipe list, which is more efficient than recalculating after every recipe. 

To enable this sort of workflow, I have created a new processor called `JamfPackageRecalculator`, which requires no inputs (other than the credentials you would supply for any JamfUploader processor), and will simply run the package recalculation endpoint.

This should be in its own recipe, and added to the end of a recipe list. So, I've created a recipe, `RecalculatePackages.jamf`, in the repo `autopkg/grahampugh-recipes` (with the same recipe in `grahampugh/jamf-upload` for those of you using this repo). 

Alternatively, if you wish to include this processor in your own recipe, add the following processor (with no arguments):

```yaml
- Processor: com.github.grahampugh.jamf-upload.processors/JamfPackageRecalculator
```

## jamf-upload.sh

Users of the `jamf-upload.sh` script ([wiki here][1]) can also benefit from these additions. You can either add the `--recalculate` option when uploading a package or run a separate command to perform the recalculation.

To recalculate while uploading a package, run a command such as:

```bash
./jamf-upload.sh pkg --prefs /path/to/prefs.plist --pkg /path/to/somepackage.pkg --recalculate 
```

To run a separate command:

```bash
./jamf-upload.sh pkgcalc --prefs /path/to/prefs.plist
```

## Conclusion

In the future we may expect not to need to recalculate the package inventory after uploading packages to JCDS, so the measures I've described here may be temporary. However, hopefully these will help improve the reliability of automated package upload workflows in the short term.

[1]: https://github.com/grahampugh/jamf-upload/wiki/jamf-upload.sh

{% include urls.md %}
