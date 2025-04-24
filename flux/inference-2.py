#!/usr/bin/env python3
import os
import sys
import math
import argparse

import torch
from diffusers import DiffusionPipeline
from accelerate import Accelerator
from torch.distributed import is_initialized, destroy_process_group


def parse_args():
    parser = argparse.ArgumentParser(description="Run FLUX.1 inference.")
    parser.add_argument(
        "--output_dir", type=str,
        default="/home/jovyan/shares/SR008.fs2/iana_kulichenko/Experiments/flux/inference_output_internvl_2",
        help="Directory to save generated images."
    )
    parser.add_argument("--num_images", type=int, default=1000, help="Number of images to generate.")
    parser.add_argument("--batch_size", type=int, default=8, help="Batch size.")
    parser.add_argument("--seed", type=int, default=11, help="Random seed for reproducibility.")
    parser.add_argument("--width", type=int, default=1024, help="Generated image width.")
    parser.add_argument("--height", type=int, default=1024, help="Generated image height.")
    parser.add_argument("--steps", type=int, default=50, help="Number of inference steps.")
    return parser.parse_args()


def main():
    args = parse_args()

    # Load Hugging Face token securely
    os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN", "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")  # fallback if not in env
    os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"

    base_model_id = "black-forest-labs/FLUX.1-dev"
    lora_checkpoint = "/home/jovyan/shares/SR008.fs2/iana_kulichenko/Experiments/flux/output_internvl-2/living_room_top_view/living_room_top_view.safetensors"

    # Initialize Accelerator
    accelerator = Accelerator()
    device = accelerator.device

    # Load pipeline
    pipeline = DiffusionPipeline.from_pretrained(base_model_id, torch_dtype=torch.bfloat16)
    pipeline.load_lora_weights(lora_checkpoint)
    pipeline.to(device)
    pipeline.set_progress_bar_config(disable=True)

    prompt = "a top-down view from the center of the living room"
    generator = torch.Generator(device=device).manual_seed(args.seed)
    num_batches = math.ceil(args.num_images / args.batch_size)

    if accelerator.is_main_process:
        os.makedirs(args.output_dir, exist_ok=True)

    current_image_idx = 0
    for batch_idx in range(num_batches):
        batch_size_eff = min(args.batch_size, args.num_images - batch_idx * args.batch_size)
        prompts = [prompt] * batch_size_eff

        if accelerator.is_main_process:
            print(f"[main] Generating batch {batch_idx + 1}/{num_batches}...")

        results = pipeline(
            prompt=prompts,
            num_inference_steps=args.steps,
            width=args.width,
            height=args.height,
            generator=generator,
        )

        if accelerator.is_main_process:
            for img in results.images:
                out_path = os.path.join(args.output_dir, f"living_room_{current_image_idx:04d}.png")
                img.save(out_path)
                print(f"[main] Saved: {out_path}")
                current_image_idx += 1

    if is_initialized():
        destroy_process_group()


if __name__ == "__main__":
    main()
