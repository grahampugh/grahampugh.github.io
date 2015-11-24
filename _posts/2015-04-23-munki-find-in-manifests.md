---
layout: post
title:  "Munki: find out in which manifests a package is available"
comments: true
---

I sometimes need to know which manifests would be affected by an update to a [Munki] package, or need to know which manifests another manifest is included within. There are no tools to do this, so I wrote a script to do it. I suspect that someone could write it much more efficiently - it takes some time to iterate through all the manifests.

{% highlight bash %}
#!/bin/bash

### A script to find which manifests contain references to a package or other manifest via included_manifests
### Your Munki repository must be mounted as a volume
### Syntax: 
### $ ./manifest-find.sh -f <package or manifest name>
### Examples:
### $ ./manifest-find.sh -f Xcode
### $ ./manifest-find.sh -f _regular_users

# Munki repo - change to suit your environment
MUNKI_REPO="/Volumes/munki_repo"

# Location for the output file. If you don't want a file, uncomment line at the end of the script to remove it
FINAL_FILE="./manifests.txt"

# If you have a complicated manifest tree, you may need to increase the iterations of this loop
for LEVEL_COUNT in {1..6}
do
	rm -f ./manifests.${LEVEL_COUNT}.txt
	touch ./manifests.${LEVEL_COUNT}.txt
done
rm -f $FINAL_FILE
touch $FINAL_FILE

# First level
while getopts ":f:" opt; do
	case $opt in
    f)
    	# echo "-f was triggered, Parameter: $OPTARG" >&2
    	MANIFEST="$OPTARG"
    	echo "Included: $MANIFEST" >> ./manifests.1.txt
    	find $MUNKI_REPO/manifests -type f -print | xargs grep -l "$OPTARG" >> ./manifests.1.txt
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

# Subsequent levels
# If you have a complicated manifest tree, you may need to increase the iterations of this loop
for MAN_LEVEL in {1..5}
do
	cat ./manifests.${MAN_LEVEL}.txt | while read LINE; do
		MAN_NAME=$(basename "${LINE}")
		# if ! grep -Fxq "$MAN_NAME" $FINAL_FILE; then
			echo $MAN_NAME >> $FINAL_FILE
		# fi
		if [[ $LINE != *client* && $LINE != *Included* ]]; then
			NEXT_LEVEL=$((MAN_LEVEL+1))
			if [ $MAN_LEVEL -lt 6 ]; then
		    	echo "Included: $MAN_NAME" >> ./manifests.${MAN_LEVEL}.txt
		    	find $MUNKI_REPO/manifests -type f -print | xargs grep -l "$MAN_NAME" >> ./manifests.${NEXT_LEVEL}.txt
		    fi
	    fi
	done
done

# sort -f $FINAL_FILE -o $FINAL_FILE

# Delete the working files
# If you have a complicated manifest tree, you may need to increase the iterations of this loop
for LEVEL_COUNT in {1..7}
do
# Uncomment these lines if you want to see the output of the intermediate steps
# echo ""
# echo "==== LEVEL ${LEVEL_COUNT} ===="
# 	cat ./manifests.${LEVEL_COUNT}.txt
  	rm -f ./manifests.${LEVEL_COUNT}.txt
done

# Print out the results to STDIN
echo ""
echo "==== MANIFESTS CONTAINING \"$MANIFEST\" ===="
cat $FINAL_FILE
echo ""
echo "Results outputted to manifests.txt"

# Uncomment this line if you want to delete the output file
# rm -f $FINAL_FILE
{% endhighlight %}

Make the script executable:

{% highlight bash %}
$ chmod +x /path/to/manifest-find.sh
{% endhighlight %}

To run the script:

{% highlight bash %}
$ /path/to/manifest-find.sh -f package-name
{% endhighlight %}

Example output, showing all manifests in which Xcode is made available (either as `managed_install` or `optional_install`):

{% highlight bash %}
$ ./manifest-find.sh -f Xcode

==== MANIFESTS CONTAINING &quot;Xcode&quot; ====
Included: Xcode
_sw_testing_group
client-it021669
_cg_testing_group
client-it000492
client-it000912
client-it011313
client-it005896
client-IT029452
client-it015180
client-IT006319
client-it006319
client-it031540
client-it000545
client-it013465
client-it015172
client-it000516
client-it031455
client-it013544

Results outputted to manifests.txt
{% endhighlight %}

{% include urls.md %}

