---
layout: post
title:  "Scripting the upload of packages to Jamf Pro with a Cloud Distribution Point located on an Amazon Web Services S3 Bucket"
comments: true
---

If you maintain a Jamf Pro server that has a Cloud Distribution Point located on an Amazon Web Services S3 Bucket, you typically either use the Jamf Pro admin user interface to upload packages, or the Jamf Admin app. This post is concerned with how to upload a package using a script, using Jamf's Classic API and the AWS command line interface tools (`aws-cli`).

## Introduction to the workflow for uploading a package via the API

To upload a package to a Jamf Pro Cloud Distribution Point hosted on AWS S3, we require the following steps:

1. Install the `aws-cli` tools and configure them to point to your S3 bucket
2. Obtain a Bearer Token for the Jamf Pro Classic API
3. Check for an existing package item in Jamf Pro
4. If replacing an existing package, sync the package to the S3 bucket
5. Upload package metadata to Jamf Pro

> NOTE: Jamf requires bundle-style installer packages (which are actually folders) to be zipped prior to upload. Most packages are flat packages which are a single archive file and do not need zipping up. Only a very few vendors still provide bundle-style packages, such as Adobe's Creative Cloud apps. The Jamf Pro admin console will perform the zip automatically when fed a bundle-style package. `JamfPackageUploader` for AutoPkg also zips up packages as required. The shell scripts I present here do not, so you will need to zip up the package prior to uploading it.

### Step 1 - install and configure the aws-cli tools

The easiest way to interact with an S3 bucket from a shell script is to install the [aws-cli][1] tool as an installer package, available from [https://aws.amazon.com/cli/][1].

To configure the tools to point to your S3 bucket, type `aws configure` to begin an interactive session. This only has to be done once. Provide your AWS Access Key ID, Secret Access Key, and optionlly provide a default region and an output format.

    % aws configure
    AWS Access Key ID [****************Z344]: 
    AWS Secret Access Key [****************/Gy7]: 
    Default region name [us-east-1]: 
    Default output format [json]: 

### Step 2 - obtaining a Bearer Token

This step is common to all Jamf Pro API queries so should be familiar to anyone who has written a script to interact with the Jamf Pro API. The endpoint is `/api/v1/auth/token`. No special privileges are required to access this endpoint.

The following example outputs the response to a file. Instead you could output to stdout and wrap the curl command into a variable.

First let's define some variables we'll need to use:

```bash
pkg_path="/path/to/my.pkg"
pkg=$(basename "$pkg_path")
pkg_dir=$(dirname "$pkg_path")
url="https://my.jamf.pro.server"
token_file="/tmp/token.json"
curl_output_file="/tmp/output.txt"
s3_bucket="myjamfpros3bucketname"
```

Now let's get the token. Note that here we are using the traditional method of obtaining a Bearer Token using Basic Authentication. If you prefer to use an API Client Secret to obtain the token, please adjust this step accordingly. All subsequent steps will be the same.

```bash
# encode the credentials into base64
credentials=$(printf "%s" "$user:$pass" | iconv -t ISO-8859-1 | base64 -i -)

# post the request to the token-issuing endpoint
curl --request POST \
    --header "authorization: Basic $credentials" \
    --url "$url/api/v1/auth/token" \
    --header 'Accept: application/json' \
    --output "$token_file"

# extract the token from the JSON response
token=$(plutil -extract token raw "$token_file")
```

### Step 3 - check if there is an existing package in Jamf Pro

First of all we want to see if there's an existing package object in Jamf. We use the Classic API for this. Don't forget that if the package name has any funky characters in it - or spaces - these will need to be escaped for any of the URLs that contain the name.

```bash
curl --request GET \
    --header "authorization: Bearer $token" \
    --header 'Accept: application/json' \
    "$url/JSSResource/packages/name/$pkg" \
    --output "$curl_output_file"
```

If we get a response, we can extract the package ID for later.

```bash
pkg_id=$(plutil -extract package.id raw -expect integer "$curl_output_file")
```

### Step 4 - sync the package to the S3 bucket

Thanks to the `sync` feature of the `aws-cli` tools, we don't need to check whether the package already exists on the S3 bucket, we can just send a sync command and if there is no existing package of this name, or the local package is different from the one on the server, then it will be replaced, otherwise it will be left alone.

```bash
aws s3 sync "$pkg_dir/" "s3://$s3_bucket/" --exclude "*" --include "$pkg"
```

> Note: I have found that in a very limited set of circumstances, using this method (`aws s3 sync`) to upload a single file will fail. This appears to happen due to specific other content in the folder that the package is placed. If you find that it fails, move the package into its own folder or an alternative, less "noisy", location. Or feel free to use `aws s3 cp "$pkg" "s3://$s3_bucket/"` instead. I just prefer the `sync` command as it builds in a check as to whether the package needs to be replaced or not.

### Step 5 - upload the package metadata to Jamf Pro

Now we need to tell Jamf Pro about the package, so we upload the package metadata to the Classic API `packages` endpoint. There are a bunch of variables you can add to the package metadata such as category, info, etc. Here we give the bare minimum: name and filename.

Note that we're using the `pkg_id` key from earlier to determine whether we are replacing an existing package's metadata or posting a new one.

```bash
pkg_data="<package>
    <name>$pkg</name>
    <filename>$pkg</filename>
</package>"

echo "Posting the package metadata to the server"
if [[ $pkg_id -gt 0 ]]; then
    req="PUT"
else
    req="POST"
fi

curl --request "$req" \
    --header "authorization: Bearer $token" \
    --header 'Content-Type: application/xml' \
    --data "$pkg_data" \
    "$url/JSSResource/packages/id/$pkg_id" \
```

And that's it! There could be a short period where the package appears as "Availability Pending" in the GUI, but in my tests, the package can still be installed.

## Complete script

I have prepared a complete script for uploading a package in shell.

- **Shell:** [Click here to see the shell script][2].

## What about JamfPackageUploader?

If you are familiar with using the AutoPkg processor `JamfPackageUploader`, a new `aws_cdp_mode` has now been added, which uses the same method as described above.

Note that `aws_cdp_mode` requires the use of the `aws-cli` tools described above. To ensure that you can use `aws_cdp_mode`, please follow the installation and configuration instructions described above. You will also need to provide the S3 bucket name using the `S3_BUCKET_NAME` key.

## Conclusion

Good luck with your testing and let me know if you find any problems. I have not attempted to find a solution for the other supported type of third party cloud distribution points, namely Rackspace and Akamai, but if those services offer a command line interaction tool, it should be easy to substitute the `aws s3` commands for something appropriate for that service. The rest of the workflow would be the same.

[1]: https://aws.amazon.com/cli/
[2]: https://gist.github.com/grahampugh/962fe352676635e179e9ff219e04d0e5

{% include urls.md %}
