---
layout: post
title:  "A Simple Munki Server Test Environment"
comments: true
---

Introduction
-------------

[Munki] and [AutoPkg] are mature tools for automated software deployment and update 
maintenance.  Both are CLI-based tools, but there are a number of GUI tools designed to 
make interacting with the tools easier.  This post describes a quick setup method using
[AutoPkgr] and [Docker-Machine], which provides a Munki server, and web-based GUIs for 
[Munki-Do] and [Sal].  

Setting up AutoPkgr
-------------

Create a Munki repo folder at `/Users/Shared/repo`. (add folders)
Download AutoPkgr.
Configure Munki Repo.
Add the following recipes:

```
DockerToolbox.munki
munkitools2.munki
osquery.munki
Sal.munki
Sal-osquery.munki
```
Add optional extras, e.g. Java, Skype, Slack...


Run Recipes Now.

Running the Docker Containers
-------------

`git clone` the docker image
cd
Configure the variables:

```
MUNKI_REPO
MUNKI_PORT
MUNKI_DO_DB
MUNKI_DO_PORT
SAL_DB
SAL_PORT
```

Post-install:
Docker IP is shown. This is the internal.
Public IP.

Client setup
-------------

Manual install & configure of Munki client, or create a client using override.

Autopkg override for Sal.

Munki-Do: create core manifest with munkitools, sal, osquery
Create default manifest with core as included_manifest, any extras as optional installs, 
and Production catalog.
Use Munki-Do to move all the packages into Production catalog.

Run MSU on client. Sal should be installed.



{% include urls.md %}

