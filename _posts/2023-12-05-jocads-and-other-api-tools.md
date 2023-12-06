---
layout: post
title:  "JOCADS - the Multitenant Object Copier and Deleter Tool for Jamf Pro"
comments: true
---

For many years while working at ETH Zürich, I developed a set of shell scripts for performing API actions on multiple Jamf instances. These remained for internal use only due to the specific nature of the ETH setup. However, as I am between jobs at the moment while waiting for a German work permit (*received today! Woohoo!*), I have taken some time to work on these scripts so that they could be used by other admins faced with dealing with multiple Jamf Pro instances, whilst still remaining functional for the specific use case at ETH. These scripts are now available for the Mac Admins community at the GitHub repo [multitenant-jamf-tools][1]. I hope they may be of use to somebody!

## jocads.sh

JOCADS - `jocads.sh` - is the "Jamf Object Copier and Deleter" script. Its role is to copy existing items from one Jamf instance to any number of others, or to delete matching items across multiple instances. It can be used interactively in a command line window, or automated using script arguments.

It also handles dependencies, so, for example, if a policy depends on any categories, smart computer groups, static computer groups, scripts, extension attributes or packages, these objects are all copied first in order, so that the policy will successfully copy.

Smart groups are often indirectly dependent on other smart groups, static groups, and extension attributes, so smart group criteria are checked to a depth of three dependencies, and copied.

Multiple objects of a single type can be copied or deleted at once, chosen from a list. For example, you could filter on all policies with "Firefox" in the title, select any number of them, and copy or delete those objects to any number of other instances.

JOCADS can be used to copy the following API objects from one instance to another:

* Advanced Computer Search
* Computer Configuration Profile
* Mobile Device Configuration Profile
* Extension Attribute
* Computer Group (smart or static)
* Dock Item
* Policy
* App Store App (Mac or iOS)
* Package Object
* Software Restriction
* Script
* Category
* Jamf Pro User (local or LDAP)
* Jamf Pro Group (local or LDAP)

Note that a package itself is not copied to another instance if each instance has its own distribution point - as this script was developed for use with multiple instances all sharing the same fileshare distribution point, no functionality has been added so far for copying packages themselves. Reach out if you might have a use for that.

JOCADS can also be used to delete most of these API objects. In certain circumstances it can also delete the actual package in addition to the package objects.

Configuration Profiles are safely copied by handling UUIDs within the profiles, maintaining the existing UUID within a single instance so that the profile is properly redeployed. Note, however, that signed profiles cannot be copied using the API without stripping the signature, so certain types of profile are not suitable for distribution via API using any tool.

A requirement at ETH Zürich was that certain computer groups should not be overwritten if they already exist on a destination Jamf instance, but that this should not prevent the script from proceeding to copy objects that have such groups as dependencies. This is achieved by providing a text file containing a list of strings which are pattern-matched during the copy process, and any group matching any of the patterns is only copied if it doesn't already exist on the destination. However, there is a way to force-copy these items for remediation of any broken objects.

## Setting up

Instructions for installing and setting up the environment for using JOCADS and the other scripts are available in the [README][2] document. 

In short, lists of instances are provided as text files. It's possible to have multiple instance lists, for example production and test instance lists. The first item in the list is defined as the default "source" instance, but you can override this to copy from any one instance to multiple others. You can also copy from an instance in one list to instances in another list.

Credentials are set up using the script `set-credentials.sh`. This asks for credentials and stores them in the login keychain for future use. In case multiple instances use the same credentials, this process can be made faster by supplying the credentials for a list of instances at once.

At present, an API user account must be used for each instance. At some point I hope to add support for API Clients.

## Other scripts

There are a bunch of other scripts that are mostly used during the initial set up of new Jamf Pro instances. These work with input variables and/or a supplied XML template rather than copying from a source instance. Scripts currently available can perform the following actions on one or multiple instances:

* Create or update an LDAP user
* Disable Engage
* Define Inventory Collection settings
* Set up a Fileshare Distribution Point
* Set up or update an LDAP server
* Set up or update the SMTP server
* Update the Activation Code
* Update an LDAP group

The script that sets up a Fileshare Distribution Point also adds the SMB share credentials into the keychain for use by the JOCADS script for deleting packages.

Further scripts are available to collect information from one or multiple Jamf Pro instances. These currently include:

* Number of computers not checked in (requires a smart group to have been copied to each instance)
* Number of installations of an app
* Number of managed and unmanaged computers and devices

## Conclusion

These scripts have been *lightly* tested since their conversion to these open source versions, as I do not currently have access to a large set of Jamf instances. Hopefully they will work in your environment, but please reach out via the GitHub repo or DM me in MacAdmins Slack with any bugs, or for any clarifications on how to set it all up! I'd also be interested to hear from anyone who uses them successfully, and if you have any ideas for potential future improvements.

[1]: https://github.com/grahampugh/multitenant-jamf-tools
[2]: https://github.com/grahampugh/multitenant-jamf-tools#readme

{% include urls.md %}
