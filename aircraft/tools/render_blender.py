"""Run: blender -b --python aircraft/tools/render_blender.py. Uses actual CAD tessellation."""
from pathlib import Path
import bpy,json,math
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
parts=json.loads((ROOT/'viewer'/'mesh.json').read_text())
for p in parts:
    mesh=bpy.data.meshes.new(p['name']);mesh.from_pydata(p['vertices'],[],p['triangles']);mesh.update()
    obj=bpy.data.objects.new(p['name'],mesh);bpy.context.collection.objects.link(obj)
    obj.color=(*p['color'],1)
    if p['category']=='canopy':obj.hide_render=True
scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO';scene.display.shading.studiolight_rotate_z=.4
scene.display.shading.color_type='OBJECT';scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH'
scene.display.shading.show_object_outline=True;scene.display.shading.background_type='WORLD'
scene.world.color=(.83,.88,.92)
scene.render.resolution_x=1600;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
bpy.ops.object.camera_add(location=(-12,-16,12))
cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=16
cam.rotation_euler=(Vector((0,0,.6))-cam.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(ROOT/'images'/'E8_Assembly_Isometric.png');bpy.ops.render.render(write_still=True)
cam.location=(0,0,18);cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=13
scene.render.filepath=str(ROOT/'images'/'E8_Assembly_Top.png');bpy.ops.render.render(write_still=True)
print('Rendered CAD assembly views')
