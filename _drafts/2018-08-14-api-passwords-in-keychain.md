---
layout: post
title:  "Using the Keychain to store passwords for Jamf Pro API calls in bash scripts"
comments: true
---

The Jamf Pro "classic" REST API uses basic authentication, which requires credentials in the form of a username and password. When making API calls in a script using `curl`, the username and password is therefore passed in plain text.

Jamf Pro's Users & Groups Interface allows you to restrict what a particular user can access. But still, hard-coding the username and password into your API scripts and committing them to git is not ideal. 

One method to avoid this is to put the credentials into a password-protected Keychain database file, and call them using the `security` command. The Keychain Database can be put in version control without exposing the API credentials, and can be locked after use. You still need to provide the credentials to unlock the keychain, so these should be provided directly in the terminal, or added as environment variables to the shell (and the shell closed when the task is completed).

Keychains can only be accessed from macOS, so this method is only useful for scripts running on a Mac.

# Setting up a keychain



# Unlocking the keychain when required


# Configuring a script to call the credentials from the keychain



[1]: https://github.com/brysontyrrell/EncryptedStrings

{% include urls.md %}
