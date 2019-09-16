import bpy
import os
import subprocess

collision_suffix = "_collision"

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

def exportSTL(ob, name, dir):
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.ops.export_mesh.stl(filepath= dir + ob.name + ".stl", use_selection=True, use_mesh_modifiers=True)

def exportDAE(ob, name, dir):
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.ops.wm.collada_export(filepath= dir + ob.name + ".dae", apply_modifiers=True, selected=True)

def main():
    root_dir, mesh_dir, urdf_dir, launch_dir = getPackagePaths("sw_gazebo_test")
    if root_dir:
        for ob in bpy.data.objects:
            if ob.type == 'MESH':
                print("Working on " + ob.name)

                if collision_suffix not in ob.name:
                    exportDAE(ob, ob.name, mesh_dir)

                    collision_name = ob.name + collision_suffix
                    try:
                        collision_file = scene.objects[ob.name + collision_suffix]
                    except:
                        collision_file = ob

                    exportSTL(collision_file, collision_name, mesh_dir)

main()
