---
layout: post
title:  "How many Jamf Pro Policies does each application need?"
comments: true
---

**TL;DR:** 7 (seven).

---

## Wait. What?

I'm in the middle of designing automation of software deployment via Jamf Pro. Up until now, I've concentrated on getting [AutoPkg] to deliver packages to the ~~JSS~~ Jamf Pro Server using [Shea Craig][@shea_craig]'s [JSSImporter] processor, and then propagating the policies to all instances using API scripts. I hope to blog about that in detail in a future post.

I work in a central IT organisation that offers our Jamf Pro service to multiple departments, or "customers". Each customer has their own Jamf Pro instance, and they have the freedom to decide how to offer software titles to their users. Some may wish to offer the titles up by Self Service, some by managed installation, or a mixture of the two. Not all customers will wish to offer some titles at all. Our aim is that the customers should not have to create their own policies for the packages we deliver; they should only have to decide how to scope them.

I was recently lucky enough to visit the [Jamf Nation User Conference]() (JNUC). In one of the sessions, presenter [William Smith][@talkingmoose] described a [recommendation for Jamf Management Templates](https://github.com/talkingmoose/Jamf-Management-Templates/wiki) which necessitates the following for each software title:

* One installer package
* One script
* Two smart groups
* Four policies

But this assumes that the app will be made available to all computers in self service. There are no other options. And there's no testing/staging workflow.

It turns out that in our environment, we need more! In this proof-of-concept, we have:

* One installer package
* One script
* **~~Six~~ Seven** smart groups
* **Seven** policies

In addition, three "global" smart groups are required.



---

## Global Groups

We set up one static and two smart groups to assign software to certain sets of computers:

1. `Testing`. We create a static group in each instance, which is self-populated by each customer with volunteer Testers.

2. `Software gets auto-installed`: We create this smart group for our customers to populate with computers on which they wish to manage installations. We don't want to assign this to anybody by default, we leave that to our customers. But, something needs to be added to the Smart Group, as an empty Smart Group scopes the same as if it were assigned to ALL computers (for some weird reason). So we set it as follows:

    ```
            User:                    is:                REPLACE WITH YOUR OWN CRITERIA
    ```

3. `Software gets auto-updated`: We create this smart group for our customers to populate with computers to which they wish to push managed updates of all eligible software. This is set up identically to the `Software gets auto-installed` group by default.

---

## Testing

As mentioned above, we use AutoPkg/JSSImporter. This creates/updates one policy, two smart groups, one package, one icon, and any required scripts and/or extension attributes associated with the installation of the package. The normal use case is that this policy should be for testing purposes.  The scope for standard software types is therefore as follows:

### Smart Group 1: "ApplicationX test users"

Providing this group allows people to be given access to test versions of individual software. It could be omitted if that was not required, and the policy would then just be scoped to the `Testing` static group.

```
        Computer Group:         member of:  Testing
```

### Smart Group 2: "ApplicationX test version installed"

This group identifies computers that already have the "untested" version of the software installed.

```
        Application Title:      is:         ApplicationX.app
and     Application Version:    is:         X.Y.Z
```

So, the policy is:

### Policy 1: "ApplicationX vX.Y.Z"

We decided that we need to make the version number clear to our testers in the Self Service interface. The default method of JSS recipes is to put the version number in the Install button, but we didn't like that.

Once the Self Service Display Name can be populated via API, we will change this policy name to `ApplicationX test version` so that it doesn't need to change every time there is an update.

```
Category:           Untested
Package:            ApplicationX-X.Y.Z.pkg
Frequency:          Ongoing
Scope:              Targets:
                        ApplicationX test users
                    Exclusions:
                        ApplicationX test version installed
Self-Service:       Enable
                    Name:                   ApplicationX vX.Y.Z
                    Button text:            Install
                    Secondary button text:  Install
```
We then test that the policy works:

* The package installs successfully.
* The policy scopes to the right groups.
* The policy falls out of scope successfully after installation by having the correct version information.
* Any associated scripts and extension attributes are successfully run.

Then what? Well, then we can remove the testing policy until the next release is imported by AutoPkg, but we need policies that allow for self-service installation, update and removal, as well as managed installation and update.

The most efficient way to manage this is with 6 policies and 5 smart groups:

---

## Smart groups

### Smart Group 3: "ApplicationX users"

This group is for computers on which ApplicationX should be made available.

The contents of this smart group will be determined by our customers. They may decide to include `All Computers`, or a subset of their users. So that the volunteer Testers see all software (untested or in production), by default it is populated as follows:

```
        Computer Group:         member of:  Testing
```

### Smart Group 4: "ApplicationX auto-install"

This group is for computers on which ApplicationX should be made automatically installed.

```
        Computer Group:         is:         ApplicationX users
and     Computer Group:         is:         Software gets auto-installed
```

### Smart Group 5: "ApplicationX auto-update"

This group is for computers on which ApplicationX should be made automatically updated when it is already installed.

```
        Computer Group:         is:         ApplicationX users
and     Application Title:      is:         ApplicationX.app
and     Computer Group:         is:         Get auto-updates
```

### Smart Group 6: "ApplicationX installed"

```
        Application Title:      is:         ApplicationX.app
```

### Smart Group 7: "ApplicationX current version installed"

```
        Application Title:      is:         ApplicationX.app
and     Application Version:    is:         X.Y.Z
```

---

## Script

We need a generic script that can uninstall standard applications. Obviously some titles will require their own custom uninstallers. Here's a simple generic one:

```bash
#!/bin/bash

# Closes and deletes an application.
# Requires the app name (not path, not .app) in Parameter 4.

applicationPath="$4"

echo "Closing application: $applicationPath"

pkill "$applicationPath"

echo "Removing application: $applicationPath"

rm -rf "/Applications/$applicationPath.app"
```

You can label Parameter 4 with `App Name (not path, not .app)`.

Munki has a more advanced method of removal using the package receipts. As far as I know, there isn't an equivalent script for Jamf Pro available yet.

---

## Policies

### Policy 2: "Install ApplicationX"

```
Category:           Triggered Installers
Package:            ApplicationX-X.Y.Z.pkg
Frequency:          Ongoing
Scope:              Targets:
                        All Computers
Trigger:            Custom:
                        ApplicationX-install
```

### Policy 3: "ApplicationX"

Once the Self-Service name can be populated via the Jamf Pro 10 API, we may change the policy name to `ApplicationX available`.

We set a user-friendly category here, since it will be seen in Self-Service. For the sake of better organisation, it would be great to have a different category for JSS view to that seen in Self Service, but that feature is not yet implemented by Jamf Pro (at least one Feature Request exists).

```
Category:           User-friendly category
Frequency:          Ongoing
Scope:              Targets:
                        Computer Groups:    ApplicationX users
                    Exclusions:
                        Computer Groups:    ApplicationX installed
Files & Processes:  Execute Command:        jamf policy -event ApplicationX-install
Self Service:       Enable
                    Name:                   ApplicationX
                    Button text:            Install
                    Secondary button text:  Install
```

### Policy 4: "Uninstall ApplicationX"

```
Category:           Uninstallers
Frequency:          Ongoing
Scripts:            Remove Application
                        Priority:           Before
                        Parameter 4:        ApplicationX
Scope:              Targets:
                        Computer Group:     ApplicationX installed
                    Exclusions:
                        Computer Group:     ApplicationX auto-install
Self Service:       Enable
                    Name:                   ApplicationX
                    Button text:            Remove
                    Secondary button text:  Remove
```

### Policy 5: "Update ApplicationX"

Once the Self-Service name can be populated via the Jamf Pro 10 API, we may change the policy name to simply `ApplicationX`.

The script for removing the application prior to update may or may not be required/advisable, depending on the application in question:

```
Category:           User-friendly category
Frequency:          Ongoing
Scripts:            Remove Application
                        Priority:           Before
                        Parameter 4:        ApplicationX
Files & Processes:  Execute Command:        jamf policy -event ApplicationX-install
Scope:              Targets:
                        Computer Groups:    ApplicationX installed
                    Exclusions:
                        Computer Groups:    ApplicationX current version installed
Self Service:       Enable
                    Name:                   Update ApplicationX
                    Button text:            Update
                    Secondary button text:  Update
```

### Policy 6: "Auto-Install ApplicationX"

```
Category:           Auto-installers
Frequency:          Ongoing
Files & Processes:  Execute Command:        jamf policy -event ApplicationX-install
Scope:              Targets:
                        Computer Groups:    ApplicationX auto-install
                    Exclusions:
                        Computer Groups:    ApplicationX installed
```

### Policy 7: "Auto-Update ApplicationX"

```
Category:           Auto-updaters
Frequency:          Ongoing
Files & Processes:  Execute Command:        jamf policy -event ApplicationX-install
Scope:              Targets:
                        Computer Groups:    ApplicationX auto-update
                    Exclusions:
                        Computer Groups:    ApplicationX current version installed
                        Computer Groups:    ApplicationX test version installed
```
---

## Maintenance

When a package of a new version of ApplicationX is available, say version X.Z.0, a new policy `ApplicationX vX.Z.0` is created by AutoPkg/JSSImporter. This does not affect the other existing policies.

Once the new version is approved for production, the following needs to be updated:

1. Policy `Install ApplicationX` needs to have the old package replaced with the new one.
2. Smart Group `ApplicationX current installed` needs to have the new software version number (or whatever criteria defines the current version is installed) replace the old one.
3. The testing policy `ApplicationX vX.Z.0` should be removed.
4. The smart group `ApplicationX test version installed` can be removed.

---

## Improvements

Once Jamf Pro 10's new Self-Service features are made available in the API, we will be able to name the Install and Update Self Service Display Names the same: "ApplicationX", while maintaining different policy names. Since only one item should be visible in Self Service at any one time, there is no need to qualify what the item does in the title name as well as the button.

Once all applications can be added to Patch Policies, which will hopefully come with a future Jamf Pro 10 update in 2018, Policies 5 and 7 will be replaced with a single Patch Policy with two different scopes. The testing policy could also **almost** be replaced with an additional scope in a patch policy, except that there would be no way of delivering a new, untested software title to the testers...

Should I mention here that you can do all the above in Munki with one `pkginfo` file, one package, two manifests and two categories? No, probably not...

How are the rest of you doing this? This workflow is still in development, and not yet fully scripted. I'd love to hear about any improvements you might have!

---

*Updated 2017-11-22 with some improvements (and another smart group!).*

{% include urls.md %}
