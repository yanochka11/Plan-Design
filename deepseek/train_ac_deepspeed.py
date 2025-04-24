#!/usr/bin/env python
import logging
import json
import re
import os
import random
import math
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional
import warnings

import numpy as np
import torch
from jsonschema import validate, ValidationError
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainerCallback,
    StoppingCriteria,
    StoppingCriteriaList,
    PreTrainedModel,
    GenerationConfig
)
from trl import GRPOConfig, GRPOTrainer
import wandb
from torch.utils.data import DataLoader
from accelerate import Accelerator

warnings.filterwarnings("ignore", message="find_unused_parameters=True")
os.environ["TORCH_DISTRIBUTED_DEFAULT_FIND_UNUSED_PARAMETERS"] = "false"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

accelerator = Accelerator(mixed_precision="bf16")

MODEL_NAME = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
MAX_LENGTH = 1024
MAX_NEW_TOKENS = 2048
NUM_TRAIN_SAMPLES = 600
NUM_VAL_SAMPLES = 100
MAX_STEPS = 200

JSON_SCHEMA = {
    "type": "object",
    "required": ["objects"],
    "properties": {
        "objects": {
            "type": "array",
            "minItems": 5,
            "maxItems": 5,
            "items": {
                "type": "object",
                "required": ["name", "size", "position"],
                "properties": {
                    "name": {"type": "string", "minLength": 1},
                    "size": {
                        "type": "object",
                        "required": ["length", "width"],
                        "properties": {
                            "length": {"type": "number", "minimum": 0.2},
                            "width":  {"type": "number", "minimum": 0.2}
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

def validate_json(layout: dict) -> bool:
    try:
        validate(instance=layout, schema=JSON_SCHEMA)
        return True
    except ValidationError:
        return False

def extract_json(text: str) -> Optional[dict]:
    match = re.search(r"<answer>(.*?)</answer>", text, re.DOTALL)
    if match:
        snippet = match.group(1).strip()
        try:
            return json.loads(snippet)
        except json.JSONDecodeError:
            return None
    return None

def compute_layout_reward(layout: dict, dims: dict) -> float:
    if not validate_json(layout):
        return 0.0, {"valid_json": 0.0}

    objs = layout.get("objects", [])
    r_count = 1.0 if len(objs) == 5 else 0.0
    r_bounds = 1.0
    r_valid_json = 1.0  # Default to valid JSON
    for obj in objs:
        x = obj["position"]["x"]
        y = obj["position"]["y"]
        L = obj["size"]["length"]
        W = obj["size"]["width"]
        if (x - L / 2) < -0.2 or (x + L / 2) > dims["length"] + 0.2:
            r_bounds = 0.0
            r_valid_json = 0.0  # Invalid JSON if out of bounds
            break
        if (y - W / 2) < -0.2 or (y + W / 2) > dims["width"] + 0.2:
            r_bounds = 0.0
            r_valid_json = 0.0  # Invalid JSON if out of bounds
            break

    rects = []
    r_collision = 1.0
    for obj in objs:
        x = obj["position"]["x"]
        y = obj["position"]["y"]
        L = obj["size"]["length"]
        W = obj["size"]["width"]
        rects.append((x - L / 2, x + L / 2, y - W / 2, y + W / 2))

    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            left1, right1, bot1, top1 = rects[i]
            left2, right2, bot2, top2 = rects[j]
            if not (right1 <= left2 or left1 >= right2 or top1 <= bot2 or bot1 >= top2):
                r_collision = 0.0
                break
        if r_collision == 0.0:
            break

    def distribution_score(objects, dims):
        if len(objects) < 2:
            return 1.0
        coords = [(o["position"]["x"], o["position"]["y"]) for o in objects]
        dists = []
        for i in range(len(coords)):
            for j in range(i + 1, len(coords)):
                dx = coords[i][0] - coords[j][0]
                dy = coords[i][1] - coords[j][1]
                dists.append(math.sqrt(dx * dx + dy * dy))
        diag = max(1e-8, math.sqrt(dims["length"] ** 2 + dims["width"] ** 2))
        avg_dist = sum(dists) / len(dists)
        scaled = avg_dist / diag
        return 1.0 if scaled >= 0.3 else 0.0

    r_dist = distribution_score(objs, dims)
    pattern = re.compile(r'^[A-Za-z0-9\s\-_]+$')
    r_names = 1.0
    for obj in objs:
        if not pattern.fullmatch(obj["name"]):
            r_names = 0.0
            break

    # Collect all the metrics
    metrics = {
        "valid_json": r_valid_json,
        "count_reward": r_count,
        "bounds_reward": r_bounds,
        "collision_reward": r_collision,
        "distribution_reward": r_dist,
        "names_reward": r_names,
    }

    total = (1.0 + r_count + r_bounds + r_collision + r_dist + r_names)
    return total / 6.0, metrics

LOG_DIR = "logs_2d"
MODEL_OUTPUT_DIR = "/home/jovyan/shares/SR008.fs2/iana_kulichenko/Experiments/train_GRPO/outputs-200-DeepSeek-R1-Distill-Qwen-1.5B-GRPO"
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(MODEL_OUTPUT_DIR, exist_ok=True)

@dataclass
class RoomDimensions:
    length: float
    width: float

    def __str__(self):
        return f"{self.length}m x {self.width}m"

    def as_dict(self) -> dict:
        return {"length": self.length, "width": self.width}

@dataclass
class TrainingSample:
    prompt: str
    room_dims: RoomDimensions
    num_objects: int

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
            f"Ensure realistic sizes for each item 'length' and 'width' (not make them small) and use the center coordinates (x, y) for positioning. Suggest best possitions. "
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

def generate_training_samples(n: int, tokenizer: AutoTokenizer) -> List[TrainingSample]:
    samples = []
    room_types = ["Living Room", "Office", "Dining Room", "Bedroom", "Meeting Hall"]
    for _ in range(n):
        dims = RoomDimensions(
            length=round(random.uniform(5.0, 10.0), 1),
            width=round(random.uniform(5.0, 10.0), 1),
        )
        data = {
            "room_name": random.choice(room_types),
            "room_dims": dims,
            "num_objects": 5
        }
        data = create_prompt(data, tokenizer)
        samples.append(TrainingSample(prompt=data["prompt"], room_dims=dims, num_objects=5))
    return samples

class JSONGeneratorAgent2D:
    def __init__(self, tokenizer, model: PreTrainedModel, accelerator):
        self.tokenizer = tokenizer
        self.model = model
        self.accelerator = accelerator
        self.gen_config = GenerationConfig(
            max_new_tokens=MAX_NEW_TOKENS,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id
        )
        self.last_completions = []
        self.last_prompts = []
        self.last_reward_metrics = []
    
    @torch.no_grad()
    def generate_layout(self, prompt: str) -> str:
        model = self.accelerator.unwrap_model(self.model)
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=MAX_LENGTH).to(self.accelerator.device)
        output_ids = model.generate(
            **inputs,
            generation_config=self.gen_config,
            stopping_criteria=StoppingCriteriaList([StopIfValidJSON(self.tokenizer)])
        )
        return self.tokenizer.decode(output_ids[0], skip_special_tokens=True)

    def calculate_batch_reward(self, completions: List[str], prompts: List[str], **kwargs) -> torch.Tensor:
        self.last_completions = completions
        self.last_prompts = prompts
        dims_list = kwargs.get("raw_dims", [])
        rewards = []
        self.last_reward_metrics = []
        for comp, dim_dict in zip(completions, dims_list):
            layout = extract_json(comp)
            if not layout:
                rewards.append(0.0)
                self.last_reward_metrics.append({"layout_reward": 0.0})
                continue
            raw_reward, metrics = compute_layout_reward(layout, dim_dict)
            rewards.append(raw_reward)
            self.last_reward_metrics.append({"layout_reward": raw_reward, **metrics})
        return torch.tensor(rewards, dtype=torch.float32, device=self.accelerator.device).clone().detach()

class StopIfValidJSON(StoppingCriteria):
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
    def __call__(self, input_ids, scores, **kwargs) -> bool:
        text = self.tokenizer.decode(input_ids[0], skip_special_tokens=True)
        match = re.search(r"<answer>\s*(\{.*?\})\s*</answer>", text, re.DOTALL)
        if match:
            snippet = match.group(1).strip()
            try:
                json.loads(snippet)
                return True
            except json.JSONDecodeError:
                pass
        return False

def init_wandb():
    wandb_api_key = "81433845ae84394ac019d935b8627aa88c74fe55"
    wandb.login(key=wandb_api_key)
    run_name = f"2D_Layout_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    run = wandb.init(
        project="Layout-Generation-2d-200",
        name=run_name,
        config={
            "model": MODEL_NAME,
            "train_samples": NUM_TRAIN_SAMPLES,
            "val_samples": NUM_VAL_SAMPLES,
            "max_length": MAX_LENGTH,
            "max_new_tokens": MAX_NEW_TOKENS,
            "max_steps": MAX_STEPS
        }
    )
    run.define_metric("step") 
    run.log({"step": 0})
    return run

class TrainingMonitor(TrainerCallback):
    def __init__(self, agent=None, accelerator=None):
        super().__init__()
        self.agent = agent
        self.accelerator = accelerator
        self.wandb_step = 0  

    def on_log(self, args, state, control, logs=None, **kwargs):
        if not self.accelerator.is_main_process or not logs:
            return

        if "rewards/calculate_batch_reward" in logs:
            logs["reward"] = logs["rewards/calculate_batch_reward"]

        self.wandb_step += 1
        logger.info(f"Logging to wandb at step {self.wandb_step}")

        wandb_dict = {
            "epoch": state.epoch,
            "learning_rate": logs.get("learning_rate", 0.0),
            "loss": logs.get("loss", 0.0),
            "reward": logs.get("reward", 0.0),
        }
        if "reward_std" in logs:
            wandb_dict["reward_std"] = logs["reward_std"]
        if "kl" in logs:
            wandb_dict["kl"] = logs["kl"]

        wandb.log(wandb_dict, step=self.wandb_step)

        if self.agent and self.agent.last_reward_metrics:
            all_keys = set()
            for entry in self.agent.last_reward_metrics:
                if isinstance(entry, dict):
                    all_keys.update(entry.keys())
            avg_stats = {}
            for k in all_keys:
                vals = [m[k] for m in self.agent.last_reward_metrics if k in m and isinstance(m[k], (int, float))]
                if vals:
                    avg_stats[f"partial/{k}"] = sum(vals) / len(vals)
            if avg_stats:
                wandb.log(avg_stats, step=self.wandb_step)
            self.agent.last_reward_metrics = []

class ModelOutputLogger(TrainerCallback):
    def __init__(self, agent: JSONGeneratorAgent2D, accelerator):
        self.agent = agent
        self.accelerator = accelerator
        self.log_dir = MODEL_OUTPUT_DIR
        os.makedirs(self.log_dir, exist_ok=True)
    
    def on_train_batch_end(self, args, state, control, **kwargs):
        if not self.accelerator.is_main_process:
            return control

        inputs = kwargs.get("inputs", {})
        completions = kwargs.get("completions", None)

        prompts = inputs["prompt"] if "prompt" in inputs else self.agent.last_prompts
        if completions is None:
            completions = self.agent.last_completions
        
        if not prompts or not completions or len(prompts) != len(completions):
            return control

        lines = [f"Global Step: {state.global_step}\n"]
        for p, c in zip(prompts, completions):
            lines.append("PROMPT:\n" + p)
            lines.append("OUTPUT:\n" + c)
            lines.append("="*50 + "\n")
        txt_data = "\n".join(lines)

        filename = os.path.join(self.log_dir, f"batch_{state.global_step}.txt")
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(txt_data)
            logger.info(f"Saved batch outputs to {filename}")
        except Exception as e:
            logger.error(f"Could not save batch log to {filename}: {e}")
        
        return control

    def on_step_end(self, args, state, control, **kwargs):
        return self.on_train_batch_end(args, state, control, **kwargs)

def main():
    
    init_wandb()
    from accelerate.state import DistributedType
    if not hasattr(accelerator.state, "distributed_type"):
        accelerator.state.distributed_type = DistributedType.DEEPSPEED
  
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, padding_side="left")
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.add_special_tokens({
        "additional_special_tokens": ["<think>", "</think>", "<answer>", "</answer>"]
    })
    
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.bfloat16
    )
    model.resize_token_embeddings(len(tokenizer))
    if hasattr(model.config, "use_cache"):
        model.config.use_cache = False

    output_dir = "/home/jovyan/shares/SR008.fs2/iana_kulichenko/Experiments/train_GRPO/grpo-200_2d_layout-1.5B"
    final_dir = "/home/jovyan/shares/SR008.fs2/iana_kulichenko/Experiments/train_GRPO/final-200_model_2d-1.5B"
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(final_dir, exist_ok=True)
    
    training_args = GRPOConfig(
        output_dir=output_dir,
        run_name=f"GRPO+AC-{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        learning_rate=5e-5,
        adam_beta1=0.9,
        adam_beta2=0.99,
        weight_decay=0.1,
        lr_scheduler_type="cosine",
        optim="paged_adamw_8bit",
        logging_steps=1,
        bf16=True,
        fp16=False,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=2,
        num_generations=8,
        max_prompt_length=MAX_LENGTH,
        max_completion_length=MAX_NEW_TOKENS,
        max_steps=MAX_STEPS,
        save_steps=15,
        max_grad_norm=0.1,
        report_to=None,
        use_vllm=False,
    )

    train_samples = generate_training_samples(NUM_TRAIN_SAMPLES, tokenizer)
    val_samples = generate_training_samples(NUM_VAL_SAMPLES, tokenizer)
    logger.info(f"Generated {len(train_samples)} train, {len(val_samples)} val samples.")
    
    train_dataset = Dataset.from_dict({
        "prompt": [s.prompt for s in train_samples],
        "raw_dims": [s.room_dims.as_dict() for s in train_samples],
    })
    val_dataset = Dataset.from_dict({
        "prompt": [s.prompt for s in val_samples],
        "raw_dims": [s.room_dims.as_dict() for s in val_samples],
    })
  
    
    model = accelerator.prepare(model)
    train_dataset = accelerator.prepare(train_dataset)
    val_dataset = accelerator.prepare(val_dataset)

    agent = JSONGeneratorAgent2D(tokenizer, model, accelerator)
    
    trainer = GRPOTrainer(
        model=accelerator.unwrap_model(model),
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        reward_funcs=[agent.calculate_batch_reward],
        callbacks=[TrainingMonitor(agent=agent), ModelOutputLogger(agent)]
    )
    
    logger.info("Starting training.")
    try:
        trainer.train()
    except KeyboardInterrupt:
        logger.warning("Training interrupted by user!")
    finally:
        logger.info("Training stopped.")
        accelerator.wait_for_everyone()
        if accelerator.is_main_process:
            unwrapped = accelerator.unwrap_model(model)
            unwrapped.save_pretrained(final_dir)
            tokenizer.save_pretrained(final_dir)
            logger.info("Model & tokenizer saved locally.")
        wandb.finish()

if __name__ == "__main__":
    main()
