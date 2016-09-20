---
layout: post
title:  "Archive E-Mails from an IMAP E-Mail account"
comments: true
---

I was recently asked to look at archiving old E-Mails from IMAP accounts so that the accounts could be deleted without losing the emails. Surprisingly, the options I found were limited:

  * Use a Mail client such as [Thunderbird][1]. Configure the IMAP account you wish to archive, and then drag messages from each mailbox in turn to local folders.
  * Purchase a commercial option such as [BeyondInbox][2]. Configure the IMAP account, and the program downloads E-Mails into folders for each mailbox, with subfolders for years and months. This is not configurable.

Whilst looking for Open Source alternatives, I came across [this Python script from Rob Iwancz][3], which dumps E-Mails from a single folder in a GMail account to the local disk. I've now adapted this script to iterate through all the mailboxes in the IMAP account, and tested that it functions on non-GMail IMAP accounts. All that's required is the username and IMAP server. The password is asked for when the script is run.

{% gist c5bbf3e8ec1641ce033791615eee25b0 %} 


[1]: https://www.mozilla.org/en-US/thunderbird/
[2]: http://www.beyondinbox.com/
[3]: https://gist.github.com/robulouski/7442321

{% include urls.md %}

