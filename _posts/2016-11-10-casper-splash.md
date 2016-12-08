---
layout: post
title:  "Configuring CasperSplash"
comments: true
---

François Tiffreau ([@ftiff])'s app [CasperSplash] is designed to be used when staging a DEP Mac using [JAMF Pro] (formerly Casper). 
It is an Application created using Swift, currently in Alpha release - there are certainly improvements to be made  to the app, but it is functional and relatively easy to set up.

![img-1]

To configure `CasperSplash.app`, you need to create a preferences file at `/Library/Preferences/io.fti.CasperSplash.plist`. The preferences file serves two purposes.  Firstly, it identifies the path where assets are stored. The default path is `/Library/CasperSplash`. The default assets are:

*  `presentation.html`: The main HTML page which occupies the main window of CasperSplash. This can of course contain relative paths to other assets such as images, css, js, other HTML files, etc.
*  `postInstall.sh`: A script that will be run after pressing "Continue".
*  Icons for each of the loading apps, the path to which is `assetPath`/`iconRelativePath`.

Secondly, it contains an array of applications that you wish to show in the right-hand window of the CasperSplash GUI.  This is manually populated, and must contain information to tell the app the name of the package as it will appear in the Casper log file (`/var/log/jamf.log`), and the path to its icon.  

At present, the application array must only contain pkg files (DMG installations and Apple Software Updates, for example, can not be listed).  Additionally, the pkg filename must have a specific form: `package_name-package_version.pkg` (the `-` and `.pkg` are obligatory). This may require renaming some packages that you have previously imported into your JSS.

An example preferences file is shown below:

~~~ xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>assetPath</key>
	<string>/Library/CasperSplash</string>
	<key>htmlPath</key>
	<string>presentation.html</string>
	<key>postInstallAssetPath</key>
	<string>postInstall.sh</string>
	<key>applicationsArray</key>
	<array>
		<dict>
			<key>canContinue</key>
			<false/>
			<key>displayName</key>
			<string>Microsoft Word 2016</string>
			<key>description</key>
			<string>Office application</string>
			<key>iconRelativePath</key>
			<string>icons/Microsoft Word.png</string>
			<key>packageName</key>
			<string>Microsoft_Word_2016</string>
		</dict>
		<dict>
			<key>canContinue</key>
			<false/>
			<key>displayName</key>
			<string>Microsoft Excel 2016</string>
			<key>description</key>
			<string>Office application</string>
			<key>iconRelativePath</key>
			<string>icons/Microsoft Excel.png</string>
			<key>packageName</key>
			<string>Microsoft_Excel_2016</string>
		</dict>
	</array>
</dict>
</plist>
~~~

In the example above, the `packageName` key shows the name `Microsoft_Word_2016`, which will therefore expect a pkg name of `Microsoft_Word_2016-XX.YY.ZZ.pkg` (the version number is not used by the app but one must exist).

The app itself can be placed anywhere where it can be executed on the System Disk. In my setup, I use [Munki-Pkg] to package up the app, icons and configs, as follows: 

~~~ bash
/Library/CasperSplash/CasperSplash.app
/Library/CasperSplash/presentation.html
/Library/CasperSplash/caspersplash.css
/Library/CasperSplash/postInstall.sh
/Library/CasperSplash/icons/ ... # all the app icons in here
/Library/Preferences/io.fti.CasperSplash.plist
~~~

The package is added to the thin provisioning profile, which triggered by Casper's "Enrollment Complete" setting. The profile also contains a script which calls all the profiles that install the various applications that CasperSplash will look for. A section of this script is shown below:

~~~ bash
#!/bin/bash

# open CasperSplash app
su $loggedInUser -c 'open -a /Library/CasperSplash/CasperSplash.app'

# Installing RootCA's
jamf policy -trigger certs

# Setting Computername
jamf policy -trigger setcomputername

# Installing Microsoft Word/Excel/Outlook/OneNote/PowerPoint 2016
jamf policy -trigger office

# Installing Code42 Crashplan
jamf policy -trigger crashplan

# Installing Enterprise Connect
jamf policy -trigger enterpriseconnect

# Installing Apple Updates
jamf policy -trigger runsoftwareupdate

# Preparing for Reboot

# Quit CasperSplash if still running
if [[ ! -z $(pgrep CasperSplash) ]]; then
	osascript -e 'quit app "CasperSplash"
fi

# we are done, so delete CasperSplash
rm -Rf /Library/CasperSplash

~~~

[img-1]: /assets/images/caspersplash-1.png



{% include urls.md %}

