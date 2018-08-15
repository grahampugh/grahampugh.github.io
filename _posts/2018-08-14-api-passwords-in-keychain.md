---
layout: post
title:  "Using the Keychain to store passwords for Jamf Pro API calls in bash scripts"
comments: true
---

The Jamf Pro "classic" REST API uses basic authentication, which requires credentials in the form of a username and password. When making API calls in a script using `curl`, the username and password is therefore passed in plain text.

Jamf Pro's Users & Groups Interface allows you to restrict what a particular user can access. But still, hard-coding the username and password into your API scripts and committing them to git is not ideal. 

It's easy enough to write a script which you run interactively, which prompts you to enter the credentials and exports them into the shell's environment. But if you're dealing with multiple API credentials each time, this can get tiresome.

Having looked at various options, such as [encrypting the credentials][1], and not being satisfied with any, I started to look at whether a keychain could be used on macOS devices to store the passwords, and whether they could be retrieved in a script.

It turns out that this is possible with the `security` command.

## Create a new keychain

If you [create a new non-login keychain][2] rather than using your local or iCloud keychains, the keychain can be put in version control (e.g. git) without exposing the API credentials, and it can be locked after use. 

## Unlock the keychain 

You need to somehow provide the password to unlock the keychain. This can be done as follows:

    security unlock-keychain -p API_KEYCHAIN_PASS KEYCHAINPATH

If you're running the script from terminal, you can leave out the password from the above command and let the GUI prompt you. If you're scheduling the script to run, you will need to export it as an environment variable or use a tool such as Jenkins which can supply secrets without exposing them to logs etc.

## Get values of a key from the keychain 

This command returns the user of a key (substitute the KEYNAME and KEYCHAINPATH accordingly):

    security find-generic-password -s KEYNAME -g KEYCHAINPATH 2>&1 | grep "acct" | cut -d \" -f 4

This command returns the password of a key (substitute the KEYNAME and KEYCHAINPATH accordingly):

    security find-generic-password -s KEYNAME -g KEYCHAINPATH 2>&1 | grep "password" | cut -d \" -f 2

The first time you run this, you will be prompted to allow the `security` command to access the key. Access to the key is maintained across devices if you copy the keychain to another computer.

## Lock the keychain

You can lock the keychain after use with the command:

    security lock-keychain KEYCHAINPATH

# Scripting it all

I have created a GitHub repository with an example of how this can be done. Head over to [keychain-creds] for details.

Have you used a different solution? I'm definitely still on the lookout for the best solution for performing basic authentication API calls securely!



[1]: https://github.com/brysontyrrell/EncryptedStrings
[2]: https://www.intego.com/mac-security-blog/create-a-non-login-keychain/


{% include urls.md %}
