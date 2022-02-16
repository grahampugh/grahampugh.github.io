---
layout: post
title:  "How do changes to the Jamf Pro API authentication affect JamfUploader and JSSImporter?"
comments: true
---

## TL;DR

It's time to plan your migration away from JSSImporter...

## About the Jamf Pro APIs

The [Jamf Pro] Classic API traditionally uses Basic Authentication - that is, for every request, you supply the username and password of an account that has the permissions required.

The newer API, known as the "Jamf Pro API" (and formerly known as the "UAPI"), has used token-based authentication since its introduction. This works by sending a regular Basic Authentication request to a specific token-generating API endpoint, which returns a "bearer token". Subsequent API requests to other endpoints use this bearer token as authentication. The bearer token expires after a period of time, after which you have to grab another.

Jamf introduced token-based authentication for its Classic API with version 10.35.0, whilst continuing to support the older Basic Authentication method. With version 10.36.0, released this week, Jamf have now introduced the option to disable Basic Authentication for the Classic API endpoints.

This post is designed to answer questions regarding the impact of these changes on the tools I maintain which rely on the Jamf Pro APIs.

## Can I use the JamfUploader processors for AutoPkg with token-based authentication?

Yes! The [JamfUploader] processors for [AutoPkg] support token-based authentication. If you are a JamfUploader user, you don't have to make any changes other than ensuring that the `grahampugh-recipes` repo has been updated. If you are using Jamf Pro 10.36.0, it is safe to disable Basic Authentication.

JamfUploader also continues to work on older versions of Jamf Pro which don't yet support token-based authentication.

## Can I use the JSSImporter processor token-based authentication?

[JSSImporter] **does not support token-based authentication**. If you use JSSImporter, you must ensure that Basic Authentication is **enabled** in your Jamf Pro settings.

To do this, navigate to `Settings` > `Jamf Pro User Accounts & Groups`, and click on the `Password Policy` button. Scroll to the bottom and ensure that the setting `Allows Basic authentication in addition to Bearer Token authentication` is enabled.

## How long can I continue to use JSSImporter?

Jamf have stated that Basic Authentication will be removed as an option "later this year". After this happens, you will need to remain on a version of Jamf Pro that supports Basic Authentication (if you are an on-premises customer), or migrate to another workflow such as using JamfUploader, [PatchBot] or [Munki].

## Will JSSImporter be updated to use token-based authentication?

The answer to this question is probably "no", or at least not by me. My organisation took the decision to end its reliance on JSSImporter, and we are fully migrating our [AutoPkg recipes][1] to JamfUploader.

## What about Spruce, python-jss, jss_helper and JSSRecipeGenerator?

The answer is unfortunately the same "no" for these tools.

Actually, JSSImporter, [Spruce], [jss_helper] and [JSSRecipeGenerator] all depend on the underlying code of [python-jss]. This is awesome but complicated python code that I inherited from [@shea_craig] after they moved on to pastures un-Jamfed. Unfortunately, my initial efforts at fixing this have proved that I don't understand the code well enough to make the necessary changes myself.

Please note that there may be other tools that currently rely on python-jss. I know that [gkluoe/git2jss] is one.

Other tools have since been developed that replace and improve on the functionality of all these tools. Please check them out:

* [Prune] - a GUI-based tool for cleaning up your Jamf, a capable successor to Spruce.
* [jctl] - A python-based tool based on an underlying framework called python-janf for interactiing with the Jamf Pro APIs, which should do most if not all of what python-jss and jss_helper could do.
* [ruby-jss] - A ruby-based framework that can also do pretty much all of what python-jss could do.

## Can I fix it?

Yes you can! If you are able and motivated to dedicate resources and python expertise to make the necessary changes to the code in order for JSSImporter (specifically, the underlying tool, python-jss) to function with token-based authentication, please get in touch - I'd be happy to hand over the JSSImporter GitHub organisation to a new maintainer.

[1]: https://github.com/eth-its/autopkg-mac-recipes-yaml

{% include urls.md %}
