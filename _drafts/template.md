---
layout: post
title:  "Java licensing, macOS, and AutoPkg - what now?"
comments: true
---

# Oracle Java now requires a license

Last year, Oracle announced that the licensing for Oracle Java SE would change going forward. Oracle's builds for the Java Development Kit (JDK) and runtime engine (JRE) would be restricted to "personal and XXXXX" (URL NEEDED). This restriction forbids use for commercial or academic purposes (URL NEEDED).

Unusually and awkwardly for software deployment administrators, this change would not be restricted to a future "major" version, such as Java JDK 12, but to patches of all currently maintained versions, including the Java 8 JRE and JDK. 

The final update to Oracle Java 8 JRE and JDK under the existing license (i.e. free) was released on XX Jan 2019. A new update released on 16 April 2019 is the first released under the new restrictive licensing scheme. Users installing this update themselves are shown a popup warning them of the change. (INSERT IMAGE)

(FIND OUT IF THE EXISTING AUTOPKG RECIPE ISNDOWNLOADING THIS VERSION)

# Alternatives

Fortunately, for many if not most or all requirements, there are alternatives to Oracle's now commercial product. 

## OpenJDK

The OpenJDK project produces an open-source version of the JDK. They currently appear to be maintaining versions 11 and 12 of the JDK. Oracle themselves, who sponsor the project, state that the update cycle for the JDK is now a new release every six months.

(INSERT THE BLURB ABOUT VERSIONING TO BE TREATED LESS AS MAJOR UPDATES)

It is not clear how long OpenJDK 11 will continue to be supported. OpenJDK 8 is no longer being maintained.

Rich Trouton maintains AutoPkg recipes for OpenJDK 11 and 12. (LINK)

## Amazon Corretto JDK

Amazon maintain freely licensed, LTS versions of JDK 8 and 11. (LINK) They State that they are (QUOTE ABOUT COMPATIBILITY).

Rich has made new AutoPkg recipes for the JDK versions 8 and 11, which take the signed packages from Amazon's download site. If you require the version reported by AutoPkg to match that reported from the CLI, and don't need a signed package, you might instead want to consider my `.pkg` recipe FOR version 8 instead (LINK).

## AdoptOpenJDK

The AdoptOpenJDK project is maintaining the widest range of JDK and JRE installers. They offer JDK and JRE LTE builds for versions 8 and 11 over a wide range of platforms, as well as version 12. These are available to download from Github (LINK).

(MAKE SOME RECIPES!)


{% include urls.md %}

