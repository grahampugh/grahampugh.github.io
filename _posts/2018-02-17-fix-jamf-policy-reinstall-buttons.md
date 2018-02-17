---
layout: post
title:  "Fix Jamf Pro 10 Reinstall Button Values"
comments: true
---

[Jamf Pro] 10 introduced a secondary Self Service button value, which appears after a policy has been run once. The default initial button value is "Install", and the default secondary value is "Reinstall". Both can be changed. Since Jamf Pro 10.2, both can also be changed via API.

As the new button value was set to "Reinstall" on all existing policies regardless of the value of the initial button value, this could be confusing for users. For example, an uninstaller policy with the initial button value "Uninstall" would show "Reinstall" after the user had run the uninstaller policy. Of course, an uninstaller policy cannot reinstall the software; it can only uninstall it again if it is (re)installed using a different policy or other means.

To prevent this confusion, I've written a script which uses the API to ensure that the secondary value is the same as the initial value on all policies. It will loop through all policies and set the `reinstall_button_text` API key to match the `install_button_text` key. You can restrict it to a particular category if you only want it to change the values of, for instance, your uninstaller policies, or are only concerned with policies that have Self Service enabled (though there is no harm in setting the value on non-Self-Service policies).

You can grab the script from my Gists:

{% gist b5f9420b4fd97d4974c5345823680ce1 %}

{% include urls.md %}
