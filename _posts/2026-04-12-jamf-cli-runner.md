---
layout: post
title:  "jamf-cli, and how you can use it with AutoPkg to automate complex Jamf workflows"
comments: true
---

## Introduction

[jamf-cli] is a new, standalone, golang-based command-line tool developed by my colleagues Keaton Svoma and Neil Martin at Jamf. It provides convenient, abstracted access to the various Jamf APIs, including Jamf Pro, Jamf Protect, and the new Platform APIs that will be available as a public beta in the near future (possibly by the time you read this!).

Users of my own [jamf-upload.sh] tool will be familiar with the concept - you don't need to know the endpoints, just give it an object type and an action, and perhaps a data file or blob to upload. Just like `jamf-upload.sh`, and [Jamf API Utility], `jamf-cli` also supports storing and accessing credentials in the keychain.

Let's look at how these two tools handle reading a computer group, as a simple example. Both these commands will output the exact same JSON smart computer group object to `/tmp/example-smart_computer_group-All Desktops.json`:

    jamf-cli pro smart-computer-groups get --name "All Desktops" --profile example > "/tmp/example-smart_computer_group-All Desktops.json"

    ./jamf-upload.sh read --type smart_computer_group --name "All Desktops" --url example --output /tmp

## Where jamf-cli excels

`jamf-cli` is a tool for performing single tasks, with additional conveniences for repeating some tasks across multiple instances (see the `multi` parameter). It uses golang SDKs under the hood, making it cross-platform (currently macOS- and Linux-compatible). A useful comparison to make between `jamf-cli` and the SDKs is to think about the relationship between `jamf-upload.sh` and the [JamfUploader] processors.

`jamf-cli` is simpler to install, as it is a compiled binary containing the SDKs, in contrast to `jamf-upload.sh`, which isn't compiled and depends on the installation of [AutoPkg] (to be fair, I made `jamf-upload.sh` primarily to help with testing the JamfUploader processors).

`jamf-cli` also goes a bit further, with a number of extremely useful "power commands" for reporting state, as well as some features lifted from JamfUploader and [Multitenant Jamf Tools], such as adjusting scope, discovering unused objects, and converting monolithic profiles.

All in all, it's a big step forward from any previous individual tool in terms of useability and functionality.

## What jamf-cli isn't

`jamf-cli` is not, in itself, Infrastructure-as-Code, Configuration-as-Code, or a CI-CD tool. However, since it is a command-line tool like `autopkg`, it can be used as a basis for Configuration-as-Code, and included in your CI-CD workflows.

## Where does jamf-cli fit in terms of automation?

While a terraform workflow, using the Jamf Pro, Protect and Platform terraform providers based on the golang SDKs ([1], [2], [3]), may suit many for maintaining their Jamf instances, for some organisations this is too prescriptive and inflexible - it largely prevents the ability to use the user interfaces for Jamf products to make one-off changes, since they would get undone the next time terraform is induced.

For individual but reproducible workflows with idempotency, you need to create a hierarchical list of `jamf-cli` commands that you can run repeatedly, setting options as required to either overwrite or leave alone any existing content. CI-CD workflows within shell scripts can definitely be built.

## But hang on, that sounds quite a lot like an AutoPkg recipe

The JamfUploader processors allow you to write an AutoPkg recipe to process a workflow of multiple steps, with the ability to decide on an object-by-object basis in each individual recipe when to replace the content of existing objects and when to leave them alone, as well as performing more esoteric actions like updating the scope of an object. See my previous post "Jamf-Upload All The Things" ([4]) for examples.

`jamf-cli` can now do all these things too. So, theoretically, I could replace some of the core parts of JamfUploader with `jamf-cli` commands, although that would introduce a dependency on top of AutoPkg that I have previously tried to avoid with JamfUploader. So, for now at least, I'm not intending to do that.

## AutoPkg + jamf-cli = JamfCLIRunner

Instead, I've taken a stab at creating a single new AutoPkg processor for driving workflows using `jamf-cli`, as a proof of concept of how it could be used in conjunction with the wide-ranging functionality that AutoPkg enjoys beyond JamfUploader for building complex workflows - a prime example of course being the creation of a deployable package and importing it to Jamf Pro, the creating the content required to deploy said package. The result is `JamfCLIRunner` ([5]).

JamfCLIRunner is built with a similar concept to JamfUploader in mind - a single process for a single action. You can add as many processes as you need - one to create a category, one to upload a script, one to update a smart group, and so on. It can work with the `StopProcessingIf` processor just like JamfUploader, so as to only update objects if necessary, meaning it can be used with scheduled recipes.

Using a single processor while maintaining the flexibility enjoyed in JamfUploader makes for longer recipes, as more parameters have to be provided to direct jamf-cli which are abstracted from JamfUploader due to the many different processors available - for example, since you use JamfScriptUploader purely to upload a script, you don't need a parameter to say "script" or "apply", and you don't need to construct or provide a JSON object that builds the script object in Jamf Pro, because that's been built into the processor.

On the other hand, you're not limited by what endpoints are available (this is also true with JamfUploader due to the `JamfObjectReader` and `JamfObjectUploader` processors, but I digress...).

Let's look at a process in a recipe for uploading a smart group in both JamfUploader and JamfCLIRunner, both of which hace been set to replace the content of any existing group.

First, using JamfComputerGroupUploader:

```yaml
  - Processor: com.github.grahampugh.jamf-upload.processors/JamfComputerGroupUploader
    Arguments:
      replace_group: True
      computergroup_name: "%GROUP_NAME%"
      computergroup_template: "%GROUP_TEMPLATE%"
```

Compare that with JamfCLIRunner:

```yaml
  - Processor: com.github.grahampugh.recipes.JamfCLIRunner/JamfCLIRunner
    Arguments:
      profile: example
      type: pro
      endpoint: smart-computer-groups
      action: apply
      confirm: "true"
      from-file: "%GROUP_TEMPLATE%"
```

The above is running the following command:

    jamf-cli --profile example pro smart-computer-groups apply --from-file "/path/to/template.json" --yes

I've also provided the ability in JamfCLIRunner to provide the template inline as data, as follows:

```yaml
  - Processor: com.github.grahampugh.recipes.JamfCLIRunner/JamfCLIRunner
    Arguments:
      profile: example
      type: pro
      endpoint: smart-computer-groups
      action: apply
      confirm: "true"
      data:
        name: "%GROUP_NAME%"
        description: Computers with outdated %NAME% package
        criteria:
          - name: Application Title
            priority: 0
            searchType: is
            value: "%NAME%.app"
            andOr: "and"
          - name: Application Version
            priority: 1
            searchType: is not
            value: "%version%"
            andOr: "and"
      output_vars:
        installed_group_id: id
        installed_group_name: name
```

The `data` YAML object is converted to JSON and added to the command as `stdin`.

By the way, the `output_vars` become important with JamfCLIRunner - this gives the opportunity to provide new variable names for the `id` and `name` of objects created, which can be used in subsequent processors without them getting overwritten by some in-between processor that also outputs an `id` and `name`.

For a working example of a complex recipe using JamfCLIRunner that is equivalent to a traditional JamfUploader recipe ([6]), checkout `JamfPro-DeployPackage-CarbonCopyCloner.jamfclirunner` ([7]). There are also a bunch of simpler recipes in that folder showing a range of use cases for JamfCLIRunner.

## Will JamfCLIRunner replace JamfUploader?

At the time of writing, `jamf-cli` is a less-than-one-week-old, largely Claude-generated tool that is not totally proven in the real world. I'm not totally in the "move fast and break things" camp, although I know that my colleagues are working hard to iron out the initial bugs, some of which I encountered while writing JamfCLIRunner. I have confidence that it will become a robust, extremely popular, and widely used tool in the next few months, especially the power commands and as the Platform API goes into general availability.

However, although I don't have any telemetry, the various interactions, numerous conference presentations, the 1,074 `#jamf-uploader` Slack channel members, and last but not least our own use of JamfUploader internally, means that JamfUploader isn't going away any time soon.

Because `jamf-cli` can handle blueprints, compliance benchmarks, Jamf Protect, and the other upcoming Platform APIs, I'm not yet decided whether to dedicate any time into creating new JamfUploader processors for these - JamfCLIRunner will work out of the box for these. Let me know if you think there's a reason to give JamfUploader this functionality.

## Conclusion

Things are moving very fast thanks to the accessibility of LLMs (especially Claude Code) within Jamf (and other organisations with talented Jamf Admins). What used to take months and years to plan and develop is turning into a fun little weekend project, so new stuff that looks cool and seems to be better than whatever we had before is being churned out all the time. It's hard to predict what will stick and which tools from the pre-LLM days will become quickly obsolete.

It may be that people don't bother using AutoPkg for the Jamf API parts of their workflow any more, so I don't know if JamfCLIRunner will be useful, or if JamfUploader use will die off. While I personally value the ability to use a single type of markup for a complete workflow that contains both Jamf and non-Jamf related actions (i.e. a recipe), time will tell whether that remains a widely held view, especially as AI will now easily write the complete workflow for you.

In the meantime, I intend to continue development, and my next task is to allow the use of keychain objects created in either `jamf-cli` or Jamf API Utility with JamfUploader, so that you don't need to worry about maintaining multiple keychain objects for multiple tools. That would also allow an AutoPkg recipe to seamlessly use both JamfUploader and JamfCLIRunner processors as appropriate, providing options for anyone still interested in using AutoPkg to power their version-controlled, reproducible Jamf workflows (of which I am one!). Watch this space.

[1]: https://github.com/deploymenttheory/go-api-sdk-jamfpro
[2]: https://github.com/Jamf-Concepts/jamfprotect-go-sdk
[3]: https://github.com/Jamf-Concepts/jamfplatform-go-sdk
[4]: https://grahamrpugh.com/2025/11/17/jamf-upload-all-the-things.html
[5]: https://github.com/autopkg/grahampugh-recipes/tree/main/JamfCLI-Runner
[6]: https://github.com/autopkg/grahampugh-recipes/blob/main/Jamf_Recipes/CarbonCopyCloner.jamf.recipe.yaml
[7]: https://github.com/autopkg/grahampugh-recipes/blob/main/JamfCLI-Recipes/JamfPro-DeployPackage-CarbonCopyCloner.jamfclirunner.recipe.yaml

{% include urls.md %}
