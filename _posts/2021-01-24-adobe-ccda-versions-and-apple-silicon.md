---
layout: post
title: "When a single Adobe package can have two versions depending on architecture"
comments: true
---

To get Adobe Creative Cloud Desktop application to work on an Apple Silicon device, Adobe have provided a patch for their latest installers.

The current version of Adobe Creative Cloud that is downloadable from [Adobe's admin console](https://adminconsole.adobe.com) (if you have access) at the time of writing is `5.3.2.471`.

The instructions at Adobe's page ["Deploy packages to Apple Silicon devices"][1] give instructions on how to patch the downloadad and unzipped meta-package. This bascially involves removing an `InstallationCheck` file and adding a folder of stuff downloadable from the link named `ASU_5.3.5`. Then you can deploy the package by your usual means.

When you install this package on a Mac running Big Sur with Intel processor, sure enough, you get version `5.3.2.471`.

![Creative Cloud Desktop App on Intel](/assets/images/adobe-ccda-intel.png)

However, if you install the _very same package_ on a Mac with Apple Silicon processor, you get version `5.3.5.518`.

![Creative Cloud Desktop App on Apple Silicon](/assets/images/adobe-ccda-m1.png)

## Scoping the Adobe Creative Cloud package in Jamf Pro

If, like me, you create ongoing policies in Jamf to install or offer in Self Service a given version of a desired app if it isn't already installed, you will have to take the multiple versions into account. You could create a complicated set of criteria where Architecture is `x86` and Application Version is `5.3.2.471`, **OR** Architecture is `arm64` and Application Version is `5.3.5.518`. Or you could create two different policies.

Or, if you make use of William Smith's ["Match Version Number or Higher.bash"][2] script, or my `VersionRegexGenerator` AutoPkg processor (see my [previous post][3], you can use the generated regex for `5.3.2.471` (quoted below) as an Application Version "matches regex" value:

    ^(\d{2,}.*|[6-9].*|5\.\d{2,}.*|5\.[4-9].*|5\.3\.\d{2,}.*|5\.3\.[3-9].*|5\.3\.2\.\d{4,}.*|5\.3\.2\.[5-9]\d{2,}.*|5\.3\.2\.4[8-9]\d{1,}.*|5\.3\.2\.47[2-9].*|5\.3\.2\.471.*)$

Since the version that gets installed on the Apple Silicon Mac is greater than `5.3.2.471`, the policy will still be excluded.

## Conclusion

The above instructions may be required for deploying any Adobe CC package which is already compatible with Apple Silicon, but I have not tried that yet. Let me know if you try it!

The CC apps that are currently compatible with Apple Silicon Mac are shown on Adobe's page ["Do Adobe apps work on Apple computers that use the M1 chip?"][4].

[1]: https://helpx.adobe.com/enterprise/kb/deploy-packages-to-arm-devices.html
[2]: https://gist.github.com/talkingmoose/2cf20236e665fcd7ec41311d50c89c0e
[3]: https://grahamrpugh.com/2020/09/17/better-jamf-policy-version-control-autopkg.html
[4]: https://helpx.adobe.com/download-install/kb/apple-silicon-m1-chip.html

{% include urls.md %}
