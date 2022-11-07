---
layout: post
title:  "Mystery solved - uninstalled system extensions still listed in System Settings"
comments: true
---

Strange behaviour had been bugging me in the Network Pane of macOS System Preferences (System Settings since macOS Ventura) ever since the introduction of system extensions in macOS Catalina 10.15. System extensions are the replacement for kernel extensions (confusingly referred to as "System Extensions" in macOS System Preferences and in dialogue boxes).

After installing the first apps that came with the new type of system extension, new items are displayed in the Network Pane. In our case this was Sophos Anti-Virus and Cisco AnyConnect. After uninstalling that software &mdash; including uninstalling the system extension of course &mdash; we found that an extension was sometimes left in the Network pane of System Preferences. 

Typically, these "orphans" lose any icon they once had, and are impossible to remove via the GUI, as the "minus" button is greyed out.

Upon further investigation, the output of `systemextensionsctl list`, which lists any installed system and network extensions, did not show the "orphaned" extension at all, at least not once the computer was rebooted (removed extensions are shown as `[terminated waiting to uninstall on reboot]` until the computer is restarted).

![Deleted System Extension showing in System Preferences on macOS Catalina][1]  
*Network pane showing content filters for Sophos, Microsoft and Cisco, none of which are listed in the command line*

The problem even remains to this day in macOS Ventura.

![Deleted System Extensions showing in System Preferences on macOS Ventura][2]  
*Network pane showing system extensions for Sophos and Cisco, none of which are listed in the command line*

After receiving a support ticket that appeared to be another instance of this behaviour, I finally decided to open an AppleCare Enterprise ticket, and had a conversation about it with other folks on the MacAdmins Slack.

## Mystery solved

The tip off was in the questioning from AppleCare support (as well as in the conversation in Slack).

> How was this extension [allow-]listed? If via MDM are those profiles still installed?

I removed my test clients from the scope of the Cisco and Sophos allow-list profiles, and sure enough, the items immediately disappeared.

So, if you have a profile allowing any system extensions that use the Sophos, Cisco, Microsoft or whatever Team ID, and any extensions by those vendors have at some point in the history of that system's current installation been installed on the client, then those extensions will continue to be listed in the Network pane of System Preferences or System Settings, until such time that the profile is removed from the client.

## But what to do about it?

If you (or your users, and therefore your Service Desk) care about those entries in the Network pane, this may not actually not be easy to resolve. The profile needs to be in place before any potential installation, otherwise the pop-up warnings are going to happen at the point of installation. So, you cannot deploy the profile to computers that have the app installed; it has to be targeted to computers to which the software is _targeted_.

Obviously this is only going to be an issue in circumstances where you need to allow the system extension to be uninstalled, which won't be the case for a lot of security software.

However, you may also encounter a particular software title with a poorly designed installer that bundles in a system extension which &mdash; depending on your installer choices &mdash; serves no purpose. This is the case with Cisco Secure Client (_née_ AnyConnect), where the extensions bundled with the installer  are not required by the VPN client (which is the only part we install), and have been known to cause problems when installed alongside other network extensions such as Sophos Anti-Virus or Microsoft Defender &mdash; not to mention causing confusion to users who have the VPN menu bar item show the duration of connection, which is hijacked by this non-functional content filter extension.

This is a small annoyance that, for such workflows, cannot currently be solved. The Cisco Secure Client extension allow-list profile must be in place at all times, ready for the next update which will install those unnecessaty and disruptive extensions again.

## Conclusion

I don't think this behaviour is intuitive. It is also inconsistent with the output of the `systemextensionsctl list`. however, it was not accepted as a bug via the AppleCare ticket:

> As it stands today, the MDM configuration must be removed by removing the profile, and this is confirmed to be known and expected by product engineering.

The supporter did encourage us to open a Feedback Request for "more intuitive" behaviour/documentation, which I have done. If this is something that bugs you or your users, I would encourage you to do the same!

[1]: /assets/images/sysext-catalina.png
[2]: /assets/images/sysext-ventura.png

{% include urls.md %}
