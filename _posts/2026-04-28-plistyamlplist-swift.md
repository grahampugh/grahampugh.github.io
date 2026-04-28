---
layout: post
title:  "Plist-Yaml-Plist revisited - a Swift binary for converting PLIST to YAML or YAML to PLIST"
comments: true
---

## Introduction

[Back in 2018][1] ([1]), I created the first version of [plist-yaml-plist], a python-based tool for converting YAML files to PLIST, or converting PLIST files to YAML. I made this primarily so that I could write and maintain AutoPkg recipes in YAML format, as it was much easier for me to read, and is more concise in comparison to PLIST-formatted recipes. This was before AutoPkg supported YAML-formatted recipes, so I routinely ran `plistyamlplist` whenever I added or altered a recipe to convert it to PLIST. I also built in a mass-conversion facility where you could convert all files in a folder.

## (Not so) Swiftly moving on

With recent developments with artificial intelligence helping us abstract ideas from knowledge of specific coding languages, the `plistyamlplist` project seemed like a good place to start experimenting with Swift. The result is the [plist-yaml-plist-swift] project, a standalone Swift binary that can replace the original python project, maintaining exactly the same functionality. I've now published the first signed-and-notarized release of the swift `plistyamlplist` binary, which you can obtain either as an installer package or a ZIP file from the [project releases page][2] ([2]). The installer package will add `plistyamlplist` to `/usr/local/bin` so you don't need to adjust your `PATH`.

Let's revisit the functionality since you may have missed the post eight years ago.

## Converting files

The `plistyamlplist` binary detects the file type you are wanting to convert

To create a PLIST clone of your YAML-crafted recipe (or any other file) in the same folder, run the following command. If `.recipe` is in the filename, the outputted file will be named in the AutoPkg standard: `SomeApp.pkg.recipe`. for other `.yaml` files, the suffix will be swapped out for `.plist`.

```sh
plistyamlplist /path/to/SomeApp.pkg.recipe.yaml
```

The other way around is of course possible:

```sh
plistyamlplist /path/to/SomeApp.pkg.recipe
```

If you want to specify a different output folder, provide the destination filepath as another argument:

```sh
plistyamlplist /path/to/SomeApp.pkg.recipe /different/path/to/SomeApp.pkg.recipe.yaml
```

## Batch converting

`plistyamlplist` accepts glob pattern matches, so you can convert all YAML (or PLIST) files in a folder using a star:

```sh
plistyamlplist '/path/to/*.yaml'
```

Alternatively, if you supply a source folder and a destination folder, then all files in that folder will be converted in the destination folder, maintaining folder structure:

```sh
plistyamlplist /path/to/YAML/ /path/to/output/
```

If your path contains `YAML` or `_YAML`, the tool automatically determines output paths. For example, if you are maintaining YAML files in a YAML folder (e.g. `/project/YAML/subfolder/file.yaml`), `plistyamlplist` will output to `/project/subfolder/file.plist`. This was most useful when AutoPkg didn't support YAML files so they could be tucked away, but may still have a use case today, for example with preference files.

## Tidying up YAML recipes

If you converted AutoPkg recipes files from PLIST or JSON to YAML using some other tool, they may be in a valid format, but not optimally readable. I am a fan of maintaining the top-level key order that was traditional in PLIST recipes, and putting a space between `Description`/`Comment`/`Identifier`/`ParentRecipe`/`MinimumVersion`, the `Input` list, the `Process` array, and any subsequent keys. I also prefer each Process to have the `Processor` listed above the `Arguments`, even though this is counteralphabetical. As an example:

```yaml
Description: Downloads the latest version of KNIME and creates a package.
Identifier: com.grahampugh.pkg.KNIME
ParentRecipe: com.grahampugh.download.KNIME
MinimumVersion: "2.3"

Input:
  BUNDLE_ID: org.knime.product
  NAME: KNIME

Process:
- Processor: AppPkgCreator
  Arguments:
    pkg_path: '%RECIPE_CACHE_DIR%/%NAME%-%version%.pkg'
```

`plistyamlplist` has these opinions baked in, so will be implemented when doing a conversion, but you can also use the `--tidy` option to "tidy up" an existing YAML recipe (or batch of YAML recipes) to match this format.

```sh
plistyamlplist /path/to/YAML/ --tidy
```

## Convert JSON to PLIST?

Yes, for some reason I've forgotten, a added the option to convert JSON to PLIST ,so this option has also been ported over, in case you wanted to maintain recipes in JSON format (I don't know why you would, but you could). Again, the file type is automatically detected.

## Conclusion

I've always found it easiest to learn a new language looking at a project that already exists that I'm interested in. Getting AI to do the initial port of `plistyamlplist` over from python to swift gives me the opportunity to look at the language in a project I'm very familiar with. So, while the project is probably not written in the most efficient or up-to-date swift yet, hopefully, I'll learn ways to improve it and teach myself swift at the same time. As a bonus, a compiled binary is easier to sign, notarize, and distribute, and is easier for folks to install and use.

Let me know if you find any bugs (thanks to Tyler Sparr for already having done so!).

[1]: https://grahamrpugh.com/2018/08/29/autopkg-recipes-in-yaml.html
[2]: https://github.com/grahampugh/plist-yaml-plist-swift/releases

{% include urls.md %}
