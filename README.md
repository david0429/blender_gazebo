# Blender Gazebo
An add-on for Blender to export worlds for Gazebo ROS.  It will export all of the models, and create launch and urdf files.

## Installation Script
There is an installation script that will install the add-on into Blender. Because you can have multiple versions of Blender, you need to tell the script where to install.  Set the environment variable ``BLENDER_SCRIPT_DIR`` to the version number folder inside your Blender installation directory

```
blender-2.80-linux-glibc217-x86_64
├── 2.80           << This Folder
│   ├── datafiles
│   ├── python
│   └── scripts
├── icons
│   ├── scalable
│   └── symbolic
└── lib
```

Once that is set, rosrun the script:

```rosrun blender_gazebo install```

After the script installs the add-on, you will need to enable it inside blender.  Edit > Preferences > Add-ons, find the add-on and check it off to enable it.

## Manual installation
If the script install doesn't work for you for some reason, you can manually install from inside Blender.

Under Edit > Preferences > Add-ons, click Install and find the blender_gazebo.py file inside the blender_gazebo directory.  Remember to enabled it after it is installed

## Usage
To use this add-on:
* Make a new package.  Make sure to add blender_gazebo as a dependency.
* Add a launch directory to your package
* In Blender, create your world.  Remember to work in meters
* In Blender, go to File > Export > Gazebo Launch (.launch)
* Navigate to the launch folder in your package
* Give your launch file a name.  It should use your Blender file name as the default name
* Click Export Gazebo
* Once it is exported, build your package and run your launch file

## Known Issues
Blender 2.80 exports standard materials in a way that RVIZ won't work with.  Make sure to use Nodes in Blender for your materials to avoid this.

## Versions
Currently only tested and supported in 2.80
