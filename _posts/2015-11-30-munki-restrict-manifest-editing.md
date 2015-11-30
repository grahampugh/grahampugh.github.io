---
layout: post
title:  "Munki-Do: Restrict who has access to edit manifests"
comments: true
---

You may wish to restrict the right to edit certain [Munki] manifests to certain users in your organisation. For example, you may wish to allow the editing of individual client manifests, but prevent editing of certain "core" manifests that affect a large number of machines. Alternatively, you may have different manifests for different organisational units, and may wish to only allow members of those units to edit their own manifests.

Munki-Do can now be configured to restrict manifest editing, based on Django group membership. To enable this feature, set `MANIFEST_RESTRICTION_KEY` in `settings.py` or with the `DOCKER_MUNKIDO_MANIFEST_RESTRICTION_KEY` Docker environment variable. With this set, a new key is added to a manifest which determines which group

Any group created in Munki-Do's Django admin interface can be used, as can 'staff' and 'superuser'. If you enter a group name which doesn't exist, only superusers will be able to edit that manifest. Superusers can edit any manifest regardless of ret restriction.

Example
=======

In this example, Users "firstline" and "staffmember" both have access to edit standard manifests, as members of an "it-support" group, but "staffmember" is also a member of the "staff" group. The "admin" user (a superuser) adds "staff" to the "User restriction" setting of the "site_default" manifest.

**Admin user has set User Restrictions to "Staff":**
![img-1]

The manifest name is displayed with "**(restricted)**" appended, to make it clear that not everyone can edit this manifest.

**"Firstline" account is not a member of the "Staff" group, and so cannot edit this manifest - no Edit button is displayed:**
![img-2]


**"Staffmember" account is a member of the "Staff" group, and so can edit this manifest - the Edit button is displayed:**
![img-3]

**If the Admin user or a member of the "Staff" group removes the User Restrictions entry, normal editing rights return, and the "(restricted)" message is removed:**
![img-4]

**If the `MANIFEST_RESTRICTION_KEY` is not set in `settings.py` or using a Docker environment variable, the User Restrictions entry is not available:**
![img-5]

Thanks go to [@GrahamGilbert] for the idea for this feature of Munki-Do.

[img-1]: /assets/images/manifest-restriction-1.png
[img-2]: /assets/images/manifest-restriction-2.png
[img-3]: /assets/images/manifest-restriction-3.png
[img-4]: /assets/images/manifest-restriction-4.png
[img-5]: /assets/images/manifest-restriction-5.png

{% include urls.md %}

