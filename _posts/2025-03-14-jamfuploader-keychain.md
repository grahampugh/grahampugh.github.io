---
layout: post
title:  "JamfUploader - store your Jamf Pro credentials in the Keychain"
comments: true
---


<img src="/assets/images/Keychain%20Access.png" alt="Keychain Access icon" width="300" align="right" hspace="10" />It's been a while since I've posted anything about [JamfUploader], but there have been many updates to this suite of processors over the past few months. One new feature I would like to highlight is the ability to store your credentials for interacting with the Jamf Pro API in your Mac's Keychain.

JamfUploader processors were an evolution of the old JSSImporter processor and python-jss framework, both now deprecated. These both expected the API account username and password to be stored in a preferences file on disk, or supplied directly to the `autopkg` command. So, during the design stage for JamfUploader, I just replicated this requirement.

However, this means the password must be stored in plain text on the device running [AutoPkg], and since AutoPkg records every supplied variable in the run receipts, the password is also saved there. Furthermore, if you frequently run recipes on multiple Jamf Pro servers during the course of the day as I do, it's a faff to constantly update the credentials in the AutoPkg prefs file, and you never know which one is stored in there, or else you have to supply the credentials in the `autopkg run` command every time.

## Storing account credentials in the Keychain

For some time, I have been wrapping my `autopkg` commands inside a shell script that retrieved the credentials from my machine's keychain and added them to the command in the script, as follows:

    autopkg run -v TheBestAppEver.jamf \
        --key JSS_URL https://mylovely.jamfcloud.com \
        --key API_USERNAME "$username" \
        --key API_PASSWORD "$password"

This is especially useful as I interact with many Jamf Pro servers using the API on a daily basis. This is the basis for the scripts in the [Multitenant Jamf Tools (MJT)][4] repo, which is a toolkit for MSPs that use Jamf Pro.

I'm not sure why it took me so long, but this past week, I realised that I could simplify all this if JamfUploader processors would read directly from the Keychain.

## How it works

You still need to supply the Jamf Pro URL when running a JamfUploader recipe. This is to allow multiple servers to be stored in the Keychain. But you no longer need to supply the API account username and password or API Client ID and Secret. Once the credentials are in the Keychain, you can just add the `JSS_URL` key to your AutoPkg prefs file, or at the command line, like this:

    autopkg run -v TheBestAppEver.jamf \
        --key JSS_URL https://mylovely.jamfcloud.com

And of course, there's nothing to stop you running AutoPkg from a script, over and over on different servers. I frequently do this:

    for jss in "https://mylovely.jamfcloud.com" "https://grahampughsolutions.jamfcloud.com" "https://myob.jamfcloud.com" https://thatforgottentestserver.jamfcloud.com"
    do
        autopkg run -v TheBestAppEver.jamf --key JSS_URL "$jss"
    done

If you need to use multiple accounts or Client IDs on the same server, this is also possible. In this case, supply the `API_USERNAME` or `CLIENT_ID` key, and JamfUploader will look for a Keychain entry for the Jamf Pro server with that specific username/ID. This might be useful if you want to use multiple accounts with least privileges for specific operations, rather than a single account that can do all of the things.

## How to create the Keychain entry

The easiest way to add a Keychain entry for your Jamf Pro server is to use a new script that I've added to the [JamfUploader Repo][2] called [set-credentials.sh][3].

Run this script and you are asked to enter the Jamf Pro URL. Then you are asked to enter either an API account username and password, or API Client ID and Secret. It doesn't matter which you enter, either will be stored in the keychain. The script verifies that the credentials are correct by attempting to get a bearer token and retrieve the Jamf Pro server version.

    ./set-credentials.sh

    Enter Jamf Pro URL
    URL : https://mylovely.jamfcloud.com

    Enter username or Client ID for mylovely.jamfcloud.com
    User/Client ID : jamfadmin

    Enter password or Client Secret for myob on mylovely.jamfcloud.com
    Password/Secret : jamfsw03

    Credentials for mylovely.jamfcloud.com (jamfadmin) added to keychain

    Verifying credentials for mylovely.jamfcloud.com (jamfadmin)
    Token request HTTP response: 200
    Version request HTTP response: 200
    Connection successful. Jamf Pro version: 11.14.1-t1740408745756   

This creates a Keychain entry of type "internet password". This is not the same as an entry that you may have stored via Safari - those are known as an "application password".

The internet password entry created by `set-credentials.sh` contains a display label showing both the URL and username, allowing you to identify multiple entries for the same URL.

![Keychain Access window showing multiple entries](/assets/images/keychain-mylovely.png)

For a reason I am not party to, when using the `security` command to add a Keychain entry (which is how `set-credentials.sh` works), the URL does not show in the "Where" field. So you have to just trust that it's there!

![Keychain Access window opened on a specific account](/assets/images/keychain-jamfadmin.png)

You can of course also create a Keychain entry manually from within the Keychain Access app. To do this, you enter the full URL as the name.

![Keychain Access window new account via the GUI](/assets/images/keychain-gui-new.png)

In this case, you will see the URL in the "Where" field, but no account name in the Display Name field.

![Keychain Access window new account via the GU - no name](/assets/images/keychain-gui-no-user.png)

If you want to show the username in the Display Label, you have to go back and edit the name after you create the entry.

![Keychain Access window new account via the GU - updated name](/assets/images/keychain-gui-edit-user.png)

> Users of the [Multitenant Jamf Tools (MJT)][4] will find an alternative `set-credentials.sh` script, which allows you to provide a list of all your Jamf Pro instances in a text file, and populate your keychain with the credentials of multiple at once (e.g. in the case that you use the same credentials for multiple instances). The MJT also contains two wrapper sripts, `autopkg-run.sh` and `jamfuploader-run.sh`, which automatically use the credentials for the instance you choose from a list for running an autopkg recipe or a single `jamf-upload.sh` command.

## Distinguishing between account usernames or API Client IDs

When JamfUploader retrieves the credentials, it checks whether the retrieved account name is a version 4 UUID (e.g. `02B6E41F-0E87-4195-B150-AC5058C55F1B`). If so, it is interpreted to be an API Client ID. This matters because the method of authentication is different using an API Client as it is using an account username.

So don't use UUIDs for account names!

You can add as many different credentials to your Keychain as you wish, but if you add more than one entry per server, be sure to specify which account you want to use, otherwise JamfUploader will just pick the first one it finds.

Please note that if an "internet password" type of Keychain entry exists for your server (or, for the specified account on your server), this takes precedence - it will try to use this even if you supply credentials in AutoPkg prefs or via the command line.

## Do I have to switch to using the Keychain?

Not at all, you can continue to supply credentials via prefs or command if you wish. If you are not running AutoPkg on a Mac, or are running an ephemeral virtual Mac, it would not be possible to use the Keychain anyway, so I am not removing that functionality.

## Conclusion

I'm glad to finally be able to prevent Jamf Pro credentials needing to be stored in AutoPkg prefs and saved to the receipts, and I hope you'll find this a convenient, more secure, and reliable way of using JamfUploader when running AutoPkg on a real Mac.

[3]: https://github.com/grahampugh/jamf-upload/blob/main/set-credentials.sh
[4]: https://github.com/grahampugh/multitenant-jamf-tools

{% include urls.md %}
