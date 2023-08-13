---
layout: post
title: "Importing Matlab into Munki"
comments: true
---

Matlab is a cross-platform commercial programming tool. Its use is licensed, either with a personal license code or through a license server. It is made available as an ISO from the Mathworks website by authorised accounts. [A silent installation method is detailed here][matlab silent installation].

Previously I had installed Matlab on a Mac, and then imported the resulting App into Munki. For R2015a, I've written up the way I imported Matlab into Munki without having to install Matlab first.

See [https://github.com/grahampugh/osx-scripts/tree/master/matlab-munki](https://github.com/grahampugh/osx-scripts/tree/master/matlab-munki) for full details.

This method involves packaging the installer ISO together with the license and configuration files into a DMG, and then using a `postinstall_script` key in the Munki pkginfo file to mount the ISO and run the silent installer script.

# minimum_update_version

An important part of the pkginfo file is that Matlab R2015a should not appear as an update for previous versions of Matlab. Each version can coexist on Macs, and users may wish to have multiple versions on their computer. All versions have the same `CFBundleIdentifier`, so to avoid this making the newer version appear to be an update of the older, the `minimum_update_version` key is used:

{% highlight xml %}
<key>installs</key>
<array>
<dict>
<key>CFBundleIdentifier</key>
<string>com.mathworks.matlab</string>
<key>CFBundleVersion</key>
<string>8.5.0</string>
<key>minosversion</key>
<string>10.7</string>
<key>path</key>
<string>/Applications/MATLAB_R2015a.app</string>
<key>type</key>
<string>application</string>
<key>version_comparison_key</key>
<string>CFBundleVersion</string>
<key>minimum_update_version</key>
<string>8.5.0</string>
</dict>
</array>
{% endhighlight %}

It should be noted that you need to have a different Name for each version of Matlab if you want them all to be separately available on the Managed Software Center, e.g. `Matlab_R2014a`, `Matlab_R2015a` etc.

[matlab silent installation]: http://uk.mathworks.com/help/install/ug/install-noninteractively-silent-installation.html

{% include urls.md %}
