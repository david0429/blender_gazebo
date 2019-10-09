bl_info = {
    "name":         "ROS Gazebo Exporter",
    "author":       "Dave Niewinski",
    "version":      (0,0,1),
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

class GazeboExport(bpy.types.Operator, ExportHelper) :
    bl_idname       = "object.exportgazebo";
    bl_label        = "Export Gazebo";
    bl_options      = {'PRESET'};

    filename_ext    = ".launch"
    filter_glob: StringProperty(default="*.launch", options={'HIDDEN'})

    collision_suffix = "_collision"

    def checkDir(self, dir):
        if not os.path.exists(dir):
            os.makedirs(dir)

    def getPackagePaths(self, launch_file, make_dirs=True):
        (dirname, filename) = os.path.split(launch_file)
        (shortname, extension) = os.path.splitext(filename)
        root_dir = os.path.abspath(os.path.join(dirname, ".."))
        mesh_dir = os.path.join(root_dir, "meshes")
        urdf_dir = os.path.join(root_dir, "urdf")
        launch_dir = os.path.join(root_dir, "launch")
        package_name = root_dir.split("/")
        package_name = package_name[-1]

        if make_dirs:
            self.checkDir(mesh_dir)
            self.checkDir(urdf_dir)
            self.checkDir(launch_dir)

        return root_dir, mesh_dir, urdf_dir, launch_dir, package_name, shortname

    def getWorldLaunch(self):
        path = bpy.utils.script_paths('addons/blender_gazebo/data')
        path = ''.join(path)
        world_launch = os.path.join(path, "world.launch")
        parser = ET.XMLParser()
        return ET.parse(world_launch)

    def writeList(self, location, list):
        out_file = open(location, 'w')
        for line in list:
            out_file.write(line)
        out_file.close()

    def writeURDF(self, name, package_name, visual, collision, urdf_dir):
        path = bpy.utils.script_paths('addons/blender_gazebo/data')
        path = ''.join(path)
        world_launch = os.path.join(path, "body.urdf.xacro")
        out_data = []

        in_file = open(body_urdf_xml, 'r')
        for line in in_file:
            out_data.append(line.replace("$NAME$", name).replace("$PACKAGE$", package_name).replace("$VISUAL$", visual).replace("$COLLISION$", collision))
        in_file.close()

        self.writeList(urdf_dir + name + ".urdf.xacro", out_data)

    def writeLaunch(self, name, package_name, launch_dir):
        path = bpy.utils.script_paths('addons/blender_gazebo/data')
        path = ''.join(path)
        world_launch = os.path.join(path, "body.launch")
        out_data = []

        in_file = open(body_launch, 'r')
        for line in in_file:
            out_data.append(line.replace("$NAME$", name).replace("$PACKAGE$", package_name))
        in_file.close()

        self.writeList(launch_dir + "/spawn_" + name + ".launch", out_data)

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
        world_launch = self.getWorldLaunch()

        for ob in bpy.data.objects:
            if ob.type == 'MESH':
                if collision_suffix not in ob.name:
                    print("Working on " + ob.name)
                    body_name = prefix + "_" + ob.name
                    visual_name = body_name + ".dae"
                    self.exportDAE(ob, visual_name, mesh_dir)

                    collision_name = ob.name + collision_suffix
                    try:
                        collision_file = bpy.data.objects[collision_name]
                        print("Found custom collision mesh")
                        collision_name = body_name + collision_suffix + ".stl"
                        self.exportSTL(collision_file, collision_name, mesh_dir)
                    except:
                        collision_name = visual_name

                    self.writeURDF(body_name, package_name, visual_name, collision_name, urdf_dir)
                    self.writeLaunch(body_name, package_name, launch_dir)
                    world_launch.getroot().append(ET.Element("include", attrib={"file": "$(find " + package_name + ")/launch/spawn_" + body_name + ".launch"}))
        world_launch.write(launch_dir + "/" + prefix + ".launch")

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
