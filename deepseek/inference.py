#!/usr/bin/env python
import os
import re
import json
import torch
import argparse
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig, StoppingCriteria, StoppingCriteriaList
from accelerate import Accelerator

MAX_LENGTH = 1024
MAX_NEW_TOKENS = 2048

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

def load_inference_model(model_name: str, checkpoint_path: str):

    accelerator = Accelerator(mixed_precision="bf16")
    tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side="left")
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.add_special_tokens({
        "additional_special_tokens": ["<think>", "</think>", "<answer>", "</answer>"]
    })
    model = AutoModelForCausalLM.from_pretrained(checkpoint_path, torch_dtype=torch.bfloat16)
    model.resize_token_embeddings(len(tokenizer))
    if hasattr(model.config, "use_cache"):
        model.config.use_cache = False
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

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=MAX_LENGTH).to(accelerator.device)
    output_ids = model.generate(
        **inputs,
        generation_config=gen_config,
        stopping_criteria=StoppingCriteriaList([StopIfValidJSON(tokenizer)])
    )
    return tokenizer.decode(output_ids[0], skip_special_tokens=True)

def run_inference(prompts_dir: str, answers_dir: str, model_name: str, checkpoint_path: str):

    os.makedirs(answers_dir, exist_ok=True)
    prompt_files = sorted([f for f in os.listdir(prompts_dir) if f.endswith('.txt')])
    model, tokenizer, accelerator, gen_config = load_inference_model(model_name, checkpoint_path)
    for fname in prompt_files:
        prompt_path = os.path.join(prompts_dir, fname)
        with open(prompt_path, "r") as f:
            prompt_text = f.read()
        output_text = generate_layout(prompt_text, model, tokenizer, accelerator, gen_config)
  
        try:
            marker = "<｜Assistant｜>"
            if marker in output_text:
                text_after = output_text.split(marker, 1)[1]
            else:
                text_after = output_text
            
            matches = re.findall(r"(\{[\s\S]*\})", text_after)
            if matches:
                snippet = matches[-1].strip()  # Use the last candidate
                layout_json = json.loads(snippet)
                answer_content = json.dumps(layout_json, indent=2)
            else:
                answer_content = output_text
        except Exception:
            answer_content = output_text
        answer_path = os.path.join(answers_dir, fname)
        with open(answer_path, "w") as f:
            f.write(answer_content)
        print(f"Saved answer: {answer_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompts_dir", type=str, required=True, help="Directory containing prompt files")
    parser.add_argument("--answers_dir", type=str, required=True, help="Directory to save answers")
    parser.add_argument("--model_name", type=str, required=True, help="Model name for inference")
    parser.add_argument("--checkpoint_path", type=str, required=True, help="Path to the model checkpoint")
    args = parser.parse_args()
    run_inference(args.prompts_dir, args.answers_dir, args.model_name, args.checkpoint_path)

if __name__ == "__main__":
    main()
