---
layout: post
title:  "Customise Atom for editing AutoPkg recipes"
comments: true
---

Just a quick one!

[AutoPkg] recipes are Plist files. But they have the suffix `.recipe`. Most text editors don't know how to handle this for syntax highlighting, so either open the recipe in plain text (urgh), or take an educated guess and give it XML highlighting.

I use GitHub's [Atom] code editor. It's not perfect (too frequent updates; can get processor-heavy), but it's open source, very customisable, and I like its code-completion abilities. I add the [Git-plus][Atom Packages: Git-plus] package to make working with Git seamless, and the [Minimap][Atom Packages: Minimap] package to add a Sublime Text-style scrolling overview bar.

At present I'm creating a lot of AutoPkg recipes for my team's [Jamf Pro] service. AutoPkg recipes open in Atom highlighted as XML by default. XML highlighting is better than none, but it doesn't highlight the `<key>`-`<string>` pairs in the optimal `plist` way.  Finally I got around to [RTFM](https://xkcd.com/293/), and it's easy to customise your Atom installation to highlight `.recipe` files properly:

* Open `~/.atom/config.cson`
* Add the following to the `core:` section:

```cson
customFileTypes:
  "text.xml.plist": [
    "recipe"
  ]
```

As an example, here's my complete `~/.atom/config.cson` file. You can guess what the other stuff does:

```cson
"*":
  core:
    customFileTypes:
      "text.xml.plist": [
        "recipe"
      ]
    telemetryConsent: "limited"
  editor:
    showInvisibles: true
    softWrap: true
    tabLength: 4
    tabType: "soft"
  "exception-reporting":
  welcome:
    showOnStartup: false
```

And here's how it looks:

![img-1]

For more information about customising languages in the Atom editor, see [Atom: Customising Language Recognition](http://flight-manual.atom.io/using-atom/sections/basic-customization/#_customizing_language_recognition)

[img-1]: /assets/images/atom.png
{% include urls.md %}
