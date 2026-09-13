---
layout: post
title:  "Jamf's Platform API is now generally available - and what JamfUploader users need to know"
comments: true
tags:
  - apple
  - mac
  - jamf
  - autopkg
  - jamfuploader
summary: "Jamf's Platform API Gateway is now generally available, bringing new environment-level integrations and updated authentication URLs. JamfUploader and JamfCLIRunner now leverage jamf-cli profiles for streamlined Platform API credential management."
---

## Introduction

As [announced on September 4][1], Jamf's Platform APIs and the Platform API Gateway is now generally available to most users. I originally described the public beta of the Platform API Gateway [back in April][2], but the gateway has changed somewhat since that initial public release. Additionally, more APIs have been made available, all accessible via credentials generated in [Jamf Account].

## What's changed?

The GA introduces new integration scope levels. In addition to the tenant-level API integrations that we have been able to generate since the initial beta, there are now also environment- and organisation-level API integrations. What are those? Read on.

### Environment-level integrations

A Platform Environment consists of one or more tenants associated with your account. At present, this can consist of only one tenant of the same product type so, for example, it could consist of one Jamf Pro tenant, one Jamf Protect tenant, and one Jamf Security Cloud tenant - which would be co-associated with a Jamf for Mac account. Existing Platform Environments are listed in Jamf Account.  

### Tenant-level integrations

Individual tenants not associated with an environment can continue to use the API with a tenant-level API integration.

However, bear in mind that not all APIs are available, for example blueprints and benchmarks APIs are not available using a tenant-level API integration any more - you have to use an environment-level API integration for that, even if the Platform Environment consists of just one tenant. For more details on scope levels and which APIs are available to which, see the [Platform API fundamentals][5] guide.

### Organisation-level integrations

These integrations are not concerned with your tool tenants, but instead are to do with managing licenses and items relevant to partners. So, we won't cover those here.

### Request URLs have changed, too

Authentication methodology remains just as with the beta, using OAuth2, although the gateway URL has changed from the old `https://<region>.apigw.jamf.com` to `https://<region>.api.jamfcloud.com`. For this reason, any API integrations that you created previously during the beta cycle were removed at GA. You have to set up new ones.

Once you've obtained the Bearer Token, the API requests are constructed differently to how they were in the beta. Previously, the tenant ID needed to be included in the API request URL; now the tenant or environment ID needs instead to be included in a header. See [Getting Started With Platform API][3].

Note also that the `/api` part of the URL is removed entirely. Instead, the API type, endpoint version, and endpoint make up the URL, for example:

    https://us.api.jamfcloud.com/pro/v1/buildings

The Jamf Pro Classic API is still available via Platform API Gateway, and has no version, so those endpoints become, for example:

    https://eu.api.jamfcloud.com/proclassic/policies

This is equivalent to the following URL if you are using the Jamf Pro API rather than Platform API:

    https://your.jamfcloud.com/JSSResource/policies

## jamf-cli

[jamf-cli] supports the new Platform API as of v1.28.0, including the storage of tenant, environment and organisation IDs in your keychain (or keystore on Linux).

The advantages of using `jamf-cli` in your scripts instead of raw API calls are that you don't have to script out the authentication step at all, don't need to worry about result pagination, and can output the result of a request in multiple formats to suit your goal. Not only that, as API endpoints evolve, jamf-cli will release a new version that uses them - you don't need to research the changes to endpoints, just keep jamf-cli updated and you'll be fine.

## JamfUploader

With the addition of so many different APIs, and the changes to the authentication method, I decided that rather than maintain an independent method of credential storage for Platform API, [JamfUploader] should instead take advantage of the utility of jamf-cli to handle it. So, I've removed the script I had previously included in the repo for adding Platform API credentials to the keychain. You can still manually provide those credentials in your recipe or prefs file, but I would instead encourage you to create a jamf-cli "profile" on your AutoPkg machine. Of course, this means installing jamf-cli on your AutoPkg machine, too.

Creating a jamf-cli profile is easy, simply run the following command and answer the prompts:

    jamf-cli config add-profile <NEW-PROFILE-NAME> --auth-method platform --environment-id "<ENTER-ENV-ID-HERE>" --url "https://<ENTER-REGION-HERE>.api.jamfcloud.com"

You will be prompted to enter the Client Secret. `--environment-id` can be switched for `--tenant-id` if that's all you have, but environments are the recommendation going forward.

To use a jamf-cli profile with JamfUploader, add the name of the profile as the value of the `JAMF_CLI_PROFILE` key in your prefs file.

With that in place, you can remove `JSS_URL`, `API_USERNAME` and `API_PASSWORD` from your autopkg prefs files; you won't need those any more.

> Note that support for the existing Jamf Pro API continues as before, including the `set-credentials.sh` and `set-api-client.sh` scripts. You don't need to change anything to continue to use these endpoints.

## JamfCLIRunner

[JamfCLIRunner] is the AutoPkg processor I introduced back in April, as a framework for making requests using jamf-cli in AutoPkg recipes. This allows you to create (or update, or delete) blueprints, benchmarks, or any other API served by jamf-cli (which means all public API endpoints!), in a recipe. See the original [JamfCLIRunner blog post][4] for more details.

JamfCLIRunner supports the exact same `JAMF_CLI_PROFILE` key as the JamfUploader processors. So, if using `jamf-cli` profiles, you can have `JamfCLIRunner` and `JamfXYZUploader` processors in the same recipe, all authenticating with the same credentials and using the same cached Bearer token to speed up workflows.

## Conclusion

Between jamf-cli, JamfUploader, and JamfCLIRunner, you have a complete credential storage, authentication layer, and API request framework with 100% endpoint coverage for performing Configuration-as-Code workflows using AutoPkg. No need for learning and maintaining different frameworks for different endpoints and processes - AutoPkg can do it all from sourcing and building a package, to constructing a configuration profile or a blueprint or a PreStage, to uploading everything to Jamf Pro, or setting up Jamf Protect analytics or AI Governance. It couldn't be easier to create start-to-finish, idempotent, version-controlled workflows to help you maintain your devices using Jamf's suite of management and security tools.

[1]: https://www.jamf.com/blog/platform-api-gateway/
[2]: https://grahamrpugh.com/2026/04/19/jamfuploader-platform.html
[3]: https://developer.jamf.com/platform-api/reference/getting-started-with-platform-api
[4]: https://grahamrpugh.com/2026/04/12/jamf-cli-runner.html
[5]: https://developer.jamf.com/platform-api/reference/platform-api-fundamentals

{% include urls.md %}
