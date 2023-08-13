---
layout: post
title: "Microsoft Office 2016 Preview and OneDrive for Business Beta don't play together, yet"
comments: true
---

As a Mac SysAdmin in a dominantly Microsoft leaning organisation, I'm led to test new MS offerings with a view to rolling them out to Mac users once they reach their production stage. Sometimes, as in the case of OneDrive for Business, the need to use it is so great that we have to offer to deploy the Beta version.

However, there appears to be a problem if you have both Office for Mac 2016 Preview and OneDrive for Business (Beta) installed. Every time you start your computer, or restart OneDrive for Business (Beta), an alert is displayed:

![img-1]

Pressing "Yes" opens "Microsoft Upload Centre" - not very informative. Opening the Microsoft Upload Centre Preferences and clicking "Delete Files" to empty the Office Document Cache apparently solved the problem for some, but not for me.

The official word from Microsoft came in a [thread of the Office365 community forum](http://community.office365.com/en-us/f/153/t/298682.aspx)

-   Close OneDrive for Business Mac (Beta)
-   Open a terminal window and delete the OfficeFileCache as follows:  
    `$ rm -rf ~/Library/Group Containers/UBF8T346G9.Office/Microsoft/AppData/Microsoft/Office/15.0/OfficeFileCache`
-   Reopen OneDrive for Business Mac (Beta)

Microsoft stated that this would need to be done everytime the OneDrive for Business process is started. Their alternative is "Choose to install **either** Office 2016 Mac Preview **or** OneDrive for Business Mac Preview on your system." So I guess these Beta programs are not ready to play with each other, yet.

[img-1]: /assets/images/one-drive-1.png

{% include urls.md %}
