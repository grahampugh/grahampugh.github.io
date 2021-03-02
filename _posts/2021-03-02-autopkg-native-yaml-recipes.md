---
layout: post
title: "YAML-formatted AutoPkg recipes can now be run natively without conversion to plist"
comments: true
---

Back in 2018, I published a blog post about how you can write AutoPkg recipes in `yaml` format, and convert them to `plist`-format to run them. See [Writing AutoPkg recipes and other plist-formatted files in yaml][1]. I've been writing all my recipes in `yaml` format asince then.

`plist` and `yaml` are both serialization standards. They both handle arrays, dictionaries, lists etc., and both can be directly imported as python data objects.

I'm very happy to say that thanks to a lot of work in particular from Elliot Jordan ([@homebysix]), AutoPkg version 2.3, released today, now supports YAML-formatted recipes natively.

Taken from my post in 2018, here is a typical recipe in YAML format:

```yaml
Description: Downloads the latest version of KNIME and creates a package.
Identifier: com.grahampugh.pkg.KNIME
MinimumVersion: "2.3"
ParentRecipe: com.grahampugh.download.KNIME

Input:
  BUNDLE_ID: org.knime.product
  NAME: KNIME

Process:
  - Processor: AppPkgCreator
    Arguments:
      pkg_path: "%RECIPE_CACHE_DIR%/%NAME%-%version%.pkg"
```

So much easier to read, even without colour coding. Easier to type. Easier to auto-generate.

## Can I start writing all my recipes in YAML format?

If you have private repositories of AutoPkg recipes, there is no reason for you to maintain `plist`-formatted recipes any more, if you prefer to use `yaml`.

However, you should use caution for some time if writing recipes for public consumption. Since it will take some time for everybody to upgrade to AutoPkg version 2.3, there will be a limit to compatibility of `yaml`-based recipes.

If keeping recipes in both formats, I do not recommend keeping them in the same repo, as this could lead to unexpected events. Additionally, do not add repos containing both sets of recipes to your AutoPkg recipe search paths, particularly if the `plist` and `yaml` recipes have the same Identifiers.

## What about RecipeOverrides?

Elliot has also added the ability to create your overrides in `yaml` format. Simply use the `autopkg make-override` command with the `--format=yaml` parameter:

```bash
autopkg make-override --format=yaml SomeRecipe.pkg
```

## Converting plist to yaml

If you wish to convert your recipes from `plist` to `yaml`, whilst acknowledging the note of caution described above, I wrote a small tool to do this.

[plist-yaml-plist]

The wrapper script `plistyamlplist.py` contains intelligence to convert in ether direction.

To convert your `yaml`-crafted recipe to `plist` format, just run the following command:

```bash
/path/to/plistyamlplist.py /path/to/KNIME.pkg.recipe /path/to/KNIME.pkg.recipe.yaml
```

(I created a symlink to `/usr/local/bin/plistyamlplist` so I don't need to specify a path every time.)

I recommend that you run this script using `python3`, as it can then do some additional prettifying of the `yaml` recipe to make it even easier to read, such as putting spaces before the Process dictionary, and placing the `Processor` key before `Arguments` key.

**Note that you should set the `MinimumVersion` value in your `yaml`-formatted recipes to `2.3` since no older version of AutoPkg will be able to read them.**

> If writing your own conversion tools, I recommend python's `ruamel.yaml` module. This is a development of the older `PyYAML` module, and includes the safeguards to ensure that strings and values are properly escaped as required.

## More details about yaml syntax in AutoPkg recipes

- If a value is set to `true` or `false` without quotes, it is detected as a boolean value.
- If a value is a whole number it will be an `int`, or if it is a valid float number it will be identified as such.
- Any other value is considered a string. This includes semantic version strings such as `1.0.0`, so these do not need to be quoted.
- Strings do not normally need to be escaped, but if they contain certain characters which are used in `yaml`, you should escape the string with single quotes, i.e. `"string"`. You may also need to do this if you wish for a valid number to be treated as a string.
- Dictionaries (`<dict>...</dict>` in plist-based recipes) are handled with a simple indent. In the above example, the `Input`section is a dictionary, and the indent is two spaces. You must be consistent in the `yaml` file (unlike in the `plist`).
- An array (`<array>...</array>`) is handled with a `-` at the same indent as the array's key, or indented two characters (either is fine). In the above example, the `Process` section is an array containing one dictionary. All items in that dictionary should be at the same level of indent as the first item's key name (so, in this example, the `Processor` and `Argument` keys).
- Converting a `plist` to a `yaml` will normally sort the items alphaetically. This is fine for AutoPkg, but if you wish to structure the yaml file in an easier order for reading, converting your files using `plistyamlplist` with python3 ensures the order as shown in the example above.

## Scripts and multiline textblocks in yaml files

The [yaml literal scalar style](http://www.yaml.org/spec/1.2/spec.html#id2795688) makes the reading of text blocks easier, and means you don't need to escape characters such as newlines. This is similar to using herestrings in bash scripts. The syntax for a literal scalar is to use a `|` to indicate a literal block of text, and to indent each line of the block two characters from the key name, e.g. as follows:

```yaml
file_content: |
  #!/bin/bash

  if [[ $1 ]]; then
      exit 0
  else
      exit 1
  fi
```

## Some example recipes

I have now shifted all my `yaml` recipes to their own repos, so that they can be used directly without interference of the `plist`-formatted versions. So check out the recipes in the following repos:

- [grahampugh/recipes-yaml](https://github.com/grahampugh/recipes-yaml) - these are the same recipes that exist in `plist` format in [autopkg/grahampugh-recipes](https://github.com/autopkg/grahampugh-recipes)
- [eth-its/autopkg-mac-recipes-yaml](https://github.com/eth-its/autopkg-mac-recipes-yaml) - these are the same recipes that exist in `plist` format in [eth-its/autopkg-mac-recipes](https://github.com/eth-its/autopkg-mac-recipes) (mainly [JamfUploader][jamfuploader] recipes).

[1]: https://grahamrpugh.com/2018/08/29/autopkg-recipes-in-yaml.html

{% include urls.md %}
