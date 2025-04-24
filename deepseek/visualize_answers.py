#!/usr/bin/env python3
import os
import json
import glob
import re
import argparse
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from shapely.geometry import box
from shapely.affinity import rotate, translate

def extract_room_dimensions_from_prompt(prompt_path: str) -> tuple:
    with open(prompt_path, "r") as f:
        content = f.read()
    pattern = r"room dimensions.*?([\d.]+)m\s*x\s*([\d.]+)m"
    m = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
    if not m:
        raise ValueError(f"Could not extract room dimensions from {prompt_path}.")
    room_length = float(m.group(1))
    room_width = float(m.group(2))
    return (room_length, room_width, 3)

def extract_room_name_from_prompt(prompt_path: str) -> str:
    """
    Extracts the room name from the prompt file.
    Looks for a pattern like: "Design a Bedroom layout" where the room name is in between.
    """
    with open(prompt_path, "r") as f:
        content = f.read()
    pattern = r"Design a\s+(.+?)\s+layout"
    m = re.search(pattern, content, re.IGNORECASE)
    if m:
        return m.group(1)
    else:
        return "Room"

def visualize_2d(objects_json, room_dimensions=(12, 10, 3), room_name="Room", save_path=None):
    room_length, room_width, _ = room_dimensions

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_aspect('equal', adjustable='box')

    # Title and labels, include the room name if provided
    title_str = f"2D {room_name} Layout: {room_length} × {room_width} m"
    ax.set_title(title_str, fontsize=14, pad=40)
    ax.set_xlabel("X (meters)", fontsize=12)
    ax.set_ylabel("Y (meters)", fontsize=12)
    ax.grid(True, linestyle="--", alpha=0.4)

    # Draw room boundary
    room_rect = patches.Rectangle((0, 0), width=room_length, height=room_width,
                                  linewidth=2, linestyle='--',
                                  edgecolor='black', facecolor='none')
    ax.add_patch(room_rect)

    margin = 1.0
    ax.set_xlim(-margin, room_length + margin)
    ax.set_ylim(-margin, room_width + margin)

    polygons = []
    names = []
    overlapping_pairs = []

    # Draw each object
    for obj in objects_json.get("objects", []):
        name = obj.get("name", "Unnamed")
        size = obj.get("size", {})
        pos = obj.get("position", {})
        rot = obj.get("rotation", {})

        length = size.get("length", 1.0)
        width_ = size.get("width", 1.0)
        x_center = pos.get("x", 0.0)
        y_center = pos.get("y", 0.0)
        yaw_deg = rot.get("yaw", 0.0)

        # Create rectangle centered at (0,0)
        rect = box(-length/2, -width_/2, length/2, width_/2)
        rotated_rect = rotate(rect, angle=yaw_deg, origin=(0,0), use_radians=False)
        final_rect = translate(rotated_rect, xoff=x_center, yoff=y_center)

        polygons.append(final_rect)
        names.append(name)

        coords = np.array(final_rect.exterior.coords)
        patch = patches.Polygon(coords, closed=True, edgecolor='blue',
                                facecolor='skyblue', alpha=0.4, linewidth=2)
        ax.add_patch(patch)

        centroid = final_rect.centroid
        ax.text(centroid.x, centroid.y, name, ha='center', va='center',
                fontsize=9, fontweight='bold',
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'),
                rotation=yaw_deg, rotation_mode='anchor')

    # Check for overlapping objects
    for i in range(len(polygons)):
        for j in range(i + 1, len(polygons)):
            if polygons[i].intersects(polygons[j]):
                overlapping_pairs.append((names[i], names[j]))
    if overlapping_pairs:
        print("Overlapping objects detected:")
        for pair in overlapping_pairs:
            print(f" - {pair[0]} overlaps with {pair[1]}")
    else:
        print("No overlapping objects detected.")

    # Label room walls
    ax.text(room_length / 2, room_width + margin * 0.4, "NORTH WALL", ha='center', va='bottom', fontsize=11, fontweight='bold')
    ax.text(room_length / 2, -margin * 0.4, "SOUTH WALL", ha='center', va='top', fontsize=11, fontweight='bold')
    ax.text(-margin * 0.4, room_width / 2, "WEST WALL", ha='center', va='center', fontsize=11, fontweight='bold', rotation=90)
    ax.text(room_length + margin * 0.4, room_width / 2, "EAST WALL", ha='center', va='center', fontsize=11, fontweight='bold', rotation=-90)

    object_count = len(objects_json.get("objects", []))
    ax.text(room_length/2, room_width + margin*1.2, f"{object_count} Object(s)", ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
        print(f"Saved plot to {save_path}")
        plt.close(fig)
    else:
        plt.show()

def numeric_sort_key(path: str):
    """Extract numeric part from filename to sort numerically."""
    base = os.path.splitext(os.path.basename(path))[0]
    try:
        return int(base)
    except ValueError:
        return base

def main():
    parser = argparse.ArgumentParser(description="Visualize 2D room layouts from answers.")
    parser.add_argument("--prompts_dir", type=str, required=True, help="Path to prompts folder")
    parser.add_argument("--answers_dir", type=str, required=True, help="Path to answers folder")
    parser.add_argument("--output_dir", type=str, required=True, help="Path to output images folder")
    args = parser.parse_args()
    
    prompt_dir = args.prompts_dir
    answer_dir = args.answers_dir
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)
    
    file_pattern = os.path.join(answer_dir, "*.txt")
    answer_files = sorted(glob.glob(file_pattern), key=numeric_sort_key)
    if not answer_files:
        print(f"No files found in {answer_dir}")
        return

    for answer_file in answer_files:
        print(f"Processing file: {answer_file}")
        try:
            with open(answer_file, "r") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Failed to load {answer_file}: {e}")
            continue
        
        base_filename = os.path.splitext(os.path.basename(answer_file))[0]
        output_file = os.path.join(output_dir, f"{base_filename}.png")
        
        prompt_file = os.path.join(prompt_dir, f"{base_filename}.txt")
        try:
            room_dims = extract_room_dimensions_from_prompt(prompt_file)
        except Exception as e:
            print(f"Error reading room dimensions from {prompt_file}: {e}")
            room_dims = (12, 10, 3)  # fallback default
        
        try:
            room_name = extract_room_name_from_prompt(prompt_file)
        except Exception as e:
            print(f"Error reading room name from {prompt_file}: {e}")
            room_name = "Room"
        
        visualize_2d(data, room_dimensions=room_dims, room_name=room_name, save_path=output_file)

if __name__ == "__main__":
    main()
