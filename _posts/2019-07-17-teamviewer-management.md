---
layout: post
title:  "Prevent TeamViewer from opening during package installation"
comments: true
excerpt: > # put a short description to make RSS feeds look better.
TeamViewer can be prevented from opening during installation if a specific file is placed in the tmp folder before installation. This can be achieved with the use of a preinstall script.
---

A customer pointed out to us that when a new version of TeamViewer was pushed to a client managed by Jamf Pro, the application would open during the installation of the package. That can be confusing to users, or badly timed.

**Note:** by TeamViewer I mean the full application that acts both as client and server. TeamViewer QuickSupport does not have this problem.

![TeamViewer main window](/assets/images/teamviewer.png)

TeamViewer provide their installer as a package. We use [AutoPkg] to obtain the package automatically, namely the `TeamViewer.pkg` recipe from `autopkg/cgerke-recipes`, which has as a parent recipe `TeamViewer.download` from `autopkg/hjuutilainen-recipes`. The `.pkg` recipe simply extracts the version and renames the package accordingly, but does not repackage. Our own internal `.jss` recipe uploads the package to our Jamf Pro distribution points.

I could not find any documentation on how to prevent the application opening, so had a look at the package using [Suspicious Package], which revealed that a script named `functions` is sourced by the `postinstall` script within the package. In `functions`, a function `restartService` determines whether the application is opened or not based on the existence of `${pathToAppPath}`.

![TeamViewer in Suspicious Package](/assets/images/suspicious-teamviewer.png)

`${pathToAppPath}` is defined as a file path further up the `functions` file:

![TeamViewer in Suspicious Package (2)](/assets/images/suspicious-teamviewer2.png)

So all we need to do is ensure the file `/tmp/tvPath` exists before installing. It needs no content. This is easily achieved with a script that can be added to a Jamf Pro policy (or a Munki `pkginfo` file), set to run before the package is installed.

```
#!/bin/sh
## preinstall script

# Set TeamViewer to only restart the service on installation
# This is achieved by touching the following file
# before installing the package

/usr/bin/touch /tmp/tvPath
```

![TeamViewer Policy in Jamf Pro](/assets/images/teamviewer-policy.png)

We've added this as a `preinstall` script to our internal `.jss` recipe.

{% include urls.md %}
