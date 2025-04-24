import bpy
import json
import math
import os
from mathutils import Vector


def remove_all_objects():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    # Remove all collections except for the main one.
    for collection in bpy.data.collections:
        if collection.name != "Collection":
            bpy.data.collections.remove(collection)

# Import .glb File
#
# This function imports a .glb file and renames the imported object.
# ------------------------------------------------------------------------------
def import_glb(file_path, object_name):
    bpy.ops.import_scene.gltf(filepath=file_path)
    imported = bpy.context.view_layer.objects.active
    if imported:
        imported.name = object_name

# Create Floor and 4 Walls
#
# Rules:
# - The floor is created as a plane and its center is shifted to (width/2, depth/2)
#   so that the bottom-left corner aligns with (0, 0) in the XY plane.
# - Walls are positioned around the perimeter:
#    * WALL_SOUTH: centered at (width/2, 0) at Y = 0.
#    * WALL_NORTH: centered at (width/2, depth).
#    * WALL_WEST: centered at (0, depth/2).
#    * WALL_EAST: centered at (width, depth/2).

def create_room(width, depth, height, wall_thickness=0.1):
    # Create the floor as a plane.
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "FLOOR"
    # Shift the floor so that its bottom-left corner is at (0, 0) on the XY plane.
    floor.location.x = width * 0.5
    floor.location.y = depth * 0.5
    floor.scale = (width, depth, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # Create a material for the floor ("FloorMaterial") with your chosen color.
    # (In your example, the color is (0.053, 0.071, 0.051, 1)).
    floor_material_name = "FloorMaterial"
    floor_mat = bpy.data.materials.new(name=floor_material_name)
    floor_mat.diffuse_color = (0.012, 0.021, 0.028, 1)
    # Explicitly assign the material to the floor object.
    if floor.data.materials:
        floor.data.materials[0] = floor_mat
    else:
        floor.data.materials.append(floor_mat)
    
    # Define parameters for the walls as tuples of (name, location, scale).
    wall_params = [
        ("WALL_SOUTH", (width / 2, 0, height / 2), (width, wall_thickness, height)),
        ("WALL_NORTH", (width / 2, depth, height / 2), (width, wall_thickness, height)),
        ("WALL_WEST", (0, depth / 2, height / 2), (wall_thickness, depth, height)),
        ("WALL_EAST", (width, depth / 2, height / 2), (wall_thickness, depth, height)),
    ]
    # Create a material for the walls ("WallMaterial") with the specified color.
    material_name = "WallMaterial"
    wall_mat = bpy.data.materials.new(name=material_name)
    wall_mat.diffuse_color = (0.053, 0.071, 0.051, 1)
    
    # Create walls as cubes, set their scale, apply transformations, and assign the wall material.
    for name, loc, scale in wall_params:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
        wall = bpy.context.active_object
        wall.name = name
        wall.scale = scale
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        if wall.data.materials:
            wall.data.materials[0] = wall_mat
        else:
            wall.data.materials.append(wall_mat)

#Join Sub-Meshes, Delete Empty Objects, and Clear Parent Transforms
#
# These functions help to clean up the scene by joining mesh children and clearing
# any parent transforms.
def select_meshes_under_empty(empty_name):
    emp = bpy.data.objects.get(empty_name)
    if emp and emp.type == 'EMPTY':
        for child in emp.children:
            if child.type == 'MESH':
                child.select_set(True)
                bpy.context.view_layer.objects.active = child
            else:
                select_meshes_under_empty(child.name)

def join_empty_children():
    empties = [o for o in bpy.data.objects if o.type == 'EMPTY' and o.parent is None]
    for e in empties:
        bpy.ops.object.select_all(action='DESELECT')
        select_meshes_under_empty(e.name)
        if bpy.context.selected_objects:
            bpy.ops.object.join()
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
            joined = bpy.context.view_layer.objects.active
            if joined:
                joined.name = e.name + "_joined"

def delete_empty_objects():
    for emp in [o for o in bpy.context.scene.objects if o.type == 'EMPTY']:
        bpy.data.objects.remove(emp)

def clear_parent_transforms():
    for o in bpy.context.scene.objects:
        if o.type == 'MESH' and o.parent:
            bpy.ops.object.select_all(action='DESELECT')
            o.select_set(True)
            bpy.context.view_layer.objects.active = o
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
            o.select_set(False)

#Adjust Orientation (Force Z-up if originally Y-up)
#
# If an imported object's dimensions suggest it's oriented in Y-up format (i.e.,
# its Y dimension is dominant), rotate it -90° about the X axis so that Z becomes up.

def force_z_up_if_needed(obj):
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    dims = obj.dimensions
    if dims.y > dims.z and dims.y > dims.x:
        bpy.ops.transform.rotate(value=-math.pi / 2, orient_axis='X')
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

#Scale Object to Specified Dimensions (Length, Width, Height)
#
# This function applies scaling factors to match the desired size.
# Length corresponds to the X axis, Width to the Y axis, and Height to the Z axis.

def scale_to_lwh(obj, length, width, height):
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    bx, by, bz = obj.dimensions
    if bx < 1e-9 or by < 1e-9 or bz < 1e-9:
        return
    sx, sy, sz = length / bx, width / by, height / bz
    obj.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Adjust Object's Vertical Position
#
# Shifts an object along the Z axis so that the bottom of its bounding box
# aligns with the specified target_z (typically, the floor level, e.g., 0).

def set_object_bottom_z(obj, target_z):
    corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    min_z = min(pt.z for pt in corners)
    obj.location.z += (target_z - min_z)


def main():
    remove_all_objects()

    json_path = "/Users/peterkrotov/Downloads/Plan-Design/Assets_10/10_jpg.rf.87c25ad7b870a0ed03359474f8cef034_3d.json"
    glb_folder = "/Users/peterkrotov/Downloads/Plan-Design/Assets_10"

    with open(json_path, "r") as f:
        data = json.load(f)

    # Retrieve room dimensions from the first JSON entry.
    w, d, h = data[0].get("room_dimensions", [8.3, 10.96, 2.5])
    create_room(w, d, h, wall_thickness=0.1)

    # Treat the rest of the JSON entries as objects in the room.
    objects_in_room = [x for x in data if "new_object_id" in x]

    # Build a mapping of object identifiers to .glb file paths.
    glb_map = {}
    for root, dirs, files in os.walk(glb_folder):
        for file in files:
            if file.lower().endswith(".glb"):
                key = file.rsplit(".glb", 1)[0]
                glb_map[key] = os.path.join(root, file)

    # Import each object from its corresponding .glb file.
    for item_data in objects_in_room:
        obj_id = item_data["new_object_id"]
        glb_path = glb_map.get(obj_id)
        if not glb_path:
            print(f"No .glb found for {obj_id}")
            continue
        import_glb(glb_path, obj_id)

    join_empty_children()
    delete_empty_objects()
    clear_parent_transforms()

    # Define rotation settings for individual objects.
    rotation_settings = {
        "sofa_1":         {"rot_x": math.radians(270), "rot_y": math.radians(0), "rot_z": math.radians(270)},
        "sofa_2":         {"rot_x": math.radians(270), "rot_y": 0.0, "rot_z": math.radians(0)},
        "side table_1":   {"rot_x": 0.0, "rot_y": 0.0, "rot_z": math.radians(90)},
        "armchair_1":     {"rot_x": math.radians(180), "rot_y": 0.0, "rot_z": math.radians(270)},
        "rug_1":          {"rot_x": 0.0, "rot_y": 0.0, "rot_z": math.radians(90)},
        "coffee table_1": {"rot_x": math.radians(270), "rot_y": 0.0, "rot_z": math.radians(90)},
        "coffee table_2": {"rot_x": math.radians(270), "rot_y": 0.0, "rot_z": math.radians(90)},
        "coffee table_3": {"rot_x": math.radians(270), "rot_y": 0.0, "rot_z": math.radians(90)},
        "coffee table_4": {"rot_x": math.radians(270), "rot_y": 0.0, "rot_z": math.radians(90)},
        "floor lamp_1":   {"rot_x": 0.0, "rot_y": 0.0, "rot_z": math.radians(90)},
        "floor plant_1":  {"rot_x": math.radians(0), "rot_y": 0.0, "rot_z": math.radians(0)},
        "floor plant_2":  {"rot_x": math.radians(0), "rot_y": 0.0, "rot_z": math.radians(0)},
        "armchair_2":     {"rot_x": math.radians(180), "rot_y": 0.0, "rot_z": math.radians(90)},
        "armchair_3":     {"rot_x": math.radians(180), "rot_y": 0.0, "rot_z": math.radians(90)},
        "sofa_3":         {"rot_x": math.radians(270), "rot_y": 0.0, "rot_z": math.radians(180)},
        "armchair_4":     {"rot_x": math.radians(180), "rot_y": 0.0, "rot_z": math.radians(270)},
        "side table_2":   {"rot_x": 0.0, "rot_y": 0.0, "rot_z": math.radians(0)},
        "side table_3":   {"rot_x": 0.0, "rot_y": 0.0, "rot_z": math.radians(90)},
        "side table_4":   {"rot_x": 0.0, "rot_y": 0.0, "rot_z": math.radians(0)},
        "window_1":       {"rot_x": math.radians(90), "rot_y": math.radians(180), "rot_z": math.radians(0)},
        "window_2":       {"rot_x": math.radians(90), "rot_y": math.radians(180), "rot_z": math.radians(90)}
    }

    # Process each imported object: set scaling, rotation, and position.
    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH':
            continue

        base_name = obj.name.replace("_joined", "")
        data_item = next((d for d in objects_in_room if d["new_object_id"] == base_name), None)
        if not data_item:
            continue

        # Get the object's position and size from the JSON.
        px, py, pz = data_item["position"]["x"], data_item["position"]["y"], data_item["position"]["z"]
        dims = data_item["size_in_meters"]
        length, width, height = dims["length"], dims["width"], dims["height"]

        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        # Ensure the object is oriented correctly (Z-up).
        force_z_up_if_needed(obj)

        # Scale the object to the specified dimensions.
        scale_to_lwh(obj, length, width, height)

        # Apply the rotation from the settings.
        rotation = rotation_settings.get(
            base_name,
            {"rot_x": 0.0, "rot_y": 0.0, "rot_z": math.radians(data_item.get("rotation_z", 0.0))}
        )
        obj.rotation_mode = 'XYZ'
        obj.rotation_euler[0] = rotation["rot_x"]
        obj.rotation_euler[1] = rotation["rot_y"]
        obj.rotation_euler[2] = rotation["rot_z"]

        # Adjust the vertical position so the object's bottom aligns with the floor.
        set_object_bottom_z(obj, pz)
        # Set the X and Y position based on the center from the JSON.
        obj.location.x = px
        obj.location.y = py

    print(">>> Scene complete: All objects adjusted to floor with correct orientation. <<<")

if __name__ == "__main__":
    main()
