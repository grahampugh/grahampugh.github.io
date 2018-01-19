---
layout: post
title:  "A Slack notification post-processor for AutoPkg/JSSImporter"
comments: true
---

If you are using [AutoPkgr] to run your [AutoPkg] recipes, you have an in-built Slack notifier. But what if you are not using AutoPkgr?

I've written an AutoPkg post-processor that you can call as part of a command-line AutoPkg run, to send a Slack notification using a webhook. I unimaginatively named it [Slacker](https://github.com/grahampugh/recipes/blob/master/PostProcessors/slacker.py).

This version is configured specifically to notify that a JSS recipe ran and updated a software title. It would be easy to copy the post-processor and change the inputs for Munki or other recipe runs.

## Creating a webhook

You will need a Slack workgroup and channel, of course, and you need to configure a webhook. To do this, follow the instructions at [https://get.slack.help/hc/en-us/articles/115005265063-Incoming-WebHooks-for-Slack](https://get.slack.help/hc/en-us/articles/115005265063-Incoming-WebHooks-for-Slack).

This should give you a webhook in the form `https://hooks.slack.com/services/XXXXXXXXX/YYYYYYYYY/ZZZZZZZZZZ`

## Running AutoPkg with the Slacker post-processor

First you need to add my repo:

```bash
autopkg repo-add https://github.com/grahampugh/recipes
```

Now run the command:

```bash
autopkg run MyRecipe.jss --post=com.github.grahampugh.recipes.postprocessors/Slacker --key webhook_url=https://hooks.slack.com/services/XXXXXXXXX/YYYYYYYYY/ZZZZZZZZZZ
```

Or, to run together with a recipe list:

```bash
autopkg run --recipe-list="/path/to/my/RecipeList.txt" --post=com.github.grahampugh.recipes.postprocessors/Slacker --key webhook_url=https://hooks.slack.com/services/XXXXXXXXX/YYYYYYYYY/ZZZZZZZZZZ
```

Any JSS recipe that results in a change should give you a Slack notification like this:

![img-1]

## Customising Slacker

I quickly put this together (hey, it's Christmas!), so it's not designed to be run with customisations. It's easiest to copy the script to your own AutoPkg git repository and make the changes you require. You can call any `<input>` or `<output>` variable that is available in any AutoPkg run. JSSImporter also outputs some JSON data that can be parsed (in my example, for instance, I extract the version number).

Add each variable you wish to parse to the `input_variables` array, for example:

```python
"category": {
    "required": False,
    "description": ("Package Category.")
},
```

Then, ensure you call that variable in the `main` definition, as follows:

```python
category = self.env.get("category")
```

You can then add this to your customised Slack output, which is in the following line:

```python
slack_text = "*New Item added to JSS:*\nURL: %s\nTitle: *%s*\nVersion: *%s*\nCategory: *%s*\nPolicy Name: *%s*" % (JSS_URL, prod_name, jss_policy_version, category, jss_policy_name)
```


[img-1]: /assets/images/slack-webhook-1.png

{% include urls.md %}
