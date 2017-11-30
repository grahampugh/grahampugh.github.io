---
layout: post
title:  "Help Make the Jamf Pro API Better"
comments: true
---

[Jamf Pro] has an extensive [API][Jamf Pro API Documentation], which enables integration with a [wide range of third party apps][Jamf Marketplace], and the ability to code your own integrations. For my work, the API is essential, as the Jamf service we provide is too complicated to support via the GUI alone.

Unfortunately, sometimes the API lags behind when new features are introduced to Jamf Pro. With Jamf Pro 10, which was released at the end of October 2017, some new features and changes were introduced which broke existing integrations with [AutoPkg], and sadly broke the ability to create a Self-Service Policy via the API.

![img-3]

---

Jamf And... AutoPkg?
----

At the [Jamf Nation User Conference 2017][JNUC], the release of Jamf Pro Version 10 was announced, and a key new feature, [Patch][Jamf Pro Patch Management], was revealed in more detail. Whilst currently restricted to a curated set of software, Jamf announced plans to open up the framework used by Patch to allow customers to add their own software titles, and AutoPkg was stated as a mechanism for adding the packages into the Patch system.

AutoPkg already integrates with Jamf, thanks to the work of [@shea_craig] and others who provided the [JSSImporter] processor. Note that this work is totally independent of Jamf. There are numerous workarounds that Shea had to implement in order to make JSSImporter work. Package upload has no published API, never has, and it turns out that in order to enable JSSImporter to import packages to some types of fileshare distribution points, namely Jamf Distribution Servers and Cloud Distribution Points, Shea had reverse-engineered how the Casper Admin application uploads packages using a private API.

In Jamf Pro 10, the method of upload has been changed. Casper Admin no longer works for uploading packages to JDS, CDP or the new Jamf Cloud Distribution Servers, therefore nor does JSSImporter. You can upload the metadata associated with a package as before, but the package itself is not uploaded. Currently you have to manually upload the package using the Jamf Pro Server GUI.

So, in many respects, the [integration between Jamf and AutoPkg][11] is broken.

![img-4]

And when it comes to Patch, there is absolutely no AutoPkg-Patch integration at present.

---

Jamf And... Creating a Policy with the API?
----

You can write an XML file containing the parameters required to create a policy. The good thing about the API is that you only need to provide non-default, required parameters. The remaining parameters are auto-created during the import. Apart from a few bugbears, such as the [inability to refer to icons that already exist in the database][1], it worked.

But [Jamf Pro 10 has broken it][2]. Specifically, Policies created using the API which add a Self-Service entry will not show the policy name in Self Service, or indeed any text at all. Your end users will have to guess what the item is based on the icon. This is only solved by manually clicking Edit and Save in the JSS GUI for every policy. The reason for this is the new “Self Service Display Name” field, which is not available in the API. In the GUI some trickery auto-fills this field with the Policy Name if it is left empty, but this doesn’t work for new items imported via the API.

![img-1]{:height="500px"}  
*Self Service items with no title*

I raised a Support Case, and publicised heavily to anyone who would listen, and was today told that the bug should be fixed when Jamf Pro 10.2 is released. Excellent news! But several bugs or sub-optimal aspects to the API remain.

---

Giving API the love it needs
---

A very telling statement from my excellent Jamf Support person alluded to the disjoint between the GUI and the API:

>Aside from this, I've found that it is partially expected behaviour from our side, as any new implementation for the GUI, is not directly released as API available. New functionality in the API takes time to implement and sometimes does not match up with the exact timeline of the features.

Many customers have requested parity between the GUI and the API, such as [this feature request by James Smith][3]. A fully-functional API would not require reverse-engineering, hacks and workarounds to enable integration with established tools such as AutoPkg. It is the missing pieces that are causing the problems.

![img-2]{:height="500px"}

How do we make the API better? How do we ensure that Jamf don't release new features at all until they are ready in the API? My supporter said it clearly:

>... but generally speaking the Jamf Nation feature request will have more impact as other users can upvote it. To speed up the process, customers can create Feature Requests, and upvote them, which will get the priority for the feature getting created and released higher, by the amount of upvotes.

>...to get the issue known and prioritised better, there is nothing else we can do from the Support Department, as the fixing of issues is prioritised from Cases attached to the PI(reporting the issue) and Upvotes for the FR for implementing new functionality.

>I'm asking for your help in sharing the feature request link with anyone else you know who would like this upvoted, and asking them to also contact support regarding the PI if they are seeing it.

So now I've got to the point of this blog post, which is to make a plea for all Jamf Pro administrators who use the API not to just make do with the imperfections and broken bits, but to make Feature Requests, upvote existing ones, and contact Jamf Support get the profile of the API higher in the list of priorities of Jamf Developers.

---

Please upvote!
----

Please follow these links and upvote or like the feature requests and posts. And if the issues affect you, make a support request!

* [Every aspect of the Jamf web GUI should be accessible via the API][3]
* [Add new Self Service policy options to the API][6] (refers to PI-004819)
* [Jamf Pro 10 API Breaking Bugs][12] (refers to PI-004722)
* [Secondary Button for Self Service Policies by API][5]
* [Dedicated self_service_icons API parameter needed!][1]
* [Facilitate uploads to cloud distribution point via API or other non-manual method][8]
* [Add Ability to POST/PUT using JSON via the JSS API][7]
* [fileupload API enhancement][9]
* [API Keys for Scripting and Automation][10]

If you have a request you would like to see added to this list, let me know! And once again, please upvote!

![img-5]

[img-1]: https://www.jamf.com/jamf-nation/file-downloads/images/c03b86f68d6d4d78a5b164aafa23ad26
[img-2]: https://www.jamf.com/jamf-nation/file-downloads/images/7adf50216ae24650b2901c719d4b53f2
[img-3]: http://cdn.ttgtmedia.com/rms/onlineImages/jamf_selfservice_desktop.jpg
[img-4]: https://ih1.redbubble.net/image.310897330.5697/flat,800x800,075,f.u1.jpg
[img-5]: https://i.imgflip.com/1zom8i.jpg

[1]: https://www.jamf.com/jamf-nation/feature-requests/6371/dedicated-self_service_icons-api-parameter-needed
[2]: https://www.jamf.com/jamf-nation/discussions/26272/jamf-pro-10-api-breaking-bugs
[3]: https://www.jamf.com/jamf-nation/feature-requests/6583/every-aspect-of-the-jamf-web-gui-should-be-accessible-via-the-api
[4]: https://www.jamf.com/jamf-nation/feature-requests/6581/set-default-text-of-the-self-service-after-button-globally-or-the-same-as-the-before-button
[5]: https://www.jamf.com/jamf-nation/feature-requests/6576/secondary-button-for-self-service-policies-by-api
[6]: https://www.jamf.com/jamf-nation/feature-requests/6724/add-new-self-service-policy-options-to-the-api
[7]: https://www.jamf.com/jamf-nation/feature-requests/2945/add-ability-to-post-put-using-json-via-the-jss-api
[8]: https://www.jamf.com/jamf-nation/feature-requests/6665/facilitate-uploads-to-cloud-distribution-point-via-api-or-other-non-manual-method
[9]: https://www.jamf.com/jamf-nation/feature-requests/6476/fileupload-api-enhancement
[10]: https://www.jamf.com/jamf-nation/feature-requests/6404/api-keys-for-scripting-and-automation
[11]: https://marketplace.jamf.com/details/autopkg/
[12]: https://www.jamf.com/jamf-nation/discussions/26272/jamf-pro-10-api-breaking-bugs

{% include urls.md %}
