---
layout: post
title: "Munki-Enroll tweaked: Leverage DeployStudio's 'Computer Information' fields to customise Munki builds"
comments: true
---

[Munki-Enroll] is a useful tool to use when installing the Munki tools on Mac clients. It enables the automated creation of unique client manifests, which makes it easy to change the group manifests of a client remotely at any time using tools like [`manifestutil`][manifestutil], [MunkiAdmin] or [MunkiWebAdmin], utilising the `included_manifest` key in Munki manifests.

I have tweaked Munki-Enroll in order to leverage a feature of [DeployStudio] called **Computer Information fields**. These are four text fields available in the **Hostname** workflow page.

![img-1]

The contents of these fields are actually written to a preference file on the host computer at `/Library/Preferences/com.apple.RemoteDesktop`, with key names `Text1`, `Text2`, `Text3`, `Text4`. If you are using [Imagr] instead of DeployStudio, you could easily script the use of these fields with commands such as:

{% highlight bash %}
sudo defaults write /Library/Preferences/com.apple.RemoteDesktop Text1 "Some text"
{% endhighlight %}

I use these fields to determine manifest enrolment using Munki-Enroll. This allows me to have only two DeployStudio workflows for all computers: one for new, out-of-box Macs which don't require a rebuild, and one for rebuilding Macs. All other imaging variations are determined by Munki manifests. My DeployStudio workflows include installing the MunkiTools package, and then a `munki-enroll.sh` script which reads the contents of the **Computer Information** fields and posts them to Munki-Enroll using `curl`:

{% highlight bash %}
COMPFIELD1=`defaults read /Library/Preferences/com.apple.RemoteDesktop Text1`
COMPFIELD2=`defaults read /Library/Preferences/com.apple.RemoteDesktop Text2`
COMPFIELD3=`defaults read /Library/Preferences/com.apple.RemoteDesktop Text3`
COMPFIELD4=`defaults read /Library/Preferences/com.apple.RemoteDesktop Text4`
{% endhighlight %}

One could just write the manifest names one wished to include in the client manifest directly into these fields, and pass them to munki-enroll. In my case, I wished to use shortcuts to make inputting quicker, so I added some processing to the script so interpret shortcuts (`COMPFIELD1`-`COMPFIELD4`) and output manifest names (`IDENTIFIER1`-`IDENTIFIER4`):

| Field   | Shortcut          | Munki manifest                                                       | Function                                    |
| ------- | ----------------- | -------------------------------------------------------------------- | ------------------------------------------- |
| #1      | empty             | \_cg_ru                                                              | Default package set for Regular Users       |
| ZA - ZF | \_cg_za - \_cg_zf | Zone (area) specific packages, including local admin user creation   |
| OA      | \_cg_zd_oa        | Zone D Student Laptop build (Open Access)                            |
| #2      | empty             | \_cg_ru                                                              | Default package set (if #1 is set to ZA-ZF) |
| AD      | \_cg_ad           | Join to Active Directory (desktop build)                             |
| ADL     | \_cg_ad_eduroam   | Join to Active Directory and add managed wifi profile (laptop build) |
| AO      | \_cg_all_optional | "Light touch" all-optional build                                     |
| #3      | empty             | -                                                                    | Do not encrypt                              |
| FV      | \_cg_encrypt      | Encrypt the Mac using Crypt                                          |

I'm not using the fourth **Computer Information** field at this time. Of course, your organisation's manifests are very unlikely to be the same, but I hope this gives you an idea of the flexibility that can be gained using the **Computer Information** fields with Munki-Enroll. I also use the contents of **Computer Information field 1** in my Munki AD-binding package to determine the Active Directory Organisational Unit.

The manifests are then passed to the Munki-Enroll web page using a `curl` command:
{% highlight bash %}
/usr/bin/curl --max-time 5 --data \
"hostname=$LOCALHOSTNAME&amp;identifier1=$IDENTIFIER1&amp;identifier2=$IDENTIFIER2&amp;identifier3=$IDENTIFIER3" \
$MUNKI_REPO_URL/munki-enroll/enroll.php
{% endhighlight %}

Note that this is a `POST` command - a change from the default munki-enroll which uses the less-secure `GET` method.

The Munki-Enroll script (`enroll.php`) has been tweaked to accept each identifier and add them as `included_manifests` to the client manifest:
{% highlight php %}
// Add parent manifest to included_manifests to achieve waterfall effect
$dict-&gt;add( 'included_manifests', $array = new CFArray() );
if ( $identifier1 != "" )
{
$array-&gt;add( new CFString( $identifier1 ) );
}
if ( $identifier2 != "" )
{
$array-&gt;add( new CFString( $identifier2 ) );
}
if ( $identifier3 != "" )
{
$array-&gt;add( new CFString( $identifier3 ) );
}
if ( $identifier4 != "" )
{
$array-&gt;add( new CFString( $identifier4 ) );
}
{% endhighlight %}

Take a look at my tweaked version of Munki-Enroll [here][munki-enroll].

The full `enroll.php` script:

{% highlight php %}

<?php
require_once( 'cfpropertylist-1.1.2/CFPropertyList.php' );
// Default catalog
$catalog = 'standard';
// Get the varibles passed by the enroll script
$identifier1 = $_POST["identifier1"];
$identifier2 = $_POST["identifier2"];
$identifier3 = $_POST["identifier3"];
$identifier4 = $_POST["identifier4"];
$hostname   = $_POST["hostname"];
// Ensure we aren't nesting a manifest within itself
// Note that this will create a default manifest - it will not honour any options from DS
if ( $identifier1 == "client-" . $hostname )
	{
		$identifier1 = "_cg_ru"; $identifier2 = "";
	}
// Check if manifest already exists for this machine
echo "\n\tMUNKI-ENROLLER. Checking for existing manifests.\n\n";
if ( file_exists( '../manifests/client-' . $hostname ) )
    {
        echo "\tComputer manifest client-" . $hostname . " already exists.\n";
        echo "\tThis will be replaced.\n\n";
    }
else
    {
        echo "\tComputer manifest does not exist. Will create.\n\n";
    }
	$plist = new CFPropertyList();
	$plist->add( $dict = new CFDictionary() );
        
    // Add manifest to production catalog by default
    $dict->add( 'catalogs', $array = new CFArray() );
    $array->add( new CFString( $catalog ) );
        
    // Add parent manifest to included_manifests to achieve waterfall effect
    $dict->add( 'included_manifests', $array = new CFArray() );
    if ( $identifier1 != "" )
        {
            $array->add( new CFString( $identifier1 ) );
        }
    if ( $identifier2 != "" )
        {
            $array->add( new CFString( $identifier2 ) );
        }
    if ( $identifier3 != "" )
        {
            $array->add( new CFString( $identifier3 ) );
        }
    if ( $identifier4 != "" )
        {
            $array->add( new CFString( $identifier4 ) );
        }
    // Save the newly created plist
    $plist->saveXML( '../manifests/client-' . $hostname );
    chmod( '../manifests/client-' . $hostname, 0775 );
    echo "\tNew manifest created: client-" . $hostname . "\n";
    echo "\tIncluded Manifest(s): " . $identifier1 . " " . $identifier2 . " " . $identifier3 . " " . $identifier4 . "\n";
        
?>

{% endhighlight %}

The full `munki-enroll.sh` script:

{% highlight bash %}
#!/bin/bash

# The Munki Repo URL

MUNKI_REPO_URL="http://your.munki.server"

COMPFIELD1=`defaults read /Library/Preferences/com.apple.RemoteDesktop Text1`
COMPFIELD2=`defaults read /Library/Preferences/com.apple.RemoteDesktop Text2`
COMPFIELD3=`defaults read /Library/Preferences/com.apple.RemoteDesktop Text3`

#COMPFIELD1: Zone splits
if [ "$COMPFIELD1" = "ZA" ]; then
IDENTIFIER1="\_cg_za"
elif [ "$COMPFIELD1" = "ZB" ]; then
IDENTIFIER1="\_cg_zb"
elif [ "$COMPFIELD1" = "ZC" ]; then
IDENTIFIER1="\_cg_zc"
elif [ "$COMPFIELD1" = "ZD" ]; then
IDENTIFIER1="\_cg_zd"
elif [ "$COMPFIELD1" = "ZE" ]; then
IDENTIFIER1="\_cg_ze"
elif [ "$COMPFIELD1" = "ZF" ]; then
IDENTIFIER1="\_cg_zf"
elif [ "$COMPFIELD1" = "ES" ]; then
IDENTIFIER1="\_cg_zd_oa_earthsci"
else
IDENTIFIER1="\_cg_ru"
fi

#COMPFIELD2: AD stuff
if [ "$COMPFIELD2" = "AD" ]; then
if [ "$IDENTIFIER1" == "_cg_ru" ]; then
IDENTIFIER1="\_cg_ru_ad"
else
IDENTIFIER2="\_cg_ru_ad"
fi
elif [ "$COMPFIELD2" = "ADL" ]; then
if [ "$IDENTIFIER1" == "_cg_ru" ]; then
IDENTIFIER1="\_cg_ru_eduroam"
else
IDENTIFIER2="\_cg_ru_eduroam"
fi
elif [ "$COMPFIELD2" = "AO" ]; then
if [ "$IDENTIFIER1" == "_cg_ru" ]; then
IDENTIFIER1="\_cg_all_optional"
else
IDENTIFIER2="\_cg_all_optional"
fi
else
if [ "$IDENTIFIER1" != "_cg_ru" ]; then
IDENTIFIER2="\_cg_ru"
else
IDENTIFIER2=""
fi
fi

#COMPFIELD3: FileVault
if [ "$COMPFIELD3" = "FV" ]; then
IDENTIFIER3="\_cg_encrypt"
else
IDENTIFIER3=""
fi

# Output for the benefit of the DeployStudio log

echo "Compfield1: $COMPFIELD1"
echo "Compfield2: $COMPFIELD2"
echo "Compfield3: $COMPFIELD3"
echo "Identifer1 is $IDENTIFIER1"
echo "Identifer2 is $IDENTIFIER2"
echo "Identifer3 is $IDENTIFIER3"

# This setting determines whether Munki should handle Apple Software Updates

# Set to false if you want Munki to only deal with third party software

defaults write /Library/Preferences/ManagedInstalls InstallAppleSoftwareUpdates -bool True

# The existence of this file prods Munki to check for and install updates upon startup

# If you'd rather your clients waited for an hour or so, comment this out

touch /Users/Shared/.com.googlecode.munki.checkandinstallatstartup

# Figures out the computer's local host name - don't use ComputerName as this may contain bad characters

LOCALHOSTNAME=$( scutil --get LocalHostName );

# Checks whether it is a valid IT tag - you can choose your own naming scheme

ITTAGCHECK=`echo $LOCALHOSTNAME | grep -iE '\<IT[0-9]{6}\>'`
if [ $? -ne 0 ]; then # Sets the LocalHostName to the serial number if we don't have an IT tag name
SERIAL=`/usr/sbin/system_profiler SPHardwareDataType | /usr/bin/awk '/Serial\ Number\ \(system\)/ {print $NF}'`
scutil --set LocalHostName "$SERIAL"
	LOCALHOSTNAME="$SERIAL"
fi

# set the ClientIdentifier to "client-LOCALHOSTNAME

defaults write /Library/Preferences/ManagedInstalls ClientIdentifier "client-$LOCALHOSTNAME"

# Sets the URL to the Munki Repository

defaults write /Library/Preferences/ManagedInstalls SoftwareRepoURL "$MUNKI_REPO_URL"

# Leave this unless you have put your munki-enroll script somewhere unusual

SUBMITURL="$MUNKI_REPO_URL/munki-enroll/enroll.php"

# Application paths

CURL="/usr/bin/curl"

$CURL --max-time 5 --data \
	"hostname=$LOCALHOSTNAME&identifier1=$IDENTIFIER1&identifier2=$IDENTIFIER2&identifier3=$IDENTIFIER3" \
 $SUBMITURL
exit 0
{% endhighlight %}

[img-1]: /assets/images/munki-enroll-1.png

{% include urls.md %}
