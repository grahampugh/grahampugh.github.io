---
layout: post
title: "JNUC Presentation - 21 October 2021 - Making package uploading and deployment easier with JamfUploader"
comments: true
---

On 21 October 2021, I proudly co-presented with [Anthony Reimer][1] at the [Virtual Jamf Nation User Conference 2021][2], on the topic **Making package uploading and deployment easier with JamfUploader**.

![JNUC2021-image-of-first-slide](/assets/images/JNUC2021-JamfUploader-frontcover.png)

This blog post is intended to provide links to everything presented in the slides.

A PDF of the slides and presenter notes is available [here](/assets/documents/JNUC2021-JamfUploader-presentation.pdf).

The video is available to watch until the end of November for registered attendees, and I will update this post when the video is posted onto YouTube after that period.

## New to AutoPkg?

If you are brand new to AutoPkg, please check out these resources to get you started:

- [AutoPkg 2020 - MacSysAdmin presentation Greg Neagle](https://managingosx.wordpress.com/2019/10/02/autopkg-2020-macsysadmin-2019-links/)
- [Writing AutoPkg Recipes - EveryWorld workshop by Anthony](https://maclabs.jazzace.ca/2020/11/26/autopkg-workshop.html)
- [Jamf and AutoPkg - JNUC presentation by Graham](https://grahamrpugh.com/2019/11/14/jamf-and-autopkg-jnuc2019-session.html)

## Sections of the presentation

### JamfUploader - A Brief History

- [Introducing JamfUploader - blog post by Graham](https://grahamrpugh.com/2020/12/14/introducing-jamf-upload.html)
- [Integrating AutoPkg and Jamf Pro - blog post by Anthony](https://maclabs.jazzace.ca/2020/12/29/integrating-autopkg-jamfpro.html)
- [JamfUploader processors - GitHub](https://github.com/grahampugh/recipes-yaml/tree/main/JamfUploaderProcessors)
- [JSSImporter]

### Starting Simple: JamfCategoryUploader & JamfPackageUploader

- Example `-pkg-upload` recipes (Slide 15).  
  Note that the link from the presentation has changed as I have updated the default GitHub branch to `main`. [github.com/autopkg/grahampugh-recipes/tree/main/Jamf_Package_Only_Recipes](https://github.com/autopkg/grahampugh-recipes/tree/main/Jamf_Package_Only_Recipes).  
  I have also converted my recipes to `yaml` format since making this presentation. To allow you to refer to the Plist recipe as shown in the presentation, I have added a subfolder called [Plist_Versions](https://github.com/autopkg/grahampugh-recipes/tree/main/Jamf_Package_Only_Recipes/Plist_Versions) which shows the original Plist examples.
- Anthony's example recipes using `FirefoxSignedPkg.pkg` as a parent recipe are available in his [jazzace/JNUC2021 GitHub repo](https://github.com/jazzace/JNUC2021).
- The examples shown in the presentation are:
  - [FirefoxSignedPkg-pkg-upload.jamf.recipe](https://github.com/jazzace/JNUC2021/blob/main/FirefoxSignedPkg-pkg-upload.jamf.recipe) (Slides 22, 23)
  - [FirefoxSignedPkg-pkg-upload.jamf.recipe.yaml](https://github.com/jazzace/JNUC2021/blob/main/FirefoxSignedPkg-pkg-upload.jamf.recipe.yaml) (Slide 24)
  - [FirefoxSignedPkg-pkg-uploadonly.jamf.recipe.yaml](https://github.com/jazzace/JNUC2021/blob/main/FirefoxSignedPkg-pkg-uploadonly.jamf.recipe.yaml) (Slides 27)

### Adding a Policy using JamfPolicyUploader

- The examples shown in the presentation are:
  - [All-Computers-Policy-Template.xml](https://github.com/jazzace/JNUC2021/blob/main/All-Computers-Policy-Template.xml) (Slide 34)
  - [FirefoxSignedPkg.jamf.recipe](https://github.com/jazzace/JNUC2021/blob/main/FirefoxSignedPkg.jamf.recipe) (Slides 22, 23)

### Putting multiple processors into a single recipe

- Example `.jamf` recipes are available in my [autopkg/grahampugh-recipes](https://github.com/autopkg/grahampugh-recipes/tree/main/Jamf_Recipes) repo.
- Example Policy and Smart Group Templates are also available in the same repo; [here](https://github.com/autopkg/grahampugh-recipes/tree/main/Jamf_Templates).
- The examples shown in the presentation are:
  - [Firefox.jamf.recipe.yaml](https://github.com/autopkg/grahampugh-recipes/blob/main/Jamf_Recipes/Firefox.jamf.recipe.yaml) (Slide 40)
  - [Policy-install-latest.xml](https://github.com/autopkg/grahampugh-recipes/blob/main/Jamf_Templates/Policy-install-latest.xml) (Slide 41)
  - [SmartGroup-update-smart.xml](https://github.com/autopkg/grahampugh-recipes/blob/main/Jamf_Templates/SmartGroup-update-smart.xml) (Slide 42)
  - [MicrosoftOffice365.jamf.recipe.yaml](https://github.com/autopkg/grahampugh-recipes/blob/main/Jamf_Recipes/MicrosoftOffice365.jamf.recipe.yaml) (Slide 44).
  - [Policy-install-latest-script.xml](https://github.com/autopkg/grahampugh-recipes/blob/main/Jamf_Templates/Policy-install-latest-script.xml) (Slide 45)
  - [MicrosoftEdge.jamf.recipe.yaml](https://github.com/autopkg/grahampugh-recipes/blob/main/Jamf_Recipes/MicrosoftEdge.jamf.recipe.yaml) (Slide 47)
  - [ExtensionAttribute-CFBundleShortVersionString.sh](https://github.com/autopkg/grahampugh-recipes/blob/main/Jamf_Scripts/ExtensionAttribute-CFBundleShortVersionString.sh) (Slide 48)
  - [Firefox.jamf.recipe.yaml](https://github.com/autopkg/grahampugh-recipes/blob/main/Jamf_Recipes/Firefox.jamf.recipe.yaml) (Slide 52)

### VersionRegexGenerator processor

This processor allows for better version comparison of packages in Jamf Pro. For more information about this processor, see:

- [Better Jamf Policy Version Control with AutoPkg and Regex - blog post by Graham](https://grahamrpugh.com/2020/09/17/better-jamf-policy-version-control-autopkg.html)
- [VersionRegexGenerator.py](https://github.com/grahampugh/recipes-yaml/blob/main/CommonProcessors/VersionRegexGenerator.py)

- The examples shown in the presentation are:
  - [MicrosoftEdge.jamf.recipe.yaml](https://github.com/autopkg/grahampugh-recipes/blob/main/Jamf_Recipes/MicrosoftEdge.jamf.recipe-regex.yaml) (Slide 55).
  - [SmartGroup-update-smart.xml](https://github.com/autopkg/grahampugh-recipes/blob/main/Jamf_Templates/SmartGroup-update-smart-regex.xml) (Slide 42)

## More Resources

- Please come and discuss **JamfUploader** processors and recipes in the `#jamf-upload` channel of the [MacAdmins Slack Workspace][macadmins slack team].

### Example recipes

- [eth-its autopkg mac recipes](https://github.com/eth-its/autopkg-mac-recipes-yaml) (all recipes including templates)
- [eth-its Jamf_Recipes](https://github.com/eth-its/autopkg-mac-recipes-yaml/tree/main/Jamf_Recipes) (just the jamf recipes)
- [grahampugh Jamf_Recipes](https://github.com/grahampugh/recipes-yaml/tree/main/Jamf_Recipes) (recipe examples that are closer to the JSS recipe standard)

[1]: https://maclabs.jazzace.ca
[2]: https://www.jamf.com/events/jamf-nation-user-conference/2021/

{% include urls.md %}
