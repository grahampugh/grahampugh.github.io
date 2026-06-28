---
layout: post
title: "Introducing Conditional Logic for JamfUploader and JamfCLIRunner"
comments: true
---

# Introduction

[AutoPkg] recipe syntax is not a programming language, but rather a markup for underlying python processors which adhere to a framework to ensure they are all compatible. Recipes essentially contain a list of actions, with all variables being added to the environment so that any processor can access the value of any variable generated at the start of the run (from Inputs, preferences, or command line parameters), or during the course of the run (output variables from each processor).

Since the AutoPkg framework itself contains no logical operators (if, else), it’s up to individual processors to include any logic that they need. This is generally confined within each processor, such as with the `StringReplacer` processor, which will only act on a matching input string but doesn’t depend on the presence of that string - a basic if/else logic - but without any direct influence on a subsequent processor. This means that each processor has to be valid for a recipe - you can’t add different processors based on an if/else discovery from a previous process. 

For example, for a recipe where you need to supply a particular software’s installer material manually with the `PKG` option, but that could potentially be provided to you in a ZIP archive or not, you can’t create a recipe to handle both circumstances. That’s because the `Unarchiver` processor doesn’t have an option to just skip to the next processor if the input file is not a ZIP - it will simply fail.

There is one obvious exception. The `StopProcessingIf` processor allows you to decide whether the recipe should continue or not based on a predicate. This is commonly used in JamfUploader recipes, for example, to end the recipe successfully without further action if the package that was created in the parent pkg recipe is the same as the one already in cache. But it doesn’t allow you to skip on to another processor - there’s no “else” option.

# Are there any use cases for conditional logic in AutoPkg recipes?

The scenario above is a simple example, but it’s arguable whether it would be worth building a more complex framework into the AutoPkg Framework just for this. It would be relatively trivial to create a Pull Request to build an option into the `Unarchiver` processor to ignore an input file that is not a ZIP archive, or to make an alternative processor in your own repo. 

Indeed, this happened with the `PathDeleter` processor, which would fail if any of the paths you added to the recipe to be deleted did not exist. To overcome this in circumstances where the outcome of some previous processor could be unpredictable, fellow Mac Admin James Smith created his own processor, `FriendlyPathDeleter`, which would just ignore any non-existent paths. This functionality has recently been folded into `PathDeleter` in the most recent beta version.

The life for Jamf Pro admins building package deployment options can be more complex than Munki admins. For example, if you wish to offer some users a self-service option for a particular software title, but automatically deploy that same title to different users, you only need one munki recipe - the scope of deployment (with apologies for using a Jamf term) is determined in Munki’s manifests, which are not adjusted by the AutoPkg recipe (they don’t change when a title version is updated).

With Jamf Pro, when a title version is updated, a common task is to update at least one smart group criterion to reflect the latest version string (or a regular expression based on that string). For this reason it makes sense to automate this action in a [JamfUploader] recipe, so we add a processor that will create or update the smart group. However, if you’re offering both Self Service and automatic installations to different scopes, you need two smart groups, and two policies. That’s fine, just add two `JamfComputerGroupUploader` and two `JamfPolicyUploader` processors to the recipe, one for Self Service and one for the automated installation (recurring trigger).

If you have more than one Jamf Pro instance and need different content in each, for example Self Service in one instance and recurring trigger in the other, then it gets more complicated - you need two recipes. Or some customer wants an uninstaller policy but the other doesn’t? That’s another recipe.

For such circumstances, it would be neat if there was some logic to be able to skip a process based on some predicate, say if an input key was set to `CREATE_SELF_SERVICE_POLICY == False`. 

Another way of removing the need for a second recipe would be with some if-then-else logic that determined which policy template to use in a `JamfPolicyUploader` process depending on a predicate. For example, if `CREATE_SELF_SERVICE_POLICY == True`, use the policy template `Policy-SelfService.xml`, but otherwise use `Policy-Ongoing.xml`. You would always need to provide keys that might not be used, like `SELF_SERVICE_DESCRIPTION`, but that’s OK, it wouldn't cause the recipe to fail.

# Could conditional logic be added to the AutoPkg framework?

Anything is possible, but let’s consider how that would look.

One way to do this would be with some kind of processor that could run sub-processors based on predicates. That would result in strange looking recipes containing indented lists of processors, perhaps something like this:

```yaml
Process:
...
  - Processor: ConditionalLoop
    predicate: "%CREATE_SELF_SERVICE_POLICY% == True"
    true_processes:
      - Processor: com.github.grahampugh.jamf-upload.processors/JamfComputerGroupUploader
        Arguments:
          group_template: ComputerGroup-Application-Installed.xml
          group_name: "%NAME% Installed"
          replace_group: True
      - Processor: com.github.grahampugh.jamf-upload.processors/JamfPolicyUploader
        Arguments:
          policy_template: Policy-SelfService.xml
          policy_name: Install %NAME% - Self Service
          replace_policy: True
    false_processes:
      - Processor: com.github.grahampugh.jamf-upload.processors/JamfComputerGroupUploader
        Arguments:
          group_template: ComputerGroup-Application-CurrentVersionInstalled.xml
          group_name: "%NAME% Current Version Installed"
          replace_group: True
      - Processor: com.github.grahampugh.jamf-upload.processors/JamfPolicyUploader
        Arguments:
          policy_template: Policy-Ongoing.xml
          policy_name: Install %NAME% - Ongoing
          replace_policy: True
```

It’s doable (and potentially without a rewrite to AutoPkg itself), but introducing sub-processors as a concept is a big shift, which could break all sorts of tooling that was built into or around AutoPkg (not least `autopkg info`).

Another way would be to introduce some sort of processor that could skip a defined number of subsequent processors based on a predicate. This would surely need to be core to AutoPkg itself. Something like this:

```yaml
Process:
...
  - Processor: SkipNextProcesses
    predicate: "%CREATE_SELF_SERVICE_POLICY% == True"
    number_to_skip: 2
  
  - Processor: com.github.grahampugh.jamf-upload.processors/JamfComputerGroupUploader
    Arguments:
      group_template: ComputerGroup-Application-Installed.xml
      group_name: "%NAME% Installed"
      replace_group: True
      
  - Processor: com.github.grahampugh.jamf-upload.processors/JamfPolicyUploader
    Arguments:
      policy_template: Policy-SelfService.xml
      policy_name: Install %NAME% - Self Service
      replace_policy: True 

  - Processor: SkipNextProcesses
    predicate: "%CREATE_SELF_SERVICE_POLICY% == False"
    number_to_skip: 2
    
  - Processor: com.github.grahampugh.jamf-upload.processors/JamfComputerGroupUploader
    Arguments:
      group_template: ComputerGroup-Application-CurrentVersionInstalled.xml
      group_name: "%NAME% Current Version Installed"
      replace_group: True
      
  - Processor: com.github.grahampugh.jamf-upload.processors/JamfPolicyUploader
    Arguments:
      policy_template: Policy-Ongoing.xml
      policy_name: Install %NAME% - Ongoing
      replace_policy: True 
```

This avoids indentations and subprocessors, but could be complex to implement.

# How I’ve implemented conditional logic for JamfUploader

The need for conditional logic within my team recently reached a tipping point for the implementation of a particular type of recipe, so I decided to go ahead with two updates. One is a self-contained processor that any AutoPkg user could make use of - `ConditionalVariableAssigner` - and the other is a new key in all JamfUploader processors - `skip_if`.

## ConditionalVariableAssigner

The new `ConditionalVariableAssigner` processor allows you to assign the value of a key based on a predicate. For example, in the scenario where we want to either create a Self Service or a recurring trigger policy based on an input key, we can set a value to a key which we then use in subsequent processors.

```yaml
Process:
...
  - Processor: com.github.grahampugh.recipes.commonprocesses/ConditionalVariableAssigner
    Arguments:
      predicate: "%CREATE_SELF_SERVICE_POLICY% == True"
      conditional_key: group_name
      value_if_true: "%NAME% - Installed"
      value_if_false: "%NAME% - Current Version Installed"

  - Processor: com.github.grahampugh.recipes.commonprocesses/ConditionalVariableAssigner
    Arguments:
      predicate: "%CREATE_SELF_SERVICE_POLICY% == True"
      conditional_key: group_template
      value_if_true: ComputerGroup-Application-Installed.xml
      value_if_false: ComputerGroup-Installed.xml    
      
  - Processor: com.github.grahampugh.recipes.commonprocesses/ConditionalVariableAssigner
    Arguments:
      predicate: "%CREATE_SELF_SERVICE_POLICY% == True"
      conditional_key: policy_name
      value_if_true: Install %NAME% - Self Service
      value_if_false: Install %NAME% - Ongoing
      
  - Processor: com.github.grahampugh.recipes.commonprocesses/ConditionalVariableAssigner
    Arguments:
      predicate: "%CREATE_SELF_SERVICE_POLICY% == True"
      conditional_key: policy_template
      value_if_true: Policy-SelfService.xml
      value_if_false: Policy-Ongoing.xml
      
  - Processor: com.github.grahampugh.jamf-upload.processors/JamfComputerGroupUploader # name/template keys conditionally defined
    Arguments:
      replace_group: True 
      
  - Processor: com.github.grahampugh.jamf-upload.processors/JamfPolicyUploader # name/template keys conditionally defined
    Arguments:
      replace_policy: True 
```

The above isn’t actually a great example as it is better served by the `skip_if` key described below, but does give you an idea of how it works. A better example would be where the template for the Self Service policy needs to be different depending on the presence of multiple target smart groups, or a computer group template needs to be different due to the individual needs of the users in different instances.

## JamfUploader skip_if keys

The new `skip_if` key allows you to add a processor to a recipe but make it immediately return to the process list without any action if a predicate is matched. It doesn’t fail, and it doesn’t stop, it simply does nothing.

Let’s continue with a similar example to above, but this time we have two optional keys, `CREATE_SELF_SERVICE_POLICY` and `CREATE_ONGOING_POLICY`. That means our recipe can optionally create one, the other, both, or neither of the groups and policies depending on the value of these keys, providing full flexibility.

```yaml
Process:
...
  - Processor: com.github.grahampugh.jamf-upload.processors/JamfComputerGroupUploader
    Arguments:
      group_template: ComputerGroup-Application-Installed.xml
      group_name: "%NAME% Installed"
      replace_group: True
      skip_if: "%CREATE_SELF_SERVICE_POLICY% == False"
      
  - Processor: com.github.grahampugh.jamf-upload.processors/JamfComputerGroupUploader
    Arguments:
      group_template: ComputerGroup-Application-CurrentVersionInstalled.xml
      group_name: "%NAME% Current Version Installed"
      replace_group: True
      skip_if: "%CREATE_ONGOING_POLICY% == False"
      
  - Processor: com.github.grahampugh.jamf-upload.processors/JamfPolicyUploader
    Arguments:
      policy_template: Policy-SelfService.xml
      policy_name: Install %NAME% - Self Service
      replace_policy: True
      skip_if: "%CREATE_SELF_SERVICE_POLICY% == False"
      
  - Processor: com.github.grahampugh.jamf-upload.processors/JamfPolicyUploader
    Arguments:
      policy_template: Policy-Ongoing.xml
      policy_name: Install %NAME% - Ongoing
      replace_policy: True
      skip_if: "%CREATE_ONGOING_POLICY% == False"
```

The possibilities are almost endless. 

For example, I am using the logic in a single recipe that can create any Jamf Auto Update title, where the logic can decide if the “installed” group needs to use an Extension Attribute or not, which configuration profiles (e.g. PPPC, System Extension, etc.) need to be deployed depending on title, and whether we want to create a Self Service policy or deploy automatically. Previously this required around 8 different recipes to cover all combinations, plus a wrapper script to determine which profiles to push.

We are also using `skip_if` in recipes where some older content in an instance needs to be deleted if found. An example would be replacing the individual Affinity 2 apps with the new single Affinity app - we can use a `JamfObjectReader` processor to discover whether something is present, and skip a `JamfObjectDeleter` process if the object is not found, preventing a recipe failure.

I have also added the same `skip_if` logic to the `JamfCLIRunner` processor, for those of you starting to experiment with Jamf's Platform APIs.

# Conclusion

I came up with `ConditionalVariableAssigner` before `skip_if`, and the latter is better for most scenarios concerning Jamf Pro. It will allow my team to reduce the number of recipes in our repo, though of course needs time to rewrite them all - no doubt something an LLM could figure out pretty well with good instructions.

Is there a use for `skip_if` in all AutoPkg processors? I’m not sure - it would add flexibility for sure, but I don’t know if the demand is there. AutoPkg has been around for well over ten years and I’ve personally only noticed 2 or 3 people publicly asking about the possibility of conditional logic being used or added. My team’s primary usage would be for that scenario I initially mentioned where we are given installer material for particular non-publicly-available apps in different formats depending on the whims of our customers.

I’m curious to hear from you if you have a scenario where you could use either `skip_if` or the `ConditionalVariableAssigner` processor in a Jamf or any other environment.