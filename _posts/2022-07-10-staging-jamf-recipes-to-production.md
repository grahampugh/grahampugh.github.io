---
layout: post
title:  "Stage packages to production with AutoPkg and JamfUploader"
comments: true
---

[AutoPkg], in conjunction with the [JamfUploader] processors, provides an automated way to import packages into Jamf Pro. For many, the package that has been imported should be tested before it is staged to production. Therefore, a common practice is for the AutoPkg `.jamf` recipe to create a policy that is scoped only to a group of testing computers. For example, when we import `Firefox-102.0.pkg` into Jamf Pro, we can write our `Firefox.jamf` recipe so that it creates a policy with that package attached to it, which is scoped to a smart or static computer group called `Firefox testing`.

Once we have tested version 102.0, how do we then stage this particular package to a policy that is scoped to all production computers? We can't just run the same AutoPkg recipe again with a different policy template, because by then version 102.0.1 could have been released, and we would inadvertently push it straight to production without it having been tested.

Apart from the obvious but tedious method of logging into the Jamf Pro admin console to manually make changes, one option is to use a different tool that works with the Jamf APIs, such as the University of Utah Marriott Library's [jctl](https://github.com/univ-of-utah-marriott-library-apple/jctl/wiki). This includes a tool called [pkgctl](https://github.com/univ-of-utah-marriott-library-apple/jctl/wiki/pkgctl) which you can use to swap out packages in existing policies.

Some people create policies that run once-per-computer, and flush them when they are ready to stage the next version to production. `jctl` can also be used to flush the policy. However, that means the policy will run even if the same version has already been installed by some other means. In some cases, that can result in an installation error which may become apparent to the end users.

A way to avoid this is to scope your policies dynamically based on what is already installed on clients. You include smart group crtieria that look for the specific application version. Now your workflow is more complicated, because when you upload a new package, you need to change criteria in one or more smart groups to match the new version that you are pushing to production. You would probably end up having to script a wrapper around `jctl` or a similar framework to suit your needs, and you will encounter multiple exceptions that need individual attention once your app portfolio increases in size, because not everything you deploy is a simple app bundle with a reliable version number in the app's `Info.plist` file.

> (`jss_helper` was a tool that did the job of promoting a package to production, but unfortunately it is dependent on `python-jss`, which is now deprecated, and will cease to function in the coming months.)

At my organisation, we scope policies dynamically, not only for the reasons stated above, but also so that users do not see items in Self Service that are already up to date. To improve this experience further, we also use [VersionRegexGenerator](/2020/09/17/better-jamf-policy-version-control-autopkg.html) to scope our policies in a safer way that removes the risk of downgrading. This makes tools like `jctl` even more difficult to use for staging.

I wanted a fully automated process for staging to production that didn't require any manual work in the Jamf Pro console, or even the manual running of scripts, because my organisation has multiple Jamf instances to deal with. Ideally I wanted AutoPkg itself to handle the staging process, rather than rely on a different tool. This will allow all exceptions to the standard app to be included in the recipes. For us, this is additionally helpful because we already use a wrapper around AutoPkg that runs a recipe multiple times over all our Jamf instances, which is integrated into a [GitLab Runner scheduling process](/2020/07/10/gitlab-runner-and-autopkg.html).

**The main requirement of this workflow is that when AutoPkg stages the package to production, it must use the existing package that is already in Jamf Pro and has been tested, rather than checking again for a new package.**

To achieve this:

1. We need separate AutoPkg recipes for the testing workflow (which will import the package) and the staging workflow (which will not import anything, simply assign the package to the correct policies).
2. We need the information from the testing run to be available for the staging run.

To handle this, I created two new shared processors: `LastRecipeRunResult` and `LastRecipeRunChecker`.

## LastRecipeRunResult

This is a post-processor that we add to the end of the normal AutoPkg run. It outputs the information about the uploaded package (name, version) to a JSON file in the Cache of that recipe. It requires no inputs, so can be added as follows:

```bash
autopkg run -v Firefox.jamf \
--post com.github.grahampugh.recipes.postprocessors/LastRecipeRunResult
```

## LastRecipeRunChecker

This is a pre-processor which reads the values from the JSON file that was written by the `LastRecipeRunResult` processor. It requires an input key which is the identifier of the recipe that ran the `LastRecipeRunResult` processor - normally the identifier of the override recipe, for example `local.jamf.Firefox`. The processor can be added to the `autopkg` command as shown below, or incorporated in the "production" recipe itself.

```bash
autopkg run -v Firefox-prod.jamf \
--pre com.github.grahampugh.recipes.preprocessors/LastRecipeRunChecker \
--key recipeoverride_identifier=local.jamf.Firefox
```

## AutoPkg recipes that stage to production

We provide a set of `.jamf` recipes for staging packages to production. We name them with `-prod.jamf` at the end, e.g. `Firefox-prod.jamf`. These recipes do not have a parent recipe. Instead, they consist of the following processes:

* `LastRecipeRunChecker`: Obtains the information about the most recent package that was uploaded by the normal AutoPkg recipe.
* `JamfUploadSharepointStageCheck`: we have an internal SharePoint site for recording tests that are carried out on applications. Apps that are ready to stage are marked as such in this site. This processor reads the SharePoint site to see if the package is ready to be staged. I won't discuss that here as it's very bespoke to our internal systems.
* `StopProcessingIf`: this checks the result of `JamfUploadSharepointStageCheck` to see if something is ready to stage to production. If not, the recipe stops here.
* `JamfComputerGroupUploader`: in these staging recipes, the relevant smart groups are created or updated. This is normally 5 groups, so there are 5 `JamfComputerGroupUploader` processor steps.
* `JamfPolicyUploader`: the necessary policies are created or updated. In our case, this is normally 5 policies.
* `JamfPolicyDeleter`: the testing policy is now superfluous, so is deleted.

Where necessary, scripts and extension attributes are of course included. Notice that there is no `JamfPackageUploader` in these recipes. We know that the package has already been uploaded, so that processor is not required - we only need to know the name of the package, and this comes out of `LastRecipeRunChecker`.

## Conclusion

I have described one way of fully automating the import of a package and its staging to production. For my organisation's multi-context Jamf environment in particular, this provides a flexible, reliable method that accounts for all the varieties and exceptions that are inevitable when dealing with deploying large numbers of third party applications and tools.

All our recipes are in an open GitHub repo, so if you are interested in examples, check out the following:

* [Jamf_Recipes](https://github.com/eth-its/autopkg-mac-recipes-yaml/tree/main/Jamf_Recipes): these are the "testing" recipes. We add the `LastRecipeRunResult` as the last step in the recipe itself rather than run it as a post-processor, to allow our automation to work for a small number of recipes where we don't want this step.
* [Jamf_Staging_Recipes](https://github.com/eth-its/autopkg-mac-recipes-yaml/tree/main/Jamf_Staging_Recipes): these are the "staging-to-production" recipes as described above. Since these recipes don't have parent `pkg` and `download` recipes, we can make use of template parent recipes, so that we don't have to copy-paste the same processor steps into all the recipes. You'll see these template recipes at the bottom of the listing, for example `_TEMPLATE-prod.jamf.recipe.yaml`.

{% include urls.md %}
