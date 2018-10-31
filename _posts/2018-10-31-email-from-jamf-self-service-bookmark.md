---
layout: post
title:  "Send an Email from Jamf Pro Self Service"
comments: true
---

This is a quick and kind of obvious one, but a quick search did not find it documented.

If your common method of receiving IT help requests is via Email, you might want your clients to be able to click a button to send to the correct address with an appropriate subject.

## A script, in a policy

It's possible to create Policies with a script to do this - this gives you the opportunity to generate additional content into the Email such as username, computer serial number etc. For example, see the answer from [@emily] in [this Jamf Nation post][2].

## Self Service Bookmark

If you just want a quick and easy way to send to the correct address, you can just create a Self Service Bookmark. Although not mentioned in the [Jamf Pro Administrator's Guide][1], the URL can be a `mailto:` address. Since `mailto:` addresses can include subject and even body fields, you can pre-populate the Subject and Body with information, such as:

```
mailto:apple-services@acme.com?subject=IT%20Help%20Request
```

Note that as with any URL, it is necessary to encode certain characters. In this example, spaces are encoded with `%20`. You can find all the URL encoding characters [here][3].

The full configuration is done in **Management Settings > Self Service > Bookmarks** (on recent versions of Jamf Pro):

![img-1](/assets/images/self-service-bookmarks-email.png)

A configured mail application on the client is required for this to function. Don't forget to choose a nice icon! Unfortunately, icons used in policies or configuration profiles are not available for re-use in Bookmarks, so you have to upload them again.

The resulting item looks like this in Self Service:

![img-2](/assets/images/email-bookmark-in-jamf.png)

If you're not familiar with Jamf Pro Self Service Bookmarks, you can determine the order of them in Self Service using the priority drop-down menu, where `1` is first and `20` is last.

When the user clicks on the Bookmark, the email it opens looks like this (if Apple Mail is your default mail client, and you're using Dark Mode):

![img-3](/assets/images/apple-mail-from-bookmark.png)


[1]: http://docs.jamf.com/10.8.0/jamf-pro/administrator-guide/Jamf_Self_Service_for_macOS_Bookmarks.html
[2]: https://www.jamf.com/jamf-nation/discussions/12166/sending-emails-via-jss
[3]: https://www.w3schools.com/tags/ref_urlencode.asp

{% include urls.md %}
