---
layout: post
title:  "Send Slack notifications when a partition size exceeds a threshold"
comments: true
---

Here is a script to send notifications to a Slack channel when a server's main partition size exceeds a safe threshold. It is tested on Red Hat 7 and macOS Mojave.

## Requirements

* Set up an [incoming webhook][1] for a Slack channel.
* Install the python `requests` module on the server or computer on which the script will be run. Either:
    * `pip install requests` on macOS
    * `yum install python-requests` on Red Hat 7

* Add your Slack webhook to the script:

    ```slack_webhook_url = 'https://hooks.slack.com/services/XXXXXXX/YYYYYYYY/ZZZZZZZZZ'
    ```

* Set the percentage threshold for partition capacity. I set it to 80%:

    ```threshold = 80
    ```

* If you need to add more partitions to the search, add them to the `partitions` list:

    ```partitions = ['/', '/data', '/boot']
    ```

* If running on a Red Hat server, copy the script to `/etc/cron.hourly` or `/etc/cron.daily` depending on how often you want notifications. If running on macOS, you will have to create a LaunchDaemon to run the script on an hourly basis (for an example on how to do that, see the answer to this [StackOverflow question][2]).

## The script

{% gist grahampugh/e0d5cc5d1a494930561c45deb5281c2d %}


[1]: https://api.slack.com/incoming-webhooks
[2]: https://stackoverflow.com/questions/23532954/running-a-terminal-command-every-hour

{% include urls.md %}
