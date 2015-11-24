---
layout: post
title:  "Munki: How to remove cruft"
comments: true
---

An issue with [Munki], especially if using [AutoPkg], is that you can quickly amass many versions of software packages, which can fill up your repository volume. There are no automated ways of clearing out old versions of software, but in many cases there is no reason to keep them.

Removing a package involves the following process:

   * Locate the imported package and delete it
   * Locate the associated pkginfo file and delete it
   * `makecatalogs`

If you're organised, you'll know exactly where every package is in the subdirectory structure of your Munki repository. But the repository can get hard to navigate. In which folder does Autopkg put Java 8? To where did your colleague import SPSS?

Use a GUI!
=============

One way of removing packages is using the [MunkiAdmin] application. Simply right- or ctrl-click on an item in the Packages list, and select Delete Package. MunkiAdmin offers to delete the package and associated `pkginfo` file, and potentially the icon.

![img-1]

Command-line alternative?
=============

If you don't wish to use MunkiAdmin, for instance if you are working remotely on a server via `ssh`, you may wish for an easy way to find and remove old packages using the command line. The munkitools don't include a tool for this task. So I wrote a script to find items in the Munki repository that match an input, list the items in order of filename (so that associated .pkg and .plist files are adjacent in the list), and offer to delete each one in term.

Pressing `y` deletes the item and moves on to the next item in the list. Pressing `n` or any other character (except `q`) skips the item and moves on to the next. Pressing `q` skips to the end of the list. After the end of the list has been reached, if anything has been deleted, `makecatalogs` is run (for this to work, this script needs to be run on a Mac with munkitools installed and configured to point to your munki repository).

{% highlight bash %}
#!/bin/bash

### A script to search your Munki repo and offer to delete items. Use with care! 
### It will search all directories including pkgs, pkgsinfo and icons.
###    Syntax: /path/to/munkirm -d <search-term>
###    For example, /path/to/munkirm -d xcode
### Search is case insensitive. 
### Options are y or Y to delete, n, N or anything else to skip, and q or Q to quit
### If any changes are made, `makecatalogs` is run
### Put munkirm in /usr/local/munki/ if you wish to run from all directories

# Munki repo - change to match your path
MUNKI_REPO=`defaults read ~/Library/Preferences/com.googlecode.munki.munkiimport.plist repo_path`

# Introductions
echo
echo "----------------------------"
echo "  MUNKI FILE REMOVAL TOOL"
echo "----------------------------"
echo "Usage:   munkirm -d <string>"
echo "<string> is case-insensitive"
echo "part strings OK, e.g. goog"
echo

# First level
while getopts ":d:" opt; do
	# Check to see if munkiimport is configured
	if [ -z ${MUNKI_REPO} ]; then
		echo "### munkiimport not configured. Run  `munkiimport --configure`"
		echo
		exit 1
	fi

	# Check to see if the repository is mounted
	if [ ! -d ${MUNKI_REPO} ]; then
		echo "### Munki repository not mounted! Cannot continue"
		echo
		exit 1
	fi
	
	case $opt in
    d)
    	# echo "-d was triggered, Parameter: $OPTARG" >&2
    	PKG="$OPTARG"
    	
    	# write find results to temporary file
    	#find $MUNKI_REPO -type f -iname "*$PKG*" > /tmp/list.txt
    	find $MUNKI_REPO -type f -iname "*$PKG*" | awk -v FS=/ -v OFS=/ '{ print $NF,$0 }' | sort -n -t / | cut -f2- -d/ > /tmp/list.txt
    	;;
    \?)
      	echo "Invalid option: -$OPTARG" >&2
      	exit 1
      	;;
    :)
      	echo "Option -$OPTARG requires an argument." >&2
      	exit 1
      	;;
  	esac
done

if [ -s /tmp/list.txt ]; then
	# Print the results first
	echo
	echo "Found these files:"
	echo
	cat /tmp/list.txt
	echo
	
	# Now offer up each file for deletion
	for file in `cat /tmp/list.txt`; do
		read -p "Delete $file (y/n/q)?  " -n 1 input    
		case $input in 
			y|Y ) 	echo
					rm -r $file 
					echo "$file Deleted!"
					echo
					REMAKE=1
					;;
			q|Q ) echo
			      echo "skipped to end"
			      echo
			      break
			      ;;
			* ) echo
			    echo "skipped"
			    echo
			    ;;
		esac
	done
else
	# No match, therefore no file
	echo "Files not found!"
	echo
fi

rm /tmp/list.txt


# Update the repo if required
if [[ $REMAKE == 1 ]]; then
	if hash makecatalogs 2>/dev/null; then
		echo "### Catalogs have changed - running makecatalogs"
		echo
		/usr/local/munki/makecatalogs $MUNKI_REPO
	else
		echo "### Catalogs have changed but you don't have makecatalogs installed!"
		echo "### Now run makecatalogs on a Mac with munkitools installed to effect the changes"
		echo
	fi
else
	echo "### Catalogs have not changed. Exiting..."
	echo
fi

exit 0
{% endhighlight %}


Make the script executable:

{% highlight bash %}
$ chmod +x /path/to/munkirm
{% endhighlight %}

To run the script (in this example, we search for 'java'):

{% highlight bash %}
$ /path/to/munkirm -d java
{% endhighlight %}

Example output:

{% highlight bash %}
$ /path/to/munkirm -d chrome

----------------------------
  MUNKI FILE REMOVAL TOOL
----------------------------
Usage:   munkirm -d 
 is case-insensitive
part strings OK, e.g. goog

Found these files:

/Volumes/munki_repo/pkgs/apps/GoogleChrome-40.0.2214.115.dmg
/Volumes/munki_repo/pkgsinfo/apps/GoogleChrome-40.0.2214.115.plist
/Volumes/munki_repo/pkgs/apps/GoogleChrome-41.0.2272.118.dmg
/Volumes/munki_repo/pkgsinfo/apps/GoogleChrome-41.0.2272.118.plist
/Volumes/munki_repo/pkgs/apps/GoogleChrome-42.0.2311.90.dmg
/Volumes/munki_repo/pkgsinfo/apps/GoogleChrome-42.0.2311.90.plist
/Volumes/munki_repo/icons/GoogleChrome.png

Delete /Volumes/munki_repo/pkgs/apps/GoogleChrome-40.0.2214.115.dmg (y/n/q)? y
/Volumes/munki_repo/pkgs/apps/GoogleChrome-40.0.2214.115.dmg Deleted!

Delete /Volumes/munki_repo/pkgsinfo/apps/GoogleChrome-40.0.2214.115.plist (y/n/q)? y
/Volumes/munki_repo/pkgsinfo/apps/GoogleChrome-40.0.2214.115.plist Deleted!

Delete /Volumes/munki_repo/pkgs/apps/GoogleChrome-41.0.2272.118.dmg (y/n/q)? n
skipped

Delete /Volumes/munki_repo/pkgsinfo/apps/GoogleChrome-41.0.2272.118.plist (y/n/q)? q
skipped to end

### Catalogs have changed - running makecatalogs

Hashing Adobe Acrobat XI Pro_3.png...
Hashing Adobe-Premiere.png...
... [makecatalogs output] ...
Created catalog /Volumes/munki_repo/catalogs/standard...
{% endhighlight %}

If you want to run this tool from any directory without requiring a path, copy it into `/usr/local/munki/`:
{% highlight bash %}
$ sudo cp /path/to/munkirm /usr/local/munki/
{% endhighlight %}

[img-1]: /assets/images/munkirm-1.png

{% include urls.md %}

