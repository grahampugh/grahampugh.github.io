---
layout: post
title:  "If you're using the SOFA feed, update the URL!"
comments: true
---

## What is SOFA?

![SOFA logo](https://sofa.macadmins.io/images/custom_logo.png)

Back in April I [posted][1] about [SOFA], short for "Simple Organized Feed for Apple Software Updates", which consists of a machine-readable feed and user-friendly web interface, providing always-up-to-date information on XProtect data, OS updates, and associated patched CVEs .

SOFA is hosted by the Mac Admins Open Source organisation, but it can be hosted in an organisation's own infrastructure, allowing a high level of control over the information if your organisation requires it.

## What's new?

The SOFA project has been a huge success, so much so that the amount of web traffic it has generated has exceeded all expectatations. As the Mac Admins Open Source organisation is providing the service free, we have been investigating how to reduce the amount of traffic while maintaining a great service. This is especially important since the release of [Nudge 2.0][2] last week, which now utilises the SOFA feed to simplify the administration of that app.

So, there are now some changes in the extension attribute scripts [provided in the SOFA project's GitHub repo][3], and we are asking you to update any of these scripts in your Jamf Pro instances if you have used them. Additionally, if you have crafted your own scripts, please take note of the following changes that you can make to reduce the web traffic:

### New Feed URL

The feed URL has changed to `https://sofafeed.macadmins.io/v1/macos_data_feed.json`. This allows the feed to use specific content encoding rules and ensure that everyone is using them. Please update any scripts that are using the old `sofa.macadmins.io` address of the json feed

### Compression

`curl` offers a `--compressed` option which allows the file to be transferred as a gzipped version, saving extra bandwidth. So, please add this option to your `curl` commands in your SOFA scripts.

### E-tags

`curl` offers the option to interrogate e-tags, which are a fingerprint of the feed, without having to download the whole file. We have updated the extension attribute scripts (and OSQuery plugin) to take advantage of e-tags, so that the feed file is only fully downloaded if it changes.

If you wrote your own scripts, you can write the e-tag to a file using curl. So, first, check if there is a cached e-tag signature file on disk, and if it is present, compare the remote file with the locally cached one using the `--etag-compare` option. If not, download the feed to disk and write the e-tag to a file by using the `--etag-save` option. Here's how:

```bash
# URL to the online JSON data
online_json_url="https://sofafeed.macadmins.io/v1/macos_data_feed.json"

# local store
json_cache_dir="/private/tmp/sofa"
json_cache="$json_cache_dir/macos_data_feed.json"
etag_cache="$json_cache_dir/macos_data_feed_etag.txt"

# ensure local store folder exists
/bin/mkdir -p "$json_cache_dir"

# check local vs online using etag (only available on macOS 12+)
if [[ -f "$etag_cache" && -f "$json_cache" ]]; then
    if /usr/bin/curl --compressed --silent --etag-compare "$etag_cache" --header "User-Agent: $user_agent" "$online_json_url" --output /dev/null; then
        echo "Cached e-tag matches online e-tag - cached json file is up to date"
    else
        echo "Cached e-tag does not match online e-tag, proceeding to download SOFA json file"
        /usr/bin/curl --compressed --location --max-time 3 --silent --header "User-Agent: $user_agent" "$online_json_url" --etag-save "$etag_cache" --output "$json_cache"
    fi
else
    echo "No e-tag cached, proceeding to download SOFA json file"
    /usr/bin/curl --compressed --location --max-time 3 --silent --header "User-Agent: $user_agent" "$online_json_url" --etag-save "$etag_cache" --output "$json_cache"
fi
```

## Conclusion

SOFA is still very new, so chagnes are inevitable as features are added, use cases grow, and problems are ironed out. We're glad you're part of the early adopters, and ask that you take a little time to ensure that you are using the latest feed and best practices. The old feed will be removed in a month or two to ensure that the old versions of these scripts are not used forever.

[1]: https://grahamrpugh.com/2024/04/29/sofa-and-jamf-pro-new-feed.html
[2]: https://github.com/macadmins/nudge/releases/tag/v2.0.0.81713
[3]: https://github.com/macadmins/sofa/blob/main/tool-scripts

{% include urls.md %}
