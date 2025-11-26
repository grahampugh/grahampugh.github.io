---
layout: post
title:  "Jamf-Upload All The Things"
comments: true
---

## Introduction

[JamfUploader] started off as a successor to [JSSImporter], the now defunct [AutoPkg] processor designed to use a python framework called [python-jss] (also defunct) to upload packages to a Jamf Pro instance and create objects required to deploy that package, such as a category, a script, a smart group, and a policy. With JamfUploader, I decided to take a modular approach, with each object getting its own processor, for example `JamfCategoryUploader`, `JamfScriptUploader`, `JamfPackageUploader`, and so on. Over time, I and other contributors have added more and more processors to handle additional endpoints and perform additional tasks beyond just uploading something.

This modular approach makes JamfUploader a powerful and flexible tool for maintaining all content in Jamf Pro, but I suspect not too many of you are aware of the utility beyond that original use case of uploading a package.

This post explains some of the wider variety of capabilities of JamfUploader.

## Contents

- [Introduction](#introduction)
- [Contents](#contents)
- [Setting up a fresh Jamf Pro instance with JamfUploader](#setting-up-a-fresh-jamf-pro-instance-with-jamfuploader)
  - [How does that work?](#how-does-that-work)
  - [How do I find out the "object\_type" key to use?](#how-do-i-find-out-the-object_type-key-to-use)
- [Deployable Content](#deployable-content)
  - [A note about Blueprints and Compliance Benchmarks](#a-note-about-blueprints-and-compliance-benchmarks)
- [Copying, Amending, and Deleting Content](#copying-amending-and-deleting-content)
  - [Deleting any object](#deleting-any-object)
  - [Cleaning up old packages](#cleaning-up-old-packages)
  - [Cleaning up unused packages](#cleaning-up-unused-packages)
  - [Copying an object from one instance to another](#copying-an-object-from-one-instance-to-another)
  - [Copying the scope of one scopeable object to another](#copying-the-scope-of-one-scopeable-object-to-another)
  - [Adjusting the scope of an existing scopeable object](#adjusting-the-scope-of-an-existing-scopeable-object)
  - [Enabling or Disabling a Policy, App Catalog App, or Extension Attribute](#enabling-or-disabling-a-policy-app-catalog-app-or-extension-attribute)
  - [Adding or removing a value from a pop-up choice-style extension attribute](#adding-or-removing-a-value-from-a-pop-up-choice-style-extension-attribute)
  - [Listing and Downloading all objects of a particular type](#listing-and-downloading-all-objects-of-a-particular-type)
- [Conclusion](#conclusion)

## Setting up a fresh Jamf Pro instance with JamfUploader

When setting up a new Jamf Pro instance, there a basically two types of content you have to create to make the instance useful:

1. Settings
2. Deployable content

Configuring the settings is something you generally only have to do once, except for any changes or new features that are introduced by Apple or Jamf over the lifetime of the instance. However, if you're maintaining multiple instances, it can be advantageous to keep the settings as code so that you can easily reproduce the same settings over and over, and push those new features and changes to all your servers consistently.

Perhaps surprisingly, this can all be done using JamfUploader. Thanks to a generic processor called `JamfObjectUploader`, plus a few specific processors such as `JamfAccountUploader`, `JamfAPIRoleUploader` and `JamfAPIClientUploader`, almost any setting can be in a template file (perhaps in your own private git repo), and AutoPkg recipes can be used to upload them.

Currently, the following settings are supported:

- User Accounts and Groups
- Activation Code
- API Roles and Clients
- Check-in Settings
- Cloud LDAP
- Computer Inventory Collection Settings
- Computer PreStage Enrollments
- Distribution Points
- Enrollment Settings
- Enrollment Customizations
- Jamf Protect Settings
- LAPS
- LDAP Server
- Mobile Device PreStage Enrollments
- Network Segments
- Self Service
- Self Service+
- SMTP Server
- SSO Settings and Certificate
- Volume Purchasing Locations

If you encounter a setting not in the list, let me know. A small number of settings are not exposed in the API, but there may be a few more that my team and I haven't needed to use.

### How does that work?

Just as with traditional JamfUploader workflows, maintaining these settings as code is a combination of recipes and template files. One great thing about using JamfUploader to maintain these is that you can use the Jamf Pro GUI to generate the settings you want once, and then use the Swagger Docs, or [developer.jamf.com](https://developer.jamf.com), or indeed the `JamfObjectReader` processor (more on that later) to download the settings in exactly the right format you'll need to upload them to another instance (or the same instance as remediation/version control) - there's no abstraction into another syntax required. Note this may be JSON or XML depending on whether the endpoint is in the Classic or Jamf Pro API.

> Remember that your API account or Client needs permissions to perform actions on each specific endpoint.

Let's take a simple example of the Check-In Settings. If we take a look at the typical settings in the Swagger docs, we get a JSON file that looks like this:

```json
{
    "checkInFrequency": 15,
    "createHooks": true,
    "hookLog": true,
    "hookPolicies": true,
    "createStartupScript": true,
    "startupLog": true,
    "startupPolicies": true,
    "startupSsh": false,
    "enableLocalConfigurationProfiles": false
}
```

If we are going to deploy the same settings to all servers, we can save this template as it is, and create a simple recipe to upload it:

```yaml
Description: Sets the Check-In Settings
Identifier: JamfMSP-private-recipes.jamf.CheckInSettings
MinimumVersion: "2.3"

Input:
  OBJECT_TEMPLATE: CheckInSettings.json
  OBJECT_TYPE: check_in_settings

Process:
  - Processor: com.github.grahampugh.jamf-upload.processors/JamfObjectUploader
    Arguments:
      object_template: "%OBJECT_TEMPLATE%"
      object_type: "%OBJECT_TYPE%"
```

However, if we need to deploy different settings to different servers, we can introduce variables into the template and override them in the recipe. In AutoPkg, variables are represented with names between percentage files, e.g. `%VARIABLE_NAME%`. So let's say we need to vary the check-in frequency, we'll replace a hard value with a variable.

```json
{
    "checkInFrequency": %CHECK_IN_FREQUENCY%,
    "createHooks": true,
    "hookLog": true,
    "hookPolicies": true,
    "createStartupScript": true,
    "startupLog": true,
    "startupPolicies": true,
    "startupSsh": false,
    "enableLocalConfigurationProfiles": false
}
```

> Note that your code editor such as Visual Studio Code might not like the syntax of the variable as it is not JSON-compliant (it looks like you are trying to add a string without quotation marks), but JamfUploader will handle the substitution just fine.

Now you add a default value for the variable to your recipe:

```yaml
Description: Sets the Check-In Settings
Identifier: my-recipes.jamf.CheckInSettings
MinimumVersion: "2.3"

Input:
  OBJECT_TEMPLATE: CheckInSettings.json
  OBJECT_TYPE: check_in_settings
  CHECK_IN_FREQUENCY: 15

Process:
  - Processor: com.github.grahampugh.jamf-upload.processors/JamfObjectUploader
    Arguments:
      object_template: "%OBJECT_TEMPLATE%"
      object_type: "%OBJECT_TYPE%"
```

Now you can override the value as required in the recipe override file or at the command line, e.g.

```bash
autopkg run -v CheckInSettings.jamf --key "CHECK_IN_FREQUENCY=30"
```

You could put all your settings in a single recipe, but you will still need separate template files for each settings type. Alternatively, if you're looking for a single workflow to create all settings in a new instance (or ensure that they are all correct in an existing instance), you can maintain individual recipes for each type of setting, and create a recipe list for all settings which you can then run when creating a new instance.

### How do I find out the "object_type" key to use?

I've listed all the currently available endpoints in the [JamfUploader Object Reference][1]. If there's a missing endpoint that you need, raise a GitHub Issue (Feature Request) in the [JamfUploader] GitHub repo, and I'll get it added so long as an API endpoint exists for that object.

## Deployable Content

For everything outside of the core management settings, I like to use the concept of building blocks, where a recipe consists of all the dependent objects required to deploy the content. This could contain any of the following types of object, all of which either have their own processor within the JamfUploader suite, or can be created using `JamfObjectUploader`:

- Advanced Computer Search
- Advanced Mobile Device Search
- App Installers Deployment
- Blueprint (see below)
- Category
- Compliance Benchmarks (see below)
- Computer Extension Attribute
- Computer Group (Smart or Static)
- Computer Configuration Profile (mobileconfig or custom plist)
- Dock Item
- Mac App Store or In-House Application
- Managed Software Updates - Plans
- Mobile Device App Store or In-House Application
- Mobile Device Configuration Profile
- Mobile Device Extension Attribute
- Package or package object
- Patch Policy
- Patch Software Title
- Policy
- Policy Icon
- Restricted Software
- Script

Let's consider a policy that creates a Self Service object that will run a script to change a setting on the computer. What are all the building blocks we need for this?

- The script that changes the setting
- An Extension Attribute that determines what the setting is currently
- A smart group to define the targets for this policy
- A smart group to exclude computers where the setting is already in the desired state
- An icon for the Self Service policy
- The policy
- A category or categories for the policy and the script

You could create a recipe for each of these objects, but if we put them all in one recipe, we don't have to think again later about the workflow to deploy this policy. It normally doesn't matter if we push the same object again for use in some other policy, but if it does, we can opt not to replace an existing object using the appropriate `replace_X` key (e.g. `replace_group: False`). An example of when this might be the case is if we want administrators to be able to change the scope of a group we have uploaded via the console without fear of the criteria being overwritten back to the defaults.

For this policy, we'll therefore need a recipe and template files for the script, the EA, the two smart groups and the policy, plus the icon. We'll also need to ensure that the categories exist. The recipe needs to create these objects in the correct order of dependency - in this case we ensure the category exists first, then upload the EA and script, followed by the two computer groups, and finally the policy (including its icon):

```yaml
Description: Creates an ongoing policy for running a single script excluding a Smart Group with EA criteria.
Identifier: my-recipes.jamf.RandomSetting
MinimumVersion: "2.3"

Input:
  EXTENSION_ATTRIBUTE_NAME: Random Setting
  EXTENSION_ATTRIBUTE_OPERATOR: is
  EXTENSION_ATTRIBUTE_VALUE: Compliant

Process:
  - Processor: com.github.grahampugh.jamf-upload.processors/JamfCategoryUploader
    Arguments:
      category_name: Maintenace

  - Processor: com.github.grahampugh.jamf-upload.processors/JamfExtensionAttributeUploader
    Arguments:
      ea_name: Random Setting
      ea_script_path: RandomSettingStatus-EA.sh
      replace_ea: "True"

  - Processor: com.github.grahampugh.jamf-upload.processors/JamfScriptUploader
    Arguments:
      script_category: Maintenance
      script_name: ApplyRandomSetting.sh
      script_path: ApplyRandomSetting.sh
      script_priority: After
      replace_script: "True"

  - Processor: com.github.grahampugh.jamf-upload.processors/JamfComputerGroupUploader
    Arguments:
      computergroup_name: Computers That Require Random Setting
      computergroup_template: ComputerGroup-TargetGroup.xml
      replace_group: "True"

  - Processor: com.github.grahampugh.jamf-upload.processors/JamfComputerGroupUploader
    Arguments:
      computergroup_name: "%EXTENSION_ATTRIBUTE_NAME% %EXTENSION_ATTRIBUTE_OPERATOR% %EXTENSION_ATTRIBUTE_VALUE%"
      computergroup_template: ComputerGroup-EA.xml
      replace_group: "True"

  - Processor: com.github.grahampugh.jamf-upload.processors/JamfPolicyUploader
    Arguments:
      policy_name: Apply Random Setting
      policy_template: Policy-SelfService-Script.xml
      icon: Maintenance.png
      replace_policy: "True"
```

### A note about Blueprints and Compliance Benchmarks

Jamf recently introduced two new features that use a different API to our familiar Classic and Jamf Pro APIs, called the [Jamf Platform API][2]. This API is currently only available to folks who had already signed up to the private beta, with a public beta due soon.

Unlike the Classic and Jamf Pro APIs, you cannot use basic authentication to generate a bearer token, nor can you use Jamf Pro credentials to create [API Roles and Clients][3] for use with the Platform API. Currently, you must (when given access) create a Platform API Client ID and Secret via the Jamf Account website. The URL used does not refer directly to your Jamf Pro URL either, since the Platform API is used for access to microservices which may underlie different Jamf web services (e.g. Jamf Pro, Jamf School). A single client may also have access to multiple microservices. I'll blog more about this once the public beta program is opened.

I have built the ability to use JamfUploader processors to read and write blueprints and compliance benchmarks, including the ability to store the credentials in the keychain. Specifically, the `JamfObjectReader` processor has been tested with the following endpoints:

- Blueprint
- Compliance Benchmarks - Rule
- Compliance Benchmarks - Baseline
- Compliance Benchmarks - Benchmark

The `JamfObjectUploader` processor has so far been tested with the following endpoints:

- Blueprint
- Blueprint - Deploy
- Blueprint - Undeploy

Please let me know your experience if you try these new endpoints out, or reach out to me in the Mac Admins Slack `#jamf-uploader` channel if you have any questions!

## Copying, Amending, and Deleting Content

A Jamf Pro server is rarely static. Setting up the initial settings and content is only the first hurdle. There are inevitable changes to make starting the day after you created the instance, for example:

- Uploaded packages get new versions
- Computer groups dynamically scoped to package or app versions need to change
- Policy icons change
- Customers require more granular scoping
- New apps are required
- A vendor changes or deprecates an app, or the installation method changes
- Apple introduce new privacy controls that require new profiles
- Certificates expire
- Licenses are renewed
- Different software update deferral settings or enforcements are required at certain times of year
- A policy, extension attribute or App Installer deployment needs to be disabled or enabled

Ideally, these updates can be made by adapting the recipe made when initially creating the content, and running it again. Sometimes, however, the real world gets in the way, and you have to either make changes to existing objects without overwriting what's already there, or you have to make changes to items that pre-exist your automation, sometimes in bulk, such as name or scope changes. You also need to clean things up, again, sometimes in bulk.

This is where these processors become most useful:

- `JamfObjectReader`
- `JamfObjectUploader`
- `JamfObjectDeleter`
- `JamfPolicyLogFlusher`
- `JamfScopeAdjuster`
- `JamfExtensionAttributePopupChoiceAdjuster`
- `JamfObjectStateChanger`
- `JamfPackageCleaner`
- `JamfUnusedPackageCleaner`

Let's go through some scenarios where some of these processors might be useful.

### Deleting any object

This is an easy one. We provide the endpoint type and the object name, and the `JamfObjectDeleter` processor will delete that object. For legacy reasons, `JamfComputerGroupDeleter` and `JamfPolicyDeleter` also still currently exist, but they serve the same purpose. I've provided a recipe for deleting any object: [DeleteObject.jamf][13]. We can run this as follows, here for example I'm deleting a computer profile called "Restrictions - Defer Software Updates - Major 90 days - Minor 30 days":

```bash
autopkg run -v DeleteObject.jamf --key OBJECT_TYPE=os_x_configuration_profile --key NAME="Restrictions - Defer Software Updates - Major 90 days - Minor 30 days"
```

### Cleaning up old packages

When you've accumulated old versions of installer packages for an existing title, you can use `JamfPackageCleaner` to clean them up, while retaining one or more of the most recent uploads. I've previously blogged about this in the post [Clean up your packages in Jamf Pro automatically with JamfPackageCleaner](https://grahamrpugh.com/2023/04/25/JamfPackageCleaner.html). I've also provided a recipe for this: [DeleteOldPackages.jamf][4].

In this example, we're requesting to remove packages beginning with the name "Firefox-", using the defaults in the recipe which is to keep the 5 most recent versions:

```bash
autopkg run -v DeleteOldPackages.jamf --key DRY_RUN=False --key NAME=Firefox
```

### Cleaning up unused packages

If your file share distribution point is getting full, or you just want to tidy up your JCDS of unused packages, then you can use `JamfUnusedPackageCleaner` on a regular basis. This processor takes some time to run, as it needs to look in all policies, patch policies, and prestage enrollments to check each package. So it's best run as a standalone recipe. I've created a recipe for this: [DeleteUnusedPackages.jamf][5]. The following command will delete all unused packages:

```bash
autopkg run -v DeleteUnusedPackages.jamf --key DRY_RUN=False
```

### Copying an object from one instance to another

If you need to copy any object from one Jamf Pro instance to another, it's technically a three-stage process:

1. Download the object from the source instance.
2. Parse the downloaded JSON or XML to remove keys that are specific to the source instance, such as the object ID, or computer/device objects listed in a smart group.
3. Upload the parsed object to the destination instance.

These steps can be done with `JamfObjectReader` and `JamfObjectUploader`. To make things easy, `JamfObjectReader` automatically removes the ID key and computer or device objects. In which case, you just need to specify the source and destination URL and credentials, and the object type and name. This can be done in individual steps or using a recipe. I've provided an example: [CopyObject.jamf][6].

Additionally, you may wish to delete or replace a key when copying the object. `JamfObjectUploader` provides the keys `elements_to_remove` and `elements_to_replace` to allow you to switch out any object in the downloaded JSON or XML file with a value of your choice.

### Copying the scope of one scopeable object to another

Let's say you want to create a new object, but the scope is somewhat complex, and you want to transfer the scope over from an existing object rather than have to define it all in the recipe. This is possible in three steps:

1. Use the appropriate processor to upload the new scopeable object without defining any scope in the XML.
2. Use `JamfObjectReader` to download the object you want to copy the scope from, specifying the value of `elements_to_retain` to `scope` so that all other keys are removed,
3. Use `JamfObjectUploader` to upload the XML to the new object you just created (specifying the `NAME` and `object_type` values). Since your XML contains only the scope, all other elements in this object will be retained.

These steps can be done with `JamfObjectReader` and `JamfObjectUploader`. To make things easy, `JamfObjectReader` automatically removes the ID key and computer or device objects. In which case, you just need to specify the source and destination URL and credentials, and the object type and name. This can be done in individual steps or using a recipe. I've provided an example: [CopyObject.jamf][6].

In this example, I'm requesting to copy a script called `MyScript.sh`. The credentials for each server are already in my Keychain so I don't need tp provide them in the command:

```bash
autopkg run -v CopyObject.jamf --key SOURCE_URL=https://mysourceserver.jamfcloud.com --key DESTINATION_URL=https://mydestinationserver.jamfcloud.com --key OBJECT_TYPE=script --key NAME=MyScript.sh
```

Additionally, you may wish to delete or replace a key when copying the object. `JamfObjectUploader` provides the keys `elements_to_remove` and `elements_to_replace` to allow you to switch out any object in the downloaded JSON or XML file with a value of your choice.

### Adjusting the scope of an existing scopeable object

If you want to add or remove elements of the scope from an existing object, such as add a target group or remove an exclusion, `JamfScopeAdjuster` can be used as many times as required to achieve the desired scope.  It's probably best for me to just point to the [README file][7] for how to use this.

### Enabling or Disabling a Policy, App Catalog App, or Extension Attribute

It's easy enough to go into the Jamf Pro web UI and toggle on or off the Enable switch on a policy, App Catalog app (where it's named "Deploy"), or script-based computer extension attribute. But if you need to do this programmatically, repetitively, or as part of a larger workflow, it may be worth using a recipe.

`JamfObjectStateChanger` is a simple processor to either enable or disable an object without making any other changes. Just feed it the `NAME` and `object_type`, and set the `object_state` value to either `enable` or `disable`. For extension attributes, you can also decide whether to keep or discard the existing data gathered, using the boolean `retain_data` key.

### Adding or removing a value from a pop-up choice-style extension attribute

You may be using pop-up choice-style extension attributes as criteria to scope items. There are many reasons why this may be the best choice to scope items. For example, my team use pop-up choice-style extension attributes where customers need categorise devices more granularly than by PreStage.

If you're scoping using EAs, you also need a smart group that contains the EA as a criterion. It can therefore be convenient to create a recipe that will add a value to an existing EA, then create a smart group containing that value. I've created a recipe that demonstrates how this works using `JamfObjectReader`, `JamfExtensionAttributePopupChoiceAdjuster`, `JamfObjectUploader`, and `JamfComputerGroupUploader`: [Computer-EA-Choice-Add.jamf][8].

### Listing and Downloading all objects of a particular type

Sometimes you just need to audit what is in an instance, or need to be able to parse through all objects of a particular type to look for patterns, errors, or something that needs to be updated. `JamfObjectReader` has some additional functions that can help here.

To get a list of all objects of a particular endpoint, use the `list_only` key, which will output a list of the IDs and names of each object. This can be used in a subsequent processor, or just outputted to a file if an output directory is specified using the `output_dir` key. We can create a generic recipe that will work for all object types as follows:

```yaml
Identifier: com.github.grahampugh.recipes.jamf.DownloadObjectList
MinimumVersion: "2.3"
Input:
  OUTPUT_DIR: /Users/Shared/Jamf/JamfUploader

Process:
  - Processor: com.github.grahampugh.jamf-upload.processors/JamfObjectReader
    Arguments:
      object_type: "%OBJECT_TYPE%"
      list_only: True
      output_dir: "%OUTPUT_DIR%"
```

This recipe is available in the `autopkg/grahampugh-recipes` repo, so you can just use that.  For example, to get a list of all computer groups in an instance and export it to a JSON file, we can run the following:

```bash
autopkg run -v DownloadObjectList.jamf --key OBJECT_TYPE=computer_group
```

The result is a file `/Users/Shared/Jamf/JamfUploader/<myinstanceshortname>-computer_groups.json`.

To download every object as its own file, we can use a similar recipe, replacing the `list_only` key with the `all_objects` key. Again, I've provided a recipe to do this.

```bash
autopkg run -v DownloadAllObjects.jamf --key OBJECT_TYPE=computer_group
```

Each object is downloaded in the format you would need if you were to upload it, so Classic API objects are downloaded as XML whereas Jamf Pro and Platform API objects are downloaded as JSON. The result is a folder full of files named after the instance shortname, object type, and object name, for example:

```txt
myinstanceshortname-computer_groups-Adobe Acrobat DC Is Installed.xml
myinstanceshortname-computer_groups-Adobe Acrobat Is Installed.xml
myinstanceshortname-computer_groups-Adobe Acrobat Reader DC Is Installed.xml
myinstanceshortname-computer_groups-Adobe Acrobat Reader Is Installed.xml
myinstanceshortname-computer_groups-Adobe After Effects 2024 Is Installed.xml
...
```

If you download scripts, extension attributes, or computer or mobile device profiles, then in addition to the XML/JSON, the respective payload is automatically extracted and placed in the same folder. This allows you to quickly and easily grab all the scripts or mobileconfig files from an instance for storage or use elsewhere. For example:

```txt
myinstanceshortname-scripts-Microsoft Office License.sh
myinstanceshortname-scripts-Microsoft Office License.sh.json
myinstanceshortname-scripts-PostinstallWacomTablet.sh
myinstanceshortname-scripts-PostinstallWacomTablet.sh.json
myinstanceshortname-scripts-PreinstallWacomTablet.sh
...
```

## Conclusion

These are just some examples of workflows that can be done with JamfUploader recipes. It's even possible to perform individual tasks without having to write recipes at all, using the provided wrapper script `jamf-upload.sh` - see my wiki entry for details on how that works: [jamf-upload.sh wiki page][9]. My team uses this frequently to upload packages and scripts to instances, for example.

Infrastructure as Code is becoming more and more into focus among Jamf Pro admins. Terraform is one way you can do this with Jamf Pro, including official support by Jamf, as announced during the [2025 JNUC keynote][10]. Terraform is an engine for driving the [Jamf Pro Provider][11] and [Jamf Platform Provider][12]. Terraform works best when used to control *everything* within a Jamf Pro instance. If something is edited manually in an instance, applying the terraform plan will put it back the way it was defined in the terraform modules.

Similarly, `JamfUploader` can be considered the Jamf Pro provider for the AutoPkg engine. Theoretically, you could use it to define everything in a Jamf Pro instance.

However, if your organisation works in a more hybrid fashion, where there may be some editing done in the web UI, or for example using other tools such as Jamf Insights, MJT, Jamf Sync, etc., or there is evolution of content away from the initial design, then `JamfUploader` offers the flexibility to control as much or little of the content in the instance as you are comfortable with. Especially for those of you already using AutoPkg and comfortable using recipes to upload packages, it's not a heavy lift to add recipes that create reliable, reproducible workflows without having to completely rewrite your maintenance manual. My own team spins up new instances with content using Terraform, and then uses JamfUploader for ongoing maintenance.

Hopefully this post has given you insights beyond the obvious `JamfUploader` workflows, into some of the other, lesser-known processors that provide an essentially complete framework for low-code, version-controlled, reproducible Jamf Pro maintanance. I hang around in the Mac Admins Slack `#jamf-uploader` channel, so feel free to ask for more details about any workflow there!

[1]: https://github.com/grahampugh/jamf-upload/blob/main/JamfUploaderProcessors/READMEs/Object%20Reference.md
[2]: https://developer.jamf.com/platform-api/reference/getting-started-with-platform-api
[3]: https://grahamrpugh.com/2024/07/30/jamf-blog-api-clients-and-roles.html
[4]: https://github.com/grahampugh/jamf-upload/blob/main/Jamf_Helper_Recipes/DeleteOldPackages.jamf.recipe.yaml
[5]: https://github.com/grahampugh/jamf-upload/blob/main/Jamf_Helper_Recipes/DeleteUnusedPackages.jamf.recipe.yaml
[6]: https://github.com/grahampugh/jamf-upload/blob/main/Jamf_Helper_Recipes/CopyObject.jamf.recipe.yaml
[7]: https://github.com/grahampugh/jamf-upload/blob/main/JamfUploaderProcessors/READMEs/JamfScopeAdjuster.md
[8]: https://github.com/grahampugh/jamf-upload/blob/main/Jamf_Helper_Recipes/Computer-EA-Choice-Add.jamf.recipe.yaml
[9]: https://github.com/grahampugh/jamf-upload/wiki/jamf-upload.sh
[10]: https://www.jamf.com/blog/jnuc-2025-keynote/
[11]: https://github.com/deploymenttheory/terraform-provider-jamfpro
[12]: https://github.com/Jamf-Concepts/terraform-provider-jamfplatform
[13]: https://github.com/grahampugh/jamf-upload/blob/main/Jamf_Helper_Recipes/DeleteObject.jamf.recipe.yaml

{% include urls.md %}
