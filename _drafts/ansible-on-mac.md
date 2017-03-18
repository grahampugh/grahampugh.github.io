---
layout: post
title:  "Ansible on Mac"
comments: true
---

Obtaining Ansible
---
As per [here][1], [install Ansible on Mac using Pip][2].

```
sudo easy_install pip
sudo pip install ansible
```

To check the installation worked:
```
[~] $ ansible --version
ansible 2.2.1.0
  config file =
  configured module search path = Default w/o overrides
```

Inventory lists

Ad-hoc commands

Playbook (yml) files

Check mode





[1]: http://docs.ansible.com/ansible/intro_installation.html#latest-releases-on-mac-osx
[2]: http://docs.ansible.com/ansible/intro_installation.html#latest-releases-via-pip

{% include urls.md %}
