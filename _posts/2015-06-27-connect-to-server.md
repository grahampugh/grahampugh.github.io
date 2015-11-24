---
layout: post
title:  "'Connect to Server' favourites across devices using Safari bookmarks"
comments: true
---

I made a comment on the **#general** channel of the [MacAdmins Slack Team] yesterday about my wish that the favourites list in the **Go > Connect to Server** list would share between devices using iCloud. This led MacAdmins Slack Team member [scriptingosx] to helpfully reply with [a simple way of achieving this using Internet Shortcuts][1].

I stumbled across another way of doing this by not reading the above blog properly. I decided to use Safari bookmarks rather than desktop shortcuts. These are automatically shared with iCloud as long as you tick the box for Safari sharing in your iCloud System Preferences.

First, it would make sense to create a bookmark folder to house your favourite shortcuts.

In Safari, click on **Bookmarks > Add Bookmark folder**.

![img-1]

Then go to **Bookmarks > Edit Bookmarks**, and drag the new folder to move it if required (I put all my favourites in the "Favourites" folder as I use the Favourites bar).

Now, open a new tab and go anywhere in the internet (it doesn't matter where) and press Ctrl-D to add a bookmark.

Select the new folder you just created and enter the Server URI address you wish to bookmark. As you're likely to want to use these addresses on multiple computers, it may be worth adding the username to the field. Take a copy of the address with **Ctrl-A, Ctrl-C**, as you'll need it in the next step.

![img-2]

Alternatively, you can just give the shortcut a descriptive name if you prefer. You'll be adding the server address below anyway.

Now, go back to the Edit Bookmarks tab, and select your entry.

![img-3]

Double click on the URL address, and paste in your server URI address, replacing whatever you bookmarked.

![img-4]

That's it. Now you have a shortcut to your server in your Safari favourites, which are accessible from all your iCloud connected devices. (Sorry, most links won't actually work on your iOS devices though!).

![img-5]

As [pointed out on the scriptingosx blog post][1], these addresses can be any valid URI address format, such as **ftp**, **ssh**, **vnc**, **smb**, and **afp** addresses, and Microsoft Remote Desktop **rdp** addresses using the format described in [this Microsoft Technet article][2], e.g. `rdp://full%20address=s:rds.mydomain.com&amp;domain=s:mydomain.com&amp;username=s:myaccount`

RDP links *do* work on your iOS device, as long as you have the Microsoft Remote Desktop app installed (although the domain doesn't pass through, despite the Technet article stating that it is compatible with iOS).

[scriptingosx]: http://scriptingosx.com
[1]: http://scriptingosx.com/2015/04/on-internet-shortcut-files/
[2]: https://technet.microsoft.com/en-us/library/dn690096.aspx

[img-1]: /assets/images/connect-to-server-1.png
[img-2]: /assets/images/connect-to-server-2.png
[img-3]: /assets/images/connect-to-server-3.png
[img-4]: /assets/images/connect-to-server-4.png
[img-5]: /assets/images/connect-to-server-5.png

{% include urls.md %}

