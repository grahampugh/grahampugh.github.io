---
layout: post
title:  "dbfileupload is dead - long live v1/packages! A new packages API endpoint for Jamf Pro"
comments: true
---

Jamf announced in the [11.4.0 Release Notes][1] that the undocumented and unsupported `dbfileupload` endpoint will be discontinued in Jamf Pro 11.6.0, along with support for the Jamf Admin application:

> Jamf Admin—Support for Jamf Admin will be discontinued with the release of Jamf Pro 11.6.0 (estimated release date: June 2024). The Jamf Admin app has been removed from the Jamf Pro Apps DMG as of Jamf Pro 11.4.0. Older versions of Jamf Admin will continue to work with Jamf Pro until all functionality and endpoints associated with Jamf Admin are removed in Jamf Pro 11.6.0. In addition, Jamf Admin content has been removed from documentation.

Although it was never officially supported, the `dbfileupload` API endpoint was used in many scripts and tools coming from the community to upload packages to any cloud-based Distribution server, whether it was Jamf's Cloud Distribution Service (JCDS), or a cloud distribution point hosted on Amazon S3, Rackspace or Akamai.

## Aren't there existing alternatives?

Alternative API endpoints for uploading to JCDS was introduced with Jamf Pro 10.49.0, although it required the JCDS to be upgraded to JCDS 2.0, something that has been ongoing for Jamf Premium Cloud customers - see my blog post ["Introducing JCDS 2.0"][2]. It is more complex to use than the `dbfileupload` endpoint as it requires the installation of a tool to communicate directly with an Amazon AWS S3 bucket, such as the `aws-cli` binary or the python `boto3` module.

Similarly, it's always been possible to upload directly to a third-party cloud DP hosted on AWS, Rackspace or Akamai using those vendors' tools, and then update the package metadata in Jamf Pro using the Classic API, although not many community tools and scripts have supported this. For example, I recently described a way of uploading to AWS in my blog post ["Scripting the upload of packages to Jamf Pro with a Cloud Distribution Point located on an Amazon Web Services S3 Bucket"][3].

## Introduction to the official "packages" API endpoint

Introduced with Jamf Pro 11.5.0, the new `packages` API endpoint can be used to upload packages to any cloud DP, agnostic to whether the service is JCDS, AWS, Akamai or Rackspace.

The new endpoint is part of the Jamf Pro API, and is a replacement for the `JSSResource/packages` endpoint of the Classic API. The Classic API endpoint remains functional, as is the `v1/jcds` endpoint introduced in 10.49.0, so scripts and tools using these endpoints do not need to be updated right away. However, since the new endpoint is simpler, has no dependencies, and works across all cloud DPs, anyone who has not yet migrated their scripts from the deprecated `dbfileupload` endpoint will want to use this.

## Uploading a package with the v1/packages endpoint

To upload a package to a Cloud Distribution Point , we require the following steps:

1. Obtain a bearer or OAuth token for the Jamf Pro API
2. Check for an existing package item in Jamf Pro
3. If replacing an existing package, upload package metadata to Jamf Pro
4. Upload the new package

> NOTE: Jamf requires bundle-style installer packages (which are actually folders) to be zipped prior to upload. Most packages are flat packages which are a single archive file and do not need zipping up. Only a very few vendors still provide bundle-style packages, such as Adobe's Creative Cloud apps. The Jamf Pro admin console will perform the zip automatically when fed a bundle-style package. `JamfPackageUploader` for AutoPkg also zips up packages as required. The shell scripts I present here do not, so you will need to zip up the package prior to uploading it.

### Step 2 - obtaining a Bearer Token

This step is common to all Jamf Pro API queries so should be familiar to anyone who has written a script to interact with the Jamf Pro API. The endpoint is `/api/v1/auth/token`. No special privileges are required to access this endpoint.

The following example outputs the response to a file. Instead you could output to stdout and wrap the curl command into a variable.

First let's define some variables we'll need to use. Note that I like to output the token to a file so that it can be used by multiple runs of the same (or other) scripts:

```bash
pkg_path="/path/to/my.pkg"
pkg=$(basename "$pkg_path")
pkg_dir=$(dirname "$pkg_path")
url="https://my.jamf.pro.server"
token_file="/tmp/token.json"
curl_output_file="/tmp/output.txt"
```

Now let's get the token. If using the traditional method of obtaining a Bearer Token using Basic Authentication, use the method below, supplying the `$user` and `$password` values directly (`curl` handles encoding of these values into base64, so there is no need to do that in a separate step).

```bash
# post the request to the token-issuing endpoint
curl --request POST \
    --url "$url/api/v1/auth/token" \
    --user "$user:$password" \
    --header 'Accept: application/json' \
    --output "$token_file"

# extract the token from the JSON response
token=$(plutil -extract token raw "$token_file")
```

If you prefer to use an API Client Secret to obtain the token, use the following request. You will need to populate the `$client_id` and `$client_secret` values as obtained from the Jamf Pro GUI:

```bash
# post the request to the token-issuing endpoint
curl --request POST \
    --url "$url/api/oauth/token" \
    --data-urlencode "client_id=$client_id" \
    --data-urlencode "grant_type=client_credentials" \
    --data-urlencode "client_secret=$client_secret" \
    --header 'Accept: application/json' \
    --output "$token_file"

# extract the token from the JSON response
token=$(plutil -extract access_token raw "$token_file")
```

### Step 2 - check if there is an existing package in Jamf Pro

First of all we want to see if there's an existing package object in Jamf. We can use the new endpoint for this. Note that we have to encode the package name for injection into the request URL.

```bash
pkg_name_encoded="$( echo "$pkg" | sed -e 's| |%20|g' | sed -e 's|&amp;|%26|g' )"

curl --request GET \
    --header "authorization: Bearer $token" \
    --header 'Accept: application/json' \
    "$url/api/v1/packages/?filter=packageName%3D%3D%22$pkg_name_encoded%22" \
    --location \
    --output "$curl_output_file"
```

If we get a response, we can determine whether there is a matching package by getting the `totalCount` value:

```bash
pkg_count=$(plutil -extract totalCount raw -expect integer "$curl_output_file")
```

And if the `$pkg_count` value is greater than 0, we can obtain the ID of the package like this:

```bash
pkg_id=$(plutil -extract results.0.id raw -expect string "$curl_output_file")
```

If `$pkg_count` is 0, however, then we are dealing with a new package.

### Step 3 - upload the package metadata to Jamf Pro

With the new `packages` endpoint, we need to tell Jamf Pro about the package *before* we upload it, so we upload the package metadata first. There are a bunch of variables you can add to the package metadata such as category, info, etc. Here we give the bare minimum required for the response to be accepted - if any of the following keys are omitted, the request will fail.

Note that we're using the `pkg_id` key from earlier to determine whether we are replacing an existing package's metadata or posting a new one. If there was no existing package, then we post to the `packages` endpoint without an ID.

```bash
# put the required variables into a single string using a heredoc
read -d '' -r data_json <<JSON
{
    "packageName": "$pkg",
    "fileName": "$pkg",
    "categoryId": "-1",
    "priority": 3,
    "fillUserTemplate": false,
    "uninstall": false,
    "rebootRequired": false,
    "osInstall": false,
    "suppressUpdates": false,
    "suppressFromDock": false,
    "suppressEula": false,
    "suppressRegistration": false
}
JSON

echo "Posting the package metadata to the server"
if [[ $pkg_id -gt 0 ]]; then
    req="PUT"
    jss_url="$url/api/v1/packages/$pkg_id"
else
    req="POST"
    jss_url="$url/api/v1/packages"
fi

curl --request "$req" \
    --header "authorization: Bearer $token" \
    --header 'Content-Type: application/json' \
    --header 'Accept: application/json' \
    --data "$data_json" \
    "$jss_url" \
    --location \
    --output "$output_file_record"
```

We get the ID of the package object as follows:

```bash
pkg_id=$(plutil -extract id raw -expect string "$output_file_record")
```

### Step 4 - upload the package

Assuming that we have determined that we need to upload the package, this is done as the final step, since we always need to supply the ID of the package metadata object. This is always done as a `POST` operation. Any existing package will be replaced.

```bash
curl --request "POST" \
    --location \
    --header "authorization: Bearer $token" \
    --header 'Content-Type: multipart/form-data' \
    --header 'Accept: application/json' \
    --form "file=@$pkg_path" \
    "$url/api/v1/packages/$pkg_id/upload"
```

And that's it! There could be a short period where the package appears as "Availability Pending" in the GUI, but in my tests, the package can still be installed.

I won't cover it here, but if you need to add a manifest to the package, you can do that with a `POST` request to the `v1/packages/$pkg_id/manifest` endpoint, with the file posted as `multipart/form-data` as above.

## Complete script

I have prepared a complete shell script for uploading a package.

- [Click here to see the shell script][4].

## What about JamfPackageUploader?

For those of you familiar with using the AutoPkg processor `JamfPackageUploader`, a new `pkg_api_mode` argument has now been added, which uses the same method as described above. This is set as the default mode for Jamf Pro servers running 11.5.0 or above, or can be explicitly set. Anyone running 11.5.0 or above and using the existing `jcds2_mode` or `aws_cli_mode` can remove the key from their preferences to enabled `pkg_api_mode`.

## Deleting Packages

Deleting packages is now straightforward, as deleting the metadata will remove the package itself. You first need to determine the ID of the package, as shown in Step 2.

```bash
curl --request DELETE \
    --location \
    --header "authorization: Bearer $token" \
    --header 'Accept: application/json' \
    "$url/api/v1/packages/$pkg_id"
```

It is now also possible to delete multiple packages in one operation. To do this, supply the package IDs in a JSON file. You should first check that each ID is a valid package:

```bash
read -d '' -r data_json <<JSON
{
  "ids": [
    "1",
    "2",
    "4",
    "8"
  ]
}
JSON

curl --request POST \
    --location \
    --header "authorization: Bearer $token" \
    --header 'Accept: application/json' \
    --data "$data_json" \
    "$url/api/v1/packages/delete-multiple"
```

## Exporting a list of packages information

You can get a list of all the packages in CSV format using the new `export` endpoint. The following example shows the bare minimum fields of ID and name.

```bash
read -d '' -r data_json <<JSON
{
  "page": 0,
  "pageSize": 100,
  "sort": [
    "id:asc"
  ],
  "filter": "",
  "fields": [
    {
      "fieldName": "id",
      "fieldLabelOverride": "Package ID"
    },
    {
      "fieldName": "packageName",
      "fieldLabelOverride": "Package Name"
    }
  ]
}
JSON

curl --request POST \
    --location \
    --header "authorization: Bearer $token" \
    --header 'accept: text/csv' \
    --header 'Content-Type: application/json' \
    --data "$data_json" \
    "$url/api/v1/packages/export" \
    --output "/path/to/file.csv"
```

## Downloading packages from the Cloud DP

The new packages endpoint does not expose the URL of the package for download, but for JCDS 2, the `v1/jcds` endpoint can be used for this. See Rich Trouton's blog post ["Updated scripts for downloading packages from a JCDS2 distribution point"][5] for details on how to do this.

## Conclusion

Good luck with your testing and let me know if you find any problems. I have not attempted to find a solution for the other supported type of third party cloud distribution points, namely Rackspace and Akamai, but if those services offer a command line interaction tool, it should be easy to substitute the `aws s3` commands for something appropriate for that service. The rest of the workflow would be the same.

[1]: https://learn.jamf.com/en-US/bundle/jamf-pro-release-notes-current/page/Deprecations_and_Removals.html
[2]: https://grahamrpugh.com/2023/08/21/introducing-jcds2.html
[3]: https://grahamrpugh.com/2024/03/06/uploading-packages-to-aws-cdp.html
[4]: https://gist.github.com/grahampugh/ba31b7dd140ec3cd75a481c89d31201b
[5]: https://derflounder.wordpress.com/2024/03/28/updated-scripts-for-downloading-packages-from-a-jcds2-distribution-point/

{% include urls.md %}
