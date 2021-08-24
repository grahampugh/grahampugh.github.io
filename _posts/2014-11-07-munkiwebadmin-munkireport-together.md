---
layout: post
title: "Making MunkiReport-PHP and MunkiWebAdmin work nicely together"
comments: true
---

If you utilise [Munki] for package deployment (and you should), you have no doubt at least looked at some of the useful web-based tools for administering and reporting on your clients. [MunkiReport-PHP] is a well-designed client reporting tool, which includes many excellent features. [MunkiWebAdmin] allows you to do a lot of the configuration of clients and manifests via a web interface.

I noticed yesterday that MunkiReport-PHP wasn’t being updated with information about clients, but MunkiWebAdmin was. That got me digging around, and I discovered that their setups interfere with each other. I didn't find documentation about this issue on either software’s setup webpage, though it is addressed on the setup instructions for [Sal], another Munki Reporting tool I'm just starting to experiment with. Both pieces of software latch onto the hourly Munki checks (which are instigated by a LaunchDaemon) using `preflight` and `postflight` scripts put into `/usr/local/munki`.

Unfortunately, installing either MunkiReport-PHP or MunkiWebAdmin overwrites the other’s preflight and postflight scripts…

As MunkiWebAdmin is installed second, it was removing the MunkiReport-PHP scripts, so nothing was being reported to MunkiReport-PHP. Fortunately, the MunkiReport-PHP installer script is helpful, in that it creates folders at `/usr/local/munki/preflight.d` and `/usr/local/munki/postflight.d`, and has a line in its own pre- and postflight scripts which attempts to run any scripts found in those folders. So, I’ve tweaked the script that creates the MWA installer package, so that rather than copying its own preflight and postflight scripts into `/usr/local/munki`, it puts them in `/usr/local/munki/preflight.d` and `/usr/local/munki/postflight.d` instead (and calls them `mwa-preflight` and `mwa-postflight`, so that I can add more scripts for other tools such as Sal later).

[Here is the original MWA installer creation script][1]

I simply changed lines 99-106 as follows:

```bash
# Create the package structure
for item in ${FILE_LIST[@]}
do
cp "${item}" "${BUILD_DIR}/"
done

# move the pre- and post-flight files, so they don't break MunkiReport-PHP
mkdir -p "${BUILD_DIR}/preflight.d"
mkdir -p "${BUILD_DIR}/postflight.d"
mv "${BUILD_DIR}/preflight" "${BUILD_DIR}/preflight.d/mwa-preflight"
mv "${BUILD_DIR}/postflight" "${BUILD_DIR}/postflight.d/mwa-postflight"

chmod -R 755 "${BUILD_DIR}/"*
chown root:wheel "${BUILD_DIR}/"*
```

For some reason I haven't yet identified, the first time MWA is installed after making this change, the MWA installer removes /usr/local/munki/preflight and postflight, so I’ve had to improve the MunkiReport-PHP munki pkginfo file so that it checks for the existence of the `/usr/local/munki/preflight` and `/usr/local/munki/postflight` files, in addition to its default check for an empty version identifier file. This forces a sequence of events where MR-PHP, then MWA, then MR-PHP again, are installed. If anyone can spot how that's happening, please let me know!

Please also note that you shouldn't do this if you don't have MunkiReport-PHP, because your MWA scripts will never get run without the MR-PHP `preflight` and `postflight` files referencing the `preflight.d` and `postflight.d` contents. I may attempt to address this at some point, but at present I'm unlikely to abandon MR-PHP, so it works for me! I'd be interested to find out how other people have solved this problem.

[1]: https://github.com/munki/munkiwebadmin/blob/master/scripts/create-mwa-scripts-installer.sh

{% include urls.md %}
