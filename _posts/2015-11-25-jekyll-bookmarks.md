---
layout: post
title: "Jekyll blogs: create a bookmarks file for commonly used weblinks"
comments: true
---

I just started using [Jekyll] for blogging, and the nature of my blog means referencing various weblinks in almost every post. A link in a Markdown is normally constructed inline like so:

```html
I just started using [Jekyll](http://jekyllrb.com/) for blogging... When
[blogging with Jekyll](http://jekyllrb.com/), I find some tasks repetitive...
```

To avoid repeated effort in scripting the links in [Markdown], I've created a list of commonly used weblinks at [`_includes/urls.md`][1]. This list is automatically referenced in each new post by adding the following code at the bottom of each post:

```html
{% raw %}{% include urls.md %}{% endraw %}
```

The syntax of this file is simply a list. I already have 43 links in the file, but here's an extract:

```
[Markdown]: http://en.wikipedia.org/wiki/Markdown
[GitHub]: https://github.com
[Jekyll]: http://jekyllrb.com/
[@GrahamRPugh]: https://twitter.com/grahamrpugh
[On The Subject Of Macs]: https://grahamrpugh.github.io
```

When referencing a link in a post, one then only needs to include the correct link text in square brackets, e.g. `[Jekyll]`. Or, if the text of the link needs to be different, the reference becomes something like `[blogging with Jekyll][jekyll]` (note that the text of the reference itself is case-insensitive).

To ensure I start a new blog post with all the required initial syntax, I start by copying a blog template file ([`_drafts/template.md`]({{ site.src_url }}/\_drafts/template.md)), which contains the following:

## {% highlight html %}

layout: post
title: "Template post"
comments: true

---

Enter content here...

{% raw %}{% include urls.md %}{% endraw %}

{% endhighlight %}

[1]: {{ site.src_url }}/\_includes/urls.md

{% include urls.md %}
