---
layout: post
title:  "Understanding Jamf Pro API Roles And Clients"
comments: true
---

Last week I posted an article in Jamf's official blog regarding how to use the new API Roles and Clients in Jamf Pro. API Roles and Clients provide a more secure way of integrating with the API than using regular accounts.

A bonus section shows how to use the Jamf Pro API to create and manage the API Roles, which is something you may wish to automate if you are handling multiple Jamf Pro instances.

**[Check out the blog post here](https://www.jamf.com/blog/understanding-jamf-pro-api-roles-and-clients/)**

![How To Image](https://media.jamf.com/images/news/2024/jamf-how-to-blog-image.webp?q=80&w=1600)

As there are some formatting issues in the above article, I am posting the content here too.

## Contents

- [Contents](#contents)
- [Introduction to the Jamf Pro APIs](#introduction-to-the-jamf-pro-apis)
- [Client Credentials-based Authentication](#client-credentials-based-authentication)
  - [What is an API Role?](#what-is-an-api-role)
  - [What is an API Client?](#what-is-an-api-client)
  - [Using an API Client to generate an access token](#using-an-api-client-to-generate-an-access-token)
- [Best practices for API Role and API Client use](#best-practices-for-api-role-and-api-client-use)
- [Bonus Section: using the Jamf Pro API to manage API Roles and Clients](#bonus-section-using-the-jamf-pro-api-to-manage-api-roles-and-clients)
  - [List existing API Roles](#list-existing-api-roles)
  - [Get a list of all possible privileges that can be assigned to an API Role](#get-a-list-of-all-possible-privileges-that-can-be-assigned-to-an-api-role)
  - [Create a new API Role](#create-a-new-api-role)
  - [Amend or delete an existing API Role](#amend-or-delete-an-existing-api-role)
  - [List existing API Clients](#list-existing-api-clients)
  - [Create a new API Client](#create-a-new-api-client)
  - [Amend or delete an existing API Client](#amend-or-delete-an-existing-api-client)
  - [Create client credentials for an API Client](#create-client-credentials-for-an-api-client)
- [Conclusion](#conclusion)
- [Further reading](#further-reading)

## Introduction to the Jamf Pro APIs

Jamf Pro has two APIs, the original API now known as the [Classic API][1], and the newer [Jamf Pro API][2] that was [introduced in 2016][7] with Casper Suite 9.93 and became a production API with Jamf Pro 10.26.0.

The Classic API used Basic Authentication for all endpoints. Basic authentication means supplying the username and password of a user account directly with every request. From a security perspective, sending credentials repeatedly over the internet could be considered a credible risk.

The Jamf Pro API supports Basic Authentication, but only for one single endpoint: `/api/v1/auth/token`. This endpoint is used to obtain a "Bearer Token", which is a unique, time-limited access token that is used to make requests to all other endpoints, and can also be revoked after use. This reduces the exposure of the original credentials, since they need only be used once per task.

This method of obtaining a Bearer Token was also added to the Classic API with Jamf Pro 10.35.0, [released April 2022][6].  Since then, it has been possible to disable Basic Authentication for the Classic API (apart from the `/api/v1/auth/token` endpoint used to obtain the bearer token), by navigating to **Settings > Jamf Pro User Accounts & Groups > Password Policy** and deselecting the **Allow Basic authentication in addition to Bearer Token authentication** checkbox.

New Jamf Pro instances created with version 10.42.0 or newer had Basic Authentication disabled by default, though it could be enabled using the checkbox above.

When a Jamf Pro instance is upgraded to Jamf Pro 11.5.0 or greater from a version older than this, the Basic Authentication checkbox is forcibly disabled. For the time being it is still possible to re-enable it, but Basic Authentication of Classic API endpoints is no longer supported, so any tools and scripts should be converted to use Bearer Token authentication as soon as possible.

For more information, see the Jamf Developer Article [Classic API Authentication Changes][3], William Smith's blog post [How to convert Classic API scripts to use bearer token authentication][4], and my personal blog post [Changes to Classic API authentication in Jamf Pro - what you need to know][5].

## Client Credentials-based Authentication

In addition to the method of obtaining a Bearer Token using Basic Authentication described above, a new, more secure way of obtaining an access token was introduced with the release of Jamf Pro 10.49.0, namely [Client Credentials-based Authentication][8]. Unlike the credentials required to obtain a Bearer Token using Basic Authentication, API Clients provide a dedicated interface for controlling access to the Jamf Pro API and the Classic API, and, importantly, have no access to the Jamf Pro user interface.

> Note that it is not currently possible to disable API access to user accounts via Bearer Token authantication.

### What is an API Role?

API Roles are are a custom collection of privileges, defining which API endpoints an API Client has access to.

You define API Roles within Jamf Pro, by navigating to **Settings > System > API roles and clients** and clicking on the **API Roles** tab.

> Note that these privilege sets are completely unrelated to any user or group privileges set in **Settings > System > User accounts and groups**.

### What is an API Client?

An API Client is a kind of account to which API Roles can be assigned. One or more API Roles can be assigned to an API Client, granting their cumulative privileges. At least one API Role must have been created before an API Client can be created, as it is not possible to assign no API Roles to an API Client.

For detailed instructions on how to set up and use API Roles and Clients, see the excellent Jamf Pro documentation [API Roles and Clients][9]. I just want to point out below the basic differences between the use of API Clients and a normal account username/password combination.

### Using an API Client to generate an access token

Once an API Client has been created, a client secret can be generated. The API Client and Secret are used together to obtain an access token using the `/api/oauth/token` endpoint. In the following example we are outputting the JSON to a file so that it can be used across multiple commands and scripts. The fictitious `client_id` is visible in the Jamf Pro console, and the `client_secret` is the one generated, which is shown only at the point of generation so needs to be stored in a password manager of your choice.

> Note: you may see short or long parameter names in `curl` statements. I've used the long names here, so here's a short glossary of equivalents that are relevant to this post:
>
> - `-X` is the same as `--request` (`POST`, `GET`, `PUT` or `DELETE`)
> - `-H` is the same as `--header`
> - `-u` is the same as `--user`
> - `-d` is the same as `--data` (but for URL-encoding, `--data-urlencode` should be specified)
> - `-o` is the same as `--output` (i.e. write the output to a file)
> - `--url` is optional; a URL can be supplied with no parameter name

```bash
/usr/bin/curl --request POST \
              --url "https://yourserver.jamfcloud.com/api/oauth/token" \
              --header 'Content-Type: application/x-www-form-urlencoded' \
              --data-urlencode 'client_id=6cabf059-21c9-44d6-bbde-02898f7430dd' \
              --data-urlencode 'grant_type=client_credentials' \
              --data-urlencode 'client_secret=dzmsPks-FwXpks80jhQGZZrAV3H2_ER0NAk91RE-xOBZvfghd98EM1hF9msfkanl' \
              --output "/tmp/access-token.txt"
```

The access token file generated by this method is different to that generated when requesting a Bearer Token using Basic Authentication, in that the key names are different. The token key is named `access_token`, but is used in exactly the same way as the token obtained using Basic Authentication. And rather than storing the expiry as a timestamp, we get a value in seconds for how long it will be until it expires - this is the `expires_in` key.

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

Since we exported the token to a file, we should invalidate the token after use to minimise risk of unwanted capture and malicious re-use. This is done using the token itself:

```bash
# revoke the Bearer Token 
/usr/bin/curl --request POST \
              --url "https://yourserver.jamfcloud.com/api/v1/auth/invalidate-token" \
              --header 'accept: application/json' \
              --header "authorization: Bearer $token"
```

> Note that unlike with a Bearer Token obtained using Basic Authentication, it is not possible to keep an access token that was generated using `/api/oauth/token` alive using the existing token, so we always need to use the Client ID and Client Secret to create a new token once the old one has expired.

## Best practices for API Role and API Client use

As pointed out by Bryson Tyrell in his article [Notes on Jamf Pro API Roles and Clients][10], if we add or remove an API Role from an API Client, this is defined as a "scope change" which requires the generatiomn of a new client secret for the changes to take effect. On the other hand, any changes made to the privileges set in an existing API Roles take immediate effect in terms of what the API Client can access - it is not necessary to generate a new client secret for these changes to take effect.

For this reason, it is recommended to create a specific API Role for each API Client, rather than trying to manage cumulative API Roles that are reused with different API Clients.

## Bonus Section: using the Jamf Pro API to manage API Roles and Clients

The Jamf Pro documentation describes how to create API Roles and API Clients in the Jamf Pro Console. However, it is possible to manage API Roles and Clients completely from the Jamf Pro API. It may seem counterintuitive to use a Jamf Pro user to manage API Roles and Clients, but for those of us interested in automating the setup of Jamf Pro instances, this is a valuable resource for avoiding manual work within the admin console of new instances.

Let's take a look at how to use the API to manage API Roles and Clients. To do this, we have to obtain a Bearer Token in the traditional way using the credentials of a user account. In this example, we will assume an admin account with the username `jamfsw` and the password `jamf1234`.

```bash
# obtain a Bearer Token using Basic Authentication, write the output to a file
/usr/bin/curl --request POST \
              --url "https://yourserver.jamfcloud.com/api/v1/auth/token" \
              --header 'accept: application/json' \
              --user "jamfsw:jamf1234" \
              --output "/tmp/bearer-token.txt"
```

We will use the token stored in `/tmp/bearer-token.txt` for the following API requests, using the following command before each use:

```bash
# extract the token from the JSON
token=$(/usr/bin/plutil -extract token raw "/tmp/bearer-token.txt")
```

### List existing API Roles

In order to manage API roles, we need to obtain a list of any existing API Roles. The following command will output a list of current API roles in JSON format, sorted by ID, to `/tmp/curl-output.txt`.

```bash
/usr/bin/curl --request GET \
              --url 'https://yourserver.jamfcloud.com/api/v1/api-roles?page=0&page-size=100&sort=id%3Aasc' \
              --header 'accept: application/json' \
              --header "authorization: Bearer $token" \
              --output "/tmp/curl-output.txt"
```

The output shows the IDs, display names and set of privileges associated with each Role:

```json
{
  "totalCount": 1,
  "results": [
    {
      "id": "1",
      "displayName": "One Role to Rule them all",
      "privileges": [
        "View License Serial Numbers"
      ]
    }
  ]
}
```

To obtain details of a specific role, add the ID of that Role to the URL, e.g. `https://yourserver.jamfcloud.com/api/v1/api-roles/1`. No additional information is stored in the individual records in comparison to the complete list.

### Get a list of all possible privileges that can be assigned to an API Role

To get a complete set of possible API Role privileges that we could add to a Role, use the `/api/v1/api-role-privileges` endpoint, as in the following request.

```bash
/usr/bin/curl --request GET \
              --url 'https://yourserver.jamfcloud.com/api/v1/api-role-privileges' \
              --header 'accept: application/json' \
              --header "authorization: Bearer $token" \
              --output "/tmp/api-role-privileges.txt"
```

The output lists all roles within a `priviliges` list.

```json
{
  "privileges": [
    "Allow User to Enroll",
    "Assign Users to Computers",
    # TRUNCATED LIST
    "View Recovery Lock",
    "View Return To Service Configurations"
  ]
}
```

Alternatively, we can search for privileges using keyword search. Here we search for all privileges associated with Static Computer Groups:

```bash
/usr/bin/curl --request GET \
              --url 'https://yourserver.jamfcloud.com/api/v1/api-role-privileges/search?name=Static%20Computer%20Groups&limit=15' \
              --header 'accept: application/json' \
              --header "authorization: Bearer $token" \
              --output "/tmp/api-role-privileges.txt"
```

The output lists all roles within a `priviliges` list.

```json
{
  "privileges": [
    "Create Static Computer Groups",
    "Delete Static Computer Groups",
    "Read Static Computer Groups",
    "Update Static Computer Groups"
  ]
}
```

### Create a new API Role

The following command will create a new role called "Amend Static Groups" which has create, read, and update privileges for Static Computer Groups. Note that the `data` key contains the `privileges` key in exactly the form it was obtained from the search above.

```bash
/usr/bin/curl --request POST \
              --url 'https://yourserver.jamfcloud.com/api/v1/api-roles' \
              --header 'accept: application/json' \
              --header 'Content-Type: application/json' \
              --header "authorization: Bearer $token" \
              --output "/tmp/curl-output.txt" \
              --data '{
                          "displayName": "Amend Static Groups",
                          "privileges": [
                              "Create Static Computer Groups",
                              "Read Static Computer Groups",
                              "Update Static Computer Groups"
                          ]
                       }'
```

The response reflects the request and returns also the ID of the new API Role:

```json
{
  "privileges": [
    "Create Static Computer Groups",
    "Update Static Computer Groups",
    "Read Static Computer Groups"
  ],
  "displayName": "Amend Static Groups",
  "id": "2"
}
```

### Amend or delete an existing API Role

To amend a specific API Role, add the ID of that Role to the URL, e.g. `https://yourserver.jamfcloud.com/api/v1/api-roles/2`, and use a `PUT` request. The contents of the `data` are exactly as with creating a new API Role (do not include the ID) and the response is also the same.

To delete a specific API Role, add the ID of that Role to the URL, and use a `DELETE` request, as below.

```bash
/usr/bin/curl --request DELETE \
              --url 'https://yourserver.jamfcloud.com/api/v1/api-roles/2' \
              --header 'accept: application/json' \
              --header "authorization: Bearer $token"
```

### List existing API Clients

If we want to create API clients using the API, we need to know the existing clients. API clients are managed via the `api-integrations` endpoint. The following command will output a list of current API roles in JSON format, sorted by ID, to `/tmp/curl-output.txt`.

```bash
/usr/bin/curl --request GET \
              --url 'https://yourserver.jamfcloud.com/api/v1/api-integrations?page=0&page-size=100&sort=id%3Aasc' \
              --header 'accept: application/json' \
              --header "authorization: Bearer $token" \
              --output "/tmp/curl-output.txt"
```

The output shows the IDs, display names and set of privileges associated with each Role:

```json
{
  "totalCount": 1,
  "results": [
    {
      "authorizationScopes": [
        "Amend Static Groups"
      ],
      "displayName": "Static Group Amendment Client",
      "enabled": true,
      "accessTokenLifetimeSeconds": 300,
      "id": 1,
      "appType": "NONE",
      "clientId": "b8b14453-8d28-4d0a-9493-c9cf7c040a1e"
    }
  ]
}
```

This gives us an idea of the possible settings we can set and amend in an API Client, namely that we can set it to Enabled or Disabled, and we can specify the lifetime of an access token in seconds.

To obtain details of a specific role, add the ID of that Role to the URL, e.g. `https://yourserver.jamfcloud.com/api/v1/api-roles/1`. No additional information is stored in the individual records in comparison to the complete list.

You can also filter the list to a specific API Client name by adding a filter to the URL. For example, to filter to the API Client named "Static Group Amendment Client", use the following URL: `https://yourserver.jamfcloud.com/api/v1/api-roles/?page=0&page-size=100&sort=id%3Aasc&filter=displayName%3D%3D%22Static%20Group%20Amendment%20Client%22` (note that we have to escape any quotation marks (`"`) with `%22` and any spaces with `%20`).

### Create a new API Client

The following command will create a new API Client called "Static Group Amendment Client" which is assigned the API Role `Amend Static Groups`. Note that the `data` key contains the `authorizationScopes` key in exactly the form it was obtained from the search above.

```bash
/usr/bin/curl --request POST \
              --url 'https://yourserver.jamfcloud.com/api/v1/api-integrations' \
              --header 'accept: application/json' \
              --header 'Content-Type: application/json' \
              --header "authorization: Bearer $token" \
              --output "/tmp/curl-output.txt" \
              --data '{
                          "authorizationScopes": [
                              "Amend Static Groups"
                          ],
                          "displayName": "Static Group Amendment Client",
                          "enabled": true,
                          "accessTokenLifetimeSeconds": 300
                       }'
```

The response reflects the request and returns also the ID of the new API Client, as well as the `clientId` which is required for generating the access token:

```json
{
  "authorizationScopes": [
    "Amend Static Groups"
  ],
  "displayName": "Static Group Amendment Client",
  "enabled": true,
  "accessTokenLifetimeSeconds": 300,
  "id": 1,
  "appType": "NONE",
  "clientId": "b8b14453-8d28-4d0a-9493-c9cf7c040a1e"
}
```

### Amend or delete an existing API Client

To amend a specific API Client, add the ID of that Client to the URL, e.g. `https://yourserver.jamfcloud.com/api/v1/api-integrations/1`, and use a `PUT` request. The contents of the `data` are exactly as with creating a new API Client (do not include the ID) and the response is also the same.

To delete a specific API Role, add the ID of that Role to the URL, and use a `DELETE` request, as below.

```bash
/usr/bin/curl --request DELETE \
              --url 'https://yourserver.jamfcloud.com/api/v1/api-integrations/1' \
              --header 'accept: application/json' \
              --header "authorization: Bearer $token"
```

### Create client credentials for an API Client

As explained earlier, to use an API client to obtain an access token, we need the Client ID and Client Secret. To generate a Client Secret using the API, use the following request:

```bash
/usr/bin/curl --request POST \
              --url 'https://yourserver.jamfcloud.com/api/v1/api-integrations/1/client-credentials' \
              --header 'accept: application/json' \
              --header "authorization: Bearer $token" \
              --output "/tmp/curl-output.txt"
```

The response contains the `clientID` and `clientSecret` keys.

```json
{
  "clientId": "b8b14453-8d28-4d0a-9493-c9cf7c040a1e",
  "clientSecret": "Bw0cZbfbe2JvK95Tnpqz1-eEnYgjSoz_lvsV-piZfK9zl4VyslX92EapYD_zkuNC"
}
```

Remember that there is no way to retrieve an existing Client Secret, neither via the GUI nor the API. So our workflow should store the Client Secret for future use.

## Conclusion

For security reasons, moving forward it is recommended to set up API Roles and Clients instead of using actual account credentials. This is especially pertinent when setting up accounts for use by third party integrations, external teams, and so on. There are currently no plans to deprecate the use of account credentials to obtain Bearer Token, but using API Roles and Clients is more secure.

For Jamf Pro admins who currently automate the setting up of users and groups in new instances using the Jamf Pro API, I have demonstrated how we can instead manage the setting up of API Roles and Clients. This could be done as part of a setup workflow at the end of which the management account with the rights to create API Roles and Clients is disabled or removed, drastically reducing the exposure surface of the Jamf Pro console.

## Further reading

Here's a summary of the links used in this article:

- [Jamf Developer Documentation - Classic API][1]
- [Jamf Developer Documentation - Jamf Pro API][2]
- [Jamf Developer Documentation - Classic API Authentication Changes][3]
- [Jamf Tech Thoughts - How to convert Classic API scripts to use bearer token authentication][4]
- [Graham Pugh's Blog - Changes to Classic API authentication in Jamf Pro - what you need to know][5]
- [What's new in the Jamf Pro 10.35 Release][6]
- [Jamf Blog - Advanced API Usage: Examples and Best Practices][7]
- [Jamf Developer Documentation - Client Credentials][8]
- [Jamf Pro Documentation - API Roles and Clients][9]
- [Bryson Tyrell's Blog Post - Notes on Jamf Pro API Roles and Clients][10]

[1]: https://developer.jamf.com/jamf-pro/reference/classic-api
[2]: https://developer.jamf.com/jamf-pro/reference/jamf-pro-api
[3]: https://developer.jamf.com/jamf-pro/docs/classic-api-authentication-changes
[4]: https://community.jamf.com/t5/tech-thoughts/how-to-convert-classic-api-scripts-to-use-bearer-token/ba-p/273910
[5]: https://grahamrpugh.com/2024/05/16/jamf-pro-api-authentication.html
[6]: https://community.jamf.com/t5/jamf-pro/what-s-new-in-the-jamf-pro-10-35-release/m-p/255145
[7]: https://www.jamf.com/blog/advanced-api-examples-and-best-practices/
[8]: https://developer.jamf.com/jamf-pro/docs/client-credentials
[9]: https://learn.jamf.com/en-US/bundle/jamf-pro-documentation-current/page/API_Roles_and_Clients.html
[10]: https://community.jamf.com/t5/tech-thoughts/notes-on-jamf-pro-api-roles-and-clients/ba-p/305058

{% include urls.md %}
