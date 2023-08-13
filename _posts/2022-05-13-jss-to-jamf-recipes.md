---
layout: post
title:  "Comparing a JamfUploader recipe to a standard JSSImporter recipe"
comments: true
---

I have now deprecated the AutoPkg processor [JSSImporter], and it will likely stop working sometime between August and December of this year, 2022 - that is, unless somebody volunteers to take it over and is able to adapt it to work with Jamf's upcoming requirement for token-based API authentication. Once this change happens, you will no longer be able to use any `.jss` recipes.

[JamfUploader] is a new set of AutoPkg processors that I designed to replace JSSImporter, and it has the same functionality as JSSImporter (and much more!), but it cannot read `.jss` recipes. This is already working with token-based auth.

JSSImporter has many options, so `.jss` recipes can come in many forms. However, a "standard" of sorts was defined, and "standard" `.jss` recipes were offered in the [autopkg/jss-recipes][1] repository.

The purpose of this blog post is to describe the "standard" JSS recipe and compare it in detail to a `.jamf` recipe that uses JamfUploader processors .I hope this will help to show how to construct a `.jamf` recipe that will do exactly the same things as the `.jss` recipe you have been using until now.

## A standard JSS recipe

Standard JSS recipes were designed to perform the following, where `Firefox` may be substituted by `Google Chrome`, `TeamViewer` or whatever:

1. Create a category for the package if it doesn't already exist.
2. Upload a package, either to a Jamf Cloud or other cloud distribution point, or to an on-premises fileshare distribution point, and assign a category and other metadata to the package object in Jamf Pro .
3. Create or update a smart group named `Firefox-update-smart`, which contains the following criteria:

    ```txt
            Application Title:      is:         Firefox.app
    and     Application Version:    is not:     X.Y.Z
    and     Computer Group          member of:  Testing
    ```

4. Create a category for the policy if it doesn't already exist.
5. Create or update a Self Service policy named `Install Latest Firefox`, which includes the uploaded package, is scoped to the `Firefox-update-smart` smart group, and is assigned a category and an icon (the icon is uploaded).

Some applications require additional items to work properly such as a script and/or an extension attribute, but here we will assume the application doesn't need these.

To achieve this, each recipe requires access to additional files:

- A smart group template file in XML form.
- A policy template file in XML form.
- A saved copy of the app icon as a PNG.

These should be stored in the same directory as the recipe, or copied into the RecipeOverrides folder.

Let's look at each of the files:

### Firefox.jss.recipe

Here is the `.jss` recipe in both `yaml` and `plist` formats:

{% gist 72870a3bbcda44c9f77c9fbe1beaced3 %}

{% gist 4d33ec7ba939648cfbacae0b46d28af1 %}

Notice that although there are several API actions required to achieve the four steps above, those actions are all bundled into one process. Keep that in mind as we look at a `.jamf` recipe later.

The recipe requires these Input keys:

```yaml
  NAME: Firefox
  CATEGORY: Productivity
  GROUP_NAME: "%NAME%-update-smart"
  GROUP_TEMPLATE: SmartGroupTemplate.xml
  POLICY_CATEGORY: Testing
  POLICY_TEMPLATE: PolicyTemplate.xml
  SELF_SERVICE_DESCRIPTION: Mozilla Firefox is a free and open source web browser.
  SELF_SERVICE_ICON: Firefox.png
```

### SmartGroupTemplate.xml

The standard SmartGroupTemplate looks like this:

{% gist 33ae2af3e8450b1aad2ab77f76d61337 %}

Here, notice some more keys that are not provided in the Input array of the recipe:

- `group_name` - this is interpreted by the JSSImporter processor from the `GROUP_NAME` key above. I'm not sure why `GROUP_NAME` is not used in the template.
- `JSS_INVENTORY_NAME` - this is a key that is interpreted by the JSSImporter processor as `%NAME%.app`, but can optionally be supplied in the recipe.
- `VERSION` - this is interpreted by the JSSImporter processor from the `version` key supplied by a parent recipe. I'm not sure why `version` is not used.

### PolicyTemplate.xml

Here's the policy template:

{% gist 951681d659213a840b2a61547935f8d3 %}

Again, we have some keys that are not supplied in the recipe but interpreted by the JSSImporter processor:

- `PROD_NAME` - this is interpreted as `NAME` but can be supplied in the recipe. I never really understood what this special key was for.
- `VERSION` - see above.

Additionally, the scope, package and scripts sections are omitted, worked out automatically by JSSImporter. This is great for "compliant" policies but is a bit of a black box for more complex setups, and had bugs. For example, JSSImporrter recipes never were able to supply both parameter labels to scripts and parameter values to policies.

```xml
    <scope>
        <!--Scope added by JSSImporter-->
    </scope>
    <package_configuration>
        <!--Package added by JSSImporter-->
    </package_configuration>
    <scripts>
        <!--Scripts added by JSSImporter-->
    </scripts>
```

## A functionally equivalent Jamf recipe

Now let's look at a functionally equivalent `.jamf` recipe. JamfUploader recipes do not bundle all the different API actions into one process. Each API action gets its own processor. So, when we want to do all the same things that a "standard" `.jss` recipe does, we will use the following processors:

1. `JamfCategoryUploader` - Create a category for the package if it doesn't already exist.
2. `JamfPackageUploader` - Upload a package, either to a Jamf Cloud or other cloud distribution point, or to an on-premises fileshare distribution point, and assign a category and other metadata to the package object in Jamf Pro.
3. `JamfComputerGroupUploader` - Create or update a smart group named `Firefox-update-smart`.
4. `JamfCategoryUploader` - Create a category for the policy if it doesn't already exist.
5. `JamfPolicyUploader` - Create or update a Self Service policy named `Install Latest Firefox`, which includes the uploaded package, is scoped to the `Firefox-update-smart` smart group, and is assigned a category and an icon (the icon is uploaded).

Including the `JamfCategoryUploader` processors is optional. If the categories already exist, and/or you want the fail if they don't, then these don't need to be in the recipe at all.

And if you don't want to create a smart group or policy, but just upload the package, you can omit the `JamfComputerGroupUploader` and `JamfPolicyUploader` processors too - just use `JamfPackageUploader`.

However, let's look at a `.jamf` recipe that functionally equivalent to a "standard" `.jss` recipe.

### Firefox.jamf.recipe.yaml

Here is the `.jamf` recipe in both `yaml` and `plist` formats:

{% gist 2460ba2a59fb30efdfe467d6f10f8d70 %}

{% gist d70fff8935f656ac242ec4163d5be706 %}

The Input array is not much changed from the `.jss` recipe:

```yaml
  NAME: Firefox
  CATEGORY: Productivity
  GROUP_NAME: "%NAME%-update-smart"
  GROUP_TEMPLATE: JamfSmartGroupTemplate.xml
  TESTING_GROUP_NAME: Testing
  POLICY_CATEGORY: Testing
  POLICY_TEMPLATE: JamfPolicyTemplate.xml
  POLICY_NAME: "Install Latest %NAME%"
  SELF_SERVICE_DISPLAY_NAME: "Install Latest %NAME%"
  SELF_SERVICE_DESCRIPTION: Mozilla Firefox is a free and open source web browser.
  SELF_SERVICE_ICON: "%NAME%.png"
  UPDATE_PREDICATE: "pkg_uploaded == False"
```

In this example, I have included extra keys for `POLICY_NAME` and `SELF_SERVICE_DISPLAY_NAME` so that these can be overridden (in contrast, those names are fixed in the `.jss` recipe), and I've included the `TESTING_GROUP_NAME` which is hard-coded as `Testing` in the SmartGroupTemplate of the `.jss` recipes, so that this can also be overridden.

The only other extra key is `UPDATE_PREDICATE`. More on that below.

Now take a look at the processes in the recipe.

First, we are supplying a category name and asking `JamfCategoryUploader` to create it if it doesn't exist.

```yaml
  - Processor: com.github.grahampugh.jamf-upload.processors/JamfCategoryUploader
    Arguments:
      category_name: "%CATEGORY%"
```

Next, we supply the category name into the `JamfPackageUploader` processor, and ask it to upload the package. It gets the `pkg_name` and `pkg_path` from the parent recipe, so we don't need to supply those values here.

```yaml
  - Processor: com.github.grahampugh.jamf-upload.processors/JamfPackageUploader
    Arguments:
      category_name: "%CATEGORY%"
```

Next comes a `StopProcessingIf` processor. This recipe includes a `StopProcessingIf` process, to check that the package was uploaded or not. `JamfPackageUploader` will not upload the package if the name is the same as an existing package. If the package is not uploaded, the recipe run will stop at `StopProcessingIf` because the predicate `pkg_uploaded == False` is matched. Including an Input key for `UPDATE_PREDICATE` allows us to force the recipe to continue to update smart group and policy even if no new package was uploaded. This provides the equivalent workflow to the JSSImporter key `STOP_IF_NO_JSS_UPLOAD` that users of JSS recipes will be familiar with.

```yaml
  - Processor: StopProcessingIf
    Arguments:
      predicate: "%UPDATE_PREDICATE%"
```

Next we supply the Smart Group Template's filename and the name of the smart group. The template can be situated anywhere in the same repo as the recipe, or in the RecipeOverrides folder. If not in these places, a full filepath can be provided.

```yaml
  - Processor: com.github.grahampugh.jamf-upload.processors/JamfComputerGroupUploader
    Arguments:
      computergroup_template: "%GROUP_TEMPLATE%"
      computergroup_name: "%GROUP_NAME%"
```

After another `JamfCategoryUploader` process to create the policy's category if absent, we supply the policy name, the policy template's filename, and the icon's filename.

```yaml
  - Processor: com.github.grahampugh.jamf-upload.processors/JamfPolicyUploader
    Arguments:
      policy_template: "%POLICY_TEMPLATE%"
      policy_name: "%POLICY_NAME%"
      icon: "%SELF_SERVICE_ICON%"
```

### JamfSmartGroupTemplate.xml

The standard SmartGroupTemplate for a `.jamf` recipe looks like this:

{% gist 200763ece4807a084a20c5691cb96cd0 %}

It is almost identical to the template for the .`jss` recipe. The only differences are that there are no special interpretation of the group name or version strings, so we supply `GROUP_NAME` and `version` directly. Also, I have decided to allow the name of the "Testing" group to be overridden, so I use the key `TESTING_GROUP_NAME` rather than hard-coding in the `Testing` group name.

### JamfPolicyTemplate.xml

Here's the policy template for the `.jamf` recipe:

{% gist c07ff16ae3b4d702bebc19949546c27e %}

In comparison to the template for the `.jss` recipe, the main difference is that there is no "special" handling of the `package_configuration`, `scope` and `scripts` sections. These are instead exactly as you will see if you download an existing policy from your Jamf server using the Classic API. 

Furthermore, there is no special interpreted keys in the template. So there is no `PROD_NAME` or `VERSION`. Instead we supply `POLICY_NAME` directly from the Input array, and `version` comes directly from the parent recipe.

## Conclusion

I hope this has given a good explanation of the small differences between the outgoing `.jss` recipe format and the new `.jamf` recipes. 

If you want to see more examples, I have converted most of the recipes from the old [jss-recipes][1] repo into `.jamf` format, available in my own recipe repo at [grahampugh-recipes/Jamf_Recipes][2].

You can also easily convert any "standard" `.jss` recipes from other repos, or ones that you wrote yourself, using the [JamfRecipeMaker][3] tool that I introduced in [a previous blog post](/2022/05/03/jamf-recipe-maker.html).

[1]: https://github.com/autopkg/jss-recipes
[2]: https://github.com/autopkg/grahampugh-recipes/Jamf_Recipes
[3]: https://github.com/autopkg/grahampugh-recipes/wiki/JamfRecipeMaker

{% include urls.md %}
