---
layout: post
title:  "Version controlling Munki and AutoPkg"
comments: true
---

__In this post I summarise what version control is, and why to add it to your Mac managament toolset. I then look at how to manage a Git-enabled Munki repository, and list other files associated with Mac management that you should consider version controlling.__

![img-1]

Why use version control?
-------------

Version control is a useful, if not essential part of a System Administrator's toolbox. Traditional file backup is good, but if you didn't notice a file corruption, or a mistake, before the next backup was made, then without version control, there is no way back to the working state. 

If you're a sole Mac administrator, running your administration tools on a Mac, then Time Machine is a basic form of version control. Versions are kept for several months, until your Time Machine disk runs out of space. However, Time Machine over a network doesn't work well over enterprise networks, and I've found it to be virtually useless over wi-fi. 

Backups to cloud services are also an option. Dropbox, Google Drive and the like all provide versioning in their UI. Collaboration is also possible, which is likely to be required in all but the smallest IT organisations.

Your organisation may offer backup with versioning using in-house solutions such as EMC Networker, or IBM's Tivoli Storage Manager.

However, all of the services I've mentioned thus far assume a single working copy of all the files. 

Collaborative Version Control
-------------

If you're working in a team, things can get more complicated. You may have multiple collaborators independently working on specific parts of a piece of software, or a new feature release, or you may have delegated some administration tasks to less experienced technicians, and wish to check their work before it affects a production service. Many people achieve this kind of work with ad hoc sending of files via email or cloud services, which becomes very hard to manage.

This is where version control systems such as [Git], [Subversion] and [Mercurial] step in. These offer a single repository which can be cloned locally onto an authorised user's computer for offline development, and pushed back to the server. Crucially, versions of the repository can be "[branched][3]" off so that a user's work can be carried out independently, without affecting a "master" or "production" version of the files. These branches can, using comparison techniques, be "merged" into the main (or any other) branch by authorised collaborators.

GitHub, BitBucket, GitLab
-------------

[GitHub] and Atlassian's [BitBucket] are cloud-based services that make managing Git and (in the case of BitBucket) Mercurial repositories easy. GitHub is widely used by Open Source Software developments, as public hosting is free, and the tools provided are the most widely developed. GitHub charge for private repositories, however, whereas BitBucket provide a number of private repositories per user. This makes BitBucket popular for in-house software development, and storage of private files.

[GitLab] also offer a cloud-based solution, but also a means of running a local Git server within your organisation. It provides a web interface similar to GitHub / BitBucket, but is on your local server. If you are using version control on a repository that contains large files, packages and/or binaries, and/or where bandwidth is an issue, this can become the best solution.

---

Munki
------------

![img-3]

[Munki] software deployment is managed using flat files, ideal for versioning using Git. However, the associated packages are stored in the same Munki repository, meaning that a whole Munki repository is likely to grow to 10s-100s GB. Storing a Munki repository on a cloud-based system is therefore likely to be expensive, and could have bandwidth issues if your central repository server is remote from your developers, if they are having to pull a whole large repository including packages down to their local computer every time they wish to make a change to something in the repository. There is also little value in version controlling the actual packages that are stored in a Munki repository, which are generally either downloaded from the internet, or created in-house using some scripted method that would most likely (or should) have its own Git repository. So, it may be most efficient to upload packages directly to the Munki server, and set the git repository to ignore the `pkgs` directory of a Munki repository and to back it up solely from the central server.

__The [Munki Wiki][munki-with-git] provides tips on how to git-enable your Munki repository, and for using Munki with git on the command line.__

*__Note:__ A version of Munki called [Simian], which runs on Google App Engine, has been developed to handle a cloud-based Munki repository, which could suit your organisation if you have good bandwidth available to your clients.* 

The common tasks associated with managing a Munki repository are as follows:

* Enrolling clients
* Importing software to the repository, and adding to a particular catalog
* Importing from AutoPkg
* Assigning software packages to manifests
* Assigning manifests to catalogs

All these tasks effect text files in the repository. Importing software obviously also adds binaries to the repository. Lets look at how these are commonly performed, and what response is required in a Git-enabled repository:

Enrolling clients
=============

Clients are "assigned" a particular manifest on the client itself. Some administrators use a common manifest for a set of clients; others assign a unique manifest per client. One method of automating the latter process is using [Munki-Enroll]. Where new clients result in a new manifest, the Git repo will need to be updated. I am not aware of a version of Munki-Enroll that automates this process yet, so it would have to be done manually.

Importing software to the repository, and adding to a particular catalog
=============

Importation of a new piece of software to a Munki Repository is typically done on the command line using the [munkiimport] command. Alternatively, it can be done using the [MunkiAdmin] software on a Mac, or manually where necessary. The process is not complete until `makecatalogs` is run, which assigns the software to the catalogs assigned in the `pkginfo` file associated with each package. At this point, the Git repository should be updated. At present, this must also be done manually.

Importing from AutoPkg
============

[AutoPkg] provides community-scripted automated updating of many software titles, including scripted recipes that automate the importation into Munki. An AutoPkg recipe exists to automate `makecatalogs` after a change to the repository has occurred as a result of an AutoPkg import. The Git repository needs to be updated after `makecatalogs` is run (or, alternatively, after each package is imported).

Some AutoPkg recipes have been written to automate this task:

* [@n8felton]'s [MunkiGitCommitter.py][2] is an [AutoPkg postprocessor][Autopkg prepostprocessors] which will add and commit each new pkginfo file to the master branch of a Git repository. This will result in a commit for each addition. The commits need to be pushed manually to the repository.
* [My][@GrahamRPugh] adaptation of the AutoPkg [MakeCatalogs recipe][1] provides a single commit to Git after a complete AutoPkg run, after `makecatalogs` has been run.
* [My][@GrahamRPugh] [MunkiGitBranchingCommitter.py][1]  is an [AutoPkg postprocessor][Autopkg prepostprocessors] which will add and commit each new pkginfo file to new, unique branch of a Git repository for examination by a repo administrator.

If you use [AutoPkgr], the good news is that an upcoming version, currently in beta testing, will allow the addition of pre- and post-processors to your recipe list, and allow your own custom MakeCatalogs recipe to run after all other Munki recipes have been processed. 

Assigning software packages to manifests
==============

Software packages are assigned to manifests by editing the `pkginfo` file associated with the package. This can be done manually or using a tool such as [MunkiAdmin] or [Munki-Trello]. If using those tools, Git must be updated manually afterwards. [Munki-Do] is especially suitable for this task, as it has been designed to have the option to handle adding, committing and pushing changes to Git, including the option to push to a new branch.

Assigning manifests to catalogs
==============

Catalogs are assigned to manifests by editing the text (XML) file named after the manifest, and then running `makecatalogs`. Manual editing, [MunkiWebAdmin] or [MunkiAdmin] can be used for these tasks, all of which require manual updating of Git afterwards. [Munki-Do] handles the updating of Git, including the option for the updates to be pushed to a new branch.

---

Other files to put under version control
--------------

The Munki repository is not the only set of files required to run effective Mac management, and any file changed locally when setting up or managing your system should be added to a version control service such as Git to provide a robust, reproducible service. A not exhaustive list follows:

* [DeployStudio] repository: Specifically, the `/Databases` (which contains client information and workflows) and `/Scripts` folders would benefit from version control. Images and packages should also be backed up, but not necessarily to a Git server.  
* __Imagr__ [(link)][Imagr]: As above, workflows and scripts should be put under version control.
* [AutoPkg] `/RecipeOverrides` folder, where you keep your local overrides to AutoPkg recipes.
* Any scripts you produce locally, such as AutoPkg recipes and package-making scripts (e.g. The Luggage).
* User profile settings, such as your `.bashrc` or `.bash_profile` files.
* Server configuration: If you're running Munki and associated reporting and management tools on a local server, you should consider versioning the files you edit to make the server work in your environment. These come under the category of Configuration Management, and could be done directly or via a [Puppet] or other config management server, where the files were under version control and changes were pushed to the server. Such files could include:
    * Security: `iptables` and `selinux` 
    * Samba: `smb.conf`
    * Apache: `httpd.conf` and `<VirtualHosts>` files
    * PHP: `php.ini` 
    * MunkiWebAdmin: `settings.py` and the database
    * Sal: `settings.py` and the database
    * Munki-Do: `settings.py` and the database
    * MunkiReport-PHP: `config.php`
    * Munki-Enroll: `config.php`
    * Databases associated with Dockerized services: these could include Munki, Sal, Munki-Do, Munki-Trello and so on. 
    * Copies of the files or commands used to run the Docker containers would also benefit from version control.

[1]: https://github.com/grahampugh/recipes/tree/master/SharedProcessors
[2]: https://github.com/autopkg/n8felton-recipes/tree/master/SharedProcessors
[Subversion]: https://subversion.apache.org
[Mercurial]: https://www.mercurial-scm.org
[3]: https://git-scm.com/book/en/v1/Git-Branching

[img-1]: http://cdn.electric-cloud.com/wp-content/uploads/2016/03/version-all-the-things.gif
[img-2]: http://opendigitalscience.eu/wp-content/uploads/2015/09/github-logo.png
[img-3]: https://munkibuilds.org/logo.jpg

{% include urls.md %}

