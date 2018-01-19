---
layout: post
title:  "Rootgate - Keep Calm and Carry On Being Secure"
comments: true
---

So everyone has tweeted, slacked, facebooked and blogged about [#rootgate][1] (or #iamroot). An oversight with the code development of macOS High Sierra resulted in requests for administrator access to certain System Preference Panes, Utility applications and Keychain Access enabling the `root` user with a null password.

Whilst the furore was so big that Apple were sure to provide a quick solution, which they [did within 24 hours][2], many scrambled to provide fixes for the bug. Many of you were probably mandated by your seniors to provide a fix. Some of whom probably hadn't considered the existing vulnerabilities on their Mac fleet. But, how serious is it really, and was your Mac really secure before this bug came around?


Clear and Present Danger
----

A lot of the panic associated with patching this bug seemed to come from quarters who do not enforce existing simple security measures that would have almost totally mitigated the risk of this bug being exploited, even before it was patched. And without enforcing these security measures, the clients remain as vulnerable as before despite applying this patch. It's basic stuff, but as I have had to repeatedly emphasise them to different parties today, I decided to share them here too.

---

What Do We Not Want To Happen?
----

![img-1]  
*Image courtesy of [KnowYourMeme.com][9]*

The Rootgate bug is a root escalation vulnerability. What does root escalation mean? It means that a standard (non-administrator) account can gain `root` access, which means it can perform administrative tasks normally reserved for administrator accounts. This includes changing system settings, but more importantly, it includes gaining access to data in the other accounts on the computer. It also means being able to change the password of another account, therefore being able to log in to the account. This could potentially give access to further information such as browsing history, passwords etc., although changing an account password normally means losing access to the Keychain, which is where all the locally-stored passwords are stored.

So, we really don't want that to happen.

---

Could This Already Happen Before Rootgate?
----

If your Mac is unencrypted - FileVault is not enabled, and no firmware password is set, then you are **already vulnerable**. Running Security Update 2017-001 will do nothing to protect you.

How? There are [multiple ways to achieve this][3], including via Recovery Mode, Single User Mode and Target Disk Mode. Basically, if someone has physical access to your computer and it is unencrypted and unprotected by a firmware password, they can do what they like with your data, short of accessing the Keychain.

---

Any extra vulnerability with Rootgate in these cases?
----

Well yes, if your computer is connected to the network, and has Screen Sharing or Remote Access enabled for either all users or all Administrators, the Rootgate bug can enable anyone with access to your network to remotely access your computer and log into it with account name `root`, no password.

---

So what should I do?
----

Take these basic security measures to minimise risk of your data being exposed. They are not specific to Rootgate, just sensible measures that everyone should take to protect their data:


### Encrypt with FileVault

[Your Mac should be encrypted.][8] Without this, anyone with physical access to your Mac can easily access your data without knowing about your account details or password.

If your computer is used by multiple users on a domain, such as in a teaching lab, then it is impractical to use FileVault. In these cases, you should [set a firmware password][12] to prevent non-administrators from booting to other partitions such as the Recovery Partition, Single-User Mode, Internet Recovery etc.

Note that it is not a bad idea to set a firmware password on all Macs, but if FileVault is enabled, your data is protected without this extra step.

### What to share, or not to share

Disable sharing on your Mac when you don’t need it. If you do need it, then restrict access as much as possible, and only to the things that are absolutely necessary. These preferences are set in Sharing preferences (choose **Apple menu > System Preferences**, then click **Sharing**). For more details on setting minimum-required access to specific users and networks, see the following Apple Knowledge Base articles:

* [Screen Sharing](https://support.apple.com/kb/PH25554)
* [File Sharing](https://support.apple.com/en-us/HT204445)
* [Remote Login (ssh)](https://support.apple.com/kb/PH25252)

### Lock your computer

[Set a Screen Saver Lock][6], and set the password to be required immediately to unlock it. And don't forget to lock your screen whenever you walk away from your computer! It's easily achievable by [setting a hot corner to enable the screen saver][4], or pressing [Ctrl-Shift-Power][5] or [Ctrl-Shift-Eject][5]

### Encrypt external drives

[Encrypt your external USB drives / keys][7] if you store sensitive data on them, including Time Machine backup drives.

### Patch your computer

Always ensure that all software updates are kept up-to-date, not only for macOS, but for all software.

### Enable 'Find My Mac'

If you are able to sign into iCloud on your Mac, [enable Find My Mac][10]. This may give you a chance to recover your Mac if it is stolen, and also gives the opportunity to remotely wipe your computer.

---

But, our management still tell us we have to push a patch for Rootgate
-----

Yes, I understand. We were also asked to push a patch for the problem, and so we wrote a script that we could push with our current management solution. This script can be pushed to all clients. It checks the following, in this order:

3. Whether the client is running 10.13. If not...
1. Whether the client has already been patched with [Security Update 2017-001][2]. If not...
2. If the script has already been run on the client and the root bug fixed.
4. If `root` is already enabled with a real password.
5. If none of the above, proceed to enable root with a complex random password (actually a UUID).

Since it has built-in checks, this script can be repeatedly run until you (or your management) are satisfied that all your clients have been patched.

{% gist b37173a492a0b79ee9a241a07a791602 %}


[1]: https://twitter.com/search?q=%23rootgate&src=tyah
[2]: https://support.apple.com/en-us/HT208315
[3]: https://www.macworld.co.uk/how-to/mac/what-do-if-forgotten-mac-password-3594395/
[4]: https://support.apple.com/kb/PH25524
[5]: https://support.apple.com/en-ca/HT201236
[6]: https://support.apple.com/kb/PH25376?locale=en_US
[7]: https://support.apple.com/kb/PH25745?locale=en_US
[8]: https://support.apple.com/en-us/HT204837
[9]: http://knowyourmeme.com/memes/make-me-a-sandwich
[10]: https://support.apple.com/guide/mac-help/use-find-my-mac-mh36811/10.13/mac/10.13
[11]: https://support.apple.com/en-us/HT204455
[12]: https://support.apple.com/en-us/HT204455

[img-1]: http://i0.kym-cdn.com/entries/icons/facebook/000/004/689/sandwich.jpg


{% include urls.md %}
