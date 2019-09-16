#!/usr/bin/env python
import rospkg
import sys

def getPackagePaths(package_name):
    rospack = rospkg.RosPack()
    if package_name in rospack.list():
        root_path = rospack.get_path(package_name) + "/"
        mesh_dir = root_path + "meshes/"
        urdf_dir = root_path + "urdf/"
        launch_dir = root_path + "launch/"
        print(root_path + "," + mesh_dir + "," + urdf_dir + "," + launch_dir)
    else:
        print("ERROR: Could not find package: " + package_name)

if __name__== "__main__":
    if len(sys.argv) == 2:
        getPackagePaths(sys.argv[1])
    else:
        print "ERROR: Run with rosrun blender_gazebo rospack.py <package_name>"
