"""Bind existing monitors using evaluated native collection-instance geometry."""
import json
import math
from pathlib import Path

root = Path(__file__).resolve().parents[3]
evidence = root / "evidence/desktop/original-office"
measurements = json.loads((evidence / "native-measurements.json").read_text())

def surface(record, side, stand_off):
    vertices = record["vertices_local"]
    minimum = [min(v[a] for v in vertices) for a in range(3)]
    maximum = [max(v[a] for v in vertices) for a in range(3)]
    point = [(minimum[a] + maximum[a]) / 2 for a in range(3)]
    point[1] = maximum[1] + stand_off if side > 0 else minimum[1] - stand_off
    matrix = record["matrix_world"]
    world = [sum(matrix[a][b] * point[b] for b in range(3)) + matrix[a][3] for a in range(3)]
    normal = [side * matrix[0][1], side * matrix[2][1], -side * matrix[1][1]]
    anchor = [world[0], world[2], -world[1]]
    rotation = [0, math.atan2(normal[0], normal[2]), 0]
    size = [maximum[0] - minimum[0], maximum[2] - minimum[2]]
    return anchor, rotation, size, normal

stations = []
records = []
for record in measurements["meshes"]:
    if not record["name"].startswith("Left display screen") or not str(record["parent"]).startswith("Desk_parent_"):
        continue
    station_id = record["parent"].removeprefix("Desk_")
    anchor, rotation, size, normal = surface(record, 1, 0.004)
    focus = {"position": [anchor[a] + 0.75 * normal[a] + (0.045 if a == 1 else 0) for a in range(3)], "target": anchor}
    stations.append({"id": station_id, "label": f"Computer {int(station_id.split('_')[-1]):02d}", "anchor": anchor, "rotation": rotation, "screenSize": [size[0] - 0.012, size[1] - 0.012], "focus": focus})
    records.append({"stationId": station_id, "sourceInstance": record["parent"], "sourceMesh": record["name"], "surfaceSizeMetres": size, "insetMetres": 0.006, "standOffMetres": 0.004, "frontNormalGltf": normal, "basis": "[Blender X, Blender Z, -Blender Y]", "anchor": anchor})
stations.sort(key=lambda s: s["id"])
assert len(stations) == 24 and len({s["id"] for s in stations}) == 24
board_record = next(r for r in measurements["meshes"] if r["name"] == "Job board writing surface" and r["parent"] == "JobBoard_board_01")
anchor, rotation, size, normal = surface(board_record, -1, 0.04)
camera = next(c for c in measurements["cameras"] if c["name"] == "Camera_Full_Office")
matrix = camera["matrix_world"]
origin = [matrix[i][3] for i in range(3)]
distance = (origin[2] - 1) / matrix[2][2]
target_blender = [origin[i] - distance * matrix[i][2] for i in range(3)]
position_blender = [target_blender[i] + 0.72 * (origin[i] - target_blender[i]) for i in range(3)]
convert = lambda p: [p[0], p[2], -p[1]]
bindings = {"modelUrl": "/office/office.glb", "overview": {"position": convert(position_blender), "target": convert(target_blender)}, "stations": stations, "board": {"anchor": anchor, "rotation": rotation, "size": size}}
(root / "desktop/public/office/bindings.json").write_text(json.dumps(bindings, indent=2) + "\n")
(evidence / "binding-measurements.json").write_text(json.dumps({"source": "scene/Sidequest_Office_Master.blend", "frame": 48, "units": "metres", "stationCount": len(stations), "stations": records, "boardSource": {"instance": board_record["parent"], "mesh": board_record["name"]}, "overviewSource": "Camera_Full_Office; same viewing direction, perspective distance at 72% of source position", "workerPolicy": "No backend workerId is inferred from authored actor IDs."}, indent=2) + "\n")
print("Wrote 24 measured monitor bindings and the original board binding")
