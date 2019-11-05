---
layout: post
title:  "AutoPkg 1.3 is incompatible with JSSImporter"
comments: true
---

AutoPkg 1.3 was released this week and unfortunately, changes that were made to the reading of the configuration file breaks JSSImporter.  Therefore, running AutoPkg recipes while [JSSImporter] is installed and configured will fail.  It is advised not to upgrade at this time.

If you already upgraded and encountered the problem, the workaround is to revert to [AutoPkg 1.2](https://github.com/autopkg/autopkg/releases/tag/v1.2). A downgrade should be possible simply by installing the [package](https://github.com/autopkg/autopkg/releases/download/v1.2/autopkg-1.2.pkg).

I'll report back when it's fixed.

{% include urls.md %}
