---
layout: post
title:  "Writing AutoPkg recipes and other plist-formatted files in yaml"
comments: true
---

[AutoPkg] recipes are `plist` files, a form of XML. Even the most simple of Autopkg recipes are somewhat voluminous. For example, here is `pkg` recipe that just does one thing, package up an `app` within a `dmg` using the `AppPkgCreator` processor:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>Description</key>
	<string>Downloads the latest version of KNIME and creates a package.</string>
	<key>Identifier</key>
	<string>com.grahampugh.pkg.KNIME</string>
	<key>Input</key>
	<dict>
		<key>BUNDLE_ID</key>
		<string>org.knime.product</string>
		<key>NAME</key>
		<string>KNIME</string>
	</dict>
	<key>MinimumVersion</key>
	<string>1.0.0</string>
	<key>ParentRecipe</key>
	<string>com.grahampugh.download.KNIME</string>
	<key>Process</key>
	<array>
		<dict>
			<key>Arguments</key>
			<dict>
				<key>pkg_path</key>
				<string>%RECIPE_CACHE_DIR%/%NAME%-%version%.pkg</string>
			</dict>
			<key>Processor</key>
			<string>AppPkgCreator</string>
		</dict>
	</array>
</dict>
</plist>
```

Without colour-coding in your text editor (shout out to [Atom] for Plist-colouring), it can be confusing to look at.

What if you could write your recipes in [yaml]? Then it would look like this:

```yaml
Description: Downloads the latest version of KNIME and creates a package.
Identifier: com.grahampugh.pkg.KNIME
Input:
  BUNDLE_ID: org.knime.product
  NAME: KNIME
MinimumVersion: 1.0.0
ParentRecipe: com.grahampugh.download.KNIME
Process:
- Processor: AppPkgCreator
  Arguments:
    pkg_path: '%RECIPE_CACHE_DIR%/%NAME%-%version%.pkg'
```

So much easier to read, even without colour coding. Easier to type. Easier to auto-generate.

`plist` and `yaml` are both serialization standards. They both handle arrays, dictionaries, lists etc. Therefore they are quite compatible.

# Converting yaml to plist

Unfortunately, AutoPkg doesn't support recipes in `yaml`. So if you want to write your recipes in `yaml`, you then have to convert them to `plist` format before AutoPkg can use them.

I wrote a small tool to do this, actually two tools, one to convert `yaml` to `plist` and one to convert `plist` to `yaml`.

[plist-yaml-plist]

To convert your `yaml`-crafted recipe to `plist` format, just run the following command:

```
/path/to/yaml-plist.py /path/to/KNIME.pkg.recipe.yaml /path/to/KNIME.pkg.recipe
```

(I created a symlink to `/usr/local/bin/yaml-plist` so I don't need to specify a path every time.)

Now you have a beautifully-crafted AutoPkg recipe, ready for overriding!

# yaml syntax

You can easily see the basic `yaml` syntax by comparing the two files above. Things to note:

* The entire `yaml` file is equivalent to the contents of the outer `<dict>...</dict>` tags of the `plist` file.
* The `<key>...</key>` is the value before the `:` in `yaml`.
* The value of the key is to the right of the `:`. The type of this value is determined by the value itself.
* If the value is `true` or `false`, it is detected as a boolean value.
* If it is a whole number it will be an `int`, or if it is a valid float number it will be identified as such.
* Otherwise, the value is considered a string.
* Strings do not automatically have to be escaped, but if they contain certain characters which are used in `yaml`, you should escape the string with single quotes, i.e. `'string'`. You may also need to do this if you wish for a valid number to be treated as a string.
* `<dict>...</dict>` lists are handled with a simple indent. In the above example, the indent is two spaces. You must be consistent in the `yaml` file (unlike in the `plist`).
* An array is handled with a `-` at the same indent as the array's key. Subsequent items in the array should be at the same level of indent as the first item's key name.

A note on handling scripts within `yaml`. A good way is to use the [yaml literal style](http://www.yaml.org/spec/1.2/spec.html#id2795688). This uses a `|` to indicate a literal block of text, e.g. as follows:

```yaml
file_content: |
    #!/bin/bash

    if [[ $1 ]]; then
        exit 0
    else
        exit 1
    fi
```

# Converting existing AutoPkg recipes to yaml

If you have existing recipes, but you would like to maintain them in `yaml`, then use my [plist-yaml-plist] tool to convert them to `yaml`:

```
/path/to/plist-yaml.py /path/to/KNIME.pkg.recipe /path/to/KNIME.pkg.recipe.yaml
```

Remember that every time you edit the `yaml` file, you need to convert it back to a `plist` before use in AutoPkg.

# Other uses for [plist-yaml-plist]

## Configuration Profiles

If you are in the business of crafting Apple Configuration Profiles, you can write these in `yaml` and then convert them. This is particularly handy for creating simple custom profiles that you then upload to your MDM tool.

For example, to write the `com.microsoft.autoupdate2` Plist that sets Office updates to manual and disables the Insider Program options, all you need is:

```yaml
DisableInsiderCheckbox: true
HowToCheck: Manual
```

Now convert to `plist`:

```
/path/to/yaml-plist.py /path/to/com.microsoft.autoupdate2.yaml /path/to/com.microsoft.autoupdate2.plist
```

You get this:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>HowToCheck</key>
    <string>Manual</string>
    <key>DisableInsiderCheckbox</key>
    <true/>
</dict>
</plist>
```

You can use this file to upload to Jamf Pro as a Custom Payload of a Configuration Profile.

I have even successfully used the tool to create a full `mobileconfig` file from `yaml`.

## Preferences Files

You could maintain your preference files in `yaml`, and convert them before adding to `~/Library/Preferences`.

For example, here are valid `com.github.autopkg` preferences in `yaml` format:

```yaml
JSS_URL: https://example.com:8443
JSS_REPOS:
- name: JPShare
  password: LaLaLaLaLa
  JSS_MIGRATED: 'True'
API_PASSWORD: LaLaLaLa
API_USERNAME: AutoPkg
FAIL_RECIPES_WITHOUT_TRUST_INFO: true
RECIPE_REPOS:
  /Users/graham/Library/AutoPkg/RecipeRepos/com.github.autopkg.jss-recipes:
    URL: https://github.com/autopkg/jss-recipes
  /Users/graham/Library/AutoPkg/RecipeRepos/com.github.grahampugh.recipes:
    URL: https://github.com/grahampugh/recipes
RECIPE_SEARCH_DIRS:
- .
- ~/Library/AutoPkg/Recipes
- /Library/AutoPkg/Recipes
- /Users/graham/Library/AutoPkg/RecipeRepos/com.github.autopkg.jss-recipes
- /Users/graham/Library/AutoPkg/RecipeRepos/com.github.grahampugh.recipes
```

Convert it straight into the correct path:

```
/path/to/yaml-plist.py /path/to/com.github.autopkg.yaml ~/Library/Preferences/com.github.autopkg.plist
```



{% include urls.md %}
