---
layout: post
title:  "Introducing JCDS 2.0 for uploading packages to Jamf Pro Cloud distribution points"
comments: true
---

🎉🥳🍾🪅 **Jamf Pro is introducing a new and official API endpoint for uploading packages to the Jamf Cloud Distribution Point.** 🎉🥳🍾🪅

This promises to provide Jamf Pro Cloud customers with a reliable method for uploading packages. This blog post explains what you need to know in order to set up scripts that will perform these updates.

The change happens when Jamf switch over customers' instances to JCDS 2.0. Jamf has informed standard customers in the US regions that they are enabling JCDS2 starting on 26 August 2023. Upgrades to JCDS2 are happening on a regionalized basis and Jamf is communicating upgrades directly to customers.

Having advocated for this for many years, my `JamfPackageUploader` processor for AutoPkg is embracing this new endpoint for JCDS users. A new `jcds2_mode` has now been added to use this endpoint. The former `jcds_mode` method, which used the unofficial "v3" API, no longer works for Jamf Cloud instances that have been switched over to JCDS 2. During the transition period, admins will have to select the appropriate mode for their instance.

Once all regions have been transitioned, I will remove `jcds_mode`, and `jcds2_mode` will become the default. I'll explain that in a future blog post.

## Introduction to the workflow for uploading a package via the API

To upload a package to the new Jamf Pro Cloud Distribution Service requires the following steps:

1. Obtain a Bearer Token
2. Check for an existing package item in Jamf Pro
3. Check for an existing package in the JCDS S3 bucket
4. Obtain credentials for the package upload endpoint
5. Upload the package to the package upload endpoint
6. Upload package metadata to Jamf Pro

That last part is important as it differs from previous methods of uploading package to Jamf Cloud. In fact, it more closely resembles the workflow for uploading packages to a local file share distribution point.

## Step 1 - obtaining a Bearer Token

This step is common to all Jamf Pro API queries so should be familiar to anyone who has written a script to interact with the Jamf Pro API. The endpoint is `/api/v1/auth/token`. No special privileges are required to access this endpoint.

The following example outputs the response to a file. Instead you could output to stdout and wrap the curl command into a variable.

First let's define some variables we'll need to repeat:
```bash
pkg="$pkg"
pkg_path="/path/to/$pkg"
url="$url"
token_file="/tmp/token.json"
curl_output_file="/tmp/output.txt"
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

Note that starting from Jamf Pro 10.49.0, you can altwernatively obtain a bearer token using new API Clients, but to avoid this post getting too complicated, I'll leave that for another blog post.

## Step 2 - check if there is an existing package in Jamf Pro

First of all we want to see if there's an existing package object in Jamf. We use the Classic API for this. Don't forget that if the package name has any funky characters in it - or spaces - these will need to be escaped for any of the URLs that contain the name.

```bash
curl --request GET \
    --header "authorization: Bearer $token" \
    --header 'Accept: application/json' \
    "$url/JSSResource/packages/name/$pkg" \
    --output "$curl_output_file"
```

If we get a response, we can get the package ID for later.

```bash
pkg_id=$(plutil -extract package.id raw -expect integer "$curl_output_file")
```

## Step 3 - check if there is an existing package in the JCDS

Now we can check if that package is also present in the JCDS.

```bash
curl --request GET \
    --header "authorization: Bearer $token" \
    --header 'Accept: application/json' \
    "$url/api/v1/jcds/files" \
    --output "$curl_output_file"
```

We need to iterate through this list to see if our package name is already in the list. To do this I convert the json to a plist so we can use PlistBuddy to extract the file name. We use grep to figure out how many packages are in the list, and then iterate through the list with a for loop.

```bash
# convert the list to a plist so we can actually work with it in bash
plutil -convert xml1 "$curl_output_file"

# count the number of items in the list
pkg_count=$(grep -c fileName "$curl_output_file")

# loop through each item in the JSON response
jcds_pkg=""
jcds_pkg_md5=0  # assign empty value to avoid errors
for ((i=1; i<=pkg_count; i++)); do
    jcds_pkg=$(/usr/libexec/PlistBuddy -c "Print :$i:fileName" "$curl_output_file")
    if [[ "$jcds_pkg" == "$pkg" ]]; then
        jcds_pkg_md5=$(/usr/libexec/PlistBuddy -c "Print :$i:md5" "$curl_output_file")
        break
    fi
done
```

Note that I've grabbed the MD5 hash data of the matching package. We can use this to compare with the local package we want to upload. If it's the same, then there's really no need to upload it again. If using python or another language, you can use the superior SHA3_512 hash instead of the MD5, but there's no built-in method of using this in bash/zsh.

```bash
# also find out the md5 hash of the local package
pkg_md5=$(md5 -q "$pkg_path")

if [[ "$jcds_pkg_md5" == "$pkg_md5" ]]; then
    echo "MD5 matches so not replacing existing package on JCDS"
    replace_jcds_pkg=0
else
    echo "MD5 hash doesn't match. Replacing existing package on JCDS"
    replace_jcds_pkg=1
fi
```

If we need to replace the package, we should delete it and then we can upload the new one.

```bash
curl --request DELETE \
    --header "authorization: Bearer $token" \
    --header 'Accept: application/json' \
    "$url/api/v1/jcds/files/$pkg" \
```

## Step 4 - obtain the session token for the package upload endpoint

The JCDS is an Amazon AWS S3 bucket to which the Jamf Pro API grants access by generating a session token. `Create` privileges to the new `Create Jamf Content Distribution Server Files` privileges set are required.

```bash
curl --request POST \
    --silent \
    --header "authorization: Bearer $token" \
    --header 'Accept: application/json' \
    "$url/api/v1/jcds/files" \
    --output "$curl_output_file"
```

This returns JSON with the following keys:

```json
"Credentials": [
    "accessKeyID": "TESTYBLF477T5THW6BNN",
    "expiration": 1678386302,
    "secretAccessKey": "tEstNvpw2AC9mggf08/Yw7krkPfYxWNoByGClLr7",
    "sessionToken": "TEsTb3JpZ2luX2VjEKr//////////wEaCXVzLWVhc3QtMS==",
    "region": "us-east-1",
    "bucketName": "sbox-test-bucket",
    "path": "tmp/fc041b05-516e-4bde-9882-a08b1cc5473c/",
    "uuid": "fc041b05-516e-4bde-9882-a08b1cc5473c"
]
```

We need to extract some keys from the JSON output to use in the next step. How you do this is down to code language and preference. In this example, I'll use plutil.

```bash
default_access_key=$(plutil -extract accessKeyID raw "$curl_output_file")
default_secret_key=$(plutil -extract secretAccessKey raw "$curl_output_file")
aws_session_token=$(plutil -extract sessionToken raw "$curl_output_file")
region=$(plutil -extract region raw "$curl_output_file")
s3_bucket=$(plutil -extract bucketName raw "$curl_output_file")
s3_path=$(plutil -extract path raw "$curl_output_file")
```

## Step 5 - uploading the package to the JCDS

To perform the upload, we need to interact with the Amazon S3 bucket directly. The easiest way to do this from a shell script is to install the [aws-cli][1] tool.

Once that is installed, we can use the variables from the previous step to configure the aws tool and upload the package.

```bash
    # add the configuration to the aws-cli config file
    aws configure set aws_access_key_id "$default_access_key"
    aws configure set aws_secret_access_key "$default_secret_key"
    aws configure set aws_session_token "$aws_session_token"
    aws configure set default.region "$region"

    # post the package
    aws s3 cp "$pkg_path" "s3://$s3_bucket/$s3_path"
```

## Step 6 - uploading the package metadata to Jamf Pro

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

## Conclusion

That's it! There are a few gotchas to work through with this workflow - it's certainly more complex than the old `dbfileupload` endpoint - but it should be more reliable. And it's officially supported for the first time!

One thing I've noticed is that if you don't check whether there's an existing package and you upload it again, you get a duplicate file with an amended filename. For example if `$pkg` already exists, you'll get `MyPackage_1.pkg`. That's why I emphasise looking for an existing package in the example above before attempting the upload. I sense that it will be worth checking for these duplicates every now and again. This will need to be done with the API, as shown in Step 3 above.

Good luck with your testing and let me know if you find any problems, or discover any refinements that could be made.

[1]: https://aws.amazon.com/cli/

{% include urls.md %}
