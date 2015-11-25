---
layout: post
title:  "Git branches with Munki-Do"
comments: true
---

I have extended the capability of [Munki-Do] to handle branching in a Git-enabled [Munki] repository, as may be required in larger IT Support teams. Munki-Do now has a `GIT_BRANCHING` option which creates a new, unique branch for each new change made. This branch is identified by Munki-Do user and timestamp. 

When enabled, each commit creates (checks out and pushes) a new branch name such as `graham_20151125152926`. After pushing the changes to the new branch, the server immediately checks out the master branch. This is done to prevent the ability for multiple Munki-Do users to be competing for the checked-out branch. Therefore, the user that made the change will not see it in their view of Munki-Do. The exception to this rule is when a user creates a new manifest, because a user needs to populate the new manifest before it is any use, and it would be unproductive for that user to have to wait for a merge of the new manifest before being able to populate it.

It is then up to a the repository administrator to create a Pull Request and merge the new branch into the master branch. Only then, and after pressing the "Update View (git pull)" button, will the user see the changes in Munki-Do.

I would recommend the repostory administrator setting up some sort of notification of changes to the repo, so that they are informed when a change is made and a merge needs to be considered. This could be, for example, an email notification, or a [Slack] notification.

If both `GIT_IGNORE_PKGS` and `GIT_BRANCHING` are enabled, then since changes are made to a new git branch and are not "live" on the production branch, it is important that the contents of the pkgs folder are not deleted at the time of commit. The act of deleting contents from the `pkgs` folder then becomes manual, to be done by the administrator performing git merges. To facilitate this, use the "Manage Orphaned Packages" link, which lists all files in the `pkgs` folder which are not referenced in a `pkginfo` file (and which are therefore irrelevant to the munki repository). These packages can then be selected and deleted using the UI. At present this link is only available to users that are marked as "Staff" in the Munki-Do admin panel.

The `GIT_BRANCHING` option is set either in `munkido/settings.py`, in the `Dockerfile`, or using the flag  
`-e DOCKER_MUNKIDO_GIT_BRANCHING=yes` in a `docker run` command. Of course, Git must also be enabled with the `GIT_PATH` variable (see my previous blog post, [Munki, Git and Munki-Do][1]). An example `docker run` command might be:

~~~ bash
docker run -d --restart=always --name munki-do \
	-p 8000:8000 \
	-v /Users/Shared/munki_repo:/munki_repo \
	-v /Users/Shared/munki-do-db:/munki-do-db \
	-e DOCKER_MUNKIDO_GIT_PATH="/usr/bin/git" \
	-e DOCKER_MUNKIDO_GIT_BRANCHING=yes \
	-e DOCKER_MUNKIDO_GIT_IGNORE_PKGS=yes \
	-e ADMIN_PASS="pass" \
	grahamrpugh/munki-do
~~~

[1]: {% post_url 2015-10-15-munki-git-munki-do %}

{% include urls.md %}

