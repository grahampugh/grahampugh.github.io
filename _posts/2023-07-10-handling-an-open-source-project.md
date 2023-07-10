---
layout: post
title:  "One Mac Admin's tips on maintaining a popular Open Source project"
comments: true
---

At the recent MacAdmins UK conference [I gave a presentation][6] about my [erase-install] script. [The video is now available here][MacAdUk 2023 Video].

At the end of this presentation, I included a section on what happens when a project you share online has become popular. This section seemed to resonate with some of my audience who, like me, would not consider themselves as software engineers but are called upon to write shell scripts as part of their admin work, and are interested in sharing their code if it can help the Mac community. So I've decided to turn that last 10 minute section into a blog post and expand on some of the areas that were covered.

I use erase-install here as an example of what you might face if you make your code available for use by others, and it starts to get used a lot. I'm sure my experiences are similar to many of our colleagues.

As this is a long post, here's a table of contents.

- [Why open source?](#why-open-source)
- [Set up a git repository](#set-up-a-git-repository)
  - [Create Readme, Changelog, and License Files](#create-readme-changelog-and-license-files)
  - [Create a Wiki](#create-a-wiki)
  - [Create an F.A.Q. page in your wiki](#create-an-faq-page-in-your-wiki)
  - [Use GitHub issues and discussions](#use-github-issues-and-discussions)
  - [Use Versions, Releases, and Tags](#use-versions-releases-and-tags)
  - [Use Feature Requests](#use-feature-requests)
  - [Use Pull Requests](#use-pull-requests)
- [Create a MacAdmins Slack channel](#create-a-macadmins-slack-channel)
- [Conclusion](#conclusion)

![A Doge dog surrounded by superlatives about open source projects](/assets/images/OpenSource/OpenSourceDoge.jpg)

## Why open source?

Making your source code openly available online is good for a few reasons:

- It gives you visibility in the field if you're trying to build a reputation.
- It can help your organisation attract new employees in the Mac Admin field by highlighting that good work is happening there.
- It helps other members of the community who might not yet have the skills you have gained.
- Exposing your work might result in somebody else improving it or adding ideas you haven't thought of inmcluding.

But what are the consequences? Is it going to generate too much work? Do you want the extra responsibility? And what happens if you don't want to continue maintaining it?

Just putting a script on GitHub doesn't necessarily mean any extra work. I have lots of scripts on GitHub that probably nobody else is using. Others might get used, but they're simple and just work, so need little documentation or support.

Erase-install has become a more complex script that has had to keep evolving as Apple have moved the goalposts a few times. It was clumped together as a quick idea and probably not particularly well written or documented. Nonetheless, it started to get found and used. And when people started using it, they started asking about it in the Mac Admins Slack, Jamf Nation, and on the GitHub page.

The following tips are based on hindsight, as well as a reminder to myself when I start a new project and think it might be able to be open sourced.

## Set up a git repository

If I had anticipated that erase-install was going to be used by many people, I would have set up some of the structures I now have in place before publishing the script. For example, when I first published the script it was as a "gist", which is more like an unstructured snippet than a proper project. But actually, repositories (repos for short) on GitHub, GitLab or Bitbucket are extremely easy (and free) to set up - not much more complex than a gist really, and easier to maintain in the long run.

Here's some basic tips on what to do when setting up a git repo for a script. The nomenclature and links given here are for GitHub, but GitLab and Bitbucket have similar features.

### Create Readme, Changelog, and License Files

Create a `README` file which contains a short description of the project, but not the full instructions. This file is best created as a Markdown file (`README.md`). In GitHub, GitLab and Bitbucket, this file will be automatically shown on the front page of the project.

Choose one of the licenses available during the repo creation process - best to set this up from the start, just in case.

Create a `CHANGELOG.md` file and record any changes you make to the script in here by date. This helps you and other users keep track of changes you made (and why!).

### Create a Wiki

Enable the [Wiki][2] feature, and link to the Wiki's Home Page from your README file. Editing the wiki is easy to do online and is a little more feature-rich than just using a README file. Linking directly from the `README` gives clear instructions to first-time visitors where to look for instructions.

### Create an F.A.Q. page in your wiki

Don't be surprised that people don't always look for documentation before they ask for help. And never underestimate how complete and explicit the documentation needs to be. Making an F.A.Q. page in your wiki has been very helpful for me. It's far quicker to just give somebody a link to something already written, than to type the same answer out over and over.

### Use GitHub issues and discussions

I've also found it to be a good idea to ask people to open a GitHub issue for any sort of bug or question that can't be answered immediately, otherwise it can be too hard to keep on top of it all.

[GitHub Discussions][1] are also useful, because not everyone is in Slack. This is not enabled by default, but I would recommend that you enable these for your repo. This allows people to ask general questions about the project without the formality of reporting a bug or requesting a new feature.

You may wish to create all these files into the `main` branch of the repo before publishing the first version of the script. You can then create a development branch while you work on the first version of the script. See below for more information about branches.

### Use Versions, Releases, and Tags

Add a version string to your script or project right from the start. If your project is a single file, add a simple version string in the script, as below. You can then use this version when recording changes in your CHANGELOG file. Don't start with a version less than 1. Your first attempt is version 1.0 (or 1.0.0). You will never have a "final" script so don't pretend that you have a beta process 😀.

```sh
version="1.0.0"
```

Using semantic versioning (e.g. `1.0.0`) gives you the flexbility to do future major refactors (`2.0.0`, `3.0.0`, etc.), feature releases (`1.1.0`, `1.2.0`, etc.), and bug fixes (`1.0.1`, `1.0.2`, etc.).

If you want to use the repo as the proper source of the script (which you should), you may need to save "unfinished" changes to your script in the repo. To prevent people downloading a non-functional script, create a new git branch for each new version that you start, and push the first change to the script since the previous working version to that branch. Don't forget to bump the `version` string in the script itself too (`2.0.0` or `1.1.0`, or `1.0.1`, depending on how big the changes are), and record those changes in the CHANGELOG as you go along. When you think you've finished a new version and tested that it works, you can merge the changes from the new branch into your `main` branch.

Setting a **tag** for each version allows you to make a **release**. Tags and releases help you help others, because people can download a specific version rather than just whatever the latest commit is, and you can identify which version people used if you're helping them with a problem.

Tags are made at the command line, and then you push them to GitHub:

```bash
git tag v20.0.1
git push --tags
```

If you're not sure what the next tag should be, just type `git tag` to get a list of existing tags.

If you need to remove a tag because you updated the code since setting a tag, and want to set that same tag again, use these commands to remove the tag locally and from GitHub:

```bash
git tag -d v20.0.1
git push --delete origin v20.0.1
```

Then you can set the tag and push it again.

In GitHub, you make a release from a Tag. Click on the Releases link, then click on the Tags tab, click on the three dots to the right of the tag you just created, and select "Create Release". You then get the opportunity to enter a name (I usually just call it the version string), add a description (I usually just copy-paste in the entry from the CHANGELOG file), and if relevant, upload a file.

### Use Feature Requests

An inevitability about sharing a project is that it might not work in different environments to your own. People also have their own ideas about how the thing should work. Both these aspects become more significant as the usage grows.

If you choose to accept feature requests, they can be the most time-consuming form of support. I've found it essential to ask people to record their Feature Request in the GitHub repo so that I could keep a good overview of the things to consider when I next have time to work on the project. 

In GitHub, Feature Requests are also created in the "Issues" section. To better distinguish between a bug report and a feature request, you can set up [templates][3] which encourage people to create their request in a form that is useful for you.

Adding [labels][4] to them also helps break them down into things you can go ahead with versus those things that require further input from the requester.

There are important questions to ask yourself when getting feature requests:

- Do I agree that the feature request is actually a useful improvement?
- Is it going to help anyone apart from the one person asking for it?
- Is it relevant to my original reason for creating the project?
- As I'm maintaining the project at work, is the request relevant to my organisation's requirements?
- How difficult and complicated is it going to be to design the change, and is it going to make the overall project more difficult to understand?
- Am I interested enough in the feature to support it in the future if it stops working for some reason?

Remember, you don't have to accept feature requests! 

### Use Pull Requests

Similar considerations apply to Pull Requests. A [Pull Request][5] is where somebody has discovered a bug or has a feature request, but instead of just asking you to fix it, they update the code themself and only ask you to merge in their changes. Luckily, Git is very clever at figuring out how to safely merge their code into yours.

I've found that I get Pull Requests more often for projects that are coded in shell, as opposed to e.g. python, because far more people understand it than other scripting languages.

I've found it really important to make sure you understood the code changes before accepting and merging the pull request. If you don't understand the code, you're just building problems into your project that may come to haunt you later.

Also, perhaps it's obvious, but - just because that person took the time to prepare the code for their request, you still don't have to accept pull requests! If you don't want to accept it, that person can still maintain a fork of the project with their changes in it - they're still benefitting from your work, and they will be able to merge any changes you make in the future into their own fork. 

The same is true if you decide that you cannot or don't want to continue maintaining the project. There are all sorts of legitimate reasons why you might want to stop maintaining some open source project - for example lack of time, a new job, or just because you stopped using it. Again, people can make their own fork and maintain it themselves, if they still have a use for it when you don't. Somebody can take the project over if they think it's still useful. Just make it clear in the `README` file and/or Wiki of the repo that your version is no longer maintained, and people will slowly move on.

## Create a MacAdmins Slack channel

It has been easier for me to help people who are having problems with erase-install since I adopted a channel in the MacAdmins Slack. In addition, monitoring for keywords that relate to the project gives me notifications when somebody mentions it in any channel. 

When I get a notification, I can see if somebody's having a problem and if so, I can advise them to ask again in the `#eraseinstall` channel, where there are an increasing number of knowledgeable people who have been helpful in answering questions by newcomers. It's easy from there to ask people to create Issues and Feature Requests in the GitHub repository for anything that's not a quick answer.

The erase-install channel has grown to over 1200 members, and averages 120 messages a week. If your channel reaches this kind of load, it can be good to turn off the notifications in the evening if you want to tune out of work, especially when you live in Europe, since a lot of the traffic comes from North America...

## Conclusion

Here's my TL;DR about making a code project public:

- Expect more work than if you had not published the thing
- You can mitigate that a bit by taking the time from the beginning to create good documentation
- Make a Slack channel if you're starting to get questions about it.
- Create FAQs as you answer questions - this can save you repeating yourself over and over.
- Keep on top of any problems by encouraging people to record it in your GitHub repo.
- Keep the code simple and readable, even if it might seem less efficient. This increases the chances that people will send you pull requests and answer their own questions.
- The MacAdmins community is amazing. You can expect a lot of thanks and a lot of help. So don't be shy in sharing your code!

That last point is the main reason I recommend open-sourcing your code. I could never have anticipated the amount of thanks I've received from people using erase-install. And, after benefitting from ths community so much, it's also only fair to give a little back, whether that's in the form of sharing code or answering questions.

![Gif from the IT Crowd of two people giving each other a high five](/assets/images/OpenSource/itcrowd-handslap.gif)


[MacAdUk 2023 Video]: https://www.youtube.com/watch?v=kUQcfXzzeQs&list=PLmBOyWhgnnx96KnkTANQ7-eREGTFy9_7P&index=15
[1]: https://docs.github.com/en/discussions
[2]: https://docs.github.com/en/communities/documenting-your-project-with-wikis/about-wikis
[3]: https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/about-issue-and-pull-request-templates
[4]: https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/managing-labels
[5]: https://docs.github.com/en/pull-requests
[6]: https://grahamrpugh.com/2023/05/14/macaduk-presentation-eraseinstall.html

{% include urls.md %}
