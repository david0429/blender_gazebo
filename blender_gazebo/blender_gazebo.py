bl_info = {
    "name":         "ROS Gazebo Exporter",
    "author":       "Dave Niewinski",
    "version":      (0,0,1),
    "blender":      (2,80,0),
    "location":     "File > Import-Export",
    "description":  "Export Gazebo",
    "category":     "Import-Export"
}

import bpy
import os
import subprocess
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
import xml.etree.ElementTree as ET

class InternalData():
    def __init__(self):
        self.text = ""

    def getRoot(self):
        return ET.fromstring(self.text)

class BodyLaunch(InternalData):
    def __init__(self):
        self.text = '''<launch>
  <param name="$NAME$_description" command="$(find xacro)/xacro --inorder '$(find $PACKAGE$)/urdf/$NAME$.urdf.xacro'" />

  <node name="spawn_$NAME$" pkg="gazebo_ros" type="spawn_model" args="-param $NAME$_description -urdf -model $NAME$" respawn="false"/>
</launch>
'''

class BodyURDF(InternalData):
    def __init__(self):
        self.text = '''<?xml version="1.0"?>
<robot name="robot" xmlns:xacro="http://www.ros.org/wiki/xacro">
  <link name="$NAME$_link">
    <inertial>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <mass value="1"/>
      <inertia ixx="1" ixy="0" ixz="0" iyy="1" iyz="0" izz="1"/>
    </inertial>
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <mesh filename="package://$PACKAGE$/meshes/$VISUAL$"/>
      </geometry>
    </visual>
    <collision>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <mesh filename="package://$PACKAGE$/meshes/$COLLISION$"/>
      </geometry>
    </collision>
  </link>

  <gazebo> <static>true</static></gazebo>
</robot>
'''

class WorldLaunch(InternalData):
    def __init__(self):
        self.text = '''<launch>
  <arg name="use_sim_time" default="true" />
  <arg name="gui" default="true" />
  <arg name="headless" default="false" />
  <arg name="world_name" default="$(find blender_gazebo)/worlds/actually_empty_world.world" />

  <include file="$(find gazebo_ros)/launch/empty_world.launch">
    <arg name="debug" value="0" />
    <arg name="gui" value="$(arg gui)" />
    <arg name="use_sim_time" value="$(arg use_sim_time)" />
    <arg name="headless" value="$(arg headless)" />
    <arg name="world_name" value="$(arg world_name)" />
  </include>
</launch>
'''

class GazeboExport(bpy.types.Operator, ExportHelper) :
    bl_idname       = "object.exportgazebo";
    bl_label        = "Export Gazebo";
    bl_options      = {'REGISTER', 'UNDO'};

    filename_ext    = ".launch"
    filter_glob: StringProperty(default="*.launch", options={'HIDDEN'})

    def __init__(self):
        self.collision_suffix = "_collision"

    def checkDir(self, dir):
        if not os.path.exists(dir):
            os.makedirs(dir)

    def getPackagePaths(self, launch_file, make_dirs=True):
        (dirname, filename) = os.path.split(launch_file)
        (shortname, extension) = os.path.splitext(filename)
        root_dir = os.path.abspath(os.path.join(dirname, ".."))
        mesh_dir = os.path.join(root_dir, "meshes/")
        urdf_dir = os.path.join(root_dir, "urdf/")
        launch_dir = os.path.join(root_dir, "launch/")
        package_name = root_dir.split("/")
        package_name = package_name[-1]

        if make_dirs:
            self.checkDir(mesh_dir)
            self.checkDir(urdf_dir)
            self.checkDir(launch_dir)

        return root_dir, mesh_dir, urdf_dir, launch_dir, package_name, shortname

    def writeURDF(self, name, package_name, visual, collision, urdf_dir):
        body_urdf = BodyURDF().getRoot()

        for c in body_urdf.findall(".//mesh"):
            for k in c.attrib.keys():
                c.set(k, c.attrib[k].replace("$PACKAGE$", package_name).replace("$VISUAL$", visual).replace("$COLLISION$", collision))
        for c in body_urdf.findall("link"):
            for k in c.attrib.keys():
                c.set(k, c.attrib[k].replace("$NAME$", name))

        outFile = open(urdf_dir + name + ".urdf.xacro", 'wb')
        outFile.write(ET.tostring(body_urdf))
        outFile.close()

    def writeLaunch(self, name, package_name, launch_dir):
        body_launch = BodyLaunch().getRoot()

        for c in body_launch.findall("*"):
            for k in c.attrib.keys():
                c.set(k, c.attrib[k].replace("$NAME$", name).replace("$PACKAGE$", package_name))

        outFile = open(launch_dir + "spawn_" + name + ".launch", 'wb')
        outFile.write(ET.tostring(body_launch))
        outFile.close()

    def exportSTL(self, ob, name, dir):
        bpy.ops.object.select_all(action='DESELECT')
        ob.select_set(True)
        bpy.ops.export_mesh.stl(filepath= dir + name, use_selection=True, use_mesh_modifiers=True)

    def exportDAE(self, ob, name, dir):
        bpy.ops.object.select_all(action='DESELECT')
        ob.select_set(True)
        bpy.ops.wm.collada_export(filepath= dir + name, apply_modifiers=True, selected=True)

    def execute(self, context):
        root_dir, mesh_dir, urdf_dir, launch_dir, package_name, prefix = self.getPackagePaths(self.filepath)
        world_launch = WorldLaunch().getRoot()

        for ob in bpy.data.objects:
            if ob.type == 'MESH':
                if self.collision_suffix not in ob.name:
                    print("Working on " + ob.name)
                    body_name = prefix + "_" + ob.name
                    visual_name = body_name + ".dae"
                    self.exportDAE(ob, visual_name, mesh_dir)

                    collision_name = ob.name + self.collision_suffix
                    try:
                        collision_file = bpy.data.objects[collision_name]
                        print("Found custom collision mesh")
                        collision_name = body_name + self.collision_suffix + ".stl"
                        self.exportSTL(collision_file, collision_name, mesh_dir)
                    except:
                        collision_name = visual_name

                    self.writeURDF(body_name, package_name, visual_name, collision_name, urdf_dir)
                    self.writeLaunch(body_name, package_name, launch_dir)
                    world_launch.append(ET.Element("include", attrib={"file": "$(find " + package_name + ")/launch/spawn_" + body_name + ".launch"}))

        outFile = open(launch_dir + "/" + prefix + ".launch", 'wb')
        outFile.write(ET.tostring(world_launch))
        outFile.close()

        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(GazeboExport.bl_idname, text="Gazebo Launch (.launch)");

def register():
    bpy.utils.register_class(GazeboExport)
    bpy.types.TOPBAR_MT_file_export.append(menu_func)

def unregister():
    bpy.utils.unregister_class(GazeboExport)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func);

if __name__ == "__main__" :
    register()
