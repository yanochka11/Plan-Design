import bpy
import json
import math
import os
import mathutils

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

# Start fresh
clear_scene()

# Function to import GLB file and assign it the provided object name
def import_glb(file_path, object_name):
    bpy.ops.import_scene.gltf(filepath=file_path)
    imported_object = bpy.context.view_layer.objects.active
    if imported_object is not None:
        imported_object.name = object_name

# Function to create a room with specified dimensions
def create_room(width, depth, height):
    # Create floor
    bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0))

    # Extrude to create walls
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, height)})
    bpy.ops.object.mode_set(mode='OBJECT')

    # Scale the walls to the desired dimensions
    bpy.ops.transform.resize(value=(width, depth, 1))

    bpy.context.active_object.location.x += width / 2
    bpy.context.active_object.location.y += depth / 2

# Function to find all GLB files in a directory and return a dictionary mapping object IDs to file paths
def find_glb_files(directory):
    glb_files = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".glb"):
                key = file.split(".")[0]  # Remove file extension to match the object ID
                glb_files[key] = os.path.join(root, file)  # Map the object ID to the file path
    return glb_files

# Function to get objects with no parent (highest level in hierarchy)
def get_highest_parent_objects():
    highest_parent_objects = []
    for obj in bpy.data.objects:
        if obj.parent is None:
            highest_parent_objects.append(obj)
    return highest_parent_objects

# Function to delete empty objects
def delete_empty_objects():
    for obj in bpy.context.scene.objects:
        if obj.type == 'EMPTY':
            bpy.context.view_layer.objects.active = obj
            bpy.data.objects.remove(obj)

# Function to select meshes under an empty object
def select_meshes_under_empty(empty_object_name):
    empty_object = bpy.data.objects.get(empty_object_name)
    if empty_object is not None and empty_object.type == 'EMPTY':
        for child in empty_object.children:
            if child.type == 'MESH':
                child.select_set(True)
                bpy.context.view_layer.objects.active = child
            else:
                select_meshes_under_empty(child.name)

# Function to rescale an object based on a target size
def rescale_object(obj, scale):
    if obj.type == 'MESH':
        bbox_dimensions = obj.dimensions
        scale_factors = (
                         scale["length"] / bbox_dimensions.x,
                         scale["width"] / bbox_dimensions.y,
                         scale["height"] / bbox_dimensions.z
                        )
        obj.scale = scale_factors

# Load objects from scene_graph.json
objects_in_room = {}
file_path = "/Users/iani.kuli/Desktop/Assets2/scene_graph.json"
with open(file_path, 'r') as file:
    data = json.load(file)
    for item in data:
        if item["new_object_id"] not in ["south_wall", "north_wall", "east_wall", "west_wall", "middle of the room", "ceiling"]:
            objects_in_room[item["new_object_id"]] = item

# Find GLB files in the directory
directory_path = "/Users/iani.kuli/Desktop/Assets2"
glb_file_paths = find_glb_files(directory_path)

# Import GLB files based on scene_graph.json
for item_id, object_in_room in objects_in_room.items():
    if item_id in glb_file_paths:
        glb_file_path = glb_file_paths[item_id]
        import_glb(glb_file_path, item_id)

# Get highest parent objects
parents = get_highest_parent_objects()
empty_parents = [parent for parent in parents if parent.type == "EMPTY"]
print(empty_parents)

# Join meshes and set origin for each empty parent
for empty_parent in empty_parents:
    bpy.ops.object.select_all(action='DESELECT')
    select_meshes_under_empty(empty_parent.name)
    
    bpy.ops.object.join()
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    
    joined_object = bpy.context.view_layer.objects.active
    if joined_object is not None:
        joined_object.name = empty_parent.name + "-joined"

# Reset active object
bpy.context.view_layer.objects.active = None

# Apply transformations and set origin for all mesh objects
MSH_OBJS = [m for m in bpy.context.scene.objects if m.type == 'MESH']
for OBJS in MSH_OBJS:
    bpy.context.view_layer.objects.active = OBJS
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
    OBJS.location = (0.0, 0.0, 0.0)
    bpy.context.view_layer.objects.active = OBJS
    OBJS.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

# Position, rotate, and scale objects based on scene_graph.json data
for OBJS in MSH_OBJS:
    item = objects_in_room[OBJS.name.split("-")[0]]
    object_position = (item["position"]["x"], item["position"]["y"], item["position"]["z"])  # X, Y, and Z coordinates
    object_rotation_z = (item["rotation"]["z_angle"] / 180.0) * math.pi + math.pi # Rotation angles in radians around the Z axis
    
    bpy.ops.object.select_all(action='DESELECT')
    OBJS.select_set(True)
    OBJS.location = object_position
    bpy.ops.transform.rotate(value=object_rotation_z,  orient_axis='Z')
    rescale_object(OBJS, item["size_in_meters"])

# Deselect all and delete empty objects
bpy.ops.object.select_all(action='DESELECT')
delete_empty_objects()

room_width = 4.0
room_depth = 4.0
room_height = 2.5

# Generate the room with specified dimensions
create_room(room_width, room_depth, room_height)

# Add a camera inside the room
cam_data = bpy.data.cameras.new("Camera")
cam_obj = bpy.data.objects.new("Camera", cam_data)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj

# Place camera near the south wall, slightly inside the room (e.g., y=0.5)
cam_obj.location = (room_width / 2.0, 0.5, room_height * 0.5)

# Make camera look at the center of the room (2,2,...)
target = mathutils.Vector((room_width / 2.0, room_depth / 2.0, room_height / 2.0))
direction = target - cam_obj.location
cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

