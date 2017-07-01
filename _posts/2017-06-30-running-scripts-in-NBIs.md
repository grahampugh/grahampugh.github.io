---
layout: post
title:  "Changing settings in DeployStudio NetBoot images"
comments: true
---

I recently ran into a problem with a [DeployStudio] NetBoot image which required a system setting to be changed. The DeployStudio NBI creation process is a somewhat closed box, normally done using the **DeployStudio Assistant** application, which only allows certain settings to be manipulated. [@MagerValp] made the build process scriptable with the [AutoDSNBI] tool, but it still uses DeployStudio Assistant to do the build.  

One solution is to mount the NetBoot image once it is built, and then manipulate the files within. Specifically, the `NetInstall.sparseimage` within the NetBoot image needs to be mounted.

Since the mounted image is not the booted volume, it isn't possible to directly run scripts on the image. But it is possible to copy scripts to the volume, and create a LaunchDaemon or LaunchAgent to run the script. To do this with `hdiutil`, you must mount the volume in a way that enables ownership to be set, using the `-owners on` flag:

```bash
# Mount the NetInstall sparseimage to manipulate it directly
mkdir -p tmp_mnt
hdiutil attach "/path/to/DeployStudioRuntime.nbi/NetInstall.sparseimage" -quiet -nobrowse -owners on -mountpoint tmp_mnt
```

Once mounted, you can copy a script containing the command you wish to run on the booted NBI somewhere, copy a LaunchDaemon to `/Library/LaunchDaemons`, and set the ownership and permissions accordingly:

```bash
# 1. Script
mkdir -p tmp_mnt/Library/Management
cp myscript.sh > tmp_mnt/Library/Management/
chmod 755 tmp_mnt/Library/Management/myscript.sh
chown -R 0:0 tmp_mnt/Library/Management

# 2. LaunchDaemon
mkdir -p tmp_mnt/Library/LaunchDaemons
chmod 644 tmp_mnt/Library/LaunchDaemons/com.me.myscript.plist
chown 0:0 tmp_mnt/Library/LaunchDaemons/com.me.myscript.plist
```

Note in this example, I set ownership to `0:0` which corresponds to `root:wheel`. The shell script must be executable, and the LaunchDaemon must be owned by root.

The LaunchDaemon should contain something like the following:

```bash
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
    <dict>
        <key>Label</key>
        <string>com.me.myscript</string>
        <key>ProgramArguments</key>
        <array>
            <string>/bin/sh</string>
            <string>/Library/Management/myscript.sh</string>
        </array>
        <key>RunAtLoad</key>
        <true/>
        <key>KeepAlive</key>
        <false/>
    </dict>
</plist>
```

In this example, the script is set to run at boot. In some cases this may be too soon as it may get overridden by a system process. You may wish to use a LaunchAgent (in DeployStudio NBI, the user is root so there are no permissions consequences to this), or set a different schedule such as by using the `StartInterval` tag.

The script is just a regular script that runs as root, e.g.:

```bash
#!/bin/sh

export MY_ENV_VARIABLE="1"
```

Once you have copied the files to the volume, you can unmount it and put it in your NetBoot server's `/Library/NetBoot/NetBootSP0` folder as normal. To unmount:

```bash
# umount the sparseimage
hdiutil eject tmp_mnt -quiet
```

-----

## Scripting the process of building the NetBoot image and then adding the customised settings

In order to maximise reproducibility, it pays to script processes where possible (or use configuration management tools).

In the example below, a single script is used to build a DeployStudio NetBoot image, and then add a script to turn off IPv6, called by a LaunchDaemon. This requires [AutoDSNBI]. Usage is as follows:

```bash
sudo ./create_custom_dsnbi.sh "<path to AutoDSNBI>" "<source>" "<netboot id>" "<netboot name>" "<destination dir>"
```

{% gist grahampugh/2ab32bbad09c33622fea493eff21e5ea %}

**Notes for interested parties:**

 * A DeployStudio NBI is stripped of many binaries, including `networksetup`. For this reason, `ipconfig` is used here to disable IPv6. Apple do not recommend using `ipconfig` to set network settings except for debugging, but it is aceeptable here as this is just a temporary system which does not need to survive a reboot.

 * The LaunchDaemon was originally set to `RunAtLoad` but this didn't have the desired effect, presumably as it was called too soon in the boot process and network settings were altered by the system after it ran. Again, one wouldn't want to normally repeatedly run an command to change a setting, but it works in the context of a temporary NetBoot image. One could easily add a line in the script to unload and delete the LaunchDaemon for something you were sure only needed to be run once.

* This has been highly simplified from my organisation's production script, so forgive any untested typos!

{% include urls.md %}
