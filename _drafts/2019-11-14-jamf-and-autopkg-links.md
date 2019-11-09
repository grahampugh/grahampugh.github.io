---
layout: post
title:  "Jamf and AutoPkg: JNUC 2019 Session Links and commands"
comments: true
---

On 14 November 2019, at 13:30, I presented at the [Jamf Nation User Conference in Minneapolis, MN, USA](https://www.jamf.com/events/jamf-nation-user-conference/2019/), on the following topic:

**Jamf Pro and AutoPkg: How JSSImporter automates package management and policy creation in Jamf Pro**

These posts detail the contents of the session, including sections originally planned that were cut due to time constraints.

---

# Contents

1. AutoPkg + JSSImporter - setup and use
2. Understand and use standard JSS recipes
3. Roll your own JSS recipes
4. The future of JSSImporter

---

# Part 1: AutoPkg + JSSImporter - setup and use

## What is AutoPkg?

* [AutoPkg Wiki]
* [AutoPkg 2020](http://docs.macsysadmin.se/2019/video/Day3Session4.mp4) by Greg Neagle, MacSysAdmin Conference, Göteburg, Sweden, 2019.

## Installing and configuring AutoPkg and JSSImporter

### Manual installation

* Install Xcode command line tools: `xcode-select --install`
* [AutoPkg Latest Release](https://github.com/autopkg/autopkg/releases/latest)
* [JSSImporter Latest Release](https://github.com/jssimporter/JSSImporter/releases/latest)
* [JSSImporter Wiki - Configuring Repositories](https://github.com/jssimporter/JSSImporter/wiki/Configuring+Repositories)

### Alternative methods of installation and setup

* [AutoPkg\_Setup\_for\_JSS][AutoPkgSetupforJSS]
* [AutoPkgr]

## AutoPkg from the command line

Searching for a recipe (searches repos in [github.com/autopkg](https://github.com/autopkg)):

    autopkg search iTerm2

Adding a repo (`git clone` a recipe):

    autopkg repo-add jss-recipes

Getting info about a recipe:

    autopkg info iTerm2.jss

Setting AutoPkg to fail if recipe are not trusted:

    defaults write com.github.autopkg FAIL_RECIPES_WITHOUT_TRUST_INFO -bool true


Making a recipe override file (saved to `~/Library/AutoPkg/RecipeOverrides` by default):

    autopkg make-override iTerm2.jss


Making a recipe override file (saved to `~/Library/AutoPkg/RecipeOverrides` by default):

    autopkg make-override iTerm2.jss

Running a recipe:

    autopkg run iTerm2.jss

Running a recipe with more verbosity:

    autopkg run -v iTerm2.jss

Running a JSS recipe with maximum verbosity:

    autopkg run -vvvv iTerm2.jss
    
Running multiple recipes in one command:

    autopkg run iTerm2.jss Google\ Chrome.jss "Microsoft Office.jss"

Running recipes from a list in a text file:

    autopkg run --recipe-list JSS_Recipes.txt

Updating all repositories (`git pull` all repos):

    autopkg repo-update all

Verifying the trust information of a recipe with verbose output (`git diff`):

    autopkg verify-trust-info -vv iTerm2.jss

Updating the trust information of a recipe:

    autopkg update-trust-info iTerm2.jss

## Getting notifications from AutoPkg runs

* [AutoPkgr]
* [autopkg-conductor] from [Rich Trouton][@rtrouton]

---

# Part 2: How to understand and use Standard JSS recipes

Standard JSS recipe policy format:

* Category `Testing`.
* Self Service
* Ongoing frequency
* Policy name: `Install Latest %NAME%`
* Package name `%NAME%-%version%.pkg`
* Update Inventory set
* Smart Group name: `NAME-update-smart`

The Standard Smart Group template creates groups as follows:

| and-or | ( / ) | Operation           | operand | value                | ( / ) |
|--------|-------|---------------------|---------|----------------------|-------|
|        |       | Application Title   | is      | %JSS_INVENTORY_NAME% |       |
| and    |       | Application Version | is not  | %version%            |       |
| and    |       | Computer Group      | is      | Testing              |       |

Templates:

* [Standard policy template](https://github.com/jssimporter/JSSImporter/blob/master/example_templates/PolicyTemplate.xml)
* [Standard smart group template](https://github.com/jssimporter/JSSImporter/blob/master/example_templates/SmartGroupTemplate.xml)
* [Example script template](https://github.com/jssimporter/JSSImporter/blob/master/example_templates/ScriptTemplate.xml)
* [Extension Attribute template - CFBundleVersion](https://github.com/jssimporter/JSSImporter/blob/master/example_templates/ExtensionAttribute-CFBundleVersion.xml)

Recipe Override example: [Atom.jss.recipe](https://gist.github.com/grahampugh/3c956e2587c3daa45e3a84e60520ae0f)

## Promoting recipes

* [jss_helper]
* [Auto-Update](https://github.com/t-lark/Auto-Update) by Tom Larkin (@tlark on [MacAdmins Slack Team])
* [Auto-Update Magic](https://github.com/homebysix/auto-update-magic) by Elliot Jordan (@homebysix on [MacAdmins Slack Team])

---

# Part 3: Roll your own JSS recipes

## Standard recipes

[JSSRecipeCreator] - example command to make `VLC.jss.recipe`:

    $ JSSRecipeCreator.py --auto ~/Library/AutoPkg/RecipeRepos/com.github.autopkg.recipes/VLC/VLC.pkg.recipe


## Package-only recipes

[JSSRecipeCreator] - example command to make `VLC.jss-upload.recipe`:


    $ JSSRecipeCreator.py --package_only --auto ~/Library/AutoPkg/RecipeRepos/com.github.autopkg.recipes/VLC/VLC.pkg.recipe
  
* [Using Autopkg for package Uploads to Jamf Cloud only](https://dazwallace.wordpress.com/2019/03/12/using-autopkg-for-package-uploads-to-jamf-cloud-only/) by Daz Wallace (@dazwallace on [MacAdmins Slack Team])
* [How to Upload Packages to Jamf Cloud using Autopkgr](https://hcsonline.com/support/white-papers/how-to-upload-packages-to-jamf-cloud-using-autopkgr) by Keith Mitnick (@kmitnick on [MacAdmins Slack Team])
* [JSS_Package_Only_Recipes](https://github.com/autopkg/grahampugh-recipes/tree/master/_JSS_Package_Only_Recipes) in `grahampugh-recipes`
## Script-only recipes

* [JSS_Script_Recipes](https://github.com/autopkg/grahampugh-recipes/tree/master/_JSS_Script_Recipes) in `grahampugh-recipes`

## Production recipes

* [JSS_Production_Recipes](https://github.com/autopkg/grahampugh-recipes/tree/master/_JSS_Production_Recipes) in `grahampugh-recipes`
* [Example autoupdate recipe](https://github.com/homebysix/auto-update-magic/tree/master/Exercise5b) from [Auto-Update Magic](https://github.com/homebysix/auto-update-magic)

---

# Part 4: The future of JSSImporter

* [AutoPkg 2.0 Beta 1](https://github.com/autopkg/autopkg/releases/tag/v2.0b1) for python 3 (does not currently work with JSSImporter)

## New options

* [STOP_IF_NO_JSS_UPLOAD](https://grahamrpugh.com/2019/06/13/jssimporter-update.html)
* [skip_scope](https://github.com/jssimporter/JSSImporter/pull/157)
* [skip_scripts](https://github.com/jssimporter/JSSImporter/pull/159)

## Feature Requests to upvote (please!)

* [Facilitate uploads to cloud distribution point via API or other non-manual method](https://www.jamf.com/jamf-nation/feature-requests/6665/facilitate-uploads-to-cloud-distribution-point-via-api-or-other-non-manual-method)
* [API connection persistence (classic API)](https://www.jamf.com/jamf-nation/feature-requests/8698/api-connection-persistence-classic-api)
* [Every aspect of the Jamf web GUI should be accessible via the API](https://www.jamf.com/jamf-nation/feature-requests/6583/every-aspect-of-the-jamf-web-gui-should-be-accessible-via-the-api)



{% include urls.md %}
