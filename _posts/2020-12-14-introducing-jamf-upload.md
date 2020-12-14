---
layout: post
title: "JamfUploader - new AutoPkg processors for importing packages to Jamf Pro"
comments: true
---

My first post for a few months, and apologies in advance as it's a long one...

I've made a new set of AutoPkg processors for importing packages to Jamf Pro. After some testing, I have now begun writing and using new recipes to replace the `.jss` recipes we have been using until now.

## Why?

[JSSImporter] is a huge benefit to my organisation, and yet has never 100% fit our workflow. I took over maintenance JSSImporter after Shea Craig was dragged away to bigger and better things. This allowed me to make some small changes to JSSImporter so that I could create "production" recipes, where I could reference smart groups but not overwrite them if they aleady existed.

However, some problems remained that were difficult to fix, because the changes needed to be made in [python-jss] - code that I fully admit I have never fully understood. And last year, a big problem loomed: when Apple stated that they will remove python runtimes from macOS in a "future version", I decided that, though I am no python whizz, I needed to attempt to upgrade the code of `python-jss` and all the associated projects to python 3.

I failed. The code of `python-jss` in particular is so clever and abstracted, with one particular aspect of it so broken in python 3, that I just couldn't figure it out. Fortunately, I received amazing expert help from Elliot Jordan, who discovered a way to shoehorn the "python 2 way" into a python-3 compatible version, so it still works today, but I still don't understand it! I spent far too many hours trying to understand the code, all the while thinking that it didn't need to be this complicated, especially just for the needs of JSSImporter, which uses just a subset of the power of `python-jss`.

Due to this gap in my understanding of the python-jss code, various niggling problems with JSSImporter remain:

- How do I attach script parameter values to policies?
- How come scripts need a separate template file, but Extension Attribute scripts have to be XML-escaped and embedded in a template?
- How do I create smart groups without scoping them directly to a policy, when I need them to be criteria within another group?
- Why are some variables in Input keys not replaced but others are?
- Why are some files in repos not found unless they are copied to the RecipeOverrides folder, but some are?
- Wouldn't it be great to not have to hack around so much to allow some groups to be overwritten but not others?
- What if I could upload a config profile from a recipe?
- Why isn't there a super-simple "package only" option for people using Jamf Patch Management?
- Why do some people's packages upload properly and others not?

Furthermore, my organisation were never able to use any existing `.jss` recipes from the community, because the "standard" set by those recipes does not meet my organisation's rather specific needs (we need an exclusion smart group in our test recipes). Ultimately, I needed more flexibility than JSSImporter or any single processor could provide.

# Back to basics

The process of importing a package into Jamf Pro is actually not one, but many possible steps:

- Check that categories exist for the package, scripts and policies, and create them if not.
- Upload one or more packages either to JCDS or copy it to an SMB or local repo, and then create or update the package metadata.
- Upload any scripts and extension attributes.
- Upload any smart/static group templates associated with the policy/ies.
- Upload any policies and any associated icons.

I decided that I would get more flexibility by making separate processors for each type of object that you might want to upload to Jamf. With this model, just like other AutoPkg processors, you can add just the processors you need to achieve what you need to do for a particular package and workflow.

I created the following processors:

- `JamfCategoryUploader`
- `JamfPackageUploader`
- `JamfScriptUploader`
- `JamfExtensionAttributeUploader`
- `JamfPolicyUploader`

Each processor is entirely self-contained and requires no dependencies - you do not need to install JSSImporter, python-jss or any other package. Due to the limitations of AutoPkg, this does mean there is code repeated in each processor, but I decided this was worth it to avoid the need for installing anything. Because we also have a need to delete an untested policy when the package is staged to production, I also created a `JamfPolicyDeleter` processor.

Each processor can be added to an AutoPkg recipe as many times as needed, just like the other familiar AutoPkg procesors like `URLDownloader`, `FileCreator` etc.

I hope that some other Jamf administrators will get interested in this project, as it is more likely to become robust and improve with increased use and participation.

## Q. Should I use JamfUploader processors instead of JSSImporter?

If your process follows closely the "standards" developed by Shea and Elliot Jordan, then a `.jss` recipe looks more simple than a `.jamf` recipe (yes, I'm claiming `.jamf`™️ 😀). If your needs deviate from that `jss-recipes` standard, I believe this is where `JamfUploader` processors will be of most benefit to you.

## Q. Are the JamfUploader processors more reliable at uploading packages than JSSImporter?

Good question! There is no public API for uploading packages to Jamf Cloud, so if you are a Jamf Cloud customer (or use some other cloud-based distribution point), you are relying on a private undocumented API. You're probably also aware that even uploading packages into Jamf Cloud via the GUI is not 100% sucessful.

Another big problem with JSSImporter and Jamf Cloud was the fact that each API call in a sequence may be sent to a different cluster node, and changes from the previous request may not have synchonised in time. Thanks to some recent hints from Jamf about the use of cookies with the API, I have incorporated some changes to both JamfUploader and JSSImporter that will hopefully address this issue.

There is still a separate issue to do with load balancer timeouts that may affect both Jamf-Upload and JSSImporter, however. There are also ongoing problems with uploading very large packages (>2GB) to Jamf Cloud using python's `requests` module, which is used by `JSSImporter`.

For all these reasons, I settled on using `curl` for API requests. This has proved generally more reliable, but is still reliant on an unofficial API for uploading packages.

> **Please contact Jamf Support about obtaining an officially supported package upload API endpoint!**

## Q. How do I use the JamfUploader processors?

The processors are in the `grahampugh-recipes` repo in the AutoPkg GitHub organisation. So, you just need to run the following command:

    autopkg repo-add grahampugh-recipes

It's still early days and I'm still fleshing out the processors. So, you would expect to have to run `autopkg update-trust-info` quite frequently were you to adopt these processors now. But, at least there is nothing to install.

## Q. Can I override existing JSS recipes to use JamfUploader processors? Is there an easy conversion tool?

No, and No. There is no "compatibility layer" built into the JamfUploader processors, as the workflow is too different. I probably won't build a recipe conversion tool for the same reason, though I do intend to build up more examples that emulate the policies and groups created by standard `.jss` recipes. However, our recipe standards are different from those of most other organisations, and I am also publishing the actual recipes we use (see Resource List below).

## Q. Can I use my existing PolicyTemplate and SmartGroupTemplate from JSSImporter?

No. JamfUploader recipes automate slightly fewer things than JSSImporter. For example, it does not inject scope, scripts and package object XML into the policy template - it will only replace simple variables (using the same method as AutoPkg, i.e. `%VARIABLE%`). So, you need to include those XML parts into your template. This is a deliberate decision as it allows more flexibility and independence between the upload of each API endpoint, and avoids some of those problems like the confusiuon between script parameter labels and parameter values in policies.

It's best to look at the existing examples to see the differences - checkout the Resources at the end of this post.

## Q. Under what circumstances would it be worth me changing from using JSSImporter to JamfUploader?

Once you start to deviate from the standard, I would argue that this project will suit you better. For example:

- If you are just uploading a package and don't need a policy, you don't need a recipe at all - you can just use `JamfPackageUploader` as a post-processor or add it to your Recipe Override. This might also particularly suit people using Jamf's Patch management system.
- If you are hand-crafting `.jss` recipes because you are adding multiple policies, adding exclusion scopes, and/or need more flexibility in the naming conventions of JSSImporter, the recipes you create will be more readable and have a more predictable flow.
- If you want more flexibility about which objects you want to update during a recipe and which not, for example if you are automating your production policies and do not want to overwrite scope since you have administrators creating bespoke scope.
- If you want to use AutoPkg to manage your scripts, extension attributes and uninstaller policies.

If your scripts need parameter headings and your policies need to supply script parameter values, you're probably already looking around for another solution...

## Q. When should I definitely not use JamfUploader?

If you have more than one distribution point in your repo, that currently won't work. I would welcome contributions towards making that work with JamfUploader.

## Q. I'm interested in trying it out / helping development / submitting PRs / writing recipes

Awesome! Check out the resources below, and join the `#jamf-upload` channel in MacAdmins Slack. This channel is for discussion and help using these processors and the sister project which is a set of standalone python scripts which can be used to do the same things that the AutoPkg processors do.

## Q. Is JSSImporter dead, Jim?

No. I understand the obligation of taking on a popular open source project, ann still have a direct need for it, since I maintain hundreds of internal `.jss` recipes that will take a long time to convert.

However, if you're interested in becoming a contributor to JSSImporter, or even taking over its maintenance along with python-jss and the other projects, I definitely want to hear from you.... especially if you understand python better than I do (which is not a high benchmark). Hop on over to the `#jss-importer` MacAdmins Slack channel and say hello.

## Resources

- The [jamf-upload Wiki](https://github.com/grahampugh/jamf-upload/wiki/Jamf-AutoPkg-Processors)
- The [JamfUploader README docs](https://github.com/autopkg/grahampugh-recipes/tree/master/JamfUploaderProcessors/READMEs)
- Example recipes:
  - [Jamf Recipes](https://github.com/autopkg/grahampugh-recipes/tree/master/Jamf_Recipes)
  - [Jamf Package-Only Recipes](https://github.com/autopkg/grahampugh-recipes/tree/master/Jamf_Package_Only_Recipes)
  - [Jamf Script Recipes](https://github.com/autopkg/grahampugh-recipes/tree/master/Jamf_Script_Recipes)
  - [Jamf Uninstall Recipes](https://github.com/autopkg/grahampugh-recipes/tree/master/Jamf_Uninstall_Recipes)
  - The [Jamf Recipes used at ETH Zürich](https://github.com/eth-its/autopkg-mac-recipes), including an explanatory [Wiki](https://github.com/eth-its/autopkg-mac-recipes/wiki)

{% include urls.md %}
