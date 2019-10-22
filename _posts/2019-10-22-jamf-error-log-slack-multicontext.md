---
layout: post
title:  "Slack notifications for errors in a multi-context Jamf Pro environment"
comments: true
---

If you're running a multi-context, on-premises [Jamf Pro] environment, you probably have some kind of third-party log aggregation and reporting tool to hand. But if you don't have that yet, here's a simple script you can use to get an aggregated output of errors and severe warnings from all your Jamf instances. It will report all log output marked as `[ERROR]` or `[SEVERE]` in the previous hour.

## Usage

This script assumes you are running Jamf Pro on a Linux server and have `anacron` installed. It also assumes that tomcat instance logs are reported to `/var/log/JSS/<instance>/JAMFSoftwareServer.log` However, it would work from any task scheduling tool.

Simply provide a Slack incoming web hook for whichever channel you want to use, and place this script into `/etc/cron.hourly`. The script needs to be executable.

The script outputs errors with the time stamp. If the error is `SEVERE`, this is explicitly printed in the output.

## The script

{% gist grahampugh/58c73bb3e46681d3d0d25dbb15126bd1 %}


{% include urls.md %}
