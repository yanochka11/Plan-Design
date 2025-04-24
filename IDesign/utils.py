import networkx as nx
from matplotlib import pyplot as plt
import numpy as np
import cv2
from copy import copy, deepcopy
import random

from constraint_functions import (
    get_above_constraint,
    get_behind_constraint,
    get_in_corner_constraint,
    get_in_front_constraint,
    get_left_of_constraint,
    get_right_of_constraint,
    get_on_constraint,
    get_under_contraint,  
)

ROOM_LAYOUT_ELEMENTS = ["south_wall", "north_wall", "west_wall", "east_wall", "ceiling", "middle of the room"]

def get_room_priors(room_dimensions):
    """
    Generates room layout priors based on the given dimensions.

    Args:
        room_dimensions (tuple): Dimensions of the room (length, width, height).

    Returns:
        list: List of dictionaries representing the priors for walls, ceiling, and floor.
    """
    x_mid = room_dimensions[0] / 2
    y_mid = room_dimensions[1] / 2
    z_mid = room_dimensions[2] / 2

    room_priors = [
        {"new_object_id": "south_wall", "itemType": "wall", "position": {"x": x_mid, "y": 0, "z": z_mid},
         "size_in_meters": {"length": room_dimensions[0], "width": 0.0, "height": room_dimensions[2]}, "rotation": {"z_angle": 0.0}},
        {"new_object_id": "north_wall", "itemType": "wall", "position": {"x": x_mid, "y": room_dimensions[1], "z": z_mid},
         "size_in_meters": {"length": room_dimensions[0], "width": 0.0, "height": room_dimensions[2]}, "rotation": {"z_angle": 180.0}},
        {"new_object_id": "east_wall", "itemType": "wall", "position": {"x": room_dimensions[0], "y": y_mid, "z": z_mid},
         "size_in_meters": {"length": room_dimensions[1], "width": 0.0, "height": room_dimensions[2]}, "rotation": {"z_angle": 270.0}},
        {"new_object_id": "west_wall", "itemType": "wall", "position": {"x": 0, "y": y_mid, "z": z_mid},
         "size_in_meters": {"length": room_dimensions[1], "width": 0.0, "height": room_dimensions[2]}, "rotation": {"z_angle": 90.0}},
        {"new_object_id": "middle of the room", "itemType": "floor", "position": {"x": x_mid, "y": y_mid, "z": 0},
         "size_in_meters": {"length": room_dimensions[0], "width": room_dimensions[1], "height": 0.0}, "rotation": {"z_angle": 0.0}},
        {"new_object_id": "ceiling", "itemType": "ceiling", "position": {"x": x_mid, "y": y_mid, "z": room_dimensions[2]},
         "size_in_meters": {"length": room_dimensions[0], "width": room_dimensions[1], "height": 0.0}, "rotation": {"z_angle": 0.0}}
    ]

    return room_priors


def extract_list_from_json(input_json):
    """
    Extracts the first list value found in a dictionary.

    Args:
        input_json (dict): Input JSON-like dictionary.

    Returns:
        list or None: Extracted list if found, otherwise None.
    """
    for value in input_json.values(): 
        if isinstance(value, list):
            return value


def is_thin_object(obj):
    """
    Determines if the object is thin based on its size dimensions.

    Args:
        obj (dict): The object with size information.

    Returns:
        bool: True if the object is considered thin, otherwise False.
    """
    size = obj["size_in_meters"]
    min_size = min(size.values())
    max_size = max(size.values())
    return min_size > 0.0 and max_size / min_size >= 40.0


def detect_and_remove_cycle(G):
    """
    Detects and removes cycles from a directed graph.

    Args:
        G (nx.DiGraph): Directed graph.

    Returns:
        nx.DiGraph: Cycle-free graph.
    """
    while True:
        try:
            # Find a cycle using nx.simple_cycles
            cycles = list(nx.simple_cycles(G))
            if not cycles:
                break  # Exit if no cycles are found

            # Remove an edge from the first cycle to break it
            cycle = cycles[0]
            edge_to_remove = (cycle[-1], cycle[0])  # Break the cycle at the first edge
            G.remove_edge(*edge_to_remove)
            print(f"Removed edge {edge_to_remove} to break the cycle.")
        except Exception as e:
            print(f"Error while detecting/removing cycles: {e}")
            break

    return G


def is_point_bbox(position):
    """
    Checks whether the plausible bounding box is effectively a point.

    Args:
        position (list or tuple): List or tuple representing bounding box coordinates 
                                  [x_min, x_max, y_min, y_max, z_min, z_max].

    Returns:
        bool: True if the bounding box represents a single point, otherwise False.
    """
    return (
        np.isclose(position[0], position[1]) and 
        np.isclose(position[2], position[3]) and 
        np.isclose(position[4], position[5])
    )

def get_rotation(obj_A, scene_graph):
    """
    Determines the rotation of an object based on its properties and relationships in the scene graph.

    Args:
        obj_A (dict): The object whose rotation needs to be determined.
        scene_graph (list): The list of objects representing the scene graph.

    Returns:
        float: The rotation angle in degrees (default is 0.0 if not specified).
    """
    layout_rot = {
        "west_wall": 270.0,
        "east_wall": 90.0,
        "north_wall": 0.0,
        "south_wall": 180.0,
        "middle of the room": 0.0,
        "ceiling": 0.0
    }

    if obj_A is None:
        print("DEBUG: get_rotation() received None as input. Returning default rotation 0.0")
        return 0.0

    # Check for direct rotation attribute
    if "rotation" in obj_A:
        return obj_A.get("rotation", {}).get("z_angle", 0.0)

    # Check for facing attribute in predefined layout
    if "facing" in obj_A and obj_A["facing"] in layout_rot:
        return layout_rot[obj_A["facing"]]

    # Traverse relationships to determine rotation from parents
    parents = []
    for x in obj_A.get("placement", {}).get("objects_in_room", []):
        parent_obj = next(
            (element for element in scene_graph if element.get("new_object_id") == x["object_id"]), 
            None
        )
        if parent_obj is None:
            print(f"DEBUG: Object '{x['object_id']}' not found in scene graph! Skipping...")
            continue
        parents.append(parent_obj)

    if parents:
        return get_rotation(parents[0], scene_graph)

    # Default rotation
    return 0.0


def find_key(dictionary, value):
    """
    Finds the first key in a dictionary that corresponds to the specified value.

    Args:
        dictionary (dict): The dictionary to search.
        value (Any): The value to search for.

    Returns:
        Any: The key corresponding to the value, or None if not found.
    """
    for key, val in dictionary.items():
        if val == value:
            return key
    return None


def get_conflicts(G, scene_graph):
    """
    Collects all types of conflicts in the given scene graph.

    Args:
        G (nx.DiGraph): The directed acyclic graph representing the scene.
        scene_graph (list): The list of objects in the scene graph.

    Returns:
        list: A list of conflicts identified in the graph.
    """
    conflicts_wall = check_wall_relationship_impossibilities(G, scene_graph)
    conflicts_corner = check_corner_relationship_impossibilities(G, scene_graph)
    conflicts_room_layout = find_room_layout_conflicts(G, scene_graph)
    conflicts_one_parent = check_corner_relationships(G, scene_graph)
    conflicts_impossible_relationships = check_impossible_relationships(G, scene_graph)

    return (
        conflicts_corner
        + conflicts_room_layout
        + conflicts_one_parent
        + conflicts_impossible_relationships
        + conflicts_wall
    )

def get_size_conflicts(G, scene_graph, user_input, room_priors, verbose=False):
    """
    Identifies conflicts related to object sizes in the scene graph.

    Args:
        G (nx.DiGraph): The directed acyclic graph representing the scene.
        scene_graph (list): The list of objects in the scene graph.
        user_input (dict): User-provided inputs and preferences.
        room_priors (list): List of room prior constraints.
        verbose (bool): Flag to enable detailed logging.

    Returns:
        list: A list of size-related conflicts in the graph.
    """
    conflicts_size = check_size_conflicts(G, scene_graph, user_input, room_priors, verbose)
    return conflicts_size


def preprocess_scene_graph(scene_graph):
    """
    Cleans and preprocesses the scene graph to correct invalid or misplaced relationships.

    Args:
        scene_graph (list): The list of objects in the scene graph.

    Returns:
        list: The preprocessed scene graph.
    """
    valid_object_ids = {obj["new_object_id"] for obj in scene_graph}

    for obj in scene_graph:
        # Remove "middle of the room" if the object is not on the floor
        if not obj.get("is_on_the_floor", True):
            obj["placement"]["room_layout_elements"] = [
                elem for elem in obj["placement"].get("room_layout_elements", [])
                if elem["layout_element_id"] != "middle of the room"
            ]

        # Update invalid "in the corner" relationships
        for elem in obj["placement"].get("room_layout_elements", []):
            if elem["preposition"] == "in the corner" and elem["layout_element_id"] in ["middle of the room", "ceiling"]:
                elem["preposition"] = "on"

        # Validate object-to-object relationships
        obj["placement"]["objects_in_room"] = [
            elem for elem in obj["placement"].get("objects_in_room", [])
            if elem["object_id"] in valid_object_ids
        ]

    return scene_graph



def build_graph(scene_graph):
    """
    Constructs a directed acyclic graph (DAG) from the scene graph.

    Args:
        scene_graph (list): The list of objects in the scene graph.

    Returns:
        nx.DiGraph: The constructed graph.
    """
    G = nx.DiGraph()

    for obj in scene_graph:
        # Add object node
        G.add_node(obj["new_object_id"])

        # Add edges for object-to-object relationships
        for constraint in obj["placement"].get("objects_in_room", []):
            if constraint["object_id"] not in G.nodes:
                G.add_node(constraint["object_id"])
            G.add_edge(
                constraint["object_id"],
                obj["new_object_id"],
                preposition=constraint.get("preposition", ""),
                adjacency=constraint.get("is_adjacent", True),
            )

    return G


def find_room_layout_conflicts(G, scene_graph):
    """
    Identifies layout conflicts in the scene graph by checking if an object
    has parents with inconsistent room layout assignments.

    Args:
        G (nx.DiGraph): Directed graph representing the scene relationships.
        scene_graph (list): List of objects with attributes like placement and relationships.

    Returns:
        list: A list of conflict descriptions as strings.
    """

    conflicts = []

    # Obtain a topological order of nodes for processing
    topological_order = list(nx.topological_sort(G))
    node_layout = dict(G.nodes(data=True))  # Dictionary to store node layout information

    for node in topological_order:
        # Skip nodes representing room layout elements
        if node not in ROOM_LAYOUT_ELEMENTS:
            parents = list(G.predecessors(node))

            # Process only if the node has parents
            if parents:
                # Collect layout information of all parents
                parents_room_layout = [node_layout[p] for p in parents]
                different_parent_room_layout = False

                # Compare each parent's layout with the first parent's layout
                for p_layout in parents_room_layout[1:]:
                    # Determine if layouts are inconsistent
                    if isinstance(p_layout, list):
                        different_parent_room_layout = (
                            p_layout != parents_room_layout[0] if isinstance(parents_room_layout[0], list)
                            else parents_room_layout[0] not in p_layout
                        )
                    elif isinstance(p_layout, str):
                        different_parent_room_layout = (
                            p_layout != parents_room_layout[0] if isinstance(parents_room_layout[0], str)
                            else p_layout not in parents_room_layout[0]
                        )
                    elif isinstance(p_layout, dict):
                        different_parent_room_layout = (
                            p_layout != parents_room_layout[0] if isinstance(parents_room_layout[0], dict)
                            else p_layout not in parents_room_layout[0]
                        )

                    # Stop further checks if a difference is found
                    if different_parent_room_layout:
                        break

                # Handle detected layout conflicts
                if different_parent_room_layout:
                    # Skip conflict if all parents' relationships are "in the corner" or include "ceiling"
                    if not all(G[p][node]["weight"]["preposition"] == "in the corner" for p in parents) and \
                       not any(p == "ceiling" for p in parents):
                        conflict_string = (
                            f"The object {node} cannot have the parents {parents} at the same time! Eliminate one."
                        )
                        conflict_string += f"\nObject to reposition: {get_object_from_scene_graph(node, scene_graph)}"
                        conflicts.append(conflict_string)
                else:
                    # No conflict; assign the layout of the first parent
                    node_layout[node] = parents_room_layout[0]
            else:
                # Assign an empty layout if there are no parents
                node_layout[node] = {}

        else:
            # Assign layout for room layout elements
            node_layout[node] = node

    return conflicts

def remove_unnecessary_edges(G):
    """
    Removes unnecessary edges from the graph, prioritizing corner relationships
    over other types of relationships. It also resolves cycles in the graph
    to ensure it remains a Directed Acyclic Graph (DAG).

    Args:
        G (nx.DiGraph): Directed graph representing the scene relationships.

    Returns:
        nx.DiGraph: Updated graph with unnecessary edges removed.
    """

    # Resolve cycles in the graph
    if not nx.is_directed_acyclic_graph(G):
        print("Cycle detected in graph, attempting to break cycles.")
        cycles = list(nx.simple_cycles(G))
        for cycle in cycles:
            if len(cycle) > 1:
                # Break cycle by removing one edge
                edge_to_remove = (cycle[0], cycle[1])
                if G.has_edge(*edge_to_remove):
                    print(f"Removing edge {edge_to_remove} to break cycle")
                    G.remove_edge(*edge_to_remove)
                else:
                    print(f"DEBUG: Edge {edge_to_remove} already removed.")
            else:
                # Handle self-loop case
                print(f"Removing self-loop on node {cycle[0]}")
                if G.has_edge(cycle[0], cycle[0]):
                    G.remove_edge(cycle[0], cycle[0])

    # Process nodes in topological order
    topological_order = list(nx.topological_sort(G))

    for node in topological_order:
        if node not in ROOM_LAYOUT_ELEMENTS:
            parents = list(G.predecessors(node))
            # Check for "in the corner" relationships
            if any(G[p][node]["weight"]["preposition"] == "in the corner" for p in parents):
                if len(parents) > 2:
                    # Remove non-corner relationships
                    for p in parents:
                        if G[p][node]["weight"]["preposition"] != "in the corner":
                            print(f"Removing edge {p} -> {node} with preposition {G[p][node]['weight']['preposition']}")
                            G.remove_edge(p, node)

    return G


def handle_under_prepositions(G, scene_graph):
    """
    Removes objects that are under another object unless the object is thin.
    If an object under another is not thin, it and its child nodes are removed
    from the scene graph and the graph.

    Args:
        G (nx.DiGraph): Directed graph representing the scene relationships.
        scene_graph (list): List of objects with attributes like placement and relationships.

    Returns:
        tuple: Updated graph (nx.DiGraph) and scene graph (list).
    """

    nodes = G.nodes()
    nodes_to_remove = []

    # Identify nodes to remove
    for node in nodes:
        incoming_e = list(G.in_edges(node, data=True))
        outgoing_e = list(G.out_edges(node, data=True))
        # Check if the node has an "under" relationship
        under_obj = any([e[2]["weight"]["preposition"] == "under" for e in incoming_e])
        if under_obj:
            obj = get_object_from_scene_graph(node, scene_graph)
            if not is_thin_object(obj):
                # Mark the node and its children for removal
                nodes_to_remove.append(node)
                for e in outgoing_e:
                    nodes_to_remove.append(e[1])

    # Remove identified nodes from the graph and scene graph
    for node in nodes_to_remove:
        print("Removing node: ", node)
        scene_graph = [x for x in scene_graph if x["new_object_id"] != node]
        if node in G.nodes():
            G.remove_node(node)

    return G, scene_graph


def check_corner_relationships(G, scene_graph):
    """
    Identifies conflicts in corner relationships within the scene graph.

    This function checks whether multiple objects are assigned to the same corner
    or if objects with "corner" relationships lack the required two wall parents.
    It also identifies vacant corners for potential resolution of conflicts.

    Args:
        G (nx.DiGraph): Directed graph representing the scene relationships.
        scene_graph (list): List of objects in the scene with placement attributes.

    Returns:
        list: A list of conflict strings describing corner relationship issues.
    """

    def find_corner_vacancy():
        """
        Finds vacant corners by identifying corners not occupied by any objects.

        Returns:
            list: List of vacant corners.
        """
        corners = [("south_wall", "west_wall"), ("south_wall", "east_wall"),
                   ("north_wall", "west_wall"), ("north_wall", "east_wall")]
        occupied_corners = []

        # Identify occupied corners
        for wall_1, wall_2 in corners:
            for node in nx.topological_sort(G):
                if node not in ROOM_LAYOUT_ELEMENTS:
                    parents = list(G.predecessors(node))
                    if wall_1 in parents and wall_2 in parents:
                        occupied_corners.append((wall_1, wall_2))

        # Return unoccupied corners
        return list(set(corners) - set(occupied_corners))

    def find_corner_occupancy():
        """
        Maps each corner to the list of objects occupying it.

        Returns:
            dict: Dictionary where keys are corners and values are lists of objects.
        """
        corners = [("south_wall", "west_wall"), ("south_wall", "east_wall"),
                   ("north_wall", "west_wall"), ("north_wall", "east_wall")]
        occupied_corners = {corner: [] for corner in corners}

        # Identify objects occupying each corner
        for wall_1, wall_2 in corners:
            for node in nx.topological_sort(G):
                if node not in ROOM_LAYOUT_ELEMENTS:
                    parents = list(G.predecessors(node))
                    if wall_1 in parents and wall_2 in parents:
                        occupied_corners[(wall_1, wall_2)].append(node)

        return occupied_corners

    topological_order = list(nx.topological_sort(G))
    conflicts = []

    # Check for conflicts in corner occupancy
    corner_occupancy = find_corner_occupancy()
    for corner, occupants in corner_occupancy.items():
        if len(occupants) > 1:
            # More than one object assigned to the same corner
            conflict_string = (
                f"The corner {corner[0].split('_')[0]}-{corner[1].split('_')[0]} is occupied by more than one object: {occupants}. "
                "Move one of them to another vacant corner."
            )
            conflict_string += "\nVacant corners: " + str(find_corner_vacancy())
            conflicts.append(conflict_string)

    # Check for objects with "corner" relationships missing required parents
    for node in topological_order:
        if node not in ROOM_LAYOUT_ELEMENTS:
            parents = list(G.predecessors(node))
            if any([G[p][node]["weight"]["preposition"] == "in the corner" for p in parents]):
                if len(parents) == 1:
                    # Object in a corner relationship has only one parent
                    vacant_corners = find_corner_vacancy()
                    vacant_corners = [f"{c[0].split('_')[0]}-{c[1].split('_')[0]} corner" for c in vacant_corners]
                    conflict_string = (
                        f"Corner relationship for {node} has only {len(parents)} parent, add another wall to the relationship. "
                        f"\nCurrent vacant corners: {vacant_corners}"
                    )
                    conflict_string += "\nObject to reposition: " + str(get_object_from_scene_graph(node, scene_graph))
                    conflicts.append(conflict_string)

    return conflicts


directional_preps = ["in front of", "left of", "behind", "right of"]

def check_corner_relationship_impossibilities(G, scene_graph):
    """
    Identifies conflicts in corner relationships where objects are positioned
    relative to corner parents in ways that are geometrically impossible.

    This function evaluates relationships such as "in front of" or "left of"
    between objects and their corner parents, ensuring they align with valid
    spatial arrangements based on parent rotation and scene graph constraints.

    Args:
        G (nx.DiGraph): Directed graph representing scene relationships.
        scene_graph (list): List of objects with placement details.

    Returns:
        list: A list of conflict strings describing impossible corner relationships.
    """

    conflicts = []

    # Define impossible directional relationships for walls
    wall_impossible_preps = {
        "south_wall": "behind",
        "north_wall": "in front of",
        "west_wall": "left of",
        "east_wall": "right of"
    }

    # Process nodes in topological order
    topological_order = list(nx.topological_sort(G))
    for node in topological_order:
        if node not in ROOM_LAYOUT_ELEMENTS:
            # Get parents excluding room layout elements
            parents_raw = list(G.predecessors(node))
            parents = list(filter(lambda x: x not in ROOM_LAYOUT_ELEMENTS, parents_raw))

            # Get rotation values for each parent
            parents_rot = [
                get_rotation(next((x for x in scene_graph if x["new_object_id"] == p), None), scene_graph)
                for p in parents
            ]

            # Check each parent's spatial relationship
            for p, r in zip(parents, parents_rot):
                # Identify corner parents
                p_parent = list(G.predecessors(p))
                corners = [
                    p_p for p_p in p_parent
                    if G[p_p][p]["weight"]["preposition"] == "in the corner"
                ]

                # Skip if the parent is not associated with two walls (not in a corner)
                if len(corners) != 2:
                    continue

                # Compute impossible prepositions for the parent
                impossible_preps = []
                for p_p in corners:
                    corner_name = f"{corners[0].split('_')[0]}-{corners[1].split('_')[0]} corner"
                    impossible_prep = wall_impossible_preps[p_p]

                    # Adjust the impossible preposition based on the parent's rotation
                    idx = directional_preps.index(impossible_prep)
                    rotated_idx = int((idx + (r // 90)) % len(directional_preps))
                    impossible_prep = directional_preps[rotated_idx]
                    impossible_preps.append(impossible_prep)

                # Check if the current relationship is impossible
                if G[p][node]["weight"]["preposition"] in impossible_preps:
                    # Construct the conflict description
                    conflict_string = [
                        f"The object {node} cannot be {G[p][node]['weight']['preposition']} the object {p} as it would be placed out of bounds.",
                        f"The {impossible_preps[0]} and {impossible_preps[1]} relationships with {p} are out of bounds.",
                        f"Find another relationship for {node} either with {p}, on the {corners[0]} or on the {corners[1]}!",
                        "IMPORTANT: You can only have one relationship in the new scene graph!",
                    ]
                    conflict_string = "\n".join(conflict_string)

                    # Add context to the conflict description
                    conflict_string += f"The object {p} is on the {corner_name}. "
                    conflict_string += " ".join([
                        f"{p} has the object {edge[1]} {edge[2]['weight']['preposition']} it."
                        for edge in G.out_edges(p, data=True)
                        if edge[1] != node and edge[2]["weight"]["adjacency"]
                    ])
                    conflict_string += "\nObject to reposition: " + str(get_object_from_scene_graph(node, scene_graph))
                    conflicts.append(conflict_string)

    return conflicts


def check_wall_relationship_impossibilities(G, scene_graph):
    """
    Identifies conflicts in relationships where objects are positioned relative
    to walls in ways that are geometrically impossible.

    This function evaluates directional relationships (e.g., "in front of", "behind") 
    between objects and walls, ensuring they align with valid spatial arrangements 
    based on the wall's rotation and position.

    Args:
        G (nx.DiGraph): Directed graph representing the scene relationships.
        scene_graph (list): List of objects with placement details.

    Returns:
        list: A list of conflict strings describing impossible wall relationships.
    """

    conflicts = []

    # Define impossible directional relationships for walls
    wall_impossible_preps = {
        "south_wall": "behind",
        "north_wall": "in front of",
        "west_wall": "left of",
        "east_wall": "right of"
    }

    # Process nodes in topological order
    topological_order = list(nx.topological_sort(G))
    for node in topological_order:
        if node not in ROOM_LAYOUT_ELEMENTS:
            # Get parents excluding room layout elements
            parents_raw = list(G.predecessors(node))
            parents = list(filter(lambda x: x not in ROOM_LAYOUT_ELEMENTS, parents_raw))

            # Get rotation values for each parent
            parents_rot = [
                get_rotation(next((x for x in scene_graph if x.get("new_object_id") == p), None), scene_graph)
                for p in parents
            ]

            # Check spatial relationship for each parent
            for p, r in zip(parents, parents_rot):
                # Identify wall parents
                p_parent_raw = list(G.predecessors(p))
                p_parent = list(filter(lambda x: x in wall_impossible_preps.keys(), p_parent_raw))

                # Get walls the parent is associated with
                walls = [
                    p_p for p_p in p_parent
                    if G[p_p][p]["weight"]["preposition"] == "on"
                ]

                # Check for impossible relationships with walls
                for p_p in walls:
                    impossible_prep = wall_impossible_preps[p_p]

                    # Adjust impossible preposition based on the parent's rotation
                    idx = directional_preps.index(impossible_prep)
                    rotated_idx = int((idx + (r // 90)) % len(directional_preps))
                    impossible_prep = directional_preps[rotated_idx]

                    # If the relationship is impossible, record the conflict
                    if G[p][node]["weight"]["preposition"] == impossible_prep:
                        conflict_string = [
                            f"The object {node} cannot be {G[p][node]['weight']['preposition']} the object {p} as it would be placed out of bounds.",
                            f"The {impossible_prep} relationship is invalid. Find another relationship for {node} either with {p}, or on the {p_p}.",
                            f"This relationship must be exclusive. IMPORTANT: you can only have one relationship in the updated scene graph!"
                        ]
                        conflict_string = "\n".join(conflict_string)

                        # Add context to the conflict description
                        conflict_string += f"The object {p} is on the {p_p}. "
                        conflict_string += " ".join([
                            f"{p} has the object {edge[1]} {edge[2]['weight']['preposition']} it."
                            for edge in G.out_edges(p, data=True)
                            if edge[1] != node and edge[2]["weight"]["adjacency"]
                        ])
                        conflict_string += "\nObject to reposition: " + str(get_object_from_scene_graph(node, scene_graph))
                        conflicts.append(conflict_string)

    return conflicts


def validate_scene_graph(scene_graph):
    """
    Validates the scene graph by ensuring all object references in relationships
    exist within the scene graph.

    Args:
        scene_graph (list): A list of objects with their placements and relationships.

    Modifies:
        Removes invalid relationships where an object references another object 
        not present in the scene graph.
    """
    object_ids = {obj["new_object_id"] for obj in scene_graph}

    for obj in scene_graph:
        if "placement" in obj and "objects_in_room" in obj["placement"]:
            # Check relationships and remove invalid references
            for relation in list(obj["placement"]["objects_in_room"]):
                if relation["object_id"] not in object_ids:
                    print(f"DEBUG: Object '{relation['object_id']}' referenced in relationships of '{obj['new_object_id']}' is not present in the scene graph.")
                    obj["placement"]["objects_in_room"].remove(relation)


def check_impossible_relationships(G, scene_graph):
    """
    Identifies conflicts where spatial relationships between objects in the graph
    are geometrically or logically impossible.

    Args:
        G (nx.DiGraph): Directed graph representing the relationships in the scene.
        scene_graph (list): List of objects with placement and metadata.

    Returns:
        list: A list of conflict strings describing impossible relationships.
    """
    conflicts = []
    topological_order = list(nx.topological_sort(G))

    # Process each node in topological order
    for node in topological_order:
        if node not in ROOM_LAYOUT_ELEMENTS:
            # Retrieve parents and children of the current node
            parents_raw = list(G.predecessors(node))
            parents = list(filter(lambda x: x not in ROOM_LAYOUT_ELEMENTS, parents_raw))
            children = list(G.successors(node))

            # Find the object data for the current node
            node_obj = next((x for x in scene_graph if x.get("new_object_id") == node), None)
            if node_obj is None:
                print(f"DEBUG: Object '{node}' not found in scene graph.")
                continue

            # Get the rotation of the current object
            node_rot = get_rotation(node_obj, scene_graph)

            # Check adjacency and exclusivity between parents and children
            for p in parents:
                edge_data = G[p][node].get("weight", {})
                prep = edge_data.get("preposition")
                adj = edge_data.get("adjacency")

                # Validate directional adjacency
                if prep in directional_preps and adj:
                    idx = directional_preps.index(prep)
                    rotated_idx = int((idx + (node_rot // 90)) % len(directional_preps))
                    impossible_prep = directional_preps[(rotated_idx + 2) % len(directional_preps)]

                    # Check for conflicting relationships with children
                    for c in children:
                        child_edge_data = G[node][c].get("weight", {})
                        if (child_edge_data.get("preposition") == impossible_prep
                                and child_edge_data.get("adjacency")):
                            conflict_string = (
                                f"The object {c} cannot be {child_edge_data['preposition']} of the object {node} "
                                f"since the object {p} occupies that spatial position. "
                                f"Find another relationship for {c} with {node}!"
                            )
                            conflict_string += "\nObject to reposition: " + str(get_object_from_scene_graph(c, scene_graph))
                            conflicts.append(conflict_string)

    return conflicts
  
def get_cluster_size(node, G, scene_graph):
    """
    Calculates the size of a cluster of objects connected to a given node in the graph,
    including directional constraints on spatial dimensions.

    Args:
        node (str): The node ID of the object in the graph.
        G (nx.DiGraph): Directed graph representing object relationships.
        scene_graph (list): List of objects with placement and size metadata.

    Returns:
        tuple: 
            - size_constraint (dict): Maximum size constraints in directional relationships 
              (e.g., "left of", "right of", "in front of", "behind").
            - children_objs (set): Set of descendant nodes (children) within the cluster.
    """
    # Retrieve object data for the given node
    node_obj = get_object_from_scene_graph(node, scene_graph)
    try:
        node_obj_rot = get_rotation(node_obj, scene_graph)
    except Exception as e:
        print(f"Error processing node: {node}")
        raise ValueError("Failed to retrieve object rotation!") from e

    # Get outgoing edges from the current node
    outgoing_e = list(G.out_edges(node, data=True))
    outgoing_nodes = [edge[1] for edge in outgoing_e]

    # Sort outgoing nodes based on topological order
    topological_order_reversed = list(reversed(list(nx.topological_sort(G))))
    topological_outgoing_nodes = [n for n in topological_order_reversed if n in outgoing_nodes]
    outgoing_e_sorted = sorted(outgoing_e, key=lambda x: topological_outgoing_nodes.index(x[1]))

    # Initialize size constraints and set for tracking descendant nodes
    size_constraint = {"left of": 0.0, "right of": 0.0, "behind": 0.0, "in front of": 0.0}
    children_objs = set()

    # Process each outgoing edge
    for edge in outgoing_e_sorted:
        # Skip if the child object has already been processed
        if edge[1] in children_objs:
            continue

        # Skip if the preposition is not directional
        if edge[2]["weight"]["preposition"] not in directional_preps:
            continue

        # Retrieve the child object and its rotation
        edge_obj = get_object_from_scene_graph(edge[1], scene_graph)
        children_objs.add(edge[1])
        edge_obj_rot = get_rotation(edge_obj, scene_graph)

        # Calculate the rotational difference between parent and child
        rot_diff = abs(node_obj_rot - edge_obj_rot)

        # Extract preposition and adjacency data
        prep = edge[2]["weight"]["preposition"]
        adj = edge[2]["weight"]["adjacency"]

        # Determine the key for size constraint based on direction
        direction_check = lambda diff, prep: (
            (diff % 180 == 0 and prep in ["left of", "right of"]) or 
            (diff % 90 == 0 and prep in ["in front of", "behind"])
        )
        size_constraint_key = "length" if direction_check(rot_diff, prep) else "width"
        side_to_add = ("left of", "right of") if size_constraint_key == "length" else ("in front of", "behind")

        # Get the size of the current object along the calculated side
        size_constraint_value = edge_obj["size_in_meters"][size_constraint_key]

        # Recursively calculate the cluster size for the child object
        edge_cluster_size, edge_children = get_cluster_size(edge[1], G, scene_graph)
        children_objs = children_objs.union(edge_children)

        # Update the size constraint based on the preposition and adjacency
        constraints = ["left of", "right of", "in front of", "behind"]
        value_to_add = size_constraint_value + edge_cluster_size[side_to_add[0]] + edge_cluster_size[side_to_add[1]]
        if prep in constraints:
            if adj:
                size_constraint[prep] = max(size_constraint[prep], value_to_add)
            else:
                size_constraint[prep] += value_to_add

    return size_constraint, children_objs


def check_size_conflicts(G, scene_graph, user_input, room_priors, verbose=False):
    """
    Checks for size conflicts in the scene graph, ensuring objects are not placed
    in locations where the size constraints would be violated.

    Args:
        G (nx.DiGraph): Directed graph representing the spatial relationships between objects.
        scene_graph (list): List of objects with placement, size, and rotation metadata.
        user_input (dict): User preferences influencing object importance or room functionality.
        room_priors (list): Information about room layout and dimensions.
        verbose (bool): If True, additional debug information is printed.

    Returns:
        list: List of dictionaries describing size conflicts.
    """
    conflicts = []
    topological_order_reversed = list(reversed(list(nx.topological_sort(G))))

    if verbose:
        print("Topological order (reversed):", topological_order_reversed)

    # Iterate through nodes in topological order to check size conflicts
    for node in topological_order_reversed:
        if node not in ROOM_LAYOUT_ELEMENTS:
            # Retrieve object data
            node_obj = get_object_from_scene_graph(node, scene_graph)
            outgoing_edges = list(G.out_edges(node, data=True))

            # Initialize size constraints
            size_constraint = {"left of": 0.0, "right of": 0.0, "behind": 0.0, "in front of": 0.0, "on": [0.0, 0.0]}

            for edge in outgoing_edges:
                edge_obj = get_object_from_scene_graph(edge[1], scene_graph)
                prep = edge[2]["weight"]["preposition"]
                adj = edge[2]["weight"]["adjacency"]
                if prep not in size_constraint and prep != "on":
                    continue

                # Handle adjacency and size updates
                if adj and prep in ["left of", "right of", "behind", "in front of"]:
                    size_constraint[prep] += edge_obj["size_in_meters"]["length" if prep in ["in front of", "behind"] else "width"]
                elif adj and prep == "on":
                    size_constraint["on"][0] += edge_obj["size_in_meters"]["length"]
                    size_constraint["on"][1] += edge_obj["size_in_meters"]["width"]

            # Check conflicts for directional constraints
            for prep in ["in front of", "behind", "left of", "right of"]:
                dimension = "length" if prep in ["in front of", "behind"] else "width"
                if node_obj["size_in_meters"][dimension] < size_constraint[prep]:
                    conflicts.append({
                        "conflict_description": f"The {dimension} of {node} is too small to accommodate the object {prep} it.",
                        "new_object_id": node,
                        "nodes_to_consider": [edge[1] for edge in outgoing_edges if edge[2]["weight"]["preposition"] == prep],
                        "user_preference": user_input
                    })

            # Check conflicts for "on" constraints
            if node_obj["size_in_meters"]["length"] < size_constraint["on"][0] or \
               node_obj["size_in_meters"]["width"] < size_constraint["on"][1]:
                conflicts.append({
                    "conflict_description": f"The area of {node} is too small to accommodate all objects placed on it.",
                    "new_object_id": node,
                    "nodes_to_consider": [edge[1] for edge in outgoing_edges if edge[2]["weight"]["preposition"] == "on"],
                    "user_preference": user_input
                })

        elif node in ROOM_LAYOUT_ELEMENTS:
            # Handle size constraints for room layout elements
            node_obj = get_object_from_scene_graph(node, room_priors)
            node_obj_rot = get_rotation(node_obj, scene_graph)
            outgoing_edges = list(G.out_edges(node, data=True))
            outgoing_nodes = [edge[1] for edge in outgoing_edges]
            topological_outgoing_nodes = [
                n for n in topological_order_reversed if n in outgoing_nodes
            ]
            outgoing_edges_sorted = sorted(
                outgoing_edges, key=lambda x: topological_outgoing_nodes.index(x[1])
            )

            # Initialize size constraints for layout elements
            outgoing_set = set()
            size_constraint = 0.0 if node != "middle of the room" else (0.0, 0.0)

            # Process outgoing edges for layout elements
            for edge in outgoing_edges_sorted:
                if edge[1] in outgoing_set:
                    continue
                edge_obj = get_object_from_scene_graph(edge[1], scene_graph)
                if not edge_obj["is_on_the_floor"]:
                    continue
                edge_obj_rot = get_rotation(edge_obj, scene_graph)
                cluster_size, e_children = get_cluster_size(edge[1], G, scene_graph)
                rot_diff = abs(node_obj_rot - edge_obj_rot)
                constraint_key = (
                    ("length", "width") if rot_diff % 180 == 0 else ("width", "length")
                )
                side_to_add = (
                    ("left of", "right of") if constraint_key[0] == "length" 
                    else ("in front of", "behind")
                )

                outgoing_set.add(edge[1])
                outgoing_set.update(e_children)

                if node == "middle of the room":
                    x = (
                        edge_obj["size_in_meters"][constraint_key[0]] +
                        cluster_size.get(side_to_add[0][0], 0) +
                        cluster_size.get(side_to_add[0][1], 0)
                    )
                    size_constraint = (max(size_constraint[0], x), size_constraint[1])
                    y = (
                        edge_obj["size_in_meters"][constraint_key[1]] +
                        cluster_size.get(side_to_add[1][0], 0) +
                        cluster_size.get(side_to_add[1][1], 0)
                    )
                    size_constraint = (size_constraint[0], max(size_constraint[1], y))
                else:
                    size_constraint += (
                        edge_obj["size_in_meters"][constraint_key[0]] +
                        cluster_size.get(side_to_add[0][0], 0) +
                        cluster_size.get(side_to_add[0][1], 0)
                    )

            # Check layout element constraints
            if verbose:
                print(f"Size constraint for {node}: {size_constraint}!")
                print(f"Outgoing Set: {outgoing_set}")

            if node != "middle of the room":
                if node_obj["size_in_meters"]["length"] < size_constraint:
                    conflict_str = (
                        f"The length of the {node} is too small to accommodate "
                        f"all of the following objects on it: "
                    )
                    conflict_str += ", ".join(outgoing_set)
                    conflict_str += f"\nUser preference: {user_input}"
                    conflicts.append(conflict_str)
            else:
                if node_obj["size_in_meters"]["length"] < size_constraint[0]:
                    conflict_str = (
                        f"The length of the {node} is too small to accommodate "
                        f"all of the following objects on it: "
                    )
                    conflict_str += ", ".join(outgoing_set)
                    conflict_str += f"\nUser preference: {user_input}"
                    conflicts.append(conflict_str)
                if node_obj["size_in_meters"]["width"] < size_constraint[1]:
                    conflict_str = (
                        f"The width of the {node} is too small to accommodate "
                        f"all of the following objects on it: "
                    )
                    conflict_str += ", ".join(outgoing_set)
                    conflict_str += f"\nUser preference: {user_input}"
                    conflicts.append(conflict_str)

    return conflicts

def get_cluster_objects(scene_graph):
    """
    Groups objects in the scene graph into clusters based on their relationships.

    Args:
        scene_graph (list): List of objects with their placements and relationships.

    Returns:
        dict: A dictionary where keys are unique sets of relationships, and values are lists of object IDs that share the same relationships.
    """
    object_ids_by_scene_graph = {}

    for obj in scene_graph:
        # Skip thin objects, as they are not added to clusters
        if is_thin_object(obj):
            continue
        
        placement = obj.get("placement")
        if placement:
            # Combine objects-in-room and room-layout-elements relationships into a set
            edges = placement["objects_in_room"] + placement["room_layout_elements"]
            scene_graph_set = frozenset([tuple(sorted(x.items())) for x in edges])
            
            # Group objects with the same relationship set
            if scene_graph_set in object_ids_by_scene_graph:
                object_ids_by_scene_graph[scene_graph_set].append(obj["new_object_id"])
            else:
                object_ids_by_scene_graph[scene_graph_set] = [obj["new_object_id"]]

    # Filter out groups with only one object or no relationships
    object_ids_groups = {k: v for k, v in object_ids_by_scene_graph.items() if len(v) > 1 and len(k) > 0}

    return object_ids_groups


def get_object_from_scene_graph(obj_id, scene_graph):
    """
    Retrieves an object from the scene graph based on its ID.

    Args:
        obj_id (str): The unique ID of the object.
        scene_graph (list): The scene graph containing all objects.

    Returns:
        dict: The object dictionary if found, else None.
    """
    return next((x for x in scene_graph if x["new_object_id"] == obj_id), None)


def has_one_parent_and_one_child(tree):
    """
    Determines if all nodes in a tree have exactly one parent and one child.

    Args:
        tree (nx.DiGraph): A directed graph representing a tree.

    Returns:
        bool: True if all nodes have one parent and one child; False otherwise.
    """
    for node in tree.nodes():
        # Check the in-degree (parents) and out-degree (children) of each node
        if tree.in_degree(node) > 1 or tree.out_degree(node) > 1:
            return False
    return True

def find_edges_to_flip(tree):
        edges_to_flip = []
        for node in tree.nodes():
            if tree.in_degree(node) > 1 or tree.out_degree(node) > 1:
                # If a node has more than one parent or child, find the edges to flip
                for parent in list(tree.predecessors(node)):
                    if tree.in_degree(node) > 1:
                        edges_to_flip.append((parent, node))
                for child in list(tree.successors(node)):
                    if tree.out_degree(node) > 1:
                        edges_to_flip.append((node, child))
        return edges_to_flip

def flip_edges(tree, root_node, verbose=False):
    """
    Adjusts a directed graph (tree) to ensure each node has exactly one parent and one child
    by flipping edges and resolving cycles.

    Args:
        tree (nx.DiGraph): The directed graph to adjust.
        root_node (str): The root node of the tree.
        verbose (bool): If True, prints debug information.

    Returns:
        tuple: The modified tree and a dictionary indicating whether each edge was flipped.
    """
    flipped_edges = {}

    # Iteratively adjust the tree structure
    while not has_one_parent_and_one_child(tree):
        # Identify edges that need flipping
        edges_to_flip = find_edges_to_flip(tree)
        if verbose:
            print(f"Edges to flip: {edges_to_flip}")
        
        if not edges_to_flip:
            break  # Exit if no more edges can be flipped

        # Flip the first edge in the list
        edge_to_flip = edges_to_flip[0]
        tree.remove_edge(*edge_to_flip)
        tree.add_edge(edge_to_flip[1], edge_to_flip[0])

        # Check if the tree now meets the parent-child constraint
        if has_one_parent_and_one_child(tree):
            flipped_edges[edge_to_flip] = True
        else:
            # Revert the flip if the tree is still invalid
            tree.remove_edge(edge_to_flip[1], edge_to_flip[0])
            tree.add_edge(edge_to_flip[0], edge_to_flip[1])

    # Remove remaining cycles in the graph
    while len(list(nx.simple_cycles(tree))) > 0:
        cycles = list(nx.simple_cycles(tree))
        for cycle in cycles:
            # Remove an edge from the cycle to break it
            tree.remove_edge(cycle[-1], cycle[0])
            if verbose:
                print(f"Removed cycle edge: {cycle[-1]} -> {cycle[0]}")

    # Mark all edges in the tree, indicating if they were flipped or not
    for edge in tree.edges():
        if edge not in flipped_edges:
            flipped_edges[edge] = False

    return tree, flipped_edges


def flip_edges_to_binary_tree(graph, root_node, verbose=False):
    """
    Converts a directed graph into a binary tree rooted at the specified node by flipping edges
    and ensuring that the graph remains connected and acyclic.

    Args:
        graph (nx.DiGraph): The input directed graph.
        root_node (str): The root node of the binary tree.
        verbose (bool): If True, provides detailed logs during execution.

    Returns:
        tuple: A binary tree (as a directed graph) and a dictionary indicating whether each edge was flipped.
    """
    tree = nx.DiGraph(graph)
    flipped_edges = {}

    if verbose:
        print(f"Root Node: {root_node}")

    # Ensure the graph is weakly connected before proceeding
    if not nx.is_weakly_connected(tree):
        print("The input graph is not weakly connected. Aborting binary tree conversion.")
        return None

    # Iteratively adjust edges to convert the graph into a binary tree
    while not is_binary_tree(tree, root_node):
        non_tree_edges = find_non_tree_edges(tree, root_node)
        if verbose:
            print(f"Non-tree edges: {non_tree_edges}")

        if not non_tree_edges:
            break  # No more edges to flip

        # Flip the first non-tree edge
        edge_to_flip = non_tree_edges[0]
        tree.remove_edge(*edge_to_flip)
        tree.add_edge(edge_to_flip[1], edge_to_flip[0])

        # Validate the new structure
        if (edge_to_flip[1], edge_to_flip[0]) not in find_non_tree_edges(tree, root_node):
            flipped_edges[edge_to_flip] = True
        else:
            # If the edge is still invalid, delete it entirely
            tree.remove_edge(edge_to_flip[1], edge_to_flip[0])
            if verbose:
                print(f"Removed edge: {edge_to_flip[1]} -> {edge_to_flip[0]} (Invalid)")

    # Mark remaining edges as not flipped
    for edge in tree.edges():
        if edge not in flipped_edges:
            flipped_edges[edge] = False

    return tree, flipped_edges


def is_binary_tree(tree, root_node):
    """
    Checks if the given directed graph is a binary tree rooted at the specified node.

    Args:
        tree (nx.DiGraph): The directed graph to check.
        root_node (str): The root node of the tree.

    Returns:
        bool: True if the graph is a binary tree, False otherwise.
    """
    # Ensure the graph is a tree (acyclic and connected)
    if not nx.is_tree(tree):
        return False

    # Check if the in-degree of every node (except root) is at most 1
    for node in tree.nodes():
        if node != root_node and tree.in_degree(node) > 1:
            return False

    # Check if each node has at most two children (out-degree <= 2)
    for node in tree.nodes():
        if tree.out_degree(node) > 2:
            return False

    return True


def remove_edges_with_connectivity(dag, verbose=False):
    """
    Recursively removes edges with weight 0 while ensuring the graph remains connected.

    Args:
        dag (nx.DiGraph): The directed acyclic graph to process.
        verbose (bool): If True, prints the edges being removed.

    Returns:
        nx.DiGraph: The modified graph with certain edges removed.
    """
    edge_to_remove = None
    for edge in dag.edges(data=True):
        if edge[2]["weight"] == 0:
            temp_dag = dag.copy()  # Make a copy of the original DAG
            temp_dag.remove_edge(edge[0], edge[1])  # Remove the edge
            undirected = temp_dag.to_undirected()
            if nx.is_connected(undirected):
                edge_to_remove = (edge[0], edge[1])
                break

    if verbose and edge_to_remove:
        print("Edge to remove: ", edge_to_remove)

    if edge_to_remove:
        dag.remove_edge(*edge_to_remove)
        return remove_edges_with_connectivity(dag, verbose)

    return dag


def find_non_tree_edges(graph, root_node):
    """
    Identifies edges in the graph that do not conform to the binary tree structure.

    Args:
        graph (nx.DiGraph): The input directed graph.
        root_node (str): The root node of the binary tree.

    Returns:
        list: A list of edges that violate the binary tree structure.
    """
    non_tree_edges = []
    for edge in graph.edges():
        temp_graph = nx.DiGraph(graph)
        temp_graph.remove_edge(*edge)
        if (
            not nx.is_weakly_connected(temp_graph) or 
            not nx.is_tree(temp_graph) or 
            not nx.has_path(G=temp_graph, source=edge[0], target=root_node)
        ):
            non_tree_edges.append(edge)

    return non_tree_edges

def clean_and_extract_edges(relationships, parent_id, verbose=False):
    """
    Cleans and extracts edges from the given relationships to construct a binary tree.

    Args:
        relationships (dict): Contains parent and children relationships.
        parent_id (str): The ID of the parent node.
        verbose (bool): If True, enables detailed debugging and visualization.

    Returns:
        tuple: Edges of the binary tree and a dictionary of flipped edges.
    """
    # Initialize a directed acyclic graph (DAG)
    dag = nx.DiGraph()

    # Add nodes and edges based on relationships
    for obj in relationships["children_objects"]:
        if obj["name_id"] != parent_id:
            dag.add_node(obj["name_id"])
    for obj in relationships["children_objects"]:
        if obj["name_id"] != parent_id:
            for rel in obj["placement"]["children_objects"]:
                if rel["name_id"] != parent_id:
                    dag.add_edge(obj["name_id"], rel["name_id"], weight=int(rel["is_adjacent"]))

    # Remove cycles from the DAG
    if verbose:
        print("Simple cycles: ", list(nx.simple_cycles(dag)))
    while len(list(nx.simple_cycles(dag))) > 0:
        cycles = list(nx.simple_cycles(dag))
        dag.remove_edge(cycles[0][-1], cycles[0][0])

    # Optional visualization of the original graph
    if verbose:
        pos_original = nx.spring_layout(dag)
        plt.figure(figsize=(10, 5))
        nx.draw(dag, pos_original, with_labels=True, font_weight="bold", node_size=700, arrowsize=20)
        plt.title("Original Graph")
        plt.show()

    # Remove edges while maintaining connectivity
    dag = remove_edges_with_connectivity(dag, verbose)

    if verbose:
        print("Edges remaining: ", dag.edges(data=True))

    # Convert the DAG into a binary tree
    binary_tree, flipped_edges = flip_edges(dag, list(dag.nodes())[0], verbose)
    if binary_tree and verbose:
        # Visualize the binary tree
        pos_binary_tree = nx.spring_layout(binary_tree)
        plt.figure(figsize=(15, 7))
        plt.subplot(121)
        nx.draw(dag, pos_original, with_labels=True, font_weight="bold", node_size=700, arrowsize=20)
        plt.title("Original Graph")

        plt.subplot(122)
        nx.draw(binary_tree, pos_binary_tree, with_labels=True, font_weight="bold", node_size=700, arrowsize=20)
        plt.title("Binary Tree")
        plt.show()

    return binary_tree.edges(), flipped_edges


def create_empty_image_with_boxes(image_size, boxes):
    """
    Creates a blank image and overlays rectangular boxes representing objects.

    Args:
        image_size (tuple): Dimensions of the image (height, width).
        boxes (list): A list of tuples containing box dimensions and labels.

    Returns:
        np.ndarray: Image with drawn boxes.
    """
    img = np.zeros((image_size[0], image_size[1], 3), dtype=np.uint8)

    for box in boxes:
        try:
            x, y, w, h, r, label = box
            x, y, w, h = int(x * 100), int(y * 100), int(w * 100), int(h * 100)

            # Adjust for rotation
            if np.isclose(r, 90.0) or np.isclose(r, 270.0):
                x, y = int(x - h / 2), int(y - w / 2)
                cv2.rectangle(img, (x, y), (x + h, y + w), (0, 255, 0), 2)
            else:
                x, y = int(x - w / 2), int(y - h / 2)
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Add labels
            cv2.putText(img, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        except Exception as e:
            print(f"[Error] Failed to draw box {box}: {e}")

    return img



def get_visualization(scene_graph, room_priors=None, output_path="scene_graph_visualization.png"):
    """
    Visualizes the scene graph by creating an image with object boxes and labels.

    Args:
        scene_graph (list): The scene graph containing object data.
        room_priors (dict, optional): Additional room configuration, if needed.
        output_path (str): Path to save the visualization image.

    Returns:
        None
    """
    visual_scene_graph = [
        (
            item["position"]["x"] + 2.0,
            item["position"]["y"] + 2.0,
            item["size_in_meters"]["length"],
            item["size_in_meters"]["width"],
            item["rotation"]["z_angle"],
            item["new_object_id"],
        )
        for item in scene_graph if "position" in item
    ]

    img = create_empty_image_with_boxes((800, 800), visual_scene_graph)
    try:
        cv2.imwrite(output_path, img)
        print(f"Visualization saved to {output_path}")
    except Exception as e:
        print(f"Failed to save visualization to {output_path}: {e}")



def calculate_overlap(box1, box2):
    """
    Calculate the overlap between two 3D bounding boxes.

    Args:
        box1 (tuple): Coordinates of the first box in the format (x_min, x_max, y_min, y_max, z_min, z_max).
        box2 (tuple): Coordinates of the second box in the same format.

    Returns:
        tuple or None: Overlapping region as a tuple (x_min, x_max, y_min, y_max, z_min, z_max),
                       or None if no overlap exists.
    """
    if box1 is None or box2 is None:
        return None

    # Compute overlap bounds
    x_min = max(box1[0], box2[0])
    x_max = min(box1[1], box2[1])
    y_min = max(box1[2], box2[2])
    y_max = min(box1[3], box2[3])
    z_min = max(box1[4], box2[4])
    z_max = min(box1[5], box2[5])

    # Check for overlap with a tolerance
    if x_min <= x_max + 1e-03 and y_min <= y_max + 1e-03 and z_min <= z_max + 1e-03:
        return (x_min, x_max, y_min, y_max, z_min, z_max)
    return None


def is_collision_3d(obj1, obj2, bbox_instead=False):
    """
    Determine whether two 3D objects collide based on their bounding boxes.

    Args:
        obj1 (dict): First object with position, rotation, and size.
        obj2 (dict or tuple): Second object, either as a dict or as a bounding box.
        bbox_instead (bool): Whether to treat obj2 as a bounding box.

    Returns:
        bool: True if the objects collide, False otherwise.
    """
    try:
        # Extract position, rotation, and size
        pos1, rot1, size1 = obj1["position"], obj1["rotation"]["z_angle"], obj1["size_in_meters"]
        if is_thin_object(obj1):
            return False

        if bbox_instead:
            # Treat obj2 as a bounding box
            pos2, rot2, size2 = (
                {"x": (obj2[1] + obj2[0]) / 2, "y": (obj2[3] + obj2[2]) / 2, "z": (obj2[5] + obj2[4]) / 2},
                0.0,
                {"length": obj2[1] - obj2[0], "width": obj2[3] - obj2[2], "height": obj2[5] - obj2[4]},
            )
        else:
            pos2, rot2, size2 = obj2["position"], obj2["rotation"]["z_angle"], obj2["size_in_meters"]
            if is_thin_object(obj2):
                return False
    except KeyError as e:
        print(f"KeyError: Missing key {e} in one of the objects. Skipping collision check.")
        return False

    def swap_dimensions_if_rotated(size, rotation):
        """Swap length and width if the object is rotated 90 or 270 degrees."""
        if np.isclose(rotation, 90.0) or np.isclose(rotation, 270.0):
            size["length"], size["width"] = size["width"], size["length"]

    def get_bounds(pos, size):
        """Calculate the bounds of an object given its position and size."""
        return (
            pos["x"] + size["length"] / 2,
            pos["x"] - size["length"] / 2,
            pos["y"] + size["width"] / 2,
            pos["y"] - size["width"] / 2,
            pos["z"] + size["height"] / 2,
            pos["z"] - size["height"] / 2,
        )

    def check_overlap(min1, max1, min2, max2):
        """Check if two ranges overlap."""
        return min1 < max2 and max1 > min2 and abs(min1 - max2) > 1e-3 and abs(max1 - min2) > 1e-3

    # Adjust dimensions for rotation
    swap_dimensions_if_rotated(size1, rot1)
    swap_dimensions_if_rotated(size2, rot2)

    # Calculate object bounds
    obj1_bounds = get_bounds(pos1, size1)
    obj2_bounds = get_bounds(pos2, size2)

    # Unpack bounds for comparison
    obj1_x_max, obj1_x_min, obj1_y_max, obj1_y_min, obj1_z_max, obj1_z_min = obj1_bounds
    obj2_x_max, obj2_x_min, obj2_y_max, obj2_y_min, obj2_z_max, obj2_z_min = obj2_bounds

    # Check for overlaps in x, y, and z dimensions
    x_check = check_overlap(obj1_x_min, obj1_x_max, obj2_x_min, obj2_x_max)
    y_check = check_overlap(obj1_y_min, obj1_y_max, obj2_y_min, obj2_y_max)
    z_check = check_overlap(obj1_z_min, obj1_z_max, obj2_z_min, obj2_z_max)

    return x_check and y_check and z_check


def get_depth(scene_graph):
    """
    Calculate the depth of each node in a directed acyclic graph (DAG) derived from the scene graph.

    Args:
        scene_graph (list): List of objects in the scene graph with their placements.

    Returns:
        dict: Dictionary with object IDs as keys and their respective depths as values.
    """
    G = nx.DiGraph()

    # Build the graph from the scene graph
    for obj in scene_graph:
        if obj["new_object_id"] not in G.nodes():
            G.add_node(obj["new_object_id"])
        obj_scene_graph = obj["placement"]

        for constraint in obj_scene_graph["room_layout_elements"]:
            if constraint["layout_element_id"] not in G.nodes():
                G.add_node(constraint["layout_element_id"])
            G.add_edge(constraint["layout_element_id"], obj["new_object_id"])

        for constraint in obj_scene_graph["objects_in_room"]:
            if constraint["object_id"] not in G.nodes():
                G.add_node(constraint["object_id"])
            G.add_edge(constraint["object_id"], obj["new_object_id"])

    # Perform a depth-first search (DFS) to calculate node depths
    visited = set()
    prior_ids = ["south_wall", "north_wall", "east_wall", "west_wall", "middle of the room", "ceiling"]
    start_nodes = [node for node in G.nodes() if node in prior_ids]
    all_nodes_depth = {}

    def dfs(node, depth):
        visited.add(node)
        all_nodes_depth[node] = depth
        for successor in G.successors(node):
            if successor not in visited:
                dfs(successor, depth + 1)
            elif successor in all_nodes_depth and all_nodes_depth[successor] < depth + 1:
                # Skip already visited nodes with smaller depth to avoid cycles
                continue
            else:
                all_nodes_depth[successor] = depth + 1

    for start_node in start_nodes:
        dfs(start_node, 0)

    # Filter out the prior IDs and return depth data
    all_nodes_depth = {k: v for k, v in all_nodes_depth.items() if k not in prior_ids}
    return all_nodes_depth


def get_possible_positions(object_id, scene_graph, room_dimensions):
    """
    Determine possible positions for an object based on its constraints in the scene graph.

    Args:
        object_id (str): The ID of the object to position.
        scene_graph (list): List of objects in the scene graph with their placements.
        room_dimensions (dict): Dimensions of the room.

    Returns:
        list: List of possible positions for the object.
    """
    obj = next(element for element in scene_graph if element.get("new_object_id") == object_id)
    obj_scene_graph = obj["placement"]
    rot = get_rotation(obj, scene_graph)
    obj["rotation"] = {"z_angle": rot}

    # Mapping of prepositions to corresponding constraint functions
    func_map = {
        "on": get_on_constraint,
        "under": get_under_constraint,
        "left of": get_left_of_constraint,
        "right of": get_right_of_constraint,
        "in front": get_in_front_constraint,
        "behind": get_behind_constraint,
        "above": get_above_constraint,
        "in the corner": get_in_corner_constraint,
        "in the middle of": get_on_constraint,
    }

    constraints = obj_scene_graph["room_layout_elements"] + obj_scene_graph["objects_in_room"]
    possible_positions = []

    # Process each constraint and determine possible positions
    for constraint in constraints:
        prep = constraint["preposition"]
        adjacency = constraint.get("is_adjacent", True)
        is_on_floor = obj["is_on_the_floor"]
        obj_A = obj
        key = "layout_element_id" if "layout_element_id" in constraint else "object_id"
        obj_B = next(element for element in scene_graph if element.get("new_object_id") == constraint[key])

        if "position" in obj_B:
            position = func_map[prep](obj_A, obj_B, adjacency, is_on_floor, room_dimensions)
            possible_positions.append(position)

    return possible_positions

def get_topological_ordering(scene_graph):
    """
    Generate a topological ordering of the scene graph nodes.

    Args:
        scene_graph (list): List of objects in the scene graph.

    Returns:
        list: Topological ordering of the graph nodes.
    """
    G = nx.DiGraph()

    # Build the directed graph from the scene graph
    for obj in scene_graph:
        if "placement" in obj:
            if obj["new_object_id"] not in G.nodes():
                G.add_node(obj["new_object_id"])
            obj_scene_graph = obj["placement"]

            for constraint in obj_scene_graph["room_layout_elements"]:
                if constraint["layout_element_id"] not in G.nodes():
                    G.add_node(constraint["layout_element_id"])
                G.add_edge(constraint["layout_element_id"], obj["new_object_id"])

            for constraint in obj_scene_graph["objects_in_room"]:
                if constraint["object_id"] not in G.nodes():
                    G.add_node(constraint["object_id"])
                G.add_edge(constraint["object_id"], obj["new_object_id"])

    # Return the topological ordering
    return list(nx.topological_sort(G))


def get_no_overlap_reason(obj, positions, cluster_constraint=None, errors={}):
    """
    Identify and log reasons for overlap conflicts between object positions.

    Args:
        obj (dict): Object under evaluation.
        positions (list): List of position candidates for the object.
        cluster_constraint (optional, dict): Additional constraint for the cluster.
        errors (dict): Dictionary to store overlap errors.

    Returns:
        dict: Updated dictionary of overlap errors.
    """
    overlaps = []
    candidate_positions = positions
    scene_graph_edges = obj["placement"]["room_layout_elements"] + obj["placement"]["objects_in_room"]

    # Include cluster constraints if provided
    if cluster_constraint is not None:
        candidate_positions += [cluster_constraint]
        scene_graph_edges += ["cluster"]

    # Compare each pair of positions for overlap
    for i, pos1 in enumerate(candidate_positions):
        for j, pos2 in enumerate(candidate_positions[i + 1:]):
            if pos1 == pos2:
                continue
            overlap = calculate_overlap(pos1, pos2)
            if overlap is None:
                overlaps.append((i, i + 1 + j))

    # Log errors for identified overlaps
    for i, j in overlaps:
        print("No Overlap between: ", i, " ", j)
        print("Object: ", obj["new_object_id"])

        if scene_graph_edges[i] == "cluster":
            key_j = "layout_element_id" if "layout_element_id" in scene_graph_edges[j] else "object_id"
            key = ("no_overlap", obj["new_object_id"], scene_graph_edges[j][key_j], scene_graph_edges[j]["preposition"], "cluster")
            errors[key] = 1 + errors.get(key, 0)

        elif scene_graph_edges[j] == "cluster":
            key_i = "layout_element_id" if "layout_element_id" in scene_graph_edges[i] else "object_id"
            key = ("no_overlap", obj["new_object_id"], scene_graph_edges[i][key_i], scene_graph_edges[i]["preposition"], "cluster")
            errors[key] = 1 + errors.get(key, 0)

        else:
            key_i = "layout_element_id" if "layout_element_id" in scene_graph_edges[i] else "object_id"
            key_j = "layout_element_id" if "layout_element_id" in scene_graph_edges[j] else "object_id"
            key = (
                "no_overlap",
                obj["new_object_id"],
                scene_graph_edges[i][key_i],
                scene_graph_edges[i]["preposition"],
                scene_graph_edges[j][key_j],
                scene_graph_edges[j]["preposition"],
            )
            errors[key] = 1 + errors.get(key, 0)

    return errors

def place_object(obj, scene_graph, room_dimensions, errors=None, verbose=False):
    """
    Place an object in the scene graph, ensuring it satisfies spatial constraints and does not collide with other objects.

    Args:
        obj (dict): The object to be placed.
        scene_graph (list): List of objects representing the scene graph.
        room_dimensions (tuple): Dimensions of the room (length, width, height).
        errors (dict, optional): Dictionary to store placement errors. Defaults to None.
        verbose (bool, optional): If True, prints detailed logs for debugging. Defaults to False.

    Returns:
        dict: Updated dictionary of placement errors.
    """
    if errors is None:
        errors = {}

    if verbose:
        get_visualization(scene_graph)

    # Check if the object exists in the scene graph
    if not any(d.get("new_object_id") == obj.get("new_object_id") for d in scene_graph):
        return errors

    try:
        # Get possible positions for the object
        positions = get_possible_positions(obj["new_object_id"], scene_graph, room_dimensions)
        if verbose:
            print(f"Object: {obj['new_object_id']}")
            print("Possible positions: ", positions)

        # Validate required keys
        if not all(key in obj for key in ["size_in_meters", "cluster"]):
            missing_keys = [key for key in ["size_in_meters", "cluster"] if key not in obj]
            raise KeyError(f"Missing keys in object '{obj['new_object_id']}': {missing_keys}")

        # Retrieve size and cluster constraints
        size = obj["size_in_meters"]
        cluster_area = obj["cluster"]["constraint_area"]

        # Compute raw and adjusted cluster constraints
        abs_length, abs_width = deepcopy(size["length"]), deepcopy(size["width"])
        x_neg, x_pos, y_neg, y_pos = cluster_area["x_neg"], cluster_area["x_pos"], cluster_area["y_neg"], cluster_area["y_pos"]
        raw_constraint = (
            x_neg + abs_length / 2,
            y_pos + abs_width / 2,
            x_pos + abs_length / 2,
            y_neg + abs_width / 2,
        )
        shift = int(obj.get("rotation", {}).get("z_angle", 0.0) // 90)
        raw_constraint = raw_constraint[-shift:] + raw_constraint[:-shift]
        cluster_constraint = (
            raw_constraint[0],
            room_dimensions[0] - raw_constraint[2],
            raw_constraint[3],
            room_dimensions[1] - raw_constraint[1],
            0.0,
            room_dimensions[2],
        )
        if verbose:
            print("Cluster constraint: ", cluster_constraint)

        # Handle cases with no valid positions
        if not positions:
            key = ("no_positions_found", obj["new_object_id"])
            errors[key] = 1 + errors.get(key, 0)
            return errors

        # Retrieve children objects for recursive placement
        children = [
            element for element in scene_graph if "placement" in element.keys()
            and obj["new_object_id"] in [x["object_id"] for x in element["placement"]["objects_in_room"]]
        ]
        topological_sorted = get_topological_ordering(scene_graph)

        # Skip placing object if it is already positioned correctly
        if "position" in obj:
            if not validate_existing_position(obj, scene_graph, cluster_constraint, positions, children):
                key = ("invalid_position", obj["new_object_id"])
                errors[key] = 1 + errors.get(key, 0)
                return errors

        # Attempt to assign a valid position within constraints
        for _ in range(50):
            x = random.uniform(cluster_constraint[0], cluster_constraint[1])
            y = random.uniform(cluster_constraint[2], cluster_constraint[3])
            z = random.uniform(cluster_constraint[4], cluster_constraint[5])
            obj["position"] = {"x": x, "y": y, "z": z}

            if verbose:
                print("Assigned position: ", obj["position"], " to object: ", obj["new_object_id"])

            # Check for collisions and break if position is valid
            if all(not is_collision_3d(obj, obj_B) for obj_B in scene_graph if obj_B != obj and "position" in obj_B):
                break
        else:
            key = ("no_valid_position", obj["new_object_id"])
            errors[key] = 1 + errors.get(key, 0)
            return errors

        # Recursively place child objects
        for child in children:
            child_errors = place_object(child, scene_graph, room_dimensions, errors, verbose=verbose)
            if child_errors:
                errors.update(child_errors)

    except KeyError as e:
        print(f"KeyError during placement of {obj['new_object_id']}: {e}")
        errors[("key_error", obj["new_object_id"])] = 1 + errors.get(("key_error", obj["new_object_id"]), 0)

    return errors





