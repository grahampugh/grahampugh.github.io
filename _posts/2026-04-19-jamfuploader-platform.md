---
layout: post
title:  "JamfUploader now supports Jamf Platform Integrations, integrates with jamf-cli"
comments: true
---

## Introduction

As of Monday, 13 April 2026, Jamf have now opened the Public Beta of the [Plaform API Gateway][1] ([1]). This provides a new method of interacting with Jamf Pro Cloud instances, Jamf Protect, Jamf School, and Platform Services such as blueprints, compliance benchmarks, declaration services and more.

Credentials for the Platform API Gateway are generated using OAuth 2.0 via [Jamf Account][2] ([2]). You supply the hosting region and tenant name, and a Tenant ID, Client ID and Client Secret are generated, which you need to save somewhere safe before leaving the page. The result is known as an "integration".

And now, JamfUploader supports using Platform API Gateway credentials for AutoPkg recipes. Additionally, JamfUploader can now integrate with [jamf-cli], allowing you to provide a `jamf-cli` profile to obtain authentication credentials rather than save credentials separately for use in either tool.

## How to provide Platform API Gateway credentials in JamfUploader

If using Platform API credentials, you supply the region, tenant ID, client ID and client secret.

- `PLATFORM_API_REGION`
- `PLATFORM_API_TENANT_ID`
- `CLIENT_ID`
- `CLIENT_SECRET`

These keys can be added to your AutoPkg prefs file, supplied at the command line, or stored in the keychain using the provided script `set-platform-credentials.sh`. This is an interactive script, you can just run it without any parameters and follow the instructions to create the keychain objects.

For processors that output to a file (for example `JamfObjectReader`), you also still need to provide the `JSS_URL` so that instance-specific output files can be named in a readable format. This isn't required for processors that are only uploading objects.

For full details on the various ways you can provide credentials for AutoPkg recipes that require them, see the wiki page [JamfUploader: Credentials][3] ([3]).

## Use JamfUploader in conjunction with jamf-cli

If you're starting to use `jamf-cli`, you will have already created at least one "profile" - the name given to a saved set of credentials for a Jamf integration. It's now possible to use the details from this profile in JamfUploader to authenticate with Jamf Pro. Just supply the profile rather than the URL. If the profile contains Oauth2 credentials, you needn't supply the URL at all, but if you are using the Platform method of authentication, for `JamfObjectReader` you will need to separately provide the `JSS_URL` for those instance-specific output files.

- `JAMF_CLI_PROFILE`

The value of this key can be added to your AutoPkg preferences, or supplied at the command line. JamfUploader will store the generated token for each profile for re-use, and properly check the expiry time and generate a new token using `jamf-cli` if it has expired.

## JamfUploader and platform services

Although you can now use Platform API Gateway integrations to authenticate to Jamf Pro, I've decided not to add support for actual Platform API endpoints such as blueprints, compliance benchmarks, and declaration services. Support for these endpoints is already baked into `jamf-cli`, and my own [JamfCLIRunner] processor integrates fully with `jamf-cli`, so I don't consider it necessary to replicate this functionality in JamfUploader. Since you can now use the same source of stored credentials for both JamfUploader and JamfCLIRunner, it's easy to create recipes that use both JamfUploader and JamfCLIRunner interchangeably.

## Conclusion

[JamfUploader] processors now have new ways of authenticating with Jamf Pro, which (hopefully!) still being fully backward-compatible. So far, I have only implemented the changes in the [grahampugh/jamf-upload][4] repo ([4]), because it is a significant code change with a reasonable risk that I've broken something. I'll be using the latest commits in my daily work for a week or two before copying the changes over to the [autopkg/grahampugh-recipes][5] repo ([5]) to minimise the chance of undiscovered bugs.

However, if you'd like to help discover the bugs, please add `grahampugh/jamf-upload` to your AutoPkg repo list, and let me know if anything isn't working!

[1]: https://developer.jamf.com/platform-api/reference/getting-started-with-platform-api
[2]: https://account.jamf.com
[3]: https://github.com/grahampugh/jamf-upload/wiki/Credentials
[4]: https://github.com/grahampugh/jamf-upload
[5]: https://github.com/autopkg/grahampugh-recipes

{% include urls.md %}
