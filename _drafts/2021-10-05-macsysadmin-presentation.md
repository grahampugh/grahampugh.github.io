---
layout: post
title: "MacSysAdmin Presentation - 07 October 2021 - AutoPkg Everything"
comments: true
---

On 07 October 2021, I am proud to be presenting at the [MacSysAdmin Online Conerernce 2021](https://www.macsysadmin.se/program/program.html), on **AutoPkg Everything - How ETH Zürich extends the AutoPkg framework beyond uploading packages**.

This post contains links to everything that was presented that is publicly available.

## Video and Slides

I will link to the video and slides once they are published.

## Jamf Policy Design

- [How many Jamf Pro Policies does each application need?](https://grahamrpugh.com/2017/11/02/how-many-policies.html) - blog post by Graham.

## Processors

### JamfUploader

- [JamfUploader - new AutoPkg processors for importing packages to Jamf Pro](https://grahamrpugh.com/2020/12/14/introducing-jamf-upload.html) - blog post by Graham.
- [Integrating AutoPkg and Jamf Pro](https://maclabs.jazzace.ca/2020/12/29/integrating-autopkg-jamfpro.html) - blog post by Anthony Reimer.
- [Making package uploading and deployment easier with JamfUploader](https://grahamrpugh.com/2021/08/18/jnuc-presentation-jamfuploader.html) - JNUC 2021 presentation by Anthony Reimer and Graham Pugh.
- [JamfUploader][jamfuploader] - a suite of shared AutoPkg processors for uploading packages and API objects to Jamf Pro. - note: includes `JamfPolicyDeleter` and `JamfUploadSlacker`.

### VersionRegexGenerator

- [Better Jamf Policy Version Control with AutoPkg and Regex - VersionRegexGenerator](https://grahamrpugh.com/2020/09/17/better-jamf-policy-version-control-autopkg.html) - blog post by Graham.
- [VersionRegexGenerator](https://github.com/autopkg/grahampugh-recipes/tree/main/CommonProcessors#VersionRegexGenerator)

### JSSImporter

- [JSSImporter][jssimporter] - a side-loaded custom AutoPkg processor for uploading packages and API objects to Jamf Pro.
- [Jamf and AutoPkg](https://grahamrpugh.com/2019/11/14/jamf-and-autopkg-jnuc2019-session.html) - JNUC 2019 presentation by Graham.
- [JSSImporter 1.0.2b3 puts the brakes on](https://grahamrpugh.com/2019/06/13/jssimporter-update.html)

### Others

- [JSSRecipeReceiptChecker](https://github.com/autopkg/grahampugh-recipes/tree/main/CommonProcessors#JSSRecipeReceiptChecker)
- [LastRecipeRunResult](https://github.com/autopkg/grahampugh-recipes/tree/main/PostProcessors#lastreciperunresult)
- [LastRecipeRunChecker](https://github.com/autopkg/grahampugh-recipes/tree/main/PreProcessors#lastreciperunchecker)
- [JamfUploadSharepointUpdater](https://github.com/eth-its/autopkg-mac-recipes-yaml/tree/main/Shared_Processors#jamfuploadsharepointupdater)
- [JamfUploadSharepointStageCheck](https://github.com/eth-its/autopkg-mac-recipes-yaml/tree/main/Shared_Processors#jamfuploadsharepointstagecheck)
- [LocalRepoUpdateChecker](https://github.com/eth-its/autopkg-mac-recipes-yaml/tree/main/Shared_Processors#localrepoupdatechecker)
- [InternalUpdateChecker](https://github.com/eth-its/autopkg-mac-recipes-yaml/blob/main/Shared_Processors/InternalUpdateChecker.py)
- [SMBMounter](https://github.com/autopkg/grahampugh-recipes/tree/main/CommonProcessors#smbmounter)
- [SMBUnmounter](https://github.com/autopkg/grahampugh-recipes/tree/main/CommonProcessors#smbunmounter)

## Example recipes

- [eth-its/autopkg_mac_recipes_yaml](https://github.com/eth-its/autopkg-mac-recipes-yaml) - Contains all ETH's [Testing](https://github.com/eth-its/autopkg-mac-recipes-yaml/tree/main/Jamf_Recipes) (`.jamf`), [Nodes](https://github.com/eth-its/autopkg-mac-recipes-yaml/tree/main/Jamf_Nodes_Recipes) (`-nodes.jamf`), [Production](https://github.com/eth-its/autopkg-mac-recipes-yaml/tree/main/Jamf_Prod_Recipes) (`-prod.jamf`) and [Uninstaller](https://github.com/eth-its/autopkg-mac-recipes-yaml/tree/main/Jamf_Uninstall_Recipes) (`-uninstall.jamf`) recipes.
- [autopkg/grahampugh-recipes - Jamf_Recipes](https://github.com/grahampugh/recipes-yaml/tree/main/Jamf_Recipes) - some `.jamf` recipe examples that are closer to the older JSS recipe standard.

## Scheduling AutoPkg

- [A beginner's guide to using AutoPkg with GitLab Runner](https://grahamrpugh.com/2020/07/10/gitlab-runner-and-autopkg.html) - blog post by Graham.
- [GitLab Runner](https://docs.gitlab.com/runner/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [AutoPkgr][autopkgr] - A native macOS app which can be used to interact with AutoPkg, including a scheduler.
- [AutoPkg-Conductor][autopkg-conductor] - a script for managing autopkg runs by [@rtrouton].

## AutoPkg for Windows

These links refer to my colleague Nick Heim's work in forking AutoPkg for Windows.

- [AutoPkg for Windows](https://github.com/NickETH/autopkg)
- [Windows recipes](https://github.com/NickETH/recipes-win)
- [Processors for Windows](https://github.com/NickETH/recipes-win/tree/master/SharedProcessors#nicks-shared-processors-for-autopkgwin)

## Other useful resources

- [AutoPkg][autopkg] - a framework for deploying packages.
- [AutoPkg 2020](https://managingosx.wordpress.com/2019/10/02/autopkg-2020-macsysadmin-2019-links/) - MacSysAdmin presentation by Greg Neagle
- [Writing AutoPkg Recipes](https://maclabs.jazzace.ca/2020/11/26/autopkg-workshop.html) - EveryWorld workshop by Anthony Reimer
- [jss_helper] - an API tool for promoting packages uploaded via JSSImporter from testing to production. Requires AutoPkg, JSSImporter and python-jss to be installed. Note that I mis-spoke in the presentation and called this "Jamf Helper".

{% include urls.md %}
