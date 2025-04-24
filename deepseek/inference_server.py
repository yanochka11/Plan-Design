#!/usr/bin/env python
import os
import re
import json
import torch
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    GenerationConfig,
    StoppingCriteria,
    StoppingCriteriaList
)
from accelerate import Accelerator
from jsonschema import validate, ValidationError

MAX_LENGTH = 1024
MAX_NEW_TOKENS = 2048

# Room dimensions for layout validation.
ROOM_DIMS = {"length": 8.6, "width": 7.2}

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
                            "width": {"type": "number", "minimum": 0.2}
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

class StopIfValidJSON(StoppingCriteria):
    """Stops generation when a valid JSON block is detected."""
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

    def __call__(self, input_ids, scores, **kwargs) -> bool:
        text = self.tokenizer.decode(input_ids[0], skip_special_tokens=True)
        # If <answer> tags exist, try to parse that substring.
        match = re.search(r"<answer>\s*(\{[\s\S]*?\})\s*</answer>", text, re.DOTALL)
        if match:
            snippet = match.group(1).strip()
            try:
                json.loads(snippet)
                return True
            except json.JSONDecodeError:
                pass
        return False

def load_inference_model(checkpoint_path: str):
    """Loads tokenizer and model from a local checkpoint."""
    accelerator = Accelerator(mixed_precision="bf16")
    tokenizer = AutoTokenizer.from_pretrained(checkpoint_path, padding_side="left")
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.add_special_tokens({
        "additional_special_tokens": ["<think>", "</think>", "<answer>", "</answer>"]
    })
    model = AutoModelForCausalLM.from_pretrained(checkpoint_path, torch_dtype=torch.bfloat16)
    model.resize_token_embeddings(len(tokenizer))
    if hasattr(model.config, "use_cache"):
        model.config.use_cache = False
    model.to(accelerator.device)
    model = accelerator.prepare(model)
    gen_config = GenerationConfig(
        max_new_tokens=MAX_NEW_TOKENS,
        temperature=0.7,
        top_p=0.9,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id,
        eos_token_id=tokenizer.eos_token_id
    )
    return model, tokenizer, accelerator, gen_config

def generate_layout(prompt: str, model, tokenizer, accelerator, gen_config) -> str:
    """Generates a response from the model given a prompt."""
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=MAX_LENGTH)
    inputs = inputs.to(accelerator.device)
    output_ids = model.generate(
        **inputs,
        generation_config=gen_config,
        stopping_criteria=StoppingCriteriaList([StopIfValidJSON(tokenizer)])
    )
    output_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    print("\n=== Raw Model Output ===\n", output_text, "\n========================\n")
    return output_text

def extract_balanced_json_strings(text: str) -> list:
    """
    Extracts all substrings from text that form balanced JSON objects.
    Returns a list of candidate JSON strings.
    """
    candidates = []
    start_index = None
    brace_count = 0
    for i, ch in enumerate(text):
        if ch == '{':
            if brace_count == 0:
                start_index = i
            brace_count += 1
        elif ch == '}':
            brace_count -= 1
            if brace_count == 0 and start_index is not None:
                candidate = text[start_index:i+1]
                candidates.append(candidate)
                start_index = None
    return candidates

def extract_final_json(output_text: str) -> dict:
    """
    Iterates over all balanced JSON substrings in the output and returns the first one
    that contains the top-level "objects" key.
    Returns {} if none is found.
    """
    candidates = extract_balanced_json_strings(output_text)
    for candidate in candidates:
        try:
            obj = json.loads(candidate)
            if isinstance(obj, dict) and "objects" in obj:
                return obj
        except json.JSONDecodeError as e:
            print("Error parsing candidate JSON:", e)
            continue
    return {}

def check_layout_validity(layout: dict, dims: dict) -> bool:
    """
    Checks layout validity:
      - Exactly 5 objects.
      - Each object is within room bounds (with a tolerance of 0.2 m).
      - No overlapping objects.
    Returns True if all conditions are met.
    """
    objs = layout.get("objects", [])
    if len(objs) != 5:
        return False
    for obj in objs:
        x, y = obj["position"]["x"], obj["position"]["y"]
        L, W = obj["size"]["length"], obj["size"]["width"]
        if (x - L/2) < -0.2 or (x + L/2) > dims["length"] + 0.2 or \
           (y - W/2) < -0.2 or (y + W/2) > dims["width"] + 0.2:
            return False
    rects = []
    for obj in objs:
        x, y = obj["position"]["x"], obj["position"]["y"]
        L, W = obj["size"]["length"], obj["size"]["width"]
        rects.append((x - L/2, x + L/2, y - W/2, y + W/2))
    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            if not (rects[i][1] <= rects[j][0] or rects[i][0] >= rects[j][1] or
                    rects[i][3] <= rects[j][2] or rects[i][2] >= rects[j][3]):
                return False
    return True

app = FastAPI()

CHECKPOINT_PATH = "/home/jovyan/shares/SR008.fs2/iana_kulichenko/Experiments/train_GRPO/grpo-200_2d_layout-1.5B/checkpoint-180"
model, tokenizer, accelerator, gen_config = load_inference_model(CHECKPOINT_PATH)

class PromptRequest(BaseModel):
    prompt: str

class InferenceResponse(BaseModel):
    answer: dict

@app.post("/infer", response_model=InferenceResponse)
def infer(request: PromptRequest):

    attempts = 8
    final_json = {}
    for i in range(attempts):
        print(f"Generation attempt {i+1}...")
        output_text = generate_layout(request.prompt, model, tokenizer, accelerator, gen_config)
        candidate = extract_final_json(output_text)
        if candidate:
            try:
                validate(instance=candidate, schema=JSON_SCHEMA)
            except ValidationError as ve:
                print(f"JSON schema validation error on attempt {i+1}: {ve}")
                candidate = {}
        else:
            print(f"No valid JSON candidate found on attempt {i+1}.")

        if candidate and check_layout_validity(candidate, ROOM_DIMS):
            final_json = candidate
            break
        else:
            print("Layout validation failed, retrying...\n")
    
    if not final_json:
        raise HTTPException(status_code=400, detail="No valid JSON found in the model output after 8 attempts.")
    
    return {"answer": final_json}

if __name__ == "__main__":
    uvicorn.run("inference_server:app", host="0.0.0.0", port=8005, reload=False)