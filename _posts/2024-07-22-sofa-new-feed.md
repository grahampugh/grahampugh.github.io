---
layout: post
title:  "If you're using the SOFA feed, please take note!"
comments: true
---

![SOFA logo](https://sofa.macadmins.io/images/custom_logo.png)

Back in April I [posted][1] about [SOFA], short for "Simple Organized Feed for Apple Software Updates", which consists of a machine-readable feed and user-friendly web interface, providing always-up-to-date information on XProtect data, OS updates, and associated patched CVEs.

SOFA is hosted by the Mac Admins Open Source organisation, but it can be hosted in an organisation's own infrastructure, allowing a high level of control over the information if your organisation requires it.

## What's new?

The SOFA project has been a huge success, so much so that the amount of web traffic it has generated has exceeded all expectations. We have been investigating ways to reduce the amount of traffic, while maintaining the same great service. This is especially important since the release of [Nudge 2.0][2] last week, which now utilises the SOFA feed, giving new opportunities to simplify the administration of the app.

So, we have made some changes in the Extension Attribute scripts we [provided in the SOFA project's GitHub repo][3], and if you are using those scripts, we are asking you to use the new versions of these scripts in your Jamf Pro instances.

Furthermore, if you have crafted your own scripts or tools that take advantage of the SOFA feed, please take note of the following changes that you can and should make, to help reduce unnecessary costs for the Mac Admins Open Source organisation:

### New Feed URL

The macOS feed URL has changed to `https://sofafeed.macadmins.io/v1/macos_data_feed.json`. This allows the feed to use specific content encoding rules and ensure that everyone is using them. Please update any scripts that are using the old `sofa.macadmins.io` address of the json feed.

Note that the URL of the iOS feed has also changed, this is now `https://sofafeed.macadmins.io/v1/ios_data_feed.json`.

### Compression

`curl` offers a `--compressed` option which allows the file to be transferred as a gzipped version, saving extra bandwidth. This option is *required* for the new feed URL - the json feed file may not download properly without it.

### ETags

`curl` offers the option to interrogate ETags, which are a fingerprint of the feed, without having to download the whole file. We have updated the Extension Attribute scripts, and the OSQuery plugin hads also been updated to take advantage of ETags, so that the feed file is only fully downloaded when changes are detected.

If you wrote your own scripts, you can write the ETag to a file using curl. You can therefore check first if there is a cached ETag signature file already on disk, and if it is present, compare the remote file with the locally cached one using the `--etag-compare` option. If there is no ETag file on disk, or the ETag doesn't match, then you can go ahead and download the feed to disk and write the ETag to a file, by using the `--etag-save` option. Here's how that works in bash code:

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
    if /usr/bin/curl --compressed --silent --etag-compare "$etag_cache" "$online_json_url" --output /dev/null; then
        echo "Cached ETag matches online ETag - cached json file is up to date"
    else
        echo "Cached ETag does not match online ETag, proceeding to download SOFA json file"
        /usr/bin/curl --compressed --location --silent "$online_json_url" --etag-save "$etag_cache" --output "$json_cache"
    fi
else
    echo "No ETag cached, proceeding to download SOFA json file"
    /usr/bin/curl --compressed --location --silent "$online_json_url" --etag-save "$etag_cache" --output "$json_cache"
fi
```

## Conclusion

SOFA is still very new, so changes are inevitable as features are added, use cases grow, and problems are ironed out. We're glad you're part of the early adopters, and ask that you take a little time to ensure that you are using the latest feed and best practices. The old feed will be removed in a month or two to ensure that the old versions of these scripts are not used forever.

We also continue to recommend hosting a mirror of the feed for your own organisation if that's feasible.

[1]: https://grahamrpugh.com/2024/04/29/sofa-and-jamf-pro-new-feed.html
[2]: https://github.com/macadmins/nudge/releases/tag/v2.0.0.81713
[3]: https://github.com/macadmins/sofa/blob/main/tool-scripts

{% include urls.md %}
