---
layout: post
title:  "Clean up your packages in Jamf Pro automatically with JamfPackageCleaner"
comments: true
---

Thanks to the excellent contribution of Henrik Engström (`@creation` on the [MacAdmins Slack][macadmins slack team]), there is a new AutoPkg processor in the [JamfUploader] suite of processors.

Jamf Pro can accumulate packages quickly if you have a broad suite of applications to deploy, and when you've automated the upload of those packages with [AutoPkg] and [JamfUploader], it's easy not to notice them build up until you start to get disk space or performance issues.

## Introducing JamfPackageUploader

`JamfPackageUploader` is a simple processor that can be used as a post-processor to run after a regular `.jamf` recipe. It checks the existing packages for names matching an assigned string and deletes the oldest packages based on ID, which is an indicator of how recent they were uploaded (ID always increases on Jamf, gaps are never infilled). You can define how many packages should be kept.

This is the simplest form of how you would run a recipe that would invoke the post-processor:

```txt
autopkg run -v AwesomeApp.jamf --post com.github.grahampugh.jamf-upload.processors/JamfPackageCleaner
```

### Name pattern matching

Without assigning any additional values, `JamfPackageCleaner` will take the value of `%NAME%`, add a dash (`-`), and look for existing packages that match that string. In the above example, this would be matches on `AwesomeApp-`, e.g. `AwesomeApp-23.0.pkg`, `AwesomeApp-24.0.pkg` etc.

For package names that do not correspond to `%NAME%`, you can override the string to match by providing a value for the `pkg_name_match` key. For example, if you add `--key pkg_name_match=Awesome_App_`, the processor will instead look for matches on the name `Awesome_App_`, e.g. `Awesome_App_23.0.pkg`, `Awesome_App_24.0.pkg` etc.

**Caution:** Please note that the pattern matching is only chacking for package names that begin with the pattern. If you have different package types that start with the same string, you may want to avoid using the post-processor on those runs. e.g. if you had packages with `Xcode-` and `Xcode-Command-Line-Tools-`, the processor matching `Xcode-` would also match `Xcode-Command-Line-Tools-` so could delete them. I may look into ways to improve that pattern matching criteria in the future to avoid such clashes.

### Number of packages to keep

The default number of packages that will be kept is 5. This can be overridden by providing a value for the `versions_to_keep` key. For example, if you add `--key versions_to_keep=3`, the processor will delete all but 3 packages.

### Failsafes

Henrik has added two failsafes to the processor to prevent disaster. These are the keys `minimum_name_length`, which ensures the package name is at least 3 characters long by default, and `maximum_allowed_packages_to_delete`, which aborts if there are more than 20 packages to delete. If your repo has got enormous, you can always increase this value for initial clean up runs using `--key maximum_allowed_packages_to_delete=100`

## Set your own defaults

You can override the defaults for all recipe runs by adding your own values to the AutoPkg preferences. To do this, use the defaults command. Here's some examples:

```txt
defaults write "$HOME/Library/Preferences/com.github.autopkg.plist" versions_to_keep -int 10
defaults write "$HOME/Library/Preferences/com.github.autopkg.plist" minimum_name_length -int 8
defaults write "$HOME/Library/Preferences/com.github.autopkg.plist" maximum_allowed_packages_to_delete -int 100
```

## API permissions required

The `JamfPackageCleaner` processor requires `Read` and `Delete` privileges for the `Packages` endpoint. You may need to go add the `Delete` privileges, as this has not been required by any existing processors in the JamfUploader suite.

## Conclusion

It's awesome to get really useful contributions to open source projects. Since this was also going to be really useful at my own organisation, I've supplemented Henrik's work to make the processor work with self-hosted Jamf Pro setups (indeed, any that have File Share Distribution Points). I've already put the processor into work and cleaned up a bunch of packages:

```txt
The following package cleaning was performed in Jamf Pro:
    Pkg Name Match  Found Matches  Versions To Keep  Deleted  
    --------------  -------------  ----------------  -------  
    Fiji-           26             10                16       
```

Thanks again to Henrik and to all others who have contributed to the JamfUploader project so far.

{% include urls.md %}
