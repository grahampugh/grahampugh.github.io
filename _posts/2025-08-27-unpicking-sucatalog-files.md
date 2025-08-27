---
layout: post
title:  "Unpicking Apple's Software Update Catalog Files"
comments: true
---

## Introduction to the sucatalog file

For many years, Apple have published software update product information via "sucatalog" files. These files have traditionally been used by the macOS system for information on available updates, including by the `softwareupdate` command. These catalog files have included information on many types of software updates, including "full" macOS installer applications, core apps, iMovie and iWork apps, plugins and drivers, and many more.

I don't pretend to be an expert on the history of these files, but it seems from their naming that the concept started around the time of macOS 10.5, or Leopard. Here's the URL of the latest `sucatalog` file that is used on macOS 15 systems:

[https://swscan.apple.com/content/catalogs/others/index-15-14-13-12-10.16-10.15-10.14-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog](https://swscan.apple.com/content/catalogs/others/index-15-14-13-12-10.16-10.15-10.14-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog)

I can only speculate as to how this URL evolved, but it's been consistent for many major OS releases now, as this compilation of the past few shows:

    https://swscan.apple.com/content/catalogs/others/index-15-14-13-12-10.16-10.15-10.14-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog
    https://swscan.apple.com/content/catalogs/others/index-14-13-12-10.16-10.15-10.14-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog
    https://swscan.apple.com/content/catalogs/others/index-13-12-10.16-10.15-10.14-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog
    https://swscan.apple.com/content/catalogs/others/index-12-10.16-10.15-10.14-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog
    https://swscan.apple.com/content/catalogs/others/index-10.16-10.15-10.14-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog
    https://swscan.apple.com/content/catalogs/others/index-10.15-10.14-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog

It's also interesting that each catalog is maintained going all the way back to Leopard, I suspect because the name is baked into each macOS major version's system somewhere. Indeed, the OG catalog [https://swscan.apple.com/content/catalogs/others/index-leopard.merged-1.sucatalog](https://swscan.apple.com/content/catalogs/others/index-leopard.merged-1.sucatalog) is still being served, and when I looked at it while writing this post, was updated today, though the most recent software update listed in the file is for the Motion app, posted October 23, 2019.

It's quite well known that there are catalogs containing information about beta releases of Apple Software, too. Typically, the URL for these "seed" catalogs includes an extra layer after `index-` and before the first macOS version, matching that version and adding `seed` or `beta`, referring (I think) to AppleSeed and Developer Seed releases. For example, the URL for software updates relating to the macOS 15 AppleSeed program are in the following URL:

    https://swscan.apple.com/content/catalogs/others/index-15seed-15-14-13-12-10.16-10.15-10.14-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog

The URL for software updates relating to macOS Tahoe developer program is as follows:

    https://swscan.apple.com/content/catalogs/others/index-26beta-26-15-14-13-12-10.16-10.15-10.14-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog.gz

## Diving into the files

The `sucatalog` files are sometimes served as gzipped files, as we saw above. That's helpful, because they are very large files. That first sucatalog file for Leopard is currently 1 MB in size. The gzipped "26beta" sucatalog file is 508 KB, but unzips to 7 MB. What's inside them to make them so large? Put simply, a lot of different software updates are still available... That latter catalog has 98,229 lines!

Let's look briefly at what's inside. Despite the `sucatalog` file suffix, these files are, as often with Apple, Property List files (PLIST) - an XML-compliant format. They consist of just four top-level keys: 

* `CatalogVersion` (always `2`)
* `ApplePostURL` (always an empty value)
* `IndexDate` (in the format `2025-08-26T21:31:52Z`, and seemingly being updated daily)
* `Products`. `Products` is a dictionary of available products.

Each entry in the `Products` dictionary consists of the following keys:

* A product ID, in the form of a 3-digit number, followed by a dash, followed by a four- or five-digit number. For example, `061-1955` refers to a DVD Player update from 2005, and `093-27146` refers to an XProtect Plist Configuration Data release from 26 August, 2025.
* `ServerMetadataURL`, a URL for a metadata file ending in `.smd`.
* `Packages`, an array consisting of a dictionary of entries, each of which contains a `URL` key, the value of which is the URL of the available `.pkg` file for this product; a `MetadataURL` key, which links to a `.pkm` file, which is an XML file with some interesting metadata regarding the package, such as its version string (`CFBundleShortVersionString`); the package `Size`; and a `Digest` value (I'm going to guess this is a hash value).
* `PostDate`, when this product was posted.
* `Distributions`, a dictionary listing any number of languages with URLs pointing to `.dist` files, which also provide additional information about the product.

Products which are macOS full installers have additional keys in their `Products` dictionary:

* `DeferredSUEnablementDate`, a date that you would imagine would be some date later than the post date, but I can't confirm that from the entries I took a look at.
* `ExtendedMetaInfo`, which is added in place of `ServerMetadataURL` for these entries, and contains a dictionary consisting of one entry, `InstallAssistantPackageIdentifiers`, itself a dictionary of bundle identifiers for components of the full installer package.

Without delving forever further into the contents of the file, I'm now going to concentrate only on the full macOS installers that are listed in the `Products` dictionary. Firstly, how do we identify that the product is a full macOS installer?

Until 2020, I think up until Monterey - the final Intel-only release - the release included a DMG installer, `BaseSystem.dmg`, amongst other files. The `InstallAssistantPackageIdentifiers` dictionary contained an `OSInstall` key (`com.apple.mpkg.OSInstall`), and an `InstallInfo` key (`com.apple.plist.InstallInfo`). 

From Big Sur onwards, this all changed as Apple Silicon devices came into play. The release started to include an `InstallAssistant.pkg` package, which contains the full installer application, as well as packages relating to firmware and installer information.

## Using information from sucatalog files to download full macOS installers

As the main author of [erase-install], a script for downloading full macOS installers and using them to update, reinstall or erase macOS systems, I've been using other Mac Admin's projects to read the sucatalog files. Originally, I adapted Greg Neagle's [installinstallmacos.py] python script for this purpose, and latterly - when python stopped being bundled with macOS by default - switched to using Nindi Gill's [mist-cli] swift command line tool to do it. I also included an alternative method, which uses the built in `softwareupdate --list-full-installers` and `softwareupdate --fetch-full-installer` commands, though these commands have had their issues over the years so never commanded the same level of confidence as the third party tools.

I've started looking into the sucatalog files myself because `mist-cli` is currently having an issue with obtaining the installers on systems running macOS 15.6 or newer, and I didn't want users of the script to be left in the lurch. The issue with `mist-cli` is not related to any change to the contents of the sucatalog files, but rather due to some change in the way the `installer` binary handles the `.dist` files that are obtained using the URLs in the `.sucatalog` files (or, I should say, how it doesn't handle them any more...). 

Both `mist-cli` and `installinstallmacos.py` use these `.dist` files to compile an distribution package which consists of not just the `InstallAssistant.pkg` package, but other items which have not proved necessary (as far as I can tell) for the purposes of using the full installers in the way that `erase-install` uses them. Indeed, to solve the issue compiling these packages on newer systems, Greg Neagle has made an update to `installinstallmacos.py` which instead just takes the `InstallAssistant.pkg` package and nothing else.

Faced with potentially pivoting back to bundling in a python distribution with erase-install and using my fork of `installinstallmacos.py` once again, I first wanted to see if I could build a way of obtaining the same information as `mist-cli` and `installinstallmacos.py` using only built-in commands. 

## Going down the rabbit hole

This process has been helped somewhat by the addition of `jq` to macOS from version 15 onwards, but we also have `PlistBuddy`, `plutil` and `xmllint` to help us, as well as `sed`, `awk`, `grep`, etc.

The information I required was as follows:

* Product ID - easy, we have this in the `sucatalog` file.
* URL of the `InstallAssistant.pkg` - also easy, it's right there too.
* Package size - we have this also.
* Release date - also there.
* Title of the release (e.g. macOS Sequoia)
* Version String (e.g. 15.6.1)
* Build String (e.g. 24G90)
* Compatibility information (which models the package will successfully install on)

For those last four items, we need to grab the Distribution file. So we need to iterate through the huge list of products in the `sucatalog` files, filter only those which contain an `InstallAssistant.pkg` URL, and grab the associated URL of the `.dist` file.

I first tried converting the entire sucatalog PLIST to JSON using `pliutil`, but this fails, as there are some keys that are not convertable to JSON.

Next, I tried extracting each `Product` dict using `plutil`, but this took forever so was unusable in practise.

The fastest method I found was to use `PlistBuddy` to obtain a list of Products. It's a bit hacky, but much faster than `plutil`, as follows:

```bash
products=$(/usr/libexec/PlistBuddy -c "Print :Products:" "$catalog_plist_path" | sed -n 's/^    \([0-9]\{3\}-[0-9]\{5\}\) = Dict {$/\1/p')
```

Using this list, I then tried to use `plutil` to convert each individual product dictionary to JSON:

```bash
package_plist=$(plutil -extract Products."$ia_product".Packages json -o - "$catalog_plist_path" 2>/dev/null)
```

This failed for no real reason - seems to be a bug. I was instead able to extract the individual product dict as XML1 (i.e. PLIST), and then convert it to JSON. Shrug emoji.

```bash
package_plist=$(plutil -extract Products."$ia_product".Packages xml1 -o - "$catalog_plist_path" 2>/dev/null)
package_json=$(echo "$package_plist" | plutil -convert json -o - - 2>/dev/null)
```

OK, now we can iterate through all the products, identify those that are macOS full installers, and grab the `InstallAssistant.pkg` URL and package size: 


```bash
ia_url=$(jq -r 'to_entries | map(select(.value.URL and (.value.URL | endswith("InstallAssistant.pkg")))) | .[0].value.URL // empty' <<< "$package_json" 2>/dev/null)
pkg_size_bytes=$(jq -r 'to_entries | map(select(.value.URL and (.value.URL | endswith("InstallAssistant.pkg")))) | .[0].value.Size // empty' <<< "$package_json" 2>/dev/null)
ia_pkg_size=$(bc <<< "scale=2; $pkg_size_bytes / 1024 / 1024 / 1024")
```

We can also grab the Post Date, and the `.dist` file URL from the Product dict, again using `plutil` because we couldn't convert to JSON at that level:

```bash
ia_post_date=$(plutil -extract Products."$ia_product".PostDate raw -o - "$catalog_plist_path" 2>/dev/null)
ia_post_date=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$ia_post_date" "+%Y-%m-%d" 2>/dev/null)
dist_file=$(plutil -extract Products."$ia_product".Distributions.English raw -o - "$catalog_plist_path" 2>/dev/null)
```

These `.dist` files are in XML format, where we can use `xmllint` to obtain the Display Name, Version String and Build String. The compatibility information is slightly more difficult, because it's contained in a C script embedded in the XML, so needs parsing with `grep`, `sed`, and `tr` (or `awk`). Note that Intel Macs have a "Board ID" with which you can test compatibility, whereas Apple Silicon Mac has a "Device ID":

```bash
ia_title=$(xmllint --xpath 'string(/installer-gui-script/title/text())' "$dist_xml" 2>/dev/null)
ia_build=$(xmllint --xpath "string(//dict/string[preceding-sibling::key[1]='BUILD']/text())" "$dist_xml" 2>/dev/null)
ia_version=$(xmllint --xpath "string(//dict/string[preceding-sibling::key[1]='VERSION']/text())" "$dist_xml" 2>/dev/null)
ia_supportedBoardIDs=$(grep "var supportedBoardIDs" "$dist_xml" 2>/dev/null | sed -E 's/.*\[\s*([^]]+)\].*/\1/' | tr -d "'")
ia_supportedDeviceIDs=$(grep "var supportedDeviceIDs" "$dist_xml" 2>/dev/null | sed -E 's/.*\[\s*([^]]+)\].*/\1/' | tr -d "'")
```

Finally, all the relevant information about each full macOS installer can be compiled into a nice JSON file, feeding the original `products` list from the first `PlistBuddy` command into an elaborate `jq` command:

```bash
jq -n \
    --arg product "$ia_product" \
    --arg post_date "$ia_post_date" \
    --arg url "$ia_url" \
    --arg title "$ia_title" \
    --arg build "$ia_build" \
    --arg version "$ia_version" \
    --arg pkg_size "$ia_pkg_size" \
    --arg compatible "$ia_compatible" \
    --argjson supported_board_ids "$(echo "$ia_supportedBoardIDs" | jq -R 'split(",") | map(ltrimstr(" ") | rtrimstr(" "))')" \
    --argjson supported_device_ids "$(echo "$ia_supportedDeviceIDs" | jq -R 'split(",") | map(ltrimstr(" ") | rtrimstr(" "))')" \
    '{
        product: $product,
        post_date: $post_date,
        url: $url,
        title: $title,
        build: $build,
        version: $version,
        pkg_size: $pkg_size,
        compatible: $compatible,
        supported_board_ids: $supported_board_ids,
        supported_device_ids: $supported_device_ids
    }' >> "$tmp_json_file"
```

And we can combine all the individual bits of JSON that were outputted to the `tmp_json_file` into one valid blob of JSON with the following "slurp" command:

```bash
jq -s '[.[] | select(type == "object")]' "$tmp_json_file" > "$installers_list_json_file"
```

Finally, for listing purposes, we can output to the terminal in a readable format with a bit more `jq` trickery:

```bash
    echo "┌────────────┬──────────────────┬─────────┬──────────┬──────────┬────────────┬────────────┐"
    echo "│ PRODUCT ID │ TITLE            │ VERSION │ BUILD    │ SIZE GB  │ DATE       │ COMPATIBLE │"
    echo "├────────────┼──────────────────┼─────────┼──────────┼──────────┼────────────┼────────────┤"

    jq -r 'sort_by(.version | split(".") | map(tonumber)) | reverse | .[] | [
        (.product // ""),
        (.title // ""),
        (.version // ""),
        (.build // ""),
        (.pkg_size // ""),
        (.post_date // ""),
        (.compatible // "")
    ] | @tsv' "$installers_list_json_file" | while IFS=$'\t' read -r ia_product ia_title ia_version ia_build ia_size ia_date ia_compatible; do
        printf "│ %-10s │ %-16s │ %-7s │ %-8s │ %-8s │ %-10s │ %-10s │\n" \
            "$ia_product" "$ia_title" "$ia_version" "$ia_build" "$ia_size" "$ia_date" "$ia_compatible"
    done
    echo "└────────────┴──────────────────┴─────────┴──────────┴──────────┴────────────┴────────────┘"
```

We get something like this:

```txt
┌────────────┬──────────────────┬─────────┬──────────┬──────────┬────────────┬────────────┐
│ PRODUCT ID │ TITLE            │ VERSION │ BUILD    │ SIZE GB  │ DATE       │ COMPATIBLE │
├────────────┼──────────────────┼─────────┼──────────┼──────────┼────────────┼────────────┤
│ 093-26142  │ macOS Tahoe Beta │ 26.0    │ 25A5349a │ 15.69    │ 2025-08-25 │ True       │
│ 093-10756  │ macOS Sequoia    │ 15.6.1  │ 24G90    │ 14.58    │ 2025-08-20 │ True       │
│ 082-08661  │ macOS Sequoia    │ 15.6    │ 24G84    │ 14.58    │ 2025-08-05 │ True       │
│ 082-44432  │ macOS Sequoia    │ 15.5    │ 24F74    │ 14.57    │ 2025-05-19 │ True       │
│ 082-33200  │ macOS Sequoia    │ 15.4.1  │ 24E263   │ 14.53    │ 2025-04-23 │ True       │
│ 082-16524  │ macOS Sequoia    │ 15.4    │ 24E248   │ 14.53    │ 2025-03-31 │ True       │
│ 082-04099  │ macOS Sequoia    │ 15.3.2  │ 24D2082  │ 12.14    │ 2025-03-20 │ False      │
│ 082-01336  │ macOS Sequoia    │ 15.3.2  │ 24D81    │ 14.20    │ 2025-03-20 │ True       │
│ 072-70706  │ macOS Sequoia    │ 15.3.1  │ 24D70    │ 14.20    │ 2025-02-17 │ True       │
│ 093-22120  │ macOS Sonoma     │ 14.7.8  │ 23H730   │ 12.71    │ 2025-08-20 │ True       │
│ 082-85709  │ macOS Sonoma     │ 14.7.7  │ 23H723   │ 12.71    │ 2025-08-05 │ True       │
│ 082-42388  │ macOS Sonoma     │ 14.7.6  │ 23H626   │ 12.72    │ 2025-05-19 │ True       │
│ 082-11498  │ macOS Sonoma     │ 14.7.5  │ 23H527   │ 12.71    │ 2025-04-18 │ True       │
│ 072-84039  │ macOS Sonoma     │ 14.7.4  │ 23H420   │ 12.71    │ 2025-02-17 │ True       │
│ 093-22004  │ macOS Ventura    │ 13.7.8  │ 22H730   │ 11.36    │ 2025-08-20 │ True       │
│ 082-87267  │ macOS Ventura    │ 13.7.7  │ 22H722   │ 11.36    │ 2025-08-05 │ True       │
│ 082-42293  │ macOS Ventura    │ 13.7.6  │ 22H625   │ 11.35    │ 2025-05-19 │ True       │
│ 082-11327  │ macOS Ventura    │ 13.7.5  │ 22H527   │ 11.36    │ 2025-04-18 │ True       │
│ 072-83845  │ macOS Ventura    │ 13.7.4  │ 22H420   │ 11.36    │ 2025-02-17 │ True       │
│ 052-60131  │ macOS Monterey   │ 12.7.4  │ 21H1123  │ 11.55    │ 2024-03-18 │ True       │
│ 042-45246  │ macOS Big Sur    │ 11.7.10 │ 20G1427  │ 11.56    │ 2023-09-11 │ True       │
└────────────┴──────────────────┴─────────┴──────────┴──────────┴────────────┴────────────┘
```

## So we can do this with built-in tools, but should we?

The answer is probably not. There may be faster ways to do the parsing described above than I was able to achieve in this exercise, but it is much slower at getting the results than either `mist-cli` or `installinstallmacos.py`, though it is comparable in speed to `softwareupdate --list-full-installers`.

Could we instead use Apple's GDMF feed (`gdmf.apple.com/v2/pmv`), which is what the [SOFA] project does - or indeed, use the SOFA feed directly? Yes, except that the GDMF feed (and by extension, the SOFA feed) doesn't contain any beta installer information, which has been a valuable functionality of `erase-install`, to me at least, so I didn't want to lose that.

## Conclusion

The latest release of [erase-install], version 38.0, includes the code above to obtain a list of installers when running on macOS 15.6 or newer. It downloads only the `InstallAssistant.pkg` for the relevant installer, directly installing the full installer application into the `Applications` folder when using the `--reinstall` or `--erase` options. The added bonus of this in comparison to how it worked with `mist-cli` and `installinstallmacos.py` is that no extra drive space is required to create a disk image containing the installer, saving around 15 GB of temporary space requirement during the download and install process.

You can still use the `--fetch-full-installer` option. On macOS older than 15.6, you can use the "native" mode described above by adding the `--native` flag - but apart from the space considerations, there's really no need. Once Nindi fixes `mist-cli`, I will probably revert to using it due to its faster speed, though if anyone has any good ideas on how to speed up the process with built-in tools, please let me know or file a PR!

One final note, I used LLMs quite extensively in pursuit of getting the correct `jq` commands. `jq` is incredibly powerful but it is its own language, and the LLMs know that language much better than me. However, it frequently makes up commands and requires very firm direction and extensive testing of every line.

{% include urls.md %}
