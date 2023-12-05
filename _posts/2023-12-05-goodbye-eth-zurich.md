---
layout: post
title:  "Personal reflections on my time at ETH Zürich"
comments: true
---

At the end of October, I said goodbye to ETH Zürich as my employers of 6.5 years. I'd like to pause to reflect on my journey.

I came to Basel, Switzerland in March 2016, leaving my previous job in the University of Bristol to follow my wife, who started a Scientific Research Fellowship at ETH Zürich's Department of Biosystems Science and Engineering. I owe my first lucky break in Switzerland to my well-connected friend **François Tiffreau**, which gained me my first experience supporting Jamf Pro, and owe my second lucky break to **Max Schlapfer**, who invited me to apply to work at ETH Zürich in the Client Delivery team.

I've been given tremendous opportunities since joining ETH, largely due to the recognition of the importance of personal development and training by my line management at the time, **Thomas Richter** and **Matteo Corti**, along with the support of Max and my other team-mate **Katiuscia Zehnder**. We arranged in-house Certified Jamf Technician training for a number of our internal customers, and Kati and I have both been lucky enough to undertake all the Jamf training courses (200, 300, 400, 370). I was encouraged to present at the Jamf Nation Live event in Munich in 2018 - my first presentation at an event of such proportions. I then presented at JNUC 2019, which was an amazing experience on such a big stage with hundread watching, and thousands having since watched on YouTube.

![The audience at JNUC 2019](/assets/images/jnuc-2019.jpg)

During the pandemic, I gave virtual presentations for the MacSysAdmins conference that normally takes place in Sweden, and together with **Anthony Reimer** for the MacAdmins Conference at Penn State University and once again JNUC. 

After two years of no in-person conferences, it was really special to go to San Diego for JNUC 2022 in person to participate in the Jamf Customer Advisory Board, and even more so to present at the MacAdmins UK conference this year in Brighton.

![San Diego and the Midway](/assets/images/pump-up-the-jamf.jpg)

Moreover, my team and I were given space to innovate. We have built some pretty cool stuff for a relatively complicated Jamf Pro environment. We have attempted to automate absolutely everything possible, while keeping the toolset small, avoiding additional tools such as ansible, puppet, chef or Munki, and sticking essentially to Jamf Pro. This gave our customers the full benefit of Jamf Pro with only one webapp to learn to use. To do this, we relied heavily on the Jamf Pro API, and version control using git (either GitHub for things that can be public, or self-hosted GitLab for things that cannot).

Many organisations use CI/CD tools for orchestrating their changes to Jamf Pro. That often involves building out their own frameworks using python, ruby, go, terraform, ansible, etc. We've used AutoPkg for as much as possible, which is a CI/CD tool in itself, since we already require it to obtain the large number of packages we deploy. That's why, by replacing JSSImporter with [JamfUploader], I have extended the capabilities of AutoPkg to encompass the updating of a large number of Jamf Pro API endpoints. We have used GitLab Runners, but only to schedule AutoPkg runs and keep secrets secret.

I'm proud to have created the JamfUploader processors for AutoPkg, and grateful to have been given the time and space to flash them out to them work beyond ETH for the benefit of all Jamf customers, recognising the importance of giving back to the community. It also been a pleasure to work with others in the community to expand the project and make it more accessible - particular thanks go to Anthony Reimer and **Marcel Keßler** for their collaborations.

![Two Jammie Awards](/assets/images/double-jammie.jpg)

I've also been glad to be heavily involved in the Jamf community. I was proud to win Jamf's "Jammie" award on two occasions, and been an active member of their Beta and Release Candidate Programs, and their Customer Advisory Board. Lately I've been very appreciative to be able to work directly with Jamf on implementing the necessary changes to JamfUploader to work with JCDS 2.0.

So as I move to my next chapter in Germany, once again reuniting with my wife who is now a Professor and Student Dean at the University of Erlangen/Nuremberg, I want to thank my colleagues at ETH IT Services and within the various IT Support Groups for their collaboration, support and friendship, and wish you all good luck with the future challenges.

_Uf Widerluege!_

![Uf widerluege](/assets/images/uf-widerluege.jpg)

{% include urls.md %}
