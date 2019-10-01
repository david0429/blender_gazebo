import bpy
import os
import subprocess
import xml.etree.ElementTree as ET

collision_suffix = "_collision"
prefix = ""

def checkDir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def getPackagePaths(package_name, make_dirs=True):
    out = subprocess.Popen(['rosrun', 'blender_gazebo', 'rospack.py', package_name], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout,stderr = out.communicate()
    out = stdout.decode().strip()

    if "ERROR" in str(out).upper() or "rosbash" in str(out):
        return [None, None, None, None]
    else:
        r_values = out.split(",")
        if make_dirs:
            for dir in r_values:
                checkDir(dir)
        return r_values

def getWorldLaunch(location):
    world_launch = location + "/data/world.launch"
    parser = ET.XMLParser()
    return ET.parse(world_launch)

def writeList(location, list):
    out_file = open(location, 'w')
    for line in list:
        out_file.write(line)
    out_file.close()

def writeURDF(name, package_name, visual, collision, urdf_dir, blender_gazebo_root_dir):
    body_urdf_xml = blender_gazebo_root_dir + "/data/body.urdf.xacro"
    out_data = []

    in_file = open(body_urdf_xml, 'r')
    for line in in_file:
        out_data.append(line.replace("$NAME$", name).replace("$PACKAGE$", package_name).replace("$VISUAL$", visual).replace("$COLLISION$", collision))
    in_file.close()

    writeList(urdf_dir + name + ".urdf.xacro", out_data)

def writeLaunch(name, package_name, launch_dir, blender_gazebo_root_dir):
    body_launch = blender_gazebo_root_dir + "/data/body.launch"
    out_data = []

    in_file = open(body_launch, 'r')
    for line in in_file:
        out_data.append(line.replace("$NAME$", name).replace("$PACKAGE$", package_name))
    in_file.close()

    writeList(launch_dir + "/spawn_" + name + ".launch", out_data)

def exportSTL(ob, name, dir):
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.ops.export_mesh.stl(filepath= dir + name, use_selection=True, use_mesh_modifiers=True)

def exportDAE(ob, name, dir):
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.ops.wm.collada_export(filepath= dir + name, apply_modifiers=True, selected=True)

def main():
    global prefix
    prefix = bpy.path.basename(bpy.context.blend_data.filepath)
    prefix = prefix[:prefix.rindex(".")]

    blender_gazebo_root_dir, mesh_dir, urdf_dir, launch_dir = getPackagePaths("blender_gazebo", make_dirs=False)
    if blender_gazebo_root_dir:
        package_name = "sw_gazebo_test"
        root_dir, mesh_dir, urdf_dir, launch_dir = getPackagePaths(package_name)

        if root_dir:

            world_launch = getWorldLaunch(blender_gazebo_root_dir)

            for ob in bpy.data.objects:
                if ob.type == 'MESH':
                    if collision_suffix not in ob.name:
                        print("Working on " + ob.name)
                        body_name = prefix + "_" + ob.name
                        visual_name = body_name + ".dae"
                        exportDAE(ob, visual_name, mesh_dir)

                        collision_name = ob.name + collision_suffix
                        try:
                            collision_file = bpy.data.objects[collision_name]
                            print("Found custom collision mesh")
                            collision_name = body_name + collision_suffix + ".stl"
                            exportSTL(collision_file, collision_name, mesh_dir)
                        except:
                            collision_name = visual_name

                        writeURDF(body_name, package_name, visual_name, collision_name, urdf_dir, blender_gazebo_root_dir)
                        writeLaunch(body_name, package_name, launch_dir, blender_gazebo_root_dir)
                        world_launch.getroot().append(ET.Element("include", attrib={"file": "$(find " + package_name + ")/launch/spawn_" + body_name + ".launch"}))
            world_launch.write(launch_dir + "/" + prefix + ".launch")
        else:
            print("Error finding desired package.  Is your workspace sourced properly?")
    else:
        print("Error finding blender_gazebo.  Is ROS or your workspace sourced properly?")
main()
