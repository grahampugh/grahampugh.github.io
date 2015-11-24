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

TITLE=Junos-Pulse
PACKAGE_NAME=${TITLE}
REVERSE_DOMAIN=net.juniper
MANAGEMENT_DIR = &quot;junos&quot;
INSTALLER_PATH = &quot;.&quot;
INSTALLER = &quot;JunosPulse.dmg&quot;
CONFIG = &quot;Default.jnprpreconfig&quot;
PAYLOAD=\
pack-server \
pack-script-postinstall

pack-server:
    @sudo mkdir -p ${WORK_D}/Library/Management/$(MANAGEMENT_DIR)
    @sudo cp $(INSTALLER_PATH)/$(INSTALLER) $(INSTALLER_PATH)/$(CONFIG) ${WORK_D}/Library/Management/$(MANAGEMENT_DIR)
    @sudo chown -R root:wheel ${WORK_D}/Library/Management/$(MANAGEMENT_DIR)
{% endhighlight %}

You may wish to sign the package with a developer ID if you are intending to make the installer available to your users for self-install, so that Gatekeeper doesn't prevent installation. You will need an Apple Mac OS X Developer Account to do this, and have your Developer ID Certificate installed on the machine you are building the package. Then, add the following line as the third line of the Makefile, changing "Your Name" to the name of your certificate in your Keychain:

{% highlight bash %}
PB_EXTRA_ARGS+= --sign &quot;Your Name&quot;
{% endhighlight %}

Create a new file named `postinstall` in the same folder using whatever editor you use, and populate as follows (this is exactly the same as Rich Trouton's `postinstall` file except for the `install_dir`):

{% highlight bash %}
#!/bin/bash
# Determine working directory
install_dir=&quot;/Library/Management/junos&quot;

#
# Installing Junos Pulse
#

# Specify location of the Junos Pulse disk image
TOOLS=$install_dir/&quot;JunosPulse.dmg&quot;

# Specify location of the Junos Pulse configuration file
VPN_CONFIG_FILE=$install_dir/&quot;Default.jnprpreconfig&quot;

# Specify a /tmp/junospulse.XXXX mountpoint for the disk image
TMPMOUNT=`/usr/bin/mktemp -d /tmp/junospulse.XXXX`

# Mount the latest Junos Pulse disk image to the /tmp/junospulse.XXXX mountpoint
hdiutil attach &quot;$TOOLS&quot; -mountpoint &quot;$TMPMOUNT&quot; -nobrowse -noverify -noautoopen

# Install Junos Pulse
/usr/sbin/installer -dumplog -verbose -pkg &quot;$(/usr/bin/find $TMPMOUNT -maxdepth 1 \( -iname \*\.pkg -o -iname \*\.mpkg \))&quot; -target &quot;$3&quot;

#
# Applying Janelia VPN configuration file
#

if [[ -d &quot;$3/Applications/Junos Pulse.app&quot; ]]; then
    echo &quot;Junos Pulse VPN Client Installed&quot;
    &quot;$3/Applications/Junos Pulse.app/Contents/Plugins/JamUI/jamCommand&quot; -importFile &quot;$VPN_CONFIG_FILE&quot;
    echo &quot;VPN Configuration Installed&quot;
else
    echo &quot;Pulse Client Not Installed&quot;
fi

#
# Clean-up
#

# Unmount the Junos Pulse disk image
/usr/bin/hdiutil detach &quot;$TMPMOUNT&quot;

# Remove the /tmp/junospulse.XXXX mountpoint
/bin/rm -rf &quot;$TMPMOUNT&quot;

exit 0
{% endhighlight %}

To create the package, run the following command:

{% highlight bash %}
$ make pkg
{% endhighlight %}

You should now have a package named `Junos-Pulse.pkg` which you can import into your software distribution system (Munki, Casper etc).

Making a DMG for manual distribution
============

For any package that you wish to make available for distribution via the web or fileshare, you may wish to enclose it in a DMG. I've created a script that automates the process of creating a dmg for any pkg file in the same folder. the output includes a visual check to see if the package is signed.

{% highlight bash %}
$ nano dmg-it.sh
{% endhighlight %}

Contents of `dmg-it.sh`:

{% highlight bash %}
#!/bin/bash

# Run this script after &quot;make pkg&quot; to create a DMG
# if you have already signed your pkg in the Makefile
# or if you dont want to sign it.
#
# This version of the script will create a DMG for each pkg in the folder it is in.

mkdir tmp
ls ./*.pkg | while read script
do
    output_Name=&quot;${script%.pkg}.dmg&quot;
    echo &quot;PKG-&gt;DMG maker. Checking for signed packages...&quot;
    pkgutil --check-signature &quot;${script}&quot;
    cp $script tmp/
    hdiutil create \
        -volname &quot;${script}&quot; \
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

You should now have `Junos-Pulse.dmg` in your folder.

[1]: https://derflounder.wordpress.com/2015/03/13/deploying-a-pre-configured-junos-pulse-vpn-client-on-os-x/
[2]: http://grahamgilbert.com/blog/2013/08/09/the-luggage-an-introduction/

{% include urls.md %}

