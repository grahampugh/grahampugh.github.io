---
layout: post
title:  "An undocumented change to Captive Network Assistant settings in OS X 10.10 Yosemite"
comments: true
---

A [captive portal] is a network that forces an HTTP client to see a special web page (usually for authentication purposes) before using the Internet normally. A captive portal turns a Web browser into an authentication device. These are commonly used on wifi networks where authentication to the private network is done via a login browser page, rather than via the use of a WEP or WPA2 key, for example in some coffee shops and airports, and hotspot providers such as [The Cloud] and [ATT-Wifi].

On Apple devices, if a captive portal is identified, a special application in `/System/Library/CoreServices` called `Captive Network Assistant.app` is opened. This is a very limited browser, separate to Safari, with no address bar or navigation buttons.

![img-1]  
**An example window in Captive Network Assistant**

Sometimes, the limitations of this browser prevent successful authentication to the wifi network, if the network hasn't been configured accordingly. In my organisation the end user needs to download a configuration profile in order to connect to our 802.1x protected network ([Eduroam]). The download of the profile is not possible from within `Captive Network Assistant.app` due to the limited functionality of the app, and must be done from a full internet browser such as Safari.

In OS X up to 10.9 Mavericks, the presence of a captive portal was established upon connection to an open wifi network by attempting to connect to the following URL, which has the key `ProbeURL`:

[http://www.apple.com/library/test/success.html][1]

This is determined in the file `/Library/Preferences/SystemConfiguration/CaptiveNetworkSupport/Settings.plist`

You will notice in this file that some of the popular HotSpot Providers have their own settings, and [orange.fr] is disabled entirely.

I'm not clear whether the necessary response is just a HTTP 200 ("OK") response, or whether it checks the contents of the page (HTML containing the word "success").

It is therefore possible to prevent the popup by allowing specific access through the captive network to this specific page only, or spoofing the page. In my organisation, fake root DNS is used to prevent the pop up [note: I don't know how that works so don't ask me!].

**(On your own Mac, you could take steps to prevent the popup appearing if you wished, by deleting or renaming `Captive Network Assistant.app`, or changing the `Settings.plist` to a localhost page, or creating an entry in `/etc/hosts` file to redirect the `ProbeURL` to a localhost page. There are umpteen blog/forum posts about doing this, [such as this one][2].)**

In **Yosemite**, something changed. In our organisation, the pop up came back. Why? Simple (once you know): Apple changed the `ProbeURL` to a new location:

[http://captive.apple.com/hotspot-detect.html][3]

Who knows why Apple decided to change this, but I hope if you're diagnosing wifi popup problems in your organisation, this will help you change your DNS settings accordingly.

[captive portal]: http://en.wikipedia.org/wiki/Captive_portal
[The Cloud]: http://www.thecloud.net
[ATT-Wifi]: http://www.att.com/gen/general?pid=5949
[Eduroam]: https://www.eduroam.org
[orange.fr]: http://www.orange.fr
[1]: http://www.apple.com/library/test/success.html
[2]: http://apple.stackexchange.com/questions/45418/how-to-automatically-login-to-captive-portals-on-os-x
[3]: http://captive.apple.com/hotspot-detect.html

[img-1]: https://www.freewave.at/wp-content/uploads/2014/08/littlesnitch_3.jpg

{% include urls.md %}

