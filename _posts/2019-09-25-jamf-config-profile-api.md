---
layout: post
title:  "Update a config profile on multiple Jamf Pro servers with the API"
comments: true
---

I work with multiple Jamf Pro instances and often need to copy a configuration profile from one instance to many others. I use the Jamf Pro Classic API.

If a configuration profile is overwritten via the API, the default setting is that the profile will only apply to new clients. That meant asking our customers to go to the profile in the Jamf Pro admin interface and manually press 'Edit ' then 'Save', so that the GUI offers the opportunity to redeploy to all clients.

In conversation with fellow Mac admin Anver Housseini, he let me know that he figured out that it is possible to change this setting via the API. I couldn't find an explicit reference to this key being used for this purpose on the internet, so I'm documenting it here. All kudos to Anver.

To do this, you need to change the following key in the downloaded XML:

```xml
    <general>
        <redeploy_on_update>Newly Assigned</redeploy_on_update>
    </general>
```

This needs to be changed to `All`:

```xml
    <general>
        <redeploy_on_update>All</redeploy_on_update>
    </general>
```

To achieve this in a shell script, simply output the downloaded XML in to a file, substitute the value with `sed`, writing to a different file, and then upload the parsed file.

Since `id` and some other keys should also be stripped out when transferring configuration profile API objects to another Jamf Pro instance, I perform a series of `sed` operations at once:

```bash
credentials=$(printf "APIuser:password" | iconv -t ISO-8859-1 | base64 -i -)

curl -X GET --header "Accept: application/xml" \
    --header "authorization: Basic $credentials" \
    "https://jss-address/JSS01/JSSResource/osxconfigurationprofiles/id/123456" \
    | xmllint --format - > fetched.xml

cat fetched.xml \
    | grep -v '<id>' \
    | sed '/<computers>/,/<\/computers>/d' \
    | sed '/<limit_to_users>/,/<\/limit_to_users>/d' \
    | sed '/<users>/,/<\/users>/d' \
    | sed '/<user_groups>/,/<\/user_groups>/d' \
    | sed 's/<redeploy_on_update>Newly Assigned<\/redeploy_on_update>/<redeploy_on_update>All<\/redeploy_on_update>/g' \
    > parsed.xml

curl -X PUT --header "Content-Type: application/xml" \
    --header "authorization: Basic $credentials" \
    --data-binary @parsed.xml \
    "https://jss-address/JSS02/JSSResource/osxconfigurationprofiles/id/98765"
```

This ensures that any changes you make to the configuration profile are redeployed to all clients.

*Note: the above code assumes that the ID of the profile on source instance `JSS01` is `123456` and the ID of the existing profile on destination instance `JSS02` is `98765`. It also assumes that the API user credentials are the same on each Jamf Pro instance.*

# Bugs

There are a couple of bugs that I have encountered when copying configuration profiles via the API:

1. You cannot copy the icon of a Self Service configuration profile.
2. Kernel Extension whitelist profiles do not copy successfully.

{% include urls.md %}
