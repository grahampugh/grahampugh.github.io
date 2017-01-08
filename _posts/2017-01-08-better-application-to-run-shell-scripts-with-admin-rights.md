---
layout: post
title:  "Writing a (better) application to run shell scripts with admin rights"
comments: true
---

Following on from my [post yesterday][1], in which I describe a method of creating an application using Automator to run shell scripts that require administrator privileges (`sudo`), I have now figured out how to achieve the same thing with AppleScript editor, with the improvement that the system dialog is used to obtain administrator privileges, rather than a custom dialog box.

To do this, create an Application in AppleScript Editor:

  * Open AppleScript Editor
  * Click File > New
  * Click File > Save
  * Enter name, select a path, select File Format > Application
  * Optionally, you may wish to sign the application with your Developer ID
  * Save

![img-1]

  * Enter the following commands:

~~~ 
set myPath to POSIX path of (path to resource "MyShellScript.sh")

do shell script quoted form of myPath with administrator privileges
~~~

  * Click on the toolbar button in the top right of AppleScript Editor that reveals the right side bar. 
  * Drag your shell script from a Finder window into the Resources list.
  * Save the application

You may wish to sign the application with your Developer ID, and make it Run Only. To do this, click File > Export..., select the Developer ID and make any required other settings changes:

![img-3]

Once saved, [add an icon to make the app appropriate for your organisation][1].

When running the application, you should be prompted with a system authentication dialog window:

![img-2]

## Example Scripts

Below is the same example as my previous post, adapted to use AppleScript Editor. 

# Jamf Pro: check for new policies

As a simple example, here is an application script that checks for connection to the JSS, and if successful, runs `jamf manage` and `jamf policy`:

{% gist grahampugh/141311cd7182e3d531d46c2251f504c5 %}

[1]: {% post_url 2017-01-07-application-to-run-shell-commands-with-admin-rights %}
[2]: http://apple.stackexchange.com/a/372
[img-1]: /assets/images/new-applescript.png
[img-2]: /assets/images/auth-rights.png
[img-3]: /assets/images/export-application.png

{% include urls.md %}


