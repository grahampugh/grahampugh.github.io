---

## Introduction

Up until Jamf Pro version 11.22, there was a single built-in way of comparing application versions in Smart Computer Group criteria. This has been done with the Application Title or Application Bundle Identifier criterion, followed by the Application Version criterion. 

![criteria1.png]

The application version that is checked is normally the value of the CFBundleShortVersionString key that resides in the Info.plist file of the application bundle. This corresponds to the version that you see in Finder if you look at the Get Info for the application, or add the Version column to the List view of Finder. 

However, for a legacy reason seemingly lost to history, the Jamf code specifies that if "Microsoft" is in the application name, Application Version will instead check the CFBundleVersion key from Info.plist instead. This has surely caused confusion to many Jamf Pro admins (not least myself when I first discovered this).