---
layout: post
title:  "Jamf-Upload All The Things"
comments: true
---

## Introduction

[JamfUploader] started off as a successor to [JSSImporter], the now defunct [AutoPkg] processor designed to use a python framework called [python-jss] (also defunct) to upload packages to a Jamf Pro instance and create objects required to deploy that package, such as a category, a script, a smart group, and a policy. With JamfUploader, I decided to take a modular approach, with each object getting its own processor, for example `JamfCategoryUploader`, `JamfScriptUploader`, `JamfPackageUploader`, and so on. Over time, I and other contributors have added more and more processors to handle additional endpoints and perform additional tasks beyond just uploading something.

This modular approach makes JamfUploader a powerful and flexible tool for maintaining all content in Jamf Pro, but I suspect not too many of you are aware of the utility beyond that original use case of uploading a package. This post explains some of the wide variety of capabilities of JamfUploader.

## Setting up a fresh Jamf Pro instance

When setting up a new Jamf Pro instance, there a basically two types of content you have to create to make the instance useful:

1. Settings
2. Deployable content

Configuring the settings is something you generally only have to do once, except for any changes or new features that are introduced by Apple or Jamf over the lifetime of the instance. However, if you're maintaining multiple instances, it can be advantageous to keep the settings as code so that you can easily reproduce the same settings over and over, and push those new features and changes to all your servers consistently.

Perhaps surprisingly, this can all be done using JamfUploader. Thanks to a generic processor called `JamfObjectUploader`, plus a few specific processors such as `JamfAccountUploader`, `JamfAPIRoleUploader` and `JamfAPIClientUploader`, almost any setting can be stored in a template file in your own git repo, and AutoPkg recipes used to upload them. Currently this includes the following settings:

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

### How does that work?

Just as with traditional JamfUploader workflows, maintaining these settings as code is a combination of recipes and template files. One great thing about using JamfUploader to maintain these is that you can use the Jamf Pro GUI to generate the settings you want once, and then use the Swagger Docs, or developer.jamf.com, or indeed the `JamfObjectReader` processor (more on that later) to download the settings in exactly the right form you'll need to upload them to another instance (or the same instance as remediation/version control) - there's no abstraction into another syntax required.

Let's take a simple example of the Check-In Settings. If we download typical settings, we get a JSON file that looks like this:

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

However, if we need to deploy different settings to different servers, we can introduce variables into the template and override them in the recipe. In AutoPkg, variables are represented with names between percentage files, e.g. `%VARIABLE_NAME%`. So let's say we need to vary the check-in frequency, we'll replace a hard value with a variable, e.g.

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

> Note that your code editor might not like the syntax of the variable as it looks like you are trying to add a string without quotation marks, but JamfUploader will handle the substitution just fine.

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

You could put all your settings in a single recipe, but you will need separate template files for each settings type. Or, maintain individual recipes for each type of setting, and create a recipe list for all settings which you can then run when creating a new instance.

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

I have built the ability to use JamfUploader processors to read and write blueprints and compliance benchmarks. Specifically, the `JamfObjectReader` processor has been tested with the following endpoints:

- Blueprint
- Compliance Benchmarks - Rule
- Compliance Benchmarks - Baseline
- Compliance Benchmarks - Benchmark

The `JamfObjectUploader` processor has so far been tested with the following endpoints:

- Blueprint
- Blueprint - Deploy
- Blueprint - Undeploy

Please let me know your experience if you try these new endpoints out!

## Copying, Amending, and Deleting Content

A Jamf Pro server is rarely static. Setting up the initial settings and content is only the first hurdle. There are inevitable changes to make from day 2 onwards, for example:

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

- JamfObjectReader
- JamfObjectUploader
- JamfObjectDeleter
- JamfPolicyLogFlusher
- JamfScopeAdjuster
- JamfExtensionAttributePopupChoiceAdjuster
- JamfObjectStateChanger
- JamfPackageCleaner
- JamfUnusedPackageCleaner

Let's go through some scenarios where some of these processors might be useful.

### Deleting any object

This is an easy one. We provide the endpoint type and the object name, and the processor will delete that object. For legacy reasons, `JamfComputerGroupDeleter` and `JamfPolicyDeleter` also still currently exist, but they serve the same purpose.

### Cleaning up old packages

When you've accumulated old versions of installer packages for an existing title, you can use `JamfPackageCleaner` to clean them up, while retaining one or more of the most recent uploads. I've previously blogged about this in the post [Clean up your packages in Jamf Pro automatically with JamfPackageCleaner](https://grahamrpugh.com/2023/04/25/JamfPackageCleaner.html). I've also provided a recipe for this: [DeleteOldPackages.jamf][4]

### Cleaning up unused packages

If your file share distribution point is getting full, or you just want to tidy up your JCDS of unused packages, then you can use `JamfUnusedPackageCleaner` on a regular basis. This processor takes some time to run, as it needs to look in all policies, patch policies, and prestage enrollments to check each package. So it's best run as a standalone recipe. I've created a recipe for this: [DeleteUnusedPackages.jamf][5].

### Copying an object from one instance to another

If you need to copy any object from one Jamf Pro instance to another, it's actually a three-stage process:

1. Download the object from the source instance.
2. Parse the downloaded JSON or XML to remove keys that are specific to the source instance, such as the object ID, or computer/device objects listed in a smart group.
3. Upload the parsed object to the destination instance.

These steps can be done with `JamfObjectReader` and `JamfObjectUploader`. To make things easy, `JamfObjectReader` automatically removes the ID key and computer or device objects. In which case, you just need to specify the source and destination URL and credentials, and the object type and name. This can be done in individual steps or using a recipe. I've provided an example: [CopyObject.jamf][6].

Additionally, you may wish to delete or replace a key when copying the object. `JamfObjectUploader` provides the keys `elements_to_remove` and `elements_to_replace` to allow you to switch out any object in the downloaded JSON or XML file with a value of your choice.

### Copying the scope of one scopeable object to another

Let's say you want to create a new object, but the scope is somewhat complex, and you want to transfer the scope over from an existing object rather than have to define it all in the recipe. This is possible in three steps. First, use the appropriate processor to upload the scopeable object without defining any scope in the XML. Second, use `JamfObjectReader` to download the object you want to copy the scope from, specifying the value of `elements_to_retain` to `scope` so that all other keys are removed, and then using `JamfObjectUploader` to upload the XML to the new object you just created (specifying the `NAME` and `object_type` values). Since your XML contains only the scope, all other elements in this object will be retained.

### Adjusting the scope of an existing scopeable object

If you want to add or remove elements of the scope from an existing object, such as add a target group or remove an exclusion, `JamfScopeAdjuster` can be used as many times as required to achieve the desired scope.  It's probably best for me to just point to the [README file][7] for how to use this.

[1]: https://github.com/grahampugh/jamf-upload/blob/main/JamfUploaderProcessors/READMEs/Object%20Reference.md
[2]: https://developer.jamf.com/platform-api/reference/getting-started-with-platform-api
[3]: https://grahamrpugh.com/2024/07/30/jamf-blog-api-clients-and-roles.html
[4]: TODO
[5]: TODO
[6]: TODO
[7]: https://github.com/grahampugh/jamf-upload/blob/f4e70acb655101fe3bdae4b47b2b549a4a29b91a/JamfUploaderProcessors/READMEs/JamfScopeAdjuster.md

{% include urls.md %}
