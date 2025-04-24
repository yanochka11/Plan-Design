#!/usr/bin/env python
import os
import sys
import re
import json
import math
import random
import glob
import argparse
from datetime import datetime
from jsonschema import validate, ValidationError
from transformers import AutoTokenizer  

BASE_DIR = "/home/jovyan/shares/SR008.fs2/iana_kulichenko/Experiments/train_GRPO"
sys.path.insert(0, BASE_DIR)

import inference
from inference import load_inference_model, generate_layout, run_inference

DEFAULT_PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")
DEFAULT_ANSWERS_DIR = os.path.join(BASE_DIR, "answers")
RESULTS_PATH = os.path.join(BASE_DIR, "test_results.txt")  # Final results saved here

for d in [DEFAULT_PROMPTS_DIR, DEFAULT_ANSWERS_DIR]:
    os.makedirs(d, exist_ok=True)

JSON_SCHEMA = {
    "type": "object",
    "required": ["objects"],
    "properties": {
        "objects": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "size", "position"],
                "properties": {
                    "name": {"type": "string", "minLength": 1},
                    "size": {
                        "type": "object",
                        "required": ["length", "width"],
                        "properties": {
                            "length": {"type": "number", "minimum": 0.1},
                            "width": {"type": "number", "minimum": 0.1}
                        }
                    },
                    "position": {
                        "type": "object",
                        "required": ["x", "y"],
                        "properties": {
                            "x": {"type": "number", "minimum": 0},
                            "y": {"type": "number", "minimum": 0}
                        }
                    }
                }
            }
        }
    }
}

def create_prompt(sample: dict, tokenizer: AutoTokenizer) -> dict:
    room_name = sample.get("room_name", "Room")
    room_dims_str = str(sample["room_dims"])
    json_schema_str = json.dumps(JSON_SCHEMA, indent=2)

    system_msg = {
        "role": "system",
        "content": (
            f"You are a 2D interior design assistant. Think briefly using <think>...</think> (do not reveal this) and then provide the final layout. "
            f"Your final answer MUST be valid JSON wrapped in <answer>...</answer> with no extra text. "
            f"Create a layout for a {room_name} with exactly 5 unique, common furniture items. "
            f"Ensure realistic sizes for each item 'length' and 'width' and use the center coordinates (x, y) for positioning. "
            f"All items must be strictly within room dimensions (length x width, where x corresponds to length and y to width): {room_dims_str}, with a minimal gap of ~0.4m, and NO overlaps between objects. "
            f"Choose only common furniture (e.g., bed, sofa, table, wardrobe, chair, bookshelf) and exclude items like 'window', 'wall', 'door', 'floor', or 'ceiling'."
        )
    }

    user_msg = {
        "role": "user",
        "content": (
            f"Design a {room_name} layout with exactly 5 common furniture items that fit strictly within the room dimensions (length x width): {room_dims_str} without overlapping. "
            f"Return ONLY valid JSON in <answer>...</answer> tags. Follow this JSON schema:\n{json_schema_str}"
        )
    }

    messages = [system_msg, user_msg]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    sample["prompt"] = prompt
    return sample


class RoomDimensions:
    def __init__(self, length: float, width: float):
        self.length = length
        self.width = width

    def __str__(self):
        return f"{self.length}m x {self.width}m"

def compute_even_distribution_score(objects: list, dims: RoomDimensions) -> float:
    if len(objects) < 2:
        return 1.0
    coords = [(obj["position"]["x"], obj["position"]["y"]) for obj in objects]
    dists = [
        math.sqrt((coords[i][0] - coords[j][0])**2 + (coords[i][1] - coords[j][1])**2)
        for i in range(len(coords)) for j in range(i+1, len(coords))
    ]
    avg_dist = sum(dists) / len(dists)
    diag = math.sqrt(dims.length**2 + dims.width**2)
    return min(max(avg_dist / diag, 0.0), 1.0)

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

def extract_final_json(content: str) -> str:
    # Try to find JSON wrapped in <answer>...</answer>
    match = re.search(r"<answer>\s*(\{.*?\})\s*</answer>", content, re.DOTALL)
    if match:
        snippet = match.group(1).strip()
        try:
            parsed = json.loads(snippet)
            return json.dumps(parsed, indent=2)
        except Exception:
            return content

    try:
        parsed = json.loads(content)
        return json.dumps(parsed, indent=2)
    except Exception:
        return content


def test_answer_file(answer_path: str, prompt_path: str) -> dict:
    try:
        with open(answer_path, "r") as f:
            content = f.read()
        # Extract only the final JSON
        extracted = extract_final_json(content)
        layout = json.loads(extracted)
    except Exception:
        return {
            "valid_json": 0.0,
            "count_reward": 0.0,
            "bounds_reward": 0.0,
            "collision_reward": 0.0,
            "distribution_reward": 0.0,
            "names_reward": 0.0,
            "reward": 0.0
        }
    try:
        dims_tuple = extract_room_dimensions_from_prompt(prompt_path)
        room_dims = RoomDimensions(dims_tuple[0], dims_tuple[1])
    except Exception as e:
        print(f"Error extracting dimensions from {prompt_path}: {e}")
        return {
            "valid_json": 0.0,
            "count_reward": 0.0,
            "bounds_reward": 0.0,
            "collision_reward": 0.0,
            "distribution_reward": 0.0,
            "names_reward": 0.0,
            "reward": 0.0
        }
    # Validate JSON structure using the schema.
    try:
        validate(instance=layout, schema=JSON_SCHEMA)
        r_valid_json = 1.0
    except ValidationError:
        r_valid_json = 0.0
        return {
            "valid_json": r_valid_json,
            "count_reward": 0.0,
            "bounds_reward": 0.0,
            "collision_reward": 0.0,
            "distribution_reward": 0.0,
            "names_reward": 0.0,
            "reward": 0.0
        }
    objs = layout.get("objects", [])
    r_count = 1.0 if len(objs) == 5 else 0.0
    r_bounds = 1.0
    for obj in objs:
        x = obj["position"]["x"]
        y = obj["position"]["y"]
        L = obj["size"]["length"]
        W = obj["size"]["width"]
        if (x - L/2) < -0.2 or (x + L/2) > (room_dims.length + 0.2) or (y - W/2) < -0.2 or (y + W/2) > (room_dims.width + 0.2):
            r_bounds = 0.0
            break
    r_collision = 1.0
    rects = []
    for obj in objs:
        x = obj["position"]["x"]
        y = obj["position"]["y"]
        L = obj["size"]["length"]
        W = obj["size"]["width"]
        rects.append((x - L/2, x + L/2, y - W/2, y + W/2))
    for i in range(len(rects)):
        for j in range(i+1, len(rects)):
            left1, right1, bottom1, top1 = rects[i]
            left2, right2, bottom2, top2 = rects[j]
            if not (right1 <= left2 or left1 >= right2 or top1 <= bottom2 or bottom1 >= top2):
                r_collision = 0.0
                break
        if r_collision == 0.0:
            break
    raw_dist = compute_even_distribution_score(objs, room_dims)
    r_dist = 1.0 if raw_dist >= 0.3 else 0.0
    pattern = re.compile(r'^[A-Za-z0-9\s\-_]+$')
    r_names = 1.0
    for obj in objs:
        if not pattern.fullmatch(obj["name"]):
            r_names = 0.0
            break
    overall_reward = (r_valid_json + r_count + r_bounds + r_collision + r_dist + r_names) / 6.0
    return {
        "valid_json": r_valid_json,
        "count_reward": r_count,
        "bounds_reward": r_bounds,
        "collision_reward": r_collision,
        "distribution_reward": r_dist,
        "names_reward": r_names,
        "reward": overall_reward
    }

# Format a table (list of rows) into a string
def format_table(table: list) -> str:
    if not table:
        return ""
    num_cols = len(table[0])
    col_widths = [max(len(row[i]) for row in table) for i in range(num_cols)]
    lines = []
    for i, row in enumerate(table):
        lines.append(" | ".join(row[j].ljust(col_widths[j]) for j in range(num_cols)))
        if i == 0:
            lines.append("-+-".join("-" * col_widths[j] for j in range(num_cols)))
    return "\n".join(lines)

# Natural sort key based on the numeric part of the filename
def numeric_sort_key(filepath: str):
    base = os.path.basename(filepath)
    m = re.match(r"(\d+)", base)
    return int(m.group(1)) if m else float('inf')

# Generate a random prompt using create_prompt and the loaded tokenizer
def generate_prompt(tokenizer: AutoTokenizer) -> str:
    room_types = ["Living Room", "Office", "Dining Room", "Bedroom", "Meeting Hall"]
    room_name = random.choice(room_types)
    room_dims = RoomDimensions(
        round(random.uniform(4.0, 10.0), 1),
        round(random.uniform(4.0, 10.0), 1)
    )
    sample = {"room_name": room_name, "room_dims": room_dims}
    sample = create_prompt(sample, tokenizer)
    return sample["prompt"]

# ---------------------------
# Main Testing Routine
# ---------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test_sample_size", type=int, default=100, help="Number of test samples")
    parser.add_argument("--prompts_dir", type=str, help="Directory containing prompts. If not provided, new prompts will be generated.")
    parser.add_argument("--answers_dir", type=str, default=DEFAULT_ANSWERS_DIR, help="Directory to save answers")
    parser.add_argument("--model_name", type=str, required=True, help="Model name for inference")
    parser.add_argument("--checkpoint_path", type=str, required=True, help="Path to the model checkpoint")
    # New flag: if set, skip running inference.
    parser.add_argument("--skip_inference", action="store_true", help="Flag to skip running inference")
    args = parser.parse_args()

    # Load the inference model (to access tokenizer for prompt creation)
    model, tokenizer, accelerator, gen_config = load_inference_model(args.model_name, args.checkpoint_path)

    # Generate or load prompts
    test_sample_size = args.test_sample_size
    if args.prompts_dir:
        prompts_dir = args.prompts_dir
        prompt_files = sorted(glob.glob(os.path.join(prompts_dir, "*.txt")), key=numeric_sort_key)
        if not prompt_files:
            print(f"No prompt files found in {prompts_dir}")
            return
    else:
        prompts_dir = DEFAULT_PROMPTS_DIR
        prompt_files = []
        for i in range(1, test_sample_size + 1):
            prompt_text = generate_prompt(tokenizer)
            prompt_file = os.path.join(prompts_dir, f"{i}.txt")
            with open(prompt_file, "w") as f:
                f.write(prompt_text)
            prompt_files.append(prompt_file)
            print(f"Saved prompt: {prompt_file}")

    # Ensure answers directory exists
    answers_dir = args.answers_dir
    os.makedirs(answers_dir, exist_ok=True)

    # Run inference if not skipped
    if not args.skip_inference:
        run_inference(prompts_dir, answers_dir, args.model_name, args.checkpoint_path)
    else:
        print("Skipping inference as per flag (--skip_inference).")

    # Post-process answer files: extract and overwrite with only the final JSON.
    answer_files = sorted(glob.glob(os.path.join(answers_dir, "*.txt")), key=numeric_sort_key)
    if not answer_files:
        print(f"No answer files found in {answers_dir}")
        return

    for answer_file in answer_files:
        with open(answer_file, "r") as f:
            content = f.read()
        extracted = extract_final_json(content)
        with open(answer_file, "w") as f:
            f.write(extracted)
        print(f"Post-processed answer file: {answer_file}")

    # Evaluate each answer against its corresponding prompt.
    total_files = len(answer_files)
    valid_json_sum = count_reward_sum = bounds_reward_sum = collision_reward_sum = distribution_reward_sum = names_reward_sum = 0.0
    rewards = []
    table = []
    header = ["File", "valid_json", "count_reward", "bounds_reward", "collision_reward", "distribution_reward", "names_reward", "reward"]
    table.append(header)

    for answer_file in answer_files:
        base_name = os.path.basename(answer_file)
        prompt_file = os.path.join(prompts_dir, base_name)
        metrics = test_answer_file(answer_file, prompt_file)
        rewards.append(metrics["reward"])
        valid_json_sum += metrics["valid_json"]
        count_reward_sum += metrics["count_reward"]
        bounds_reward_sum += metrics["bounds_reward"]
        collision_reward_sum += metrics["collision_reward"]
        distribution_reward_sum += metrics["distribution_reward"]
        names_reward_sum += metrics["names_reward"]

        row = [
            base_name,
            f"{metrics['valid_json']:.1f}",
            f"{metrics['count_reward']:.1f}",
            f"{metrics['bounds_reward']:.1f}",
            f"{metrics['collision_reward']:.1f}",
            f"{metrics['distribution_reward']:.1f}",
            f"{metrics['names_reward']:.1f}",
            f"{metrics['reward']:.2f}"
        ]
        table.append(row)
    table_str = format_table(table)
    with open(RESULTS_PATH, "w") as f:
        f.write(table_str)

    stats = (
        f"Total files: {total_files}\n"
        f"Valid JSON: {valid_json_sum}/{total_files}\n"
        f"Count reward: {count_reward_sum}/{total_files}\n"
        f"Bounds reward: {bounds_reward_sum}/{total_files}\n"
        f"Collision reward: {collision_reward_sum}/{total_files}\n"
        f"Distribution reward: {distribution_reward_sum}/{total_files}\n"
        f"Names reward: {names_reward_sum}/{total_files}\n"
        f"Average overall reward: {sum(rewards)/len(rewards):.2f}\n"
    )
    with open(RESULTS_PATH, "a") as f:
        f.write("\n" + stats)

    print(f"Test results saved to {RESULTS_PATH}")
    print("\n" + table_str)
    print("\n" + stats)

if __name__ == "__main__":
    main()
