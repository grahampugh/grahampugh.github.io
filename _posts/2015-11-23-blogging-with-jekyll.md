---
layout: post
title:  "Blogging with Jekyll"
comments: true
---

This blog has run on [WordPress](https://www.wordpress.com) for a while, but I have 
increasingly found its format to be somewhat frustrating, particularly when it comes 
to quoting code, which is a frequent occurrence in this blog. I prefer to edit in 
[Markdown](http://en.wikipedia.org/wiki/Markdown). I've also been keen to 
embrace version control where possible.  I've therefore taken the step to migrate the blog 
to [GitHub](https://github.com/grahampugh), and use [Jekyll](http://jekyllrb.com/). 
GitHub provides [free hosting for Jekyll blogs](http://pages.github.com/).

Here, I describe the steps I took to create this blog:

   * [Registering with GitHub](https://github.com)
   * Creating a special repository for the blog
   * Installing Jekyll on my computer
   * Cloning a template blog
   * Editing the template to create the blog identity
   * Editing `index.html`, and `archive.html` 
   * Adding Pagination
   * Adding comment fields and counts to posts using Disqus
   * Adding Google Analytics
   * Creating the first blog post
   * Migrating posts from Wordpress

Creating a special repository for the blog
=======================

A GitHub Pages repository is like a normal repository, but must be registered with a 
specific name referring to your GitHub account name, for instance 
[grahampugh.github.io](grahampugh.github.io). Instructions for setting up this repository
are found at [https://pages.github.com/#user-site](https://pages.github.com/#user-site).

When the repository is set up, you can clone the empty repository to your computer:

{% highlight bash %}
$ git clone {{ site.src_url }}
{% endhighlight %}


Installing Jekyll on my computer
=======================

Installing Jekyll allows you to run a 
development server on your computer, so that you 
can easily preview your blog posts as you write them, without having to upload them to 
GitHub. Installation is easy - just follow the instructions here: 
[http://jekyllrb.com/docs/installation/](http://jekyllrb.com/docs/installation/)

Cloning a template blog
=======================

When run from the root folder of your new repository, `jekyll build .` command builds a template site on your computer. The 
`jekyll build --watch` command automatically watches for changes to the files in the 
current folder, and regenerates the site as necessary. For more details see 
[http://jekyllrb.com/docs/usage/](http://jekyllrb.com/docs/usage/)

Editing the template to create the blog identity
=======================

The site settings are contained in the root directory, in `_config.yml`. I edited the 
file as follows:

{% highlight yaml %}
# Site settings
title: On The Subject Of Macs
email: g.r.pugh@gmail.com
description: > # this means to ignore newlines until "baseurl:"
  The Blog of a Mac Support Specialist in a UK University
baseurl: "" # the subpath of your site, e.g. /blog
url: "http://grahampugh.github.io" # the base hostname & protocol for your site
twitter_username: GrahamRPugh
github_username:  grahampugh
{% endhighlight %}

Editing index.html, and archive.html
=======================

The default template has a list of blog posts in [`index.html`]({{ site.src_url }}/index.html). I altered this to include 
the first 50 words of each post:

{% highlight html %}
    <p class="post-meta">{% raw %}{{ post.content | strip_html | truncatewords: 50 }}{% endraw %}</p>
{% endhighlight %}

I moved the original list-style page to [`archive.html`]({{ site.src_url }}/archive.html). 

Adding Pagination
=======================

Pagination enables you to restrict the number of posts visible on the first page of an index or list page, so that the page doesn't get too long. To set this up, install as follows:

{% highlight bash %}
$ gem install jekyll-paginate
{% endhighlight %}

In the [`_config.yml`]({{ site.src_url }}/_config.yml) file, append the following lines:

{% highlight yaml %}
#pagination
gems: [jekyll-paginate]
paginate: 5
{% endhighlight %}

The numeric value for the `paginate` setting can be altered to set the number of items to be listed per page.

Adding comment fields and counts to posts using Disqus
=======================

[Disqus](http://disqus.com/) is the most common embedded comment system used with Jekyll blogs. After you [register with Disqus](https://disqus.com/admin/create/), you are provided with a block of code to add to your site template. I created a file at [`_includes/comments.html`]({{ site.src_url }}/_includes/comments.html) with the following content:

{% highlight html %}
{% raw %}{% if page.comments %}{% endraw %}
<div id="disqus_thread"></div>
<script type="text/javascript">
	/* * * CONFIGURATION VARIABLES: EDIT BEFORE PASTING INTO YOUR WEBPAGE * * */
	var disqus_shortname = 'grahamrpugh'; // required: replace example with your forum shortname
	var disqus_developer = 1; // Comment out when the site is live
	var disqus_identifier = "{% raw %}{{ page.url }}{% endraw %}";
	/* * * DON'T EDIT BELOW THIS LINE * * */
	(function() {
		var dsq = document.createElement('script'); dsq.type = 'text/javascript'; dsq.async = true;
		dsq.src = '//' + disqus_shortname + '.disqus.com/embed.js';
		(document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq);
	})();
</script>
<noscript>Please enable JavaScript to view the <a href="http://disqus.com/?ref_noscript">comments powered by Disqus.</a></noscript>
<a href="http://disqus.com" class="dsq-brlink">comments powered by <span class="logo-disqus">Disqus</span></a>
{% raw %}{% endif %}{% endraw %}
{% endhighlight %}

This is referenced in any page where comments should be added. In my case, I've added it to the template for blog posts, which is [`_layouts/post.html`]({{ site.src_url }}/_layouts/post.html):

{% highlight html %}
{% raw %}{% include comments.html %}{% endraw %}
{% endhighlight %}

Additionally, comments must be enabled in the [YAML "front matter"](http://jekyllrb.com/docs/frontmatter/) of each file (including the blog template file and each individual blog file. So that I don't forget, I have a draft blog template at [`_drafts/template.md`]({{ site.src_url }}/_drafts/template.md), which I copy to start each new blog file:

{% highlight markdown %}
---
layout: post
title:  "Template post"
comments: true
---

Enter content here...
{% endhighlight %}

You can enable comment counts by adding the following line to the bottom of your default html page template, just before the `</body>` tag. The default template file is at [`_layouts/default.html`]({{ site.src_url }}/_layouts/default.html):

{% highlight html %}
<script id="dsq-count-scr" src="//grahamrpugh.disqus.com/count.js" async></script>
{% endhighlight %}

Then, in the `index.html` and `archive/index.html` files, add the following code where you wish the comment count of each post to be shown:

{% highlight html %}
<a class="post-meta" href="{% raw %}{{ post.url }}{% endraw %}index.html#disqus_thread" data-disqus-identifier="{% raw %}{{ post.url }}{% endraw %}"></a>
{% endhighlight %}

Adding Google Analytics
=======================

Any website can be registered for [Google Analytics](http://www.google.com/analytics/), which provides usage statistics for your site. Register your `username.github.io` site, and then create the file [`_includes/google_analytics.html`]({{ site.src_url }}/_includes/google_analytics.html), to contain the embed code provided for you by Google.  Then, add a reference to `_includes/google_analytics.html` in your default template, which is at [`_layouts/default.html`]({{ site.src_url }}/_layouts/default.html):

{% highlight html %}
{% raw %}{% include google_analytics.html %}{% endraw %}
{% endhighlight %}

Pushing the new repository to GitHub
=======================

Once the repository is set up, it can be pushed to the repository as with any git repository:

{% highlight bash %}
$ git push --set-upstream origin master
{% endhighlight %}

The site should now be visible at your site URL.

Creating the first blog post
=======================

This is the first new post using Jekyll. To create it, I made a copy of [`_drafts/template.md`]({{ site.src_url }}/_drafts/template.md):

{% highlight bash %}
$ cp _drafts/template.md _drafts/blogging-with-jekyll.md
{% endhighlight %}

I edited the title in the [YAML "front matter"](http://jekyllrb.com/docs/frontmatter/) to `Blogging with Jekyll`, and created the content.

The [kramdown version of Markdown used with Jekyll](http://kramdown.gettalong.org) does not include the quoting of code snippets using the {% raw %}```{% endraw %} syntax. Code is highlighted between `{% raw %}{% highlight html %}{% endraw %}`...`{% raw %}{% endhighlight %}{% endraw %}` tags (`html` can be substituted for `bash`, `yaml`, `markdown`, `python` etc.).

To preview a blog while it is in the draft folder, run the following command:

{% highlight bash %}
$ jekyll serve --drafts
{% endhighlight %}

Then browse to `http://localhost:4000/`.
