---
layout: post
title:  "SOFA, and how to use it with Jamf Pro"
comments: true
---

## What is SOFA?

![SOFA logo](https://github.com/macadmins/sofa/raw/main/images/custom_logo.png)

[SOFA], short for "Simple Organized Feed for Apple Software Updates", is a new open source resource for Mac Admins, developed primarily by Henry Stamerjohann of Zentral. It consists of a machine-readable feed and user-friendly web interface, providing always-up-to-date information on XProtect data, OS updates, and the CVEs (critical vulnerabilities) that have been reported as patched by Apple in each release. CVEs that are reported as actively exploited are listed distinctly.

SOFA is hosted by the Mac Admins Open Source organisation, but it can be hosted in an organisation's own infrastructure, allowing a high level of control over the information.

There are many ways this feed will be useful to Mac Admins, so you're going to read many blog posts about it in the future. This post describes how to integrate the macOS and XProtect data exposed in SOFA with Jamf Pro, using extension attribute scripts.

## macOS Version Check

Many existing tools use data from the client to verify if macOS is up to date on a Mac. Typically, obtaining the latest available version either involves interrogating `/Library/Preferences/com.apple.SoftwareUpdate.plist` on the local system for the results of the system's last software update check, or running `softwareupdate --list` to perform a new check. The current system version is then compared with the latest available version reported by either of those methods. I described these methods in the post [Do you need to use the softwareupdate command to discover available updates?][1]. However, if the software update checks on the system are not functional, we won't get an accurate comparison.

The SOFA feed information is polled directly from Apple's servers, so provides a quick way of performing the comparison without relying on software update checks on the system to be working - so long as the system can reach the SOFA web page.

The SOFA feed includes information of which macOS models are compatible with each major version. We can use this information when determining whether a system is running the latest compatible OS.

The Extension Attribute script provided in the SOFA GitHub is named [macOSVersionCheck-EA.sh][3] ([click here][3]). This checks the local system version against the latest compatible version in the SOFA JSON feed, and sends either `Pass` or `Fail` to the Jamf Pro server. This can then be used to scope non-compliant computers into a Smart Group, which can be used to push MDM/DDM software update commands or any other compliance-related action.

In this example, we have named the Extension Attribute `macOS Version Check`. The Smart Group is named `macOS not up to date`. The single criterion is that `macOS Version Check` is `Fail`.

![macOS not up to date smart group](/assets/images/macOS-not-up-to-date-smart-group.png)

Here, we use this smart group in Software Update to initiate MDM update commands.

![Software Update Beta](/assets/images/software-update-beta-scope.png)

## XProtect Version Check

I recently published a post [Is XProtect up to date?][2], which described how to check Apple's feed directly to see if the local system is up to date. This functions well, though it does require a certain amount of `grep` and `cut` hackery to get the correct version.

SOFA provides this information in a more readable JSON format, so we have an opportunity to use the SOFA feed to test whether XProtect and XProtect Remediator are up to date.

The Extension Attribute script provided in the SOFA GitHub is named [XProtectVersionCheck-EA.sh][4] ([click here][4]). This checks the local system version against the latest compatible version in the SOFA JSON feed, and sends either `Pass` or `Fail` to the Jamf Pro server. This can then be used to scope non-compliant computers into a Smart Group, which, as with the macOS check, can be used to push MDM/DDM software update commands or any other compliance-related action.

In this example, we have named the Extension Attribute `XProtect Version Check`. The Smart Group is named `XProtect not up to date`. The single criterion is that `XProtect Version Check` is `Fail`.

![XProtect not up to date smart group](/assets/images/xprotect-not-up-to-date-smart-group.png)

## Conclusion

SOFA is sure to be extremely useful to Mac Admins, and its feed will no doubt be used in many projects in the future. The extension attributes described here are just two examples of how to use the feed to trigger processes in Jamf Pro and any other management tool. I'm looking forward to seeing what else comes out of Henry's innovation.

[1]: https://grahamrpugh.com/2022/09/29/software-update-check.html
[2]: https://grahamrpugh.com/2023/12/06/xprotect-version-check.html
[3]: https://github.com/macadmins/sofa/blob/main/tool-scripts/macOSVersionCheck-EA.sh
[4]: https://github.com/macadmins/sofa/blob/main/tool-scripts/XProtectVersionCheck-EA.sh

{% include urls.md %}
