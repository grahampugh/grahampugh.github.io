---
layout: post
title: "A script to clean up your AutoPkg Cache folder"
comments: true
---

The longer you use [AutoPkg] without cleaning up the Cache folder, the more cruft you're going to get. Much of the cruft is older downloads and any packages generated.

Depending on your setup, you may be able to just delete the entire Cache folder periodically. In our setup, we cannot do that as we require the latest package and the recipe receipts to be kept in the Cache for further use. Additionally, we would rather keep the latest download so that comparisons with previous runs can be done to prevent re-download.

Prompted by a full system drive on one of my AutoPkg runners, I've finally got around to writing a rough-and-ready script to do the cleanup. The script will keep a specified number of packages in the root of each directory in the `RECIPE_CACHE_DIR`, defaulting to the 2 most recent, and a specified number of files in the `downloads` folder within each cache directory, again defaulting to the 2 most recent.

The script `autopkg-cache-clean.sh` is available here: [https://github.com/grahampugh/osx-scripts/blob/master/autopkg-scripts/autopkg-cache-clean.sh](https://github.com/grahampugh/osx-scripts/blob/master/autopkg-scripts/autopkg-cache-clean.sh).

Please note this is very crudely written to suit our needs. If you have complex recipes that write multiple files to the `downloads` folder, output packages to a different folder than the `RECIPE_CACHE_DIR`, or some other variation, you should adapt the script accordingly. It also won't clean up any other folders left behind by recipes that don't do their own cleanup.

Here's an example output:

```bash
% ./autopkg-cache-clean.sh

Folder: local.jss.Parallels Desktop
Deleting /Users/autopkg/Library/AutoPkg/Cache/local.jss.Parallels Desktop/Parallels_Desktop_15.1.1.pkg
Deleting /Users/autopkg/Library/AutoPkg/Cache/local.jss.Parallels Desktop/Parallels_Desktop_16.0.0.pkg
Deleting /Users/autopkg/Library/AutoPkg/Cache/local.jss.Parallels Desktop/Parallels_Desktop_15.0.0.pkg
Deleting /Users/autopkg/Library/AutoPkg/Cache/local.jss.Parallels Desktop/Parallels_Desktop_14.0.0.pkg.zip
Deleting /Users/autopkg/Library/AutoPkg/Cache/local.jss.Parallels Desktop/Parallels_Desktop_14.0.0.pkg

Folder: local.jss.Adobe Creative Cloud
Deleting /Users/autopkg/Library/AutoPkg/Cache/local.jss.Adobe Creative Cloud/Adobe Creative Cloud-5.3.5.518.pkg.zip
Deleting /Users/autopkg/Library/AutoPkg/Cache/local.jss.Adobe Creative Cloud/Adobe Creative Cloud-5.3.5.518.pkg
Deleting /Users/autopkg/Library/AutoPkg/Cache/local.jss.Adobe Creative Cloud/AdobeCreativeCloudInstaller-5.3.1.470.pkg
Deleting /Users/autopkg/Library/AutoPkg/Cache/local.jss.Adobe Creative Cloud/Adobe Creative Cloud-5.0.0.354.pkg.zip
Deleting /Users/autopkg/Library/AutoPkg/Cache/local.jss.Adobe Creative Cloud/Adobe Creative Cloud-5.0.0.354.pkg

Folder: local.jss.Adobe Photoshop CC 2020 SDL
Deleting /Users/autopkg/Library/AutoPkg/Cache/local.jss.Adobe Photoshop CC 2020 SDL/Adobe_Photoshop_CC_EN_NUL-21.0.1.pkg.zip
Deleting /Users/autopkg/Library/AutoPkg/Cache/local.jss.Adobe Photoshop CC 2020 SDL/Adobe_Photoshop_CC_EN_NUL-21.0.1.pkg

Folder: local.jss.SeqMonk/downloads
Deleting /Users/autopkg/Library/AutoPkg/Cache/local.jss.SeqMonk/downloads/seqmonk_v1.47.1_osx64.dmg
Deleting /Users/autopkg/Library/AutoPkg/Cache/local.jss.SeqMonk/downloads/seqmonk_v1.47.0_osx64.dmg
Deleting /Users/autopkg/Library/AutoPkg/Cache/local.jss.SeqMonk/downloads/seqmonk_v1.46.0_osx64.dmg

Total 514 folders parsed
Total 12 pkgs deleted
Total 3 downloads deleted
```

{% include urls.md %}
