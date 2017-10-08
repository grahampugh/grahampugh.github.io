---
layout: post
title:  "Configuring SplashBuddy"
comments: true
---

François Tiffreau-Levaux ([@ftiff])'s [SplashBuddy] application (formerly CasperSplash) is an Application created using Swift, designed to be used when staging a DEP Mac using [JAMF Pro] (formerly Casper). It can equally used to onboard User-Initiated Enrollments. Current in 1.0 release candidate phase, it is fully functional, and relatively easy to set up. the latest version can be downloaded from the [releases page](https://github.com/ftiff/SplashBuddy/releases).

![img-1]

The downloaded `zip` file contains all you need to create an installer package.

To configure `SplashBuddy.app`, edit preferences file in the package, at `/Library/Preferences/io.fti.SplashBuddy.plist`. The preferences file serves two purposes.  

Firstly, it contains an array of applications that you wish to show in the right-hand window of the SplashBuddy GUI.  This is manually populated, and must contain information to tell the app the name of the package as it will appear in the Jamf log file (`/var/log/jamf.log`), and the path to its icon.  

At present, the application array must only contain pkg files (DMG installations and Apple Software Updates, for example, can not be listed).  Additionally, the pkg filename must have a specific form: `package_name-package_version.pkg` (the `-` and `.pkg` are obligatory). This may require renaming some packages that you have previously imported into your JSS.

Secondly, it identifies the path where assets are stored. The default path is `/Library/Application Support/SplashBuddy`. This contains:

* `SplashBuddy.launch.sh`: A script that when launched will cause SplashBuddy to always launch until `/Users/${loggedInUser}/Library/Containers/io.fti.SplashBuddy/Data/Library/.SplashBuddyDone` is touched.

* `postInstall.sh`: A script that will be run after pressing "Continue". This is used to touch the above file, but other commands can be added as required.

* Icons for each of the loading apps. You must provide an icon for each app listed in `io.fti.SplashBuddy.plist`.

* Presentation files for the main window. These are stored in `Presentation.bundle`. This contains a folder named `Base.lproj` that should be renamed to `en.lproj` if you wish to serve the app to English language computers. Inside the `en.lproj` folder should the following assets:

   * `index.html`: The main HTML page which occupies the main window of SplashBuddy.
   * Any other assets such as images, style sheets, javascript files, other HTML files, YouTube videos etc., which can be linked using relative paths from `index.html`. The pictured example above uses a CSS file and the JPEG image of coffee.

An example preferences file is shown below:

~~~ xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>assetPath</key>
	<string>/Library/Application Support/SplashBuddy</string>
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
			<true/>
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

Once configured, run `./build_pkg.sh` to package up SplashBuddy.

In my usage with Jamf Pro, the package is added to a "thin provisioning" profile, which is triggered by Jamf Pro's `Enrollment Complete` trigger. The profile also contains a script which calls all the profiles that install the various applications that SplashBuddy will look for. A section of an example script is shown below:

~~~ bash
#!/bin/bash

# open SplashBuddy app
su $loggedInUser -c 'open -a /Library/Application Support/SplashBuddy/SplashBuddy.app'

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

# Quit SplashBuddy if still running
if [[ $(pgrep SplashBuddy) ]]; then
	pkill SplashBuddy
fi

# we are done, so delete SplashBuddy
rm -rf '/Library/Application Support/SplashBuddy'
rm /Library/Preferences/io.fti.SplashBuddy.plist
rm /Library/LaunchAgents/io.fti.SplashBuddy.launch.plist
~~~

**Note:** this post was updated October 8, 2017 from the original post of 10 November, 2016.

[img-1]: /assets/images/SplashBuddy-1.png


{% include urls.md %}
