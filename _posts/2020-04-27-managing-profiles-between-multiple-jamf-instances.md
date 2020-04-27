---
layout: post
title:  "Managing Configuration Profiles between Jamf Pro instances using the Classic API"
comments: true
---

If you manage multiple Jamf Pro instances, you may be used to using the Jamf Pro "Classic" API to copy endpoints between them. 

I help manage over 30 Jamf Pro instances, and I use the API in scripts to duplicate items from a Template instance to all the customer instances. The script I use extends on the abilities of [Jamf Migrator], a macOS application that can help copy endpoints from one source instance to one destination, to allow me to propagate items to all 30+ instances with a single command.  

This post is not about that script. It's about a recent problem I encountered when copying configuration profiles from one instance to other instances using the API, and how I solved it. 

Consider this scenario:

1. Create a configuration profile in a template Jamf Pro instance, including some scope.
2. Copy the new profile with the API to destination instances. The profile is deployed to any computers in scope.
3. Make changes to the profile in the template instance, such as alter a setting or change the scope.
4. Copy the amended profile to destination instances.

Stage 2 of the above workflow involves downloading the profile data from the source as an XML file, parsing the XML to remove `id` tags which may be different on the destination, checking that a profile with the same name as the one we just created does not yet exist on the destination instance, and then uploading the XML data using a `POST` request. 

After we make changes, Stage 4 involves a similar process, but when the check for an existing profile comes back positive, issuing a `PUT` request to the endpoint with the same name.

As in a shell script, this process would look something like this:

```bash
# Get the profile from the source instance and format it nicely to help with parsing
curl -X GET \
    -H "Accept: application/xml" \
    -H "authorization: Basic $template_instance_encrypted_credentials" \
    "https://jamfserver/template/JSSResource/osxconfigurationprofiles/name/ExampleProfile" \
| xmllint --format - > "/path/to/ExampleProfile-fetched.xml"

# Parse the XML to remove IDs and ensure the profile is redeployed to all computers in scope
cat "/path/to/ExampleProfile-fetched.xml" \
| grep -v '<id>' \
| sed 's/<redeploy_on_update>Newly Assigned<\/redeploy_on_update>/<redeploy_on_update>All<\/redeploy_on_update>/g' \
> "/path/to/ExampleProfile-parsed.xml"

# Check the destination server to see if an existing profile of this name exists
existing_id=$(
    curl -s -N -X GET \
        -H "Accept: application/xml" \
        -H "authorization: Basic $destination_instance_encrypted_credentials" \
        "https://jamfserver/destination/JSSResource/osxconfigurationprofiles" \
    | xmllint --xpath "//os_x_configuration_profiles/os_x_configuration_profile[name = 'ExampleProfile']/id/text()" - 2>/dev/null
)

# if it exists, do a PUT to that ID
if [[ $existing_id ]]; then
    curl -i -X PUT \
        -H "Content-Type: application/xml" \
        -H "authorization: Basic $destination_instance_encrypted_credentials" \
        --data-binary @"/path/to/os_x_configuration_profile-ExampleProfile-parsed.xml" \
        "https://jamfserver/destination/JSSResource/osxconfigurationprofiles/id/${existing_id}"

# if not, do a POST to ID 0
else
    curl -i -X POST \
        -H "Content-Type: application/xml" \
        -H "authorization: Basic $destination_instance_encrypted_credentials" \
        --data-binary @"/path/to/os_x_configuration_profile-ExampleProfile-parsed.xml" \
        "https://jamfserver/destination/JSSResource/osxconfigurationprofiles/id/0"
fi
```

## All good? Not so fast...

The above process works for most API endpoints (policies, smart groups, categories, package metadata, App Store apps...), with a few tweaks required here and there for some endpoints to make it work, such as ensuring dependencies are already in place, dealing with self service icons and so on.

Unfortunately, I encountered some strange behaviour when copying the profile the second time, i.e. with the `PUT` request to overwrite the existing profile.

The request is successful. The profile is updated on the destination server with the changes made.

But now, there are **two** profiles of the same name on the clients in scope. One with the old settings, one with the new settings. Or, if you changed the scope, the computers no longer in scope still have the profile installed, with the old settings.

And worse still, if you delete the profile from the destination instance, the computers still have the original profile. There's no way to get rid of it, as it is no longer shown in Jamf.

It's an "orphaned" profile. Only by removing the MDM profile, so effectively unenrolling the device, can we remove the orphaned profile.

## ID or UUID, that is the question

I opened a case with Jamf Support, who initially told me "don't do that", and if I must, "use Jamf Migrator". I did not try the latter, as I know Jamf Migrator uses the API, so it either will have the same problem, or they have programmatically solved it, and I wanted to know how. But then the ticket was read by another Support Engineer, who was able to reproduce the problem and come up with a more helpful solution. A Product Issue was also opened (`PI-008168`), as the API is behaving inconsistently:

* When uploading a new configuration profile to a destination instance via a `POST` request, the UUID of the profile is stripped out by Jamf to ensure that the profile could not inherit a UUID that already exists on that server (as UUIDs need to be Unique!).

* However, when uploading a configuration profile using `PUT`, if the profile exists (based on `id` or `name`), the profile is overwritten, including the UUID, effectively creating a different profile as far as Apple/MDM is concerned, but removing any trace of the "old" profile from the server, i.e. the profile with the UUID that was created with the `POST` request.

So, we need to ensure the UUID remains constant as changes are made to a profile. There are two ways to go about this:

1. When creating the profile on the template instance, ensure that there is no scope. Copy the profile to the destination instance with a POST request, and then immediately copy it again using a `PUT` request. This will ensure the profile has the same UUID as the template. Then, you can add scope to the profile and copy again.

2. Copy the new profile as normal with a `POST` request. Then, when copying subsequently, get the UUID from the destination instance and substitute it into the XML of the downloaded profile before uploading it to the destination instance with a `PUT` request. This also ensures that the profile retains the same UUID.

We decided to go with option 2, because it allows existing profiles to be used without remediation, and it also allows new profiles to be crafted with a single action, rather than having to engineer the "double post" solution.

So, the code for the copying process changes to the following:

```bash
# Get the profile from the source instance
curl -X GET \
    -H "Accept: application/xml" \
    -H "authorization: Basic $template_instance_encrypted_credentials" \
    "https://jamfserver/template/JSSResource/osxconfigurationprofiles/name/ExampleProfile" \
| xmllint --format - \
> "/path/to/ExampleProfile-fetched.xml"

# Parse the XML to remove IDs and ensure the profile is redeployed to all computers in scope
cat "/path/to/ExampleProfile-fetched.xml" \
| grep -v '<id>' \
| sed 's/<redeploy_on_update>Newly Assigned<\/redeploy_on_update>/<redeploy_on_update>All<\/redeploy_on_update>/g' \
> "/path/to/ExampleProfile-parsed.xml"

# if it exists, do a PUT to that ID
if [[ $existing_id ]]; then
    # grab the UUID from the template
    template_uuid=$(
        cat "/path/to/os_x_configuration_profile-ExampleProfile-parsed.xml" \
        | xmllint --xpath "//uuid/text()" - 2>/dev/null
    )

    # grab the UUID from the destination
    existing_uuid=$(
        curl -s -N -X GET \
            -H "Accept: application/xml" \
            -H "authorization: Basic $destination_instance_encrypted_credentials" \
            "https://jamfserver/destination/JSSResource/osxconfigurationprofiles/id/${existing_id}" \
        | xmllint --xpath "//uuid/text()" - 2>/dev/null
    )

    # now substitute this existing uuid and write a new parsed file
    cat "/path/to/os_x_configuration_profile-ExampleProfile-parsed.xml" \
    | sed 's/'"${template_uuid}"'/'"${existing_uuid}"'/g' \
    > "/path/to/os_x_configuration_profile-ExampleProfile-parsed-destination.xml"

    # and finally, do the PUT request
    curl -i -X PUT \
        -H "Content-Type: application/xml" \
        -H "authorization: Basic $destination_instance_encrypted_credentials" \
        --data-binary @"/path/to/os_x_configuration_profile-ExampleProfile-parsed-destination.xml" \
        "https://jamfserver/destination/JSSResource/osxconfigurationprofiles/id/${existing_id}"

# if not, do a POST to ID 0
else
    curl -i -X POST \
        -H "Content-Type: application/xml" \
        -H "authorization: Basic $destination_instance_encrypted_credentials" \
        --data-binary @"/path/to/os_x_configuration_profile-ExampleProfile-parsed.xml" \
        "https://jamfserver/destination/JSSResource/osxconfigurationprofiles/id/0"
fi
```

Note that in the above code, I have not included additional steps that I have in my scripts for ensuring that categories and scope are in place on the destination. If categories or computer groups that are in the XML are not present on the destination instance, the `POST` and `PUT` requests will fail with a `409` conflict error. 

How to remove an "orphaned" configuration profile
===

I also had a few profiles out in the wild that had been orphaned before I had become fully aware of this issue. I wanted to build a method of fixing this problem without having to re-enroll the devices. I found the following procedure does the trick:

* Run the following command on an affected computer - it will reveal the UUID (`profileUUID`) of a named profile: 

    ```bash
    sudo profiles list -verbose | grep -A 5 "ExampleProfile"

    _computerlevel[24] attribute: name: ExampleProfile
    _computerlevel[24] attribute: configurationDescription: 
    _computerlevel[24] attribute: installationDate: 2020-04-23 08:08:54 +0000
    _computerlevel[24] attribute: organization: My Organization
    _computerlevel[24] attribute: profileIdentifier: 0fd1fa10-225a-40b4-b433-72de5314b7d6
    _computerlevel[24] attribute: profileUUID: 0fd1fa10-225a-40b4-b433-72de5314b7d6
    ```

* Generate a "dummy" profile in Jamf that does as little as possible, certainly nothing that would be noticed by users, with no scope. Give it a name that makes it clear that it is deployed by you for fixing the problem. Copy it to the instance on which the affected device(s) are enrolled. Retain the downloaded XML.

* Substitute the UUID from the "orphaned" profile into the XML of the downloaded profile, as in this example snippet below (the rest of the above script remiains the same), and then upload it to the affected instance with a PUT request:

    ```bash
    # now substitute the orphaned uuid and write a new parsed file
    cat "/path/to/os_x_configuration_profile-DummyProfile-parsed.xml" \
    | sed 's/'"${template_uuid}"'/0fd1fa10-225a-40b4-b433-72de5314b7d6/g' \
    > "/path/to/os_x_configuration_profile-DummyProfile-parsed-destination.xml"
    ```

* Verify that the UUID is now correct in the profile on the destination by going to the `/api` URL of the affected instance, and looking up the profile in the `osxconfgurationprofiles` endpoint (on one occasion I had to copy the profile a third time to get the correct UUID injected into the profile - not sure why).

* Add the affected devices to the scope of the profile in the Jamf GUI. If it affects too many computers and/or too many instances to do manually, you could scope to `All Computers` on the template instance and copy the profile again - just bear in mind this will deploy the "dummy" profile to devices that may not be affected by the problem, so make sure the profile does not do anything unexpected!

* The "orphaned" profile should now update on the affected devices, so the name of it should change to the name of your "dummy" profile.

* Now you can delete the profile from the affected instances, or remove the affected devices from its scope, and it should be removed from the affected devices completely.

# Conclusion and caveats

Now that Jamf have acknowledged that the behaviour of copying configuration profiles is somewhat inconsistent, I hope they will improve the API so that the above workaround is not required in the future. But for now, we have a (hopefully) reliable method of maintaining configuration profiles across multiple Jamf Pro instances. Thanks to the Jamf Engineer for helping point me in the right direction as to the behaviour of the Classic API. In the process, figuring out how to clear out orphaned profiles using a "dummy" profile has also been helpful for us. 

Note that I have not checked the code of Jamf Migrator to see if the developers already use this workaround, as it is a Swift application (I'm not familiar with Swift code), and it does not serve my own particular requirements for copying to multiple instances at once, so I anyway needed to solve the problem in my own scripts. I'd be interested to hear whether the problem occurs (or not) when using Jamf Migrator.

I have also not yet tested this out on profiles that were signed and uploaded to Jamf. Since there would be a UUID embedded in the signed portion of the profile which would be difficult for Jamf to strip out during the `POST` request, these may behave differently.

{% include urls.md %}
