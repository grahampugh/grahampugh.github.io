---
layout: post
title:  "JamfUploader and package inventory recalculation"
comments: true
---

If you're a Jamf Pro cloud customer using the Jamf Cloud Distribution Service (JCDS) for packages, you may have noticed that some packages may take time to be fully available after uploading them. This can occur regardless of whether you upload the package via the web interface or using the Jamf Pro API.

<img src="/assets/images/jamfpro-pkgs-availability-pending.png" alt="Siri" width="300"/>

Since the release of Jamf Pro 11.10, it is now possible to force a recalculation of the packages list in the GUI, using the Refresh button that is displayed within any of the packages that are listed as "availability pending". This button actually recalculates all packages, not just the one that's listed as pending, so if you have a bunch of "pending" packages, this should sort them all out, so long as the package is actually present on the JCDS.

## Recalculating the package list via the API

It's also possible to recalculate the packages list via the Jamf Pro API.

{% include urls.md %}
