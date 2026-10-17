"""Read supplied native geometry with Blender automatic script execution disabled."""
import bpy
import json
from pathlib import Path
from mathutils import Vector

bpy.context.scene.frame_set(48)
records = []
depsgraph = bpy.context.evaluated_depsgraph_get()
for instance in depsgraph.object_instances:
    obj = instance.object
    material_names = [slot.material.name if slot.material else None for slot in obj.material_slots]
    screen = "Display dark glass" in material_names
    board = "board" in obj.name.lower() and max(obj.dimensions) > 3
    if obj.type != "MESH" or not (screen or board):
        continue
    vertices = [list(instance.matrix_world @ vertex.co) for vertex in obj.data.vertices]
    records.append({"name": obj.name, "materials": material_names, "matrix_world": [list(row) for row in instance.matrix_world], "vertices_world_blender": vertices, "vertices_local": [list(vertex.co) for vertex in obj.data.vertices], "parent": instance.parent.name if instance.parent else (obj.parent.name if obj.parent else None), "is_instance": instance.is_instance})
cameras = []
for obj in bpy.data.objects:
    if obj.type == "CAMERA":
        cameras.append({"name": obj.name, "matrix_world": [list(row) for row in obj.matrix_world], "type": obj.data.type, "ortho_scale": obj.data.ortho_scale})
target = Path(__file__).resolve().with_name("native-measurements.json")
target.write_text(json.dumps({"blenderVersion": bpy.app.version_string, "frame": 48, "meshes": records, "cameras": cameras}, indent=2) + "\n")
print("Measured", len(records), "native screen/monitor/board meshes")
for record in records[:35]:
    print(record["name"], record["materials"], len(record["vertices_world_blender"]))
