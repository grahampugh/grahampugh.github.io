---
layout: post
title: "Buggy 802.1x authentications in OS X 10.10 Yosemite - UPDATE: Fixed with 10.10.1"
comments: true
---

Reports from my organisation's Network Team, after consultation with Cisco, are that in some situations Yosemite 802.1x authentications can take up to 20 seconds (due to buggy behaviour in the OS) - this causes a problem when roaming between two access points of similar strength which leads to your connection apparently disappearing from under you for 20secs.

This can obviously play havoc with connections to central network resources, remote desktop applications and so on.

The bug only manifests itself on 802.1x wireless networks, so can lead to mistaken diagnoses of problems with the 802.1x network.

Apple are apparently aware of the issue, but haven't produced a fix yet.

**UPDATE 2014-11-04:** Apple haven't fixed this yet, but have [provided a workaround][1], which involves editing the appropriate Keychain entry.

**UPDATE: 2014-11-22:** Most reports indicate that this bug was fixed with the OS X 10.10.1 release.

[1]: http://support.apple.com/en-us/TS5258

{% include urls.md %}
