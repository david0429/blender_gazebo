import bpy
import os
import subprocess

collision_suffix = "_collision"
prefix = ""

def checkDir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def getPackagePaths(package_name):
    out = subprocess.Popen(['rosrun', 'blender_gazebo', 'rospack.py', package_name], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout,stderr = out.communicate()
    out = stdout.decode().strip()
    if "ERROR" in str(out):
        return [None, None, None, None]
    else:
        r_values = out.split(",")
        for dir in r_values:
            checkDir(dir)
        return r_values

def writeURDF(name, directory, visual, collision):
    pass

def exportSTL(ob, name, dir):
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.ops.export_mesh.stl(filepath= dir + name + ".stl", use_selection=True, use_mesh_modifiers=True)

def exportDAE(ob, name, dir):
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.ops.wm.collada_export(filepath= dir + name + ".dae", apply_modifiers=True, selected=True)

def main():
    global prefix
    prefix = bpy.path.basename(bpy.context.blend_data.filepath)
    prefix = prefix[:prefix.rindex(".")]
    
    root_dir, mesh_dir, urdf_dir, launch_dir = getPackagePaths("sw_gazebo_test")
    if root_dir:
        for ob in bpy.data.objects:
            if ob.type == 'MESH':
                if collision_suffix not in ob.name:
                    print("Working on " + ob.name)
                    visual_name = prefix + "_" + ob.name
                    exportDAE(ob, visual_name, mesh_dir)

                    collision_name = ob.name + collision_suffix
                    try:
                        collision_file = bpy.data.objects[collision_name]
                        print("Found custom collision mesh")
                        collision_name = visual_name + collision_suffix
                        exportSTL(collision_file, collision_name, mesh_dir)
                    except:
                        collision_name = visual_name

main()
