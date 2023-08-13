---
layout: post
title:  "JNUC Presentation - 14 November 2019 - Jamf Pro and AutoPkg"
comments: true
---

On 14 November 2019, at 13:30, I will be presenting at the [Jamf Nation User Conference in Minneapolis, MN, USA](https://www.jamf.com/events/jamf-nation-user-conference/2019/), on the following topic:

**Jamf Pro and AutoPkg: How JSSImporter automates package management and policy creation in Jamf Pro**

![JNUC2019](https://media.jamf.com/images/events/user-conferences/national-user-conferences/2017/hyatt-regency-sidebar.jpg)

[AutoPkg] is a community framework for capturing software installers from external or internal sources, automating the process of packaging these installers, and uploading the packages to a management system such as Jamf Pro, avoiding the need to manually obtain and package up software. Using a concept of “recipes”, which can be shared via GitHub, members of the Mac Admin community can easily benefit from and contribute to the pooled resources to minimise duplication of effort.

![AutoPkg](https://avatars0.githubusercontent.com/u/5170557)

[JSSImporter] is an AutoPkg processor designed by Shea Craig which facilitates the import of software packages into Jamf Pro using the Jamf Pro API. It is the only method of automating the connection between AutoPkg and Jamf Pro.

In this session, I will explain how JSSImporter works, and help attendees understand and construct AutoPkg JSS recipes, giving simple and complex examples. I will explain specific settings that are required to make JSSImporter work on Jamf Pro cloud instances and distribution points. I will show some of the different workflows that are being employed in the community to suit particular needs.

Finally, as a member of the team maintaining JSSImporter and [python-jss], I will explain the current state of affairs in terms of current and future development. With the deprecation of python 2.7 on the horizon, we are at a critical point in the future functionality of AutoPkg and JSSImporter.

## See you there!

If you are attending JNUC, I hope to see you at the session and hope that I will leave you with some new ideas on how to use AutoPkg in your organisation.  If you cannot attend, there should be a video available a short time afterwards.

I will be compiling a comprehensive list of resources to accompany the session, which I will publish ahead of the session.

{% include urls.md %}
