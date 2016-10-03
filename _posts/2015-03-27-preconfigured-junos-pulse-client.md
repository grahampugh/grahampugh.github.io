---
layout: post
title:  "Creating a pre-configured Junos Pulse VPN client on OS X with The Luggage"
comments: true
---

[Rich Trouton][@rtrouton]'s [Der Flounder] blog recently described [how to create a pre-configured Junos Pulse VPN client on OS X][1].

I prefer to use Unixorn's [The Luggage] rather than a GUI package creator, so here I adapt Rich's instructions for The Luggage users.

Installing the Luggage
=============

If you don't already have The Luggage, install it as follows (as per [@grahamgilbert]'s blog post [The Luggage: An Introduction][2]:

{% highlight bash %}
$ cd
$ git clone https://github.com/unixorn/luggage.git
{% endhighlight %}

At this point, if you don't already have git installed, you will be prompted to do so. If that happens, install git and rerun the last command. Then continue:

{% highlight bash %}
$ cd luggage
$ make bootstrap_files
{% endhighlight %}

Creating the package
=============

Now The Luggage is installed, copy your Junos Pulse installer and config file into a new folder:

{% highlight bash %}
$ mkdir -p ~/luggage-packages/junos
$ cp /path/to/JunosPulse.dmg /path/to/Default.jnprpreconfig ~/luggage-packages/junos/
{% endhighlight %}

Create a new file named `Makefile` in the same folder using whatever editor you use, and populate as follows:

{% highlight bash linenos %}
USE_PKGBUILD=1
include /usr/local/share/luggage/luggage.make
#PB_EXTRA_ARGS+= --sign "Your Org"  ## uncomment this line if you wish to sign the package

TITLE=Pulse-Secure-Configured
PACKAGE_NAME=${TITLE}
PACKAGE_VERSION=5.2r5.0-b869  ## change to reflect the current version
REVERSE_DOMAIN=net.juniper
MANAGEMENT_DIR = "junos"
INSTALLER_PATH = "."
INSTALLER = "ps-pulse-mac-5.2r5.0-b869-installer.dmg"
CONFIG = "Default.jnprpreconfig"  ## change to suit your config file
PAYLOAD=\
	pack-server \
	pack-script-postinstall
 
pack-server:
	@sudo mkdir -p ${WORK_D}/Library/Management/$(MANAGEMENT_DIR)
	@sudo cp $(INSTALLER_PATH)/$(INSTALLER) ${WORK_D}/Library/Management/$(MANAGEMENT_DIR)/Pulse-Secure.dmg
	@sudo cp $(INSTALLER_PATH)/$(CONFIG) ${WORK_D}/Library/Management/$(MANAGEMENT_DIR)/config.jnprpreconfig
	@sudo chown -R root:wheel ${WORK_D}/Library/Management/$(MANAGEMENT_DIR)
{% endhighlight %}

You may wish to sign the package with a developer ID if you are intending to make the installer available to your users for self-install, so that Gatekeeper doesn't prevent installation. You will need an Apple Mac OS X Developer Account to do this, and have your Developer ID Certificate installed on the machine you are building the package. Then, add the following line as the third line of the Makefile, changing "Your Name" to the name of your certificate in your Keychain:

{% highlight bash  %}
PB_EXTRA_ARGS+= --sign "Your Org"
{% endhighlight %}

Create a new file named `postinstall` in the same folder using whatever editor you use, and populate as follows (this is exactly the same as Rich Trouton's `postinstall` file except for the `install_dir`):

{% highlight bash linenos %}
#!/bin/bash
 
# Determine working directory
 
install_dir="/Library/Management/junos"
 
#
# Installing Junos Pulse
#
 
# Specify location of the Junos Pulse disk image
 
  TOOLS=$install_dir/"Pulse-Secure.dmg"
 
# Specify location of the Junos Pulse configuration file
 
  VPN_CONFIG_FILE=$install_dir/"config.jnprpreconfig"
 
# Specify a /tmp/junospulse.XXXX mountpoint for the disk image
 
  TMPMOUNT=`/usr/bin/mktemp -d /tmp/junospulse.XXXX`
 
# Mount the latest Junos Pulse disk image to the /tmp/junospulse.XXXX mountpoint
 
  hdiutil attach "$TOOLS" -mountpoint "$TMPMOUNT" -nobrowse -noverify -noautoopen
 
# Install Junos Pulse
 
  /usr/sbin/installer -dumplog -verbose -pkg "$(/usr/bin/find $TMPMOUNT -maxdepth 1 \( -iname \*\.pkg -o -iname \*\.mpkg \))" -target "$3"
 
#
# Applying Janelia VPN configuration file
#
 
if [[ -d "$3/Applications/Junos Pulse.app" ]]; then
 
    echo "Junos Pulse VPN Client Installed"
    "$3/Applications/Junos Pulse.app/Contents/Plugins/JamUI/jamCommand" -importFile "$VPN_CONFIG_FILE"
    echo "VPN Configuration Installed"

elif [[ -d "$3/Applications/Pulse Secure.app" ]]; then

    echo "Pulse Secure VPN Client Installed"
    "$3/Applications/Pulse Secure.app/Contents/Plugins/JamUI/jamCommand" -importFile "$VPN_CONFIG_FILE"
    echo "VPN Configuration Installed"
else
    echo "Pulse Client Not Installed"
fi
 
#
# Clean-up
#
 
# Unmount the Junos Pulse disk image
 
  /usr/bin/hdiutil detach "$TMPMOUNT"
 
# Remove the /tmp/junospulse.XXXX mountpoint
 
  /bin/rm -rf "$TMPMOUNT"
 
exit 0
{% endhighlight %}

To create the package, run the following command:

{% highlight bash %}
$ make pkg
{% endhighlight %}

You should now have a package named `Pulse-Secure-Configured.pkg` which you can import into your software distribution system (Munki, Casper etc).

Making a DMG for manual distribution
============

For any package that you wish to make available for distribution via the web or fileshare, you may wish to enclose it in a DMG. I've created a script that automates the process of creating a dmg for any pkg file in the same folder. the output includes a visual check to see if the package is signed.

{% highlight bash %}
$ nano dmg-it.sh
{% endhighlight %}

Contents of `dmg-it.sh`:

{% highlight bash %}
#!/bin/bash

# Run this script after "make pkg" to create a DMG
#
# This version of the script will create a DMG for each pkg in the folder it is in.

mkdir tmp
ls ./*.pkg | while read script
do
    output_Name="${script%.pkg}.dmg"
    echo "PKG->DMG maker. Checking for signed packages..."
    pkgutil --check-signature "${script}"
    cp $script tmp/
    hdiutil create \
        -volname "${script}" \
        -srcfolder ./tmp \
        -ov \
        $output_Name
    rm tmp/*
done
rm -rf tmp
exit 0
{% endhighlight %}

Make it executable, then run it:

{% highlight bash %}
$ chmod o+x dmg-it.sh
$ ./dmg-it.sh
{% endhighlight %}

You should now have `Pulse-Secure-Configured.dmg` in your folder.

*Note:* This post was updated 04 October 2016. The installed Pulse Secure app is now correctly named *Pulse Secure.app*, so the script now checks for this as well as *Junos Pulse.app*. 



[1]: https://derflounder.wordpress.com/2015/03/13/deploying-a-pre-configured-junos-pulse-vpn-client-on-os-x/
[2]: http://grahamgilbert.com/blog/2013/08/09/the-luggage-an-introduction/

{% include urls.md %}

