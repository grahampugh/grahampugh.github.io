---
layout: post
title:  "Maintain daily, weekly and monthly MySQL backups"
comments: true
---

Here is a quick bash script to create backups of MySQL databases on a daily, weekly and monthly basis using `mysqldump`. It maintains a specified number of each backup interval before deleting them to prevent the server filling up to infinity with backups.

The script is designed to take a complete backup of all databases, and then take individual backups for each database. Though this increases the overall backup size, it serves two different purposes. If the entire server goes down, you'll want to restore all databases and schemas in one go. If you're wanting to undo an error in a particular database, it's nice to have a dump of that database to restore.

Databases are dumped to `.sql` files which are compressed to `gzip`. The folder structure mirrors the database names, with the complete backup going into a folder named `all`.

## Credentials

To prevent putting user and password details into the script in plain text, you can create a file at `/etc/.my.cnf` with the credentials:

```
[mysqldump]
user=root
password=PUTYOURROOTPASSWORDHERE
```

Ensure that only root can read the file:

```
chmod 600 /etc/.my.cnf
```

## Storing the backups

Create a directory to store the backups. This might best be on a mounted volume in case of total disaster. But here, it's just on a local partition, because YOLO:

```
mkdir /data/MySQL-Backups
chmod 600 /data/MySQL-Backups
```

Make sure this folder corresponds to the folder stated in the script below.


## The script

This script should go into `/etc/cron.daily` on a Red Hat or CentOS server on which the MySQL database is situated. Otherwise, add an entry into your `crontab` or create a LaunchDaemon. It's easy to change the number of daily, weekly and monthly backups kept by changing the number in the `DAILY_DELETE_NAME`, `WEEKLY_DELETE_NAME` and `MONTHLY_DELETE_NAME` variable definitions.

Note that the script won't work on macOS unless you install the `coreutils` to get GNU date options (not covered here).

{% gist grahampugh/aa0d98968206336bfb12c78e94c88393 %}


[1]: https://api.slack.com/incoming-webhooks
[2]: https://stackoverflow.com/questions/23532954/running-a-terminal-command-every-hour

{% include urls.md %}
