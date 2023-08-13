---
layout: post
title: "How to script the uninstallation of macOS System Extensions"
comments: true
---

Modern System Extensions on macOS are generally installed via an application bundle. They can be bundled within the application with which they are associated (for example **Microsoft Defender ATP**), or in specific applications along side the main app that deliver the system extension (examples include **Sophos Anti-Virus** and **Cisco AnyConnect**).

As an example, Cisco AnyConnect's network system extension is delivered via an application called `Cisco AnyConnect Socket Filter.app` in the same `Cisco` subfolder in `Applications` as the main AnyConnect app. Inside this app you will see the system extension bundle itself, inside `Contents/Library/SystemExtensions`:

![Cisco AnyConnect System Extension](/assets/images/SysExtCiscoNetwork.png)

In Terminal, you can see the status of the installed System Extension using the command `systemextensionsctl list`:

```txt
% systemextensionsctl list
1 extension(s)
--- com.apple.system_extension.network_extension
enabled    active    teamID    bundleID (version)    name    [state]
*    *    DE8Y96K9QP   com.cisco.anyconnect.macos.acsockext (4.9.06037/4.9.06037)    Cisco AnyConnect Socket Filter Extension    [activated enabled]
```

If a System Extension has been enabled, it cannot be deleted using a command like `rm`. If you delete the associated application, the System Extension will remain activated.

There is a command for uninstalling System Extensions, but it currently requires that SIP is disabled:

```txt
% systemextensionsctl uninstall DE8Y96K9QP
At this time, this tool cannot be used if System Integrity Protection is enabled.
This limitation will be removed in the near future.
Please remember to re-enable System Integrity Protection!
```

Hopefully this will be resolved soon, as promised in the dialog.

It is also apparent that developers can build in the deactivation of the System Extension into their application, which allows it to be removed on reboot. For example, Cisco have added the `-deactivateExt` argument to the app to deactivate it:

```txt
% sudo /Applications/Cisco/Cisco\ AnyConnect\ Socket\ Filter.app/Contents/MacOS/Cisco\ AnyConnect\ Socket\ Filter -deactivateExt
```

This brings up a window asking for an admin password to perform the deactivation:

![System Extension password dialog](/assets/images/CiscoSocketFilterDeactivation.png)

After supplying the password, the System Extension is shown as terminated when running the `systemextensionsctl list` command:

```bash
% systemextensionsctl list
1 extension(s)
--- com.apple.system_extension.network_extension
enabled    active    teamID    bundleID (version)    name    [state]
          DE8Y96K9QP     com.cisco.anyconnect.macos.acsockext (4.9.06037/4.9.06037)     Cisco AnyConnect Socket Filter Extension     [terminated waiting to uninstall on reboot]
```

After rebooting, the item is gone.

If your vendor's uninstaller does not build in the deactivation of the System Extension, and you do run their uninstaller, you may get into the state where there is no application associated with the activated System Extension. The only way I have found to delete the System Extension in this case is to reboot into Recovery Mode/OS, disable SIP, boot back into the system, and then use the above command. Then, boot into recovery again to re-enable SIP (as this doesn't seem to be possible from the main booted system any more in Big Sur). Ugh.

## Removing System Extensions via the GUI

If you drag the application that delivered the System Extension to the Trash/Bin, a dialog appears, indicating that the System Extension will be deleted. An admin password is also required to complete the removal, but at least Recovery Mode is not required.

![System Extension removal warning Sophos](/assets/images/SysExtRemovalSophos.png)

There is what I would consider a bug in Apple's implementation of this method of System Extension removal, in that you seem to have to remove the app bundle itself to get the dialog and therefore initiate the approved removal of the System Extension. If you instead remove any parent folder, such as the `Sophos` or `Cisco` folder in which the applications are situated, you do not get the dialog, and the System Extensions are not deactivated, leaving you in the state described above.

This is particularly apparent with the `Sophos Scan` application, because this app is not actually the one delivering the System Extension. Instead, an app within that app is doing it:

![Sophos System Extension](/assets/images/SysExtSophosScan.png)

So if you drag `/Applications/Sophos/Sophos Scan.app` to the Trash, nothing happens to the System Extension. You have to drag `/Applications/Sophos/Sophos Scan.app/Contents/MacOS/SophosScanD.app` to the Trash first.

## How to help your users and do the removal programmatically

In a managed environment, we want to make it as easy as possible for our users and administrators to safely and fully delete applications without leaving their system in a messed up state. Providing documentation for the above GUI method of System Extension removal is of course possible, but to lower the chances of error, it is better to script the process as much as possible. This is where AppleScript comes into play.

AppleScript pre-dates OS X, and AppleScript commands often more closely resemble the GUI processes than the closest UNIX commands. AppleScript includes a method of removing applications, and we can use this to emulate the GUI process of dragging the application to Trash.

For example, here we are removing Microsoft Defender ATP including the System Extensions, by calling AppleScript commands via the `osascript` UNIX command:

```txt
% osascript \
    -e 'tell application "Finder"' \
    -e activate \
    -e 'move application file "Microsoft Defender ATP" of folder "Applications" of startup disk to trash' \
    -e 'end tell'
```

Note that multiple lines of AppleScript are represented by series of `-e` flags.

Here we are removing the Cisco AnyConect Network Extension, which is inside the `Cisco` folder:

```txt
% osascript \
    -e 'tell application "Finder"' \
    -e activate \
    -e 'move application file "Cisco AnyConnect Socket Filter" of folder "Cisco" of folder "Applications" of startup disk to trash' \
    -e 'end tell'
```

In my tests, these commands should be run as `sudo`, which means it can be run from a management tool.

Since you are using a `tell application` command, Privacy Preferences Policy Control comes into play, so you may want to whitelist your Management Tool's access to Finder to prevent another dialog window appearing.

These commands bring up the same dialogs as if dragging the applications to Trash in the GUI, but at least you are able to ensure that the correct app bundle is being deleted to trigger the System Extension removal, and you can ensure the correct order of events in your uninstaller scripts to ensure that no System Extensions are left orphaned.

For completion, here are the commands for removing the two Sophos System Extensions:

```txt
% osascript \
    -e 'tell application "Finder"' \
    -e activate \
    -e 'move application file "Sophos Network Extension" of folder "Sophos" of folder "Applications" of startup disk to trash' \
    -e 'end tell'

% osascript \
    -e 'tell application "Finder"' \
    -e activate \
    -e 'move application file "SophosScanD" of folder "MacOS" of folder "Contents" of application file "Sophos Scan" of folder "Sophos" of folder "Applications" of startup disk to trash' \
    -e 'end tell'
```

Note that if there is an app within an app, you must call `application file` rather than `folder` for the parent app bundle. Also, `.app` is optional in the name of the `application file`, you can add it or omit it.

## Conclusion

System Extension removal is a bit messy in the current versions of macOS. The output of the `systemextensionsctl uninstall` command promises that it will get easier in the future, and there may be other methods not yet discovered (by me, at least). But in the meantime, if you want to ensure as best as possible that the uninstallation of applications that include System Extensions goes as smoothly as possible, consider using AppleScript's `move application file to trash` method.

{% include urls.md %}
