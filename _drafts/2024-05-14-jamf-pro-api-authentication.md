---
layout: post
title:  "Changes to the Classic API in Jamf Pro - what you need to know"
comments: true
---

> Note: My colleague William Smith created a similar blog post [How to convert Classic API scripts to use bearer token authentication][11] in 2022. This post serves as a timely reminder of what is changing with the Classic API, as well as providing updated information about the possible ways to authenticate against both Jamf Pro APIs.

## Contents

1. [Introduction](#introduction)
2. [End of support of Basic Authentication - what does it mean?](#end-of-support-of-basic-authentication---what-does-it-mean)
3. [How to adapt an existing shell script to use a Bearer Token](#how-to-adapt-an-existing-shell-script-to-use-a-bearer-token)
4. [Additional tips and tricks](#additional-tips-and-tricks)
5. [Client Credentials-based Authentication](#client-credentials-based-authentication)
6. [Conclusion](#conclusion)
7. [Further Reading](#further-reading)

## Introduction

From its introduction, the original API for Jamf Pro, now known as the Classic API, used Basic Authentication for all endpoints. Basic authentication means supplying the username and password of a user account directly with every request. From a security perspective, sending credentials repeatedly over the internet could be considered a credible risk.

The Jamf Pro API was [first introduced in 2016][1] with Casper Suite 9.93, although it remained in beta until the release of Jamf Pro 10.26.0. This separate API supports Basic Authentication, but only for one single endpoint: `/api/v1/auth/token`. This endpoint is used to obtain a "Bearer Token", which is a unique, time-limited access token that is used to make requests to all other endpoints, and can also be revoked after use. This reduces the exposure of the original credentials, since they need only be used once per task.

From Jamf Pro version 10.35.0, [released April 2022][2], Bearer Token authentication was introduced for the Classic API. Since then, it has been possible to disable Basic Authentication for the Classic API (apart from the `/api/v1/auth/token` endpoint used to obtain the bearer token), by navigating to **Settings > Jamf Pro User Accounts & Groups > Password Policy** and deselecting the **Allow Basic authentication in addition to Bearer Token authentication** checkbox.

New Jamf Pro instances created with version 10.42.0 or newer had Basic Authentication disabled by default, though it could be enabled using the checkbox above.

## End of support of Basic Authentication - what does it mean?

Basic Authentication in the Classic API is no longer supported and will be turned off for all 11.5.0 instances to provide enhanced security. **This does not remove the ability to obtain a Bearer Token using basic authentication**, which is then used to authenticate requests to the Classic API.

If you have composed your own scripts, or are using other people's scripts, that communicate with the Jamf Pro API, you will already be familiar with how to go about obtaining, using and revoking a Bearer Token. If, however, you have previously only needed to communicate using the Classic API, you may need to make some changes to these scripts to continue to use them on Jamf Pro 11.5.0 and above.

> Note that although it is no longer supported as of version 11.5.0, it *is* currently possible to re-enable Basic Authentication for the Classic API.

## How to adapt an existing shell script to use a Bearer Token

In this post I will concentrate on the use of shell scripts (bash, zsh), as this is the most common method of communicating with the API. For help with other languages, the [Jamf Pro Classic API Reference][4] has examples of how to use the APIs with many different programming languages. 

Let's say we want to get a list of computers on a Jamf Pro server. In the past we would have used a single `curl` command such as the example below. 

> Note: you may see short or long parameter names in `curl` statements. I've used the long names here, so here's a short glossary of equivalents that are relevant to this post:
> * `-X` is the same as `--request` (`POST`, `GET`, `PUT` or `DELETE`)
> * `-H` is the same as `--header`
> * `-u` is the same as `--user`
> * `-d` is the same as `--data` (but for URL-encoding, `--data-urlencode` should be specified)
> * `-o` is the same as `--output` (i.e. write the output to a file)
> * `--url` is optional; a URL can be supplied with no parameter name

In all examples, we will assume an admin account with the username `jamfsw` and the password `jamf1234`.

```bash
# request list of computers using Basic Authentication 
/usr/bin/curl --request GET \
              --url "https://yourserver.jamfcloud.com/JSSResource/computers" \
              --header 'accept: application/json' \
              --user "jamfsw:jamf1234"
```

From Jamf Pro 11.5.0, we need to change this to first create a Bearer Token, and then use it to get the computer list. Note that we need to extract the token from the JSON output we receive. To do this we use the `plutil` tool which has gained the ability to extract JSON data since macOS 12 Monterey (for more details on the use of `plutil`, see Richard Purves' blog post [Plutil JSON parsing for Fun and Profit][10]).

```bash
# obtain a Bearer Token using Basic Authentication, write the output into a variable
request=$(
    /usr/bin/curl --request POST \
                  --url "https://yourserver.jamfcloud.com/api/v1/auth/token" \
                  --header 'accept: application/json' \
                  --user "jamfsw:jamf1234"
)

# extract the token from the JSON
token=$(/usr/bin/plutil -extract token raw -o - - <<< "$request")

# request list of computers using Bearer Token 
/usr/bin/curl --request GET \
              --url "https://yourserver.jamfcloud.com/JSSResource/computers" \
              --header 'accept: application/json' \
              --header "authorization: Bearer $token"
```

If we have multiple `curl` requests to use in a single script, we can continue to use the token for each request. If/when we want to revoke the token at the end of the script, so that it cannot be used again, this is done using the token itself:

```bash
# revoke the Bearer Token 
/usr/bin/curl --request POST \
              --url "https://yourserver.jamfcloud.com/api/v1/auth/invalidate-token" \
              --header 'accept: application/json' \
              --header "authorization: Bearer $token"
```

## Additional tips and tricks

### Use the same Bearer Token for multiple scripts

If you have a workflow that runs several scripts each of which are communicating with the Jamf Pro or Classic APIs, you may wish to reuse the Bearer Token to minimise the number of Basic Authentication requests made, and to speed up the transactions. In this case, I would recommend outputting it to a file.

Here's an example of exporting the token to a file at `/tmp/bearer-token.txt`.

```bash
# obtain a Bearer Token using Basic Authentication, write the output to a file
/usr/bin/curl --request POST \
              --url "https://yourserver.jamfcloud.com/api/v1/auth/token" \
              --header 'accept: application/json' \
              --user "jamfsw:jamf1234" \
              --output "/tmp/bearer-token.txt"
```

Now we can get the token from any script using `plutil` as before.

```bash
# extract the token from the JSON
token=$(/usr/bin/plutil -extract token raw "/tmp/bearer-token.txt")
```

Note that since the token is now written to disk, it's more important to revoke the token if we don't need it any more.

### Check the expiration of an existing token

If we're storing the token in a file for use over multiple runs of scripts over an extended period of time, we may wish to check that it is still valid. We can check the token's expiry limit in the JSON file that contains the token. If we want to compare the expiry time to the current time, it's best to convert the timestamp to a Universal Time Epoch to rule out timezone issues.

```bash
# check the expiry time of the token
expires=$(/usr/bin/plutil -extract expires raw "/tmp/bearer-token.txt" | /usr/bin/awk -F . '{print $1}')

# convert expiry time to a UTC epoch
expiration_epoch=$(/bin/date -j -f "%Y-%m-%dT%T" "$expires" +"%s")

# compare expiry epoch to current time
current_time_epoch=$(/bin/date -j -f "%Y-%m-%dT%T" "$(/bin/date -u +"%Y-%m-%dT%T")" +"%s")

if [[ $expiration_epoch -gt $current_time_epoch ]]; then
    echo "Token valid until the following epoch time: $expiration_epoch"
else
    echo "No valid token available"
fi
```

### Create a new token using an existing token

By default, tokens expire after 20 minutes, but we can use a currently valid token to generate a new token using the `/api/v1/auth/keep-alive` endpoint, giving us another 20 minutes.

```bash
# obtain a Bearer Token using an existing token, write the output to a file
/usr/bin/curl --request POST \
              --url "https://yourserver.jamfcloud.com/api/v1/auth/keep-alive" \
              --header 'accept: application/json' \
              --header "authorization: Bearer $token" \
              --output "/tmp/bearer-token.txt"
```

## Client Credentials-based Authentication

A new, more secure way of obtaining a Bearer Token was introduced with the release of Jamf Pro 10.49.0. This allows us to obtain a Bearer Token using an API Client, which would normally be configured from within Jamf Pro. Unlike the credentials required to obtain a Bearer Token using Basic Authentication, API Clients have no access to the Jamf Pro user interface. 

Privileges are assigned to an API Client using one or more API Roles, which are also configured in the Jamf Pro user interface, with the privileges of each API Role acting cumulatively on the API Client. In most circumstances, it will be simplest to create one API Role per API Client.

For detailed instructions on how to set up and use API Roles and Clients, see [Jamf Pro Documentation: API Roles and Clients][5]. I just want to point out the basic differences between the use of API Clients and a normal account username/password combination.

### Obtaining a Bearer Token

When [setting up an API Client][5], we obtain a Client ID and we generate a Client Secret. These are required to obtain the token. The endpoint used for obtaining the token is `/api/oauth/token`. As earlier, in this example we are outputting the JSON to a file for further use, but we can import it into a variable or environment variable exactly as described above.

```bash
/usr/bin/curl --request POST \
              --url "https://yourserver.jamfcloud.com/api/oauth/token" \
              --header 'Content-Type: application/x-www-form-urlencoded' \
              --data-urlencode 'client_id=6cabf059-21c9-44d6-bbde-02898f7430dd' \
              --data-urlencode 'grant_type=client_credentials' \
              --data-urlencode 'client_secret=dzmsPks-FwXpks80jhQGZZrAV3H2_ER0NAk91RE-xOBZvfghd98EM1hF9msfkanl' \
              --output "/tmp/access-token.txt"
```

The access token file generated by this method is different to that generated when requesting a token using Basic Authentication, in that the key names are different. The token key is named `access_token`, but is used in exactly the same way as the token obtained using Basic Authentication.
And rather than storing the expiry as a timestamp, we get a value in seconds for how long it will be until it expires - this is the `expires_in` key. 

Let's look at how we extract the token, and how to calculate if the token is still valid. 

```bash
# extract the token from the JSON
token=$(/usr/bin/plutil -extract access_token raw "/tmp/access-token.txt")

# compare expiry epoch to current time
current_time_epoch=$(/bin/date +%s)
expires_in=$(/usr/bin/plutil -extract expires_in raw "/tmp/access-token.txt")
expiration_epoch=$(($current_epoch + $token_expires_in - 1))

if [[ $expiration_epoch -gt $current_time_epoch ]]; then
    echo "Token valid until the following epoch time: $expiration_epoch"
else
    echo "No valid token available"
fi
```

Two last things to note, token expiration is achieved exactly as before using the `/api/v1/auth/invalidate-token` endpoint. But it is not possible to keep a bearer token alive that was generated using `/api/oauth/token`, so we always need to use the Client ID and Client Secret to create a new token.

## Conclusion

I hope this post provides clarity on what is being removed from Jamf Pro and what remains. To reiterate, we can continue to use normal account credentials to interact with the API, but if your scripts are using those credentials to directly request a Classic API endpoint, then before Jamf Pro is upgraded to 11.5.0, you will need to adapt the scripts to use those credentials to generate a Bearer Token, and then use that Bearer Token to make those subsequent requests.

For security reasons, moving forward you may want to consider setting up API Roles and Clients instead of using actual account credentials. This is especially pertinent when setting up accounts for use by third party integrations, external teams, and so on. However, this does not need to be done before the release of Jamf Pro 11.5.0.

## Further Reading

* [Jamf Pro API Overview][6] - includes code examples for obtaining a Bearer Token using Basic Authentication, and provides details on the HTTP Response Codes we may encounter.
* [Classic API Reference][4] - Details on how to use the Classic API and a list of all endpoints.
* [Classic API Authentication Changes][3] - Details on the depracation of the use of Basic Authentication for Classic API endpoints.
* [Jamf Pro API Reference][8] - Details on how to use the Jamf Pro API and a list of all endpoints.
* [How to convert Classic API scripts to use bearer token authentication][11] - Jamf Tech Thoughts post by William Smith.
* [API Roles and Clients][5] - Technical documentation about API Roles and Clients, detailing how to set them up in the Jamf Pro user interface.
* [Client Credentials][7] - Further details about API Roles and Clients, including a recipe for obtaining a Bearer Token using API Clients.
* [API code recipes][9] - Easy to read shell code recipes for many of the workflows described in this post.

[1]: https://www.jamf.com/blog/advanced-api-examples-and-best-practices/
[2]: https://community.jamf.com/t5/jamf-pro/what-s-new-in-the-jamf-pro-10-35-release/m-p/255145
[3]: https://developer.jamf.com/jamf-pro/docs/classic-api-authentication-changes
[4]: https://developer.jamf.com/jamf-pro/reference/classic-api
[5]: https://learn.jamf.com/en-US/bundle/jamf-pro-documentation-current/page/API_Roles_and_Clients.html
[6]: https://developer.jamf.com/jamf-pro/docs/jamf-pro-api-overview
[7]: https://developer.jamf.com/jamf-pro/docs/client-credentials
[8]: https://developer.jamf.com/jamf-pro/reference/jamf-pro-api
[9]: https://developer.jamf.com/jamf-pro/recipes
[10]: https://richard-purves.com/2021/12/10/plutil-json-parsing-for-fun-and-profit/
[11]: https://community.jamf.com/t5/tech-thoughts/how-to-convert-classic-api-scripts-to-use-bearer-token/ba-p/273910

{% include urls.md %}
