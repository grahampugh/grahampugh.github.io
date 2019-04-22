---
layout: post
title:  "Java SE licensing, macOS, and AutoPkg - what now?"
comments: true
---

# Oracle Java SE now requires a license subscription

In July 2018, Oracle announced that the licensing for Oracle Java SE (Standard Edition) would [change going forward](https://www.oracle.com/technetwork/java/javase/terms/license/javase-license.html). Commercial (including academic) users need to buy into a Java SE Subscription.

>The new [Oracle Technology Network License Agreement for Oracle Java SE](https://www.oracle.com/technetwork/java/javase/terms/license/javase-license.html) is substantially different from prior Oracle JDK licenses. The new license permits certain uses, such as personal use and development use, at no cost -- but other uses authorized under prior Oracle JDK licenses may no longer be available. Please review the terms carefully before downloading and using this product. An FAQ is available [here](https://www.oracle.com/technetwork/java/javase/overview/oracle-jdk-faqs.html).
>
>Commercial license and support is available with a low cost [Java SE Subscription](https://www.oracle.com/java/java-se-subscription.html).

This includes the use case of installing a Java Runtime to operate some other software that doesn't have Java bundled in. An example is the SPSSStatistics installer, which needs Java 8 to function.

Unusually and awkwardly for software deployment administrators, this change would not be restricted to a future "major" version, such as Java SE JDK 12, but to patches of all currently maintained versions, including the version 8 JRE and JDK, and the version 11 JDK. As a result, existing [AutoPkg] recipes such as the core [OracleJava8](https://github.com/autopkg/recipes/tree/master/OracleJava) and novaksam's [OracleJava8JDK](https://github.com/autopkg/novaksam-recipes/blob/master/Recipes%20-%20pkg/OracleJava8JDK.pkg.recipe) recipes no longer function and are likely to be deprecated rather than updated.

The final updates to Oracle Java 8 JRE and JDK under the existing license (i.e. free) were released in Jan 2019. A new update released on 16 April 2019 is the first released under the new restrictive licensing scheme.

The updates appear [still publicly available](https://www.oracle.com/technetwork/java/javase/downloads/jre8-downloads-2133155.html), but you are redirected to an Oracle login page if you attempt to download. If you attempt to update inline, you get a warning about the license changes.

For extensive details about the changes to licensing, see this [Java Champions article on Medium](https://medium.com/@javachampions/java-is-still-free-2-0-0-6b9aa8d6d244).


# OpenJDK

Fortunately, for many if not most or all requirements, there are alternatives to Oracle's commercial Java SE product. As stated on [Oracle's Java download page](https://www.oracle.com/technetwork/java/javase/downloads/jre8-downloads-2133155.html):

>Oracle also provides the latest OpenJDK release under the open source [GPL license](https://openjdk.java.net/legal/gplv2+ce.html) at [jdk.java.net](https://jdk.java.net).

A number of organisations are stepping in to maintain supported versions of OpenJDK.

## Oracle OpenJDK

Oracle's [OpenJDK project](https://jdk.java.net) is an open-source version of the JDK. They currently appear to be maintaining versions 11 and 12 of the JDK. Oracle themselves, who sponsor the project, state that the update cycle for the JDK is now a new release every six months. While [Oracle state that these are not major releases but rather "feature releases"](https://blogs.oracle.com/java-platform-group/update-and-faq-on-the-java-se-release-cadence), many users and administrators may prefer to work with a Long Term Support (LTS) version. This is not offered (for free) by Oracle.

It is not clear how long OpenJDK 11 will continue to be supported. OpenJDK 8 is no longer being maintained.

[Rich Trouton][@rtrouton] maintains AutoPkg recipes for [OpenJDK 11](https://github.com/autopkg/rtrouton-recipes/tree/master/OpenJDK11) and [OpenJDK 12](https://github.com/autopkg/rtrouton-recipes/tree/master/OpenJDK12).

**Note:** Red Hat have stated that they are taking the lead in the support of OpenJDK, and are maintaining LTS installers for Red Hat, CentOS and Windows. However, to date, they do not provide a macOS installer.


## AdoptOpenJDK

The AdoptOpenJDK project is maintaining a wide range of JDK and JRE installers. They offer JDK and JRE LTE builds for versions 8 and 11 over a wide range of platforms, as well as version 12. These are available to download from Github (LINK).

I have made recipes for [AdoptOpenJDK 8 JDK and JRE](https://github.com/grahampugh/recipes/tree/master/AdoptOpenJDK).


## Amazon Corretto JDK

Amazon maintain freely licensed, LTS versions of JDK 8 and 11. (https://docs.aws.amazon.com/corretto/index.html).

[Rich Trouton][@rtrouton] maintains AutoPkg recipes for the JDK versions 8 and 11, which take the signed packages from Amazon's download site.

If you require the version reported by AutoPkg to match that reported from the CLI, and don't need a signed package, you might want to consider my [pkg recipes for versions 8 and 11](https://github.com/grahampugh/recipes/tree/master/AmazonCorrettoJDK).


## Azul Zulu JDK

Azul Systems are providing LTS versions of Open JDK 12, 11, 8 and 7, with a separate JRE available for version 8 (see [download page](https://www.azul.com/downloads/zulu/#)). They are the only third-party provider to include the JavaFX features in their builds.

So far, no AutoPkg recipes are available for Azul Zulu).


## SapMachine

[SapMachine](https://sap.github.io/SapMachine/) is SAP's downstream fork of the OpenJDK project. It is used to build and maintain a SAP supported version of OpenJDK for SAP customers and partners who wish to use OpenJDK to run their applications.

SAP maintain an LTS version of OpenJDK 11 for macOS. [Rich Trouton][@rtrouton] maintains [AutoPkg recipes for SapMachine](https://github.com/autopkg/rtrouton-recipes/tree/master/SapMachine), but note that this will download version 12.


# Conclusion

Oracle have caused some confusion by the change to their licensing agreements. It is important for Mac administrators to act, since unless the new licensing subscription has been adopted in your organization, any Mac clients with Oracle Java installed are now likely not updated since January, or are not licensed for use.

For most people on macOS who require Java, there are open source alternatives available. The Java Runtime Engine (JRE) is enough for most needs, and this is still being offered by AdoptOpenJDK and Azul.

AutoPkg recipes are available for the OpenJDK versions you are most likely to need. However, any software with a Java dependency should be tested with each open source version before deploying it to users.

If you know of any other maintained versions of the JDK and/or JRE, or of any AutoPkg recipes not mentioned here, please let me know!

{% include urls.md %}
