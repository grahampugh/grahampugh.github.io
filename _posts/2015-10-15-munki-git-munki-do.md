---
layout: post
title:  "Munki, Git and Munki-Do"
categories: munki git munki-do
comments: true
---

[Munki-Do](https://github.com/grahampugh/munki-do) inherited from its father [MunkiWebAdmin by Greg Neagle et al.](https://github.com/munki/munkiwebadmin), the ability to commit to a Git-initiated Munki Repo when making changes to Munki manifests.

Over the past few days I’ve been looking at how Git can interact with Munki. [Using Git with Munki is covered in the Munki Wiki.](https://github.com/munki/munki/wiki/Munki-With-Git) It describes how to set up a git repository on a server with which you have CLI access.

In my tests, I’ve been using a private repository on [Bitbucket](https://bitbucket.org/). I also started with an existing Munki repo, rather than setting up a new one.

Setting up git on an existing Munki Repo
----------------------------------------

Setting up the test Munki repo with Git was done as follows:

   * An empty repo was set up on Bitbucket.org
   * The existing munki_repo folder was initialised for git using the commands: `cd /path/to/munki_repo; git init`
   * The pkgs folder was set to be ignored, as I didn’t want the large pkg/dmg/app files to be uploaded to the repo. This was done by editing `/path/to/munki_repo/.gitignore` and simply adding the line `pkgs` to the file.
   * Then, sync the repo to the server:

{% highlight bash %}
$ git add .
$ git commit -m "Initial import"
$ git remote add origin git@bitbucket.org:myaccount/my_test_munki_repo.git
$ git push --set-upstream origin master
{% endhighlight %}

Munki-with-Git challenges
----------------------------------------

Version control is an essential tool in any Mac Administrator’s workflow. However, using Git with Munki has challenges due to the munki repository containing potentially very large packages, unsuitable for free cloud Git repositories such as Bitbucket, and challenging for paid private repositories on Github or elsewhere due to bandwidth issues. Even using your local organisation’s Git service could have bandwidth issues.

A solution such as [Git Fat](https://github.com/jedbrown/git-fat) could help with these issues, as the large files are dealt with separately. [Alistair Banks describes an example Git Fat setup here.](https://www.afp548.com/2014/11/24/introduction-to-git-fat-for-munki/) [Git-LFS](https://github.com/github/git-lfs/blob/master/docs/spec.md) is another solution that could help. I intend to test these out and report in a future post.

Configuring Munki-Do for Git
----------------------------------------

I have extended the functionality of Munki-Do so that it can now update Git repos when changes are made to pkginfo files, and therefore catalogs. In Munki-Do, Git is enabled by setting the path to the git command on the system hosting Munki-Do, in [settings.py](https://github.com/grahampugh/docker-munki-do/blob/master/django/settings.py). In my case, I’m running Munki-Do in a Docker Container, and the path is as follows:

{% highlight bash %}
GIT_PATH = '/usr/bin/git'
{% endhighlight %}

Bitbucket doesn’t respond to `--author` flags in git commit commands, so Munki-Do has been recoded to set the author variables based on the current user using `git config user.name` and `git config user.email` commands.

Since the Bitbucket repository is a private one, to enable automated interaction with the Bitbucket server, an ssh key needs to be generated on Munki-Do’s host, and the public key imported to the Bitbucket repo. [The process for doing this is described here.](https://confluence.atlassian.com/bitbucket/set-up-ssh-for-git-728138079.html)

My test Munki-Do host is a [Docker Container](https://github.com/grahampugh/docker-munki-do), so I imported my SSH key from my host Mac into the Docker Container using commands in the Dockerfile:

{% highlight bash %}
ADD id_rsa /root/.ssh/id_rsa
RUN touch /root/.ssh/known_hosts
RUN chown root: /root/.ssh/id_rsa && chmod 600 /root/.ssh/id_rsa
RUN ssh-keyscan bitbucket.org >> /root/.ssh/known_hosts
{% endhighlight %}

Note that `id_rsa` must be first copied from `~/.ssh/` to the same folder as the `Dockerfile`.

In my testing, sometimes the above `ssh-keyscan` command is not successful during `docker build`, in which case your git commits will fail. Take notice of the output of the build to ensure success! You can run the command again in a bash shell in the container if it fails during build.

