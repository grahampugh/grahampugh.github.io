---
layout: post
title:  "Is XProtect up to date?"
comments: true
---

Your organisation may want to ensure that XProtect is up to date on Mac. So long as Software Update settings are set to "Install Security Updates and System Files", all should be well... assuming that Software Update is functioning today... 

But how can you *verify* that the XProtect version on the system *is* the latest version available? For that, you need to check against Apple's software catalogs or some external source.

## Silent Knight

Howard Oakley's excellent [Silent Knight][1] app and [silnite][1] command line tool checks the system version against his own GitHub repo, where he maintains a history of updates for XProtect and other tools.

`silnite` outputs a JSON file when run, so you'll need to use a JSON interpreter to read the data. When testing this out, I've used the excellent [Little JSON Tool][2] (`ljt`) code snippet from [Joel Bruner][3].

```bash
# Latest XProtect Version
xProtectLatestVersion=$(ljt /XProtectE < /path/to/silnite_output_file.json)

# System XProtect Version
xProtectInstalledVersion=$(ljt /XProtectV < /path/to/silnite_output_file.json)
```

That's great, but to use this, you have to deploy `silnite` to all your Mac fleet, which requires maintenance, and create a method of running it periodically.

## Apple Software Update Catalogs

Alternatively, you can interrogate Apple's software catalog directly using `curl`, and compare this with the installed version.

```bash
CURRENT_CATALOG="https://swscan.apple.com/content/catalogs/others/index-14-13-12-10.16-10.15-10.14-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog"

# create cache directory
/bin/mkdir -p "/var/sucatalog"

# download catalog
curl -s "$CURRENT_CATALOG" > "/var/sucatalog/current-catalog.sucatalog"

# get the latest XProtect config data URL
xProtectURL=$(grep -m 1 -o 'https.*XProtectPlistConfigData.*pkm' < "/var/sucatalog/current-catalog.sucatalog")

# download the config data file and extract the version string 
xProtectLatestVersion=$(curl -s "$xProtectURL" | grep -o 'CFBundleShortVersionString[^ ]*' | cut -d '"' -f 2)

# obtain the installed XProtect version
xProtectInstalledVersion=$(defaults read /Library/Apple/System/Library/CoreServices/XProtect.bundle/Contents/Info.plist CFBundleShortVersionString)

# compare the two to find if the latest version is installed
if [[ "$xProtectLatestVersion" == "$xProtectInstalledVersion" ]]; then
    echo "Latest version installed"
else
    echo "Latest version NOT installed"
fi
```

## Best practice for Jamf Pro

Note that with either of these methods, polling the internet is required. If you were intending to use an Extension Attribute, it's generally better to avoid polling the internet directly from an EA, as there could be delays or timeouts. So, it's best to create a LaunchDaemon to run a script which does the internet polling at intervals, and let the EA read the output from files downloaded by that script.

If you want to go that route, you'll need a policy to deploy the script and LaunchDaemon, and the EA can then read the downloaded files to do the comparison... so, only marginally less work than deploying `silnite`, but arguably better as it polls Apple's software update catalogs directly rather than an independent list that may or may not be current.

I've prepared versions of both these scripts, go check them out if you're interested: [check-xprotect-version](https://github.com/grahampugh/osx-scripts/tree/main/check-xprotect-version)

## Conclusion

In all probability, it's OK to rely on `softwareupdate` to keep XProtect and other security components up to date. But if you really want to verify it, choose one of the methods above.

Similar methods could be utilised for the other security components such as GateKeeper and MRT (though MRT appears to be obsolete since macOS 12) - `silnite` reports all these values, and they are all present in the `.sucatalog`. Here's some hints:

```bash
# MRT
MRT_URL=$(grep -m 1 -o 'https.*MRTConfigData.*pkm' < "/var/sucatalog/current-catalog.sucatalog")

# Gatekeeper
GatekeeperURL=$(grep -m 1 -o 'https.*GatekeeperConfigData.pkm' < "/var/sucatalog/current-catalog.sucatalog")
```

[1]: https://eclecticlight.co/lockrattler-systhist/
[2]: https://github.com/brunerd/ljt
[3]: https://github.com/brunerd

{% include urls.md %}
