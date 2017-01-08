---
layout: post
title:  "Blogging with Jekyll"
comments: true
---

This blog has run on [WordPress.com] for a while, but I have 
increasingly found its format to be somewhat frustrating, particularly when it comes 
to quoting code, which is a frequent occurrence in this blog. I prefer to edit in 
[Markdown], which **is** possible on WordPress.com, but has limitations. I've also been keen to 
embrace version control where possible, and the ability to edit offline is useful, especially while travelling. I've therefore taken the step to migrate the blog 
to [GitHub], and use [Jekyll]. 
GitHub provides [free hosting for Jekyll blogs][1].

Here, I describe the steps I took to create this blog:

   * [Registering with GitHub][GitHub]
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
[grahampugh.github.io][2]. Instructions for setting up this repository
are found at [https://pages.github.com/#user-site][3].

When the repository is set up, you can clone the empty repository to your computer:

{% highlight bash %}
$ git clone {% raw %}{{ site.src_url }}{% endraw %}
{% endhighlight %}


Installing Jekyll on my computer
=======================

Installing Jekyll allows you to run a 
development server on your computer, so that you 
can easily preview your blog posts as you write them, without having to upload them to 
GitHub. [Installation is easy][Jekyll installation].

Cloning a template blog
=======================

When run from the root folder of your new repository, `jekyll build .` command builds a template site on your computer. The 
`jekyll build --watch` command automatically watches for changes to the files in the 
current folder, and regenerates the site as necessary. For more details see 
[http://jekyllrb.com/docs/usage/][4]

Editing the template to create the blog identity
=======================

The site settings are contained in the root directory, in `_config.yml`. I edited the 
file as follows:

~~~ yaml
# Site settings
title: On The Subject Of Macs
email: g.r.pugh@gmail.com
description: > # this means to ignore newlines until "baseurl:"
  The Blog of a Mac Support Specialist in a UK University
baseurl: "" # the subpath of your site, e.g. /blog
url: "http://grahampugh.github.io" # the base hostname & protocol for your site
twitter_username: GrahamRPugh
github_username:  grahampugh
~~~

Editing index.html, and archive.html
=======================

The default template has a list of blog posts in [`index.html`]({{ site.baseurl }}{% link index.html %}). I altered this to include the first 50 words of each post:

~~~ html
<p class="post-meta">{{ post.content | strip_html | truncatewords: 50 }}</p>
~~~

I moved the original list-style page to [`archives/index.html`]({{ site.baseurl }}{% link archives/index.html %}). 

Adding Pagination
=======================

Pagination enables you to restrict the number of posts visible on the first page of an index or list page, so that the page doesn't get too long. To set this up, install as follows:

~~~ bash
$ gem install jekyll-paginate
~~~

In the [`_config.yml`]({{ site.src_url }}/_config.yml) file, append the following lines:

~~~ yaml
#pagination
gems: [jekyll-paginate]
paginate: 10
paginate_path: "/page/:num"
~~~

The numeric value for the `paginate` setting can be altered to set the number of items to be listed per page.

An includes file determines how the links to other pages are displayed. This is [`_includes/pagination.html`]({{ site.src_url }}/_includes/pagination.html):

~~~ html
{% raw %}{% if paginator.total_pages > 1 %}{% endraw %}
<div class="pagination">
	{% raw %}{% if paginator.previous_page %}{% endraw %}
		<a rel="prev" href="{% raw %}{{ paginator.previous_page_path | replace: 'index.html', '/' | prepend: site.baseurl | replace: '//', '/' }}{% endraw %}">&laquo; Newer</a>
	{% raw %}{% else %}{% endraw %}
		<span>&laquo; Newer</span>
	{% raw %}{% endif %}{% endraw %}

	{% raw %}{% for page in (1..paginator.total_pages) %}{% endraw %}
		{% raw %}{% if page == paginator.page %}{% endraw %}
			<em>{% raw %}{{ page }}{% endraw %}</em>
		{% raw %}{% elsif page == 1 %}{% endraw %}
			<a href="{% raw %}{{ '/' | prepend: site.baseurl | replace: '//', '/' }}{% endraw %}">{% raw %}{{ page }}{% endraw %}</a>
		{% raw %}{% else %}{% endraw %}
			<a href="{% raw %}{{ site.paginate_path | replace: 'index.html', '/' | prepend: site.baseurl | replace: '//', '/' | replace: ':num', page }}{% endraw %}">{% raw %}{{ page }}{% endraw %}</a>
		{% raw %}{% endif %}{% endraw %}
	{% raw %}{% endfor %}{% endraw %}

	{% raw %}{% if paginator.next_page %}{% endraw %}
		<a rel="next" href="{% raw %}{{ paginator.next_page_path | replace: 'index.html', '/' | prepend: site.baseurl | replace: '//', '/' }}{% endraw %}">Next &raquo;</a>
	{% raw %}{% else %}{% endraw %}
		<span>Older &raquo;</span>
	{% raw %}{% endif %}{% endraw %}
</div>
{% raw %}{% endif %}{% endraw %}
~~~

This must be referenced in [`index.html`]({{ site.baseurl }}{% link index.html %}) at the point where the links should be displayed (at the end of the list of posts):

~~~ html
{% raw %}{% include pagination.html %}{% endraw %}
~~~

Finally, for pagination to actually work, the reference to `site.posts` must be changed to `paginator.posts`:

~~~ html
{% raw %}{% for post in paginator.posts %}{% endraw %}
~~~

Adding comment fields and counts to posts using Disqus
=======================

[Disqus](http://disqus.com/) is the most common embedded comment system used with Jekyll blogs. After you [register with Disqus](https://disqus.com/admin/create/), you are provided with a block of code to add to your site template. I created a file at [`_includes/comments.html`]({{ site.src_url }}/_includes/comments.html) with the following content:

~~~ html
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
~~~

This is referenced in any page where comments should be added. In my case, I've added it to the template for blog posts, which is [`_layouts/post.html`]({{ site.src_url }}/_layouts/post.html):

~~~ html
{% raw %}{% include comments.html %}{% endraw %}
~~~

Additionally, comments must be enabled in the [YAML front matter][5] of each file (including the blog template file and each individual blog file. 

You can enable comment counts by adding the following line to the bottom of your default html page template, just before the `</body>` tag. The default template file is at [`_layouts/default.html`]({{ site.src_url }}/_layouts/default.html):

~~~ html
<script id="dsq-count-scr" src="//grahamrpugh.disqus.com/count.js" async></script>
~~~

Then, in the [`index.html`]({{ site.src_url }}/index.html) and [`archive/index.html`]({{ site.src_url }}/archive/index.html) files, add the following code where you wish the comment count of each post to be shown:

~~~ html
<a class="post-meta" href="{% raw %}{{ post.url }}{% endraw %}index.html#disqus_thread" data-disqus-identifier="{% raw %}{{ post.url }}{% endraw %}"></a>
~~~

Adding Google Analytics
=======================

Any website can be registered for [Google Analytics](http://www.google.com/analytics/), which provides usage statistics for your site. Register your `username.github.io` site, and then create the file [`_includes/google_analytics.html`]({{ site.src_url }}/_includes/google_analytics.html), to contain the embed code provided for you by Google.  Then, add a reference to `_includes/google_analytics.html` in your default template, which is at [`_layouts/default.html`]({{ site.src_url }}/_layouts/default.html):

~~~ html
{% raw %}{% include google_analytics.html %}{% endraw %}
~~~

Pushing the new repository to GitHub
=======================

Once the repository is set up, it can be pushed to the repository as with any git repository:

~~~ bash
$ git push --set-upstream origin master
~~~

The site should now be visible at your site URL.

Creating the first blog post
=======================

This is the first new post using Jekyll. In the spirit of Git versioning, rather than working on a file in the `_drafts` folder, I first checkout a new Git branch, and then create the post in the place where it will ultimately reside. The file for the post is created by making a copy of [`_drafts/template.md`]({{ site.src_url }}/_drafts/template.md):

~~~ bash
$ git checkout -b 2015-11-23-blogging-with-jekyll
$ cp _drafts/template.md _posts/2015-11-23-blogging-with-jekyll.md
~~~

I edited the title in the [YAML front matter][5] to `Blogging with Jekyll`, and created the content.

The [kramdown version of Markdown used with Jekyll][kramdown] does not include the quoting of code snippets using the ``` syntax. Code is highlighted between `` ` ``...`` ` `` tags (`html` can be substituted for `bash`, `yaml`, `markdown`, `python` etc.). If quoting Jekyll Liquid tags (e.g. `{% raw %}{% include google_analytics.html %}{% endraw %}`), one must embed the code in `{% raw %}{% raw ... endraw %}{% endraw %}` tags.

To preview the blog, run the following command:

~~~ bash
$ jekyll serve
~~~

Then browse to `http://localhost:4000/` and navigate to the new post.

Once satisfied that all is well with the new post and/or any changes made, push the changes, and then go to Github and create a pull request. Review the changes and merge the branch to master to publish the new post.

[1]: http://pages.github.com/
[2]: https://grahampugh.github.io
[3]: https://pages.github.com/#user-site
[4]: http://jekyllrb.com/docs/usage/
[5]: http://jekyllrb.com/docs/frontmatter/
[Jekyll installation]: http://jekyllrb.com/docs/installation/

{% include urls.md %}

