---
layout: post
title:  "Writing an application to run shell commands with admin rights"
comments: true
---

The Mac users I support have admin rights, and I have recently had cause to provide end users with an easy way to run various shell commands which require admin rights (via `sudo`). My aim was not to have to repeatedly send support emails or provide articles which require users to open Terminal and type in one or a more commands. 

# Jamf Pro policy

If you are using [Jamf Pro] and your users are familiar with using the Self Service app, you can create self-service policies which run scripts with admin rights.

# Shell script in a Payload-free Package

If you aren't able to or do not wish to use Self Service, another method is to package up a shell script in a payload-free package, which will prompt the user for admin rights when they "install" it. But it is a little abstract for users to "install" something when they just want to run a tool.  

# Shell script in an Application

The obvious answer is to wrap the script in an application, which is pushed to their Mac. The user can just double-click on the application and the commands are run silently. If an input is required, then a GUI is required. I am not yet familiar with Swift or making Cocoa applications, but for something as simple as running a few shell commands, AppleScript dialog boxes are sufficient.

# Admin rights?

However, if the shell script contains `sudo` commands, it will fail to run. One can wrap each shell command in an AppleScript command such as: 

~~~ bash
do shell script "/bin/bash -s <<'EOF'
cd /Users/myusername/Git/myproject/
/usr/bin/git remote remove orig
EOF" with administrator privileges
~~~

This quickly becomes messy to program when there is more than one `sudo` command, and it can be difficult to find the right escape characters for more complicated shell commands, such as those which contain regex, `awk` and `sed`.

# sudo -S

I found a solution in the command `sudo -S`:

~~~ 
       -S, --stdin Write the prompt to the standard error and read the
                   password from the standard input instead of using the
                   terminal device.  The password must be followed by a
                   newline character.
~~~

This means that one can `echo` the authentication password to stdin, and pipe that into the `sudo` command. The password can be obtained from an AppleScript dialog box.

I prepared a template which can be used at the beginning of any script to obtain the logged in user's password and place it in the variable `$authPass`. It checks that the username and password are correct, and have admin rights. 

Wherever `sudo` is required, replace it with `echo $authPass | sudo -S`. The template creates a function which replaces the stock `sudo` command.

**Note:** There are obvious dangers with echoing an administrator password, so one should be careful with the scripting: for instance definitely do not `set -x`.

~~~ bash
#!/bin/bash

### Script designed to be placed in a "Run Shell Script" action in Automator
### This allows the administrator password to be called, and used in the script where sudo is required
### Beware: the inputted password is used in echo commands
### Usage: Use `sudo` without a path to ensure the `sudo` function is called rather than the actual command

# Dialog Title
dialogTitle="Name of this application"

# obtain the password from a dialog box
authPass=$(/usr/bin/osascript <<EOT
tell application "System Events"
    activate
    repeat
        display dialog "This application requires administrator privileges. Please enter your administrator account password below to continue:" ¬
            default answer "" ¬
            with title "$dialogTitle" ¬
            with hidden answer ¬
            buttons {"Quit", "Continue"} default button 2
        if button returned of the result is "Quit" then
            return 1
            exit repeat
        else if the button returned of the result is "Continue" then
            set pswd to text returned of the result
            set usr to short user name of (system info)
            try
                do shell script "echo test" user name usr password pswd with administrator privileges
                return pswd
                exit repeat
            end try
        end if
        end repeat
        end tell
EOT
)

# Abort if the Quit button was pressed
if [ "$authPass" == 1 ]; then
    /bin/echo "User aborted. Exiting..."
    exit 0
fi

# function that replaces sudo command
sudo () {
    /bin/echo $authPass | /usr/bin/sudo -S "$@"
}

###==========================
### Shell script follows here
###==========================
~~~

The script can be written in your favourite text editor. Then, to create the app, open Automator, add the action "Run Shell Script" to the workflow, and copy-and-paste the script into the box.  Once saved, [add an icon to make the app appropriate for your organisation][1].

![img-1]

I link to a number of these types of apps from the [Hello-IT] status bar application, in order to provide self-help tools to end users.

## Example Scripts

I have used this method for various simple self-help and IT Support applications, and will blog about them in the future.  They show a variety of ways to use an application that runs commands with `sudo`. 

# Jamf Pro: check for new policies

As a simple example, here is an application script that checks for connection to the JSS, and if successful, runs `jamf manage` and `jamf policy`:

![img-2]

{% gist grahampugh/59de17415678f05a30728e7704c9e63d %}

[1]: http://apple.stackexchange.com/a/372
[img-1]: /assets/images/automator-jamf-policy.png
[img-2]: /assets/images/jamf-policy-checker.png

{% include urls.md %}


