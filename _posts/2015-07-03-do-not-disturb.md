---
layout: post
title: "A 'Do Not Disturb' application for Munki"
comments: true
---

A Mac user complained that Managed Software Center popped up in the middle of a conference presentation. I started looking into how to suppress notifications.

<img align="right" src="/assets/images/do-not-disturb.png" alt="do-not-disturb" width="150" height="150" />As a quick fix, I created an AppleScript application which suppresses notifications for 24 hours, utilising the `SuppressUserNotification` key in `/Library/Preferences/ManagedInstalls.plist`.

The application sets the key to `TRUE`, and runs a preflight script every time Munki runs on a client to check whether 24 hours have passed or not, after which it will reset the key back to `FALSE`.

# The application

If you use MunkiReport-PHP and/or Sal clients in your organisation, or else have no reporting tools, then you can download the pre-made [Munki Do-Not-Disturb package].

If you use MunkiWebAdmin or some other reporting tool which uses an incompatible preflight script, then [follow the instructions for compiling it yourself][munki do-not-disturb].

(See also my [earlier post on getting MunkiWebAdmin to work with MunkiReport-PHP and/or Sal](2014-11-07-making-munkireport-php-and-munkiwebadmin-work-nicely-together)).

![img-2]

# Importing into Munki

Now import to Munki and place in the manifest of the people you wish to have access. The uninstall method needs changing to ensure proper removal:

{% highlight xml %}
<key>uninstall_method</key>
<string>uninstall_script</string>
<key>uninstall_script</key>
<string>#!/bin/sh
/bin/rm -rf "/Applications/Managed Software Center Do Not Disturb.app" \
/usr/local/munki/preflight.d/msc-do-not-disturb.py
/usr/bin/defaults write /Library/Preferences/ManagedInstalls.plist SuppressUserNotification -bool FALSE
/usr/sbin/pkgutil --forget uk.ac.bris.MSC-Do-Not-Disturb</string>
<key>uninstallable</key>
<true/>
{% endhighlight %}

# Alternatives

You could permanently disable notifications, but that would mean users never become aware of updates, so some applications that require intervention such as closing blocking applications could get somewhat out of date.

There is interest in the use of Apple's Notification Centre for Managed Software Updates, but this is not yet considered reliable. If it becomes suitable, then Apple's built-in Do Not Disturb feature could be utilised.

**UPDATE: I've tweaked this app based on an idea by <a href="http://philec.wordpress.com/">Arjen van Bochoven</a>.**

**UPDATE 2: Graham Gilbert created a menubar "Do Not Disturb" app written in Swift, which is better than this app for users of Yosemite and newer. Get it here: [Munki-DND]. My app works with Snow Leopard and above, so may be still of use to some.**

[img-1]: /assets/images/do-not-disturb.png
[img-2]: /assets/images/do-not-disturb-2.png
[munki-dnd]: https://github.com/grahamgilbert/munki-dnd
[do-not-disturb package]: https://github.com/grahampugh/munki-do-not-disturb/releases

{% include urls.md %}
