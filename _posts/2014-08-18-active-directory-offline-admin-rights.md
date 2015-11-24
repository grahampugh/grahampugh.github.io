---
layout: post
title:  "Give Active Directory group members admin rights to their Mac while offline"
comments: true
---

When joining a Mac to Active Directory, you can specify domain users or groups to which you wish to grant administrator rights to the computer.  This is done in Directory Utility by ticking the "Allow administration by:" box and entering a domain\username pair:

![img-1]

Alternatively, a simple command performs the same task:

~~~ bash
$ dsconfigad -groups "DOMAIN\GroupName"
~~~

You can also populate multiple groups (or users), separated by commas:

~~~ bash
$ dsconfigad -groups "DOMAIN\GroupName1,DOMAIN\GroupName2,DOMAIN\User23"
~~~

This can be altered without unbinding / rebinding the domain.

This is a useful feature if you are automating your Mac builds using tools such as [DeployStudio] and/or [Munki], because you can pre-create and populate the AD group(s), and script the AD bind such that the correct groups are added to the "Allow Administration By" field, so there is nothing to do manually on the Mac itself.

However, a limitation of this feature is that users with an AD account in the "Allow Administration By" group are not cached, even if they have a Mobile Account on the Mac. So, unless the domain controllers can be interrogated when the user attempts to perform an elevated task, they will be denied.

Mobile Users can be added to the computer's "admin" group manually, using a command:

~~~ bash
$ /usr/sbin/dseditgroup -o edit -a USERNAME -t user admin
~~~

<p>Similarly they can be removed, thus:</p>

~~~ bash
$ /usr/sbin/dseditgroup -d edit -a USERNAME -t user admin
~~~

Automating the process
=============

My solution is [`check_local_admin.sh`][check_local_admin], a script which checks the members of the AD group in the "Allow Administration By" field, and if they also have an existing Mobile Account on the Mac, adds them to the "admin" group which gives them offline admin rights.

To keep the user rights in sync, for instance, to remove local admin rights from an AD user if you remove them from the AD group, the script can be run as a LaunchDaemon. This waits 15 seconds on startup to give networking a chance to fire up, then checks for access to AD. If it can't see Active Directory, it does nothing, so user rights will only change when in contact with the domain controllers.

For more details on how to download or recreate the package for your establishment, check out my Git [osx-scripts Git repository][check_local_admin].

Please let me know how you get on.

[img-1]: /assets/images/directory-utility-1.png

{% include urls.md %}

