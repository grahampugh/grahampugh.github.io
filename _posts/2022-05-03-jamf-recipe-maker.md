---
layout: post
title:  "JamfRecipeMaker - use AutoPkg to make Jamf recipes automatically!"
comments: true
---

In case you missed it, the [JSSImporter] processor is deprecated, and will cease to function when Jamf remove basic authentication from the Classic API endpoints, which they have announced will happen sometime between August and December 2022.

The [JamfUploader] project is my replacement of [JSSImporter], for Jamf Pro customers that want to continue to benefit from the power of [AutoPkg] for obtaining deployable packages for thousands of third party applications and other software.

JamfUploader-based (`.jamf`) recipes are modular in design (see my original blog post, [JamfUploader - new AutoPkg processors for importing packages to Jamf Pro](/2020/12/14/introducing-jamf-upload.html)). The design is significantly different to JSSImporter-based (`.jss`) recipes, so new recipes need to be written.

## Is there an easy way to convert a `.jss` recipe to a `.jamf` recipe?

JamfUploader is designed to be more flexible than JSSImporter, so a straight conversion may well not be the best course of action. For example, if you're using Patch Management, or creating multiple policies, JSSImporter recipes were not well designed for this, and you can benefit from the new opportunities available with JamfUploader.

However, if your policy and smart group design is compatible with the "standard" design devised for `.jss` recipes, you may be contemplating having to write a bunch of `.jamf` recipe that do exactly the same thing as those existing "standard" `.jss` recipes that are currently available in the [jss-recipes][1] and various other repos, notably [rtrouton-recipes][2].

To help achieve this, I've developed a novel idea - a new AutoPkg processor that reads from a `.jss` recipe while running it, and writes a new `.jamf` recipe. 

**Say hello to `JamfRecipeMaker`.**

## Huh? An AutoPkg processor that reads one recipe and writes another?

Exactly. Sounds weird, but when you run an AutoPkg recipe, all the relevant variable values are written as environment variables, so it's all available for doing whatever you want. In a "standard" `.jss` recipe, the only values we really need to obtain are:

- `ParentRecipe`
- `NAME`
- `CATEGORY`
- `POLICY_CATEGORY`
- `SELF_SERVICE_DESCRIPTION`

We just need to write these to a file in the correct structure of a `.jamf` recipe. This is pretty much what Elliot Jordan's excellent [Recipe Robot] app is doing when generating a `.jss` or indeed `.munki` recipe, after all.

## How does JamfRecipeMaker work?!

We can use `JamfRecipeMaker` as a pre-processor (or post-processor if you like) when running a `.jss` recipe. There are 2 main options:

(1) Create a recipe that just uploads a package and nothing else. This is functionally equivalent to `.jss-upload` recipes as was described in [Daz Wallace][@dazwallace]'s 2019 blog post [Using Autopkg for package Uploads to Jamf Cloud only][4]. These types of `.jamf` recipe do not need any information from a `.jss` recipe (we only need `ParentRecipe` and `NAME`), so can be run directly from a `.pkg` recipe.

```bash
autopkg run Flux.pkg --pre com.github.grahampugh.recipes.commonprocessors/JamfRecipeMaker
```

(2) Create a recipe that uploads a package, smart group and policy. This is functionally equivalent to standard `.jss` recipes.

```bash
    autopkg run Flux.jss --key make_policy=True --post com.github.grahampugh.recipes.commonprocessors/JamfRecipeMaker
```

The advantage of adding the processor as a pre-processor is that if the `.jss` recipe stops mid-run, the `.jamf` recipe is already generated.

Both these options make recipes in YAML format by default. You can instead output a PLIST recipe by adding `--key format=plist` to your command.

If you wish to ensure that the categories associated with the package and policy are created if they do not yet exist, add `--key make_categories=True`.

The `make_categories`, `make_policy` and `format` keys can instead be added to your AutoPkg prefs:

```bash
defaults write ~/Library/Preferences/com.github.autopkg.plist make_policy -bool YES
defaults write ~/Library/Preferences/com.github.autopkg.plist make_categories -bool YES
defaults write ~/Library/Preferences/com.github.autopkg.plist format plist
```

You'll probably want to supply your own Recipe Identifier prefix too, either using a `--key` or by adding to your prefs:

```bash
defaults write ~/Library/Preferences/com.github.autopkg.plist RECIPE_IDENTIFIER_PREFIX com.acme.autopkg-recipes
```
And you can specify the output path for the `jamf` recipes. The default is whatever directory you run the command from (`.`):

```bash
defaults write ~/Library/Preferences/com.github.autopkg.plist RECIPE_OUTPUT_PATH /path/to/my/recipe-repo/Jamf_Recipes
```

For full documentation, incluiding more options for feeding in variables, see the [JamfRecipeMaker wiki][3].

## Do I have to install anything special to use JamfRecipeMaker?

No, so long as you have added the [grahampugh-recipes][5] repo, you should be good to go.

There are some additional requirements, specifically the `ruamel.yaml` python module. That's because I yanked most of the code from my existing [plist-yaml-plist] project for converting PLIST to YAML and vice versa. The processor will attempt to install `ruamel.yaml` into the AutoPkg python library if missing, so you shouldn't have to do anything in advance to make this work. But let me know if you encounter any problems with that.

## One more thing! I've already used JamfRecipeMaker to make around 100 `.jamf` and `-pkg-upload.jamf` recipes

Since it's possible to run this against a recipe list, I decided to convert all the working recipes in the [jss-recipes][1] repo to `.jamf` and `-pkg-upload.jamf` recipes. These are now in the [grahampugh-recipes][5] repo (see the `Jamf_Recipes` and `Jamf_Package_Upload_Only` folders), and they are searchable via the `autopkg search` command.

### Caveats

Please note that I don't use these recipes, as my organisation's requirements are not the same as that "standard" design. So, these generated recipes have not been tested. They are simply there to try and help adoption of JamfUploader sooner.

The `-pkg-upload.jamf` recipes are all likely to work, because all the `.jss` recipes did complete when I was generating them, and all the `.jamf` recipes should upload the packages. However, `JamfRecipeMaker` does not currently look for scripts, extension attributes or other customisations away from the "standard" basic `.jss` recipe design, and I have not edited the automatically-generated recipes. So, treat the recipes as a basis for developing your own recipes to suit your own particular workflows. If you decide to use these recipes in production and discover the recipes that aren't working as they should, I would welcome PRs that add the scripts, extension attributes or whatever else is required to make them fully functional.

## Conclusion

I hope the `JamfRecipeMaker` processor and the auto-generated `.jamf` recipes will make the migration from JSSImporter to JamfUploader quicker and easier for some organisations.

I am aware that [AutoPkgr] has still not been updated to include support for YAML-based recipes, but is still widely used by members of the Mac Admins community. I could easily generate all the `.jamf` recipes again in PLIST format with a different recipe identifier, but I'm concerned about all the duplicate entries in the AutoPkg search results that would occur as a result.

I would consider removing the YAML recipes and re-creating them as PLIST recipes if there is enough demand. Let me know in the [MacAdmins Slack Team] `#jamf-upload` or `#autopkg` channels if this would be useful.

[1]: https://github.com/autopkg/jss-recipes
[2]: https://github.com/autopkg/rtrouton-recipes
[3]: https://github.com/autopkg/grahampugh-recipes/wiki/JamfRecipeMaker
[4]: https://dazwallace.wordpress.com/2019/03/12/using-autopkg-for-package-uploads-to-jamf-cloud-only/
[5]: https://github.com/autopkg/grahampugh-recipes

{% include urls.md %}
