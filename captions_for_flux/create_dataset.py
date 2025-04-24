#!/usr/bin/env python
import os
import shutil

input_images_dir = "/home/jovyan/shares/SR008.fs2/iana_kulichenko/Experiments/captions/input_images"
output_prompts_dir = "/home/jovyan/shares/SR008.fs2/iana_kulichenko/Experiments/captions/output_prompts_2"
dataset_dir = "/home/jovyan/shares/SR008.fs2/iana_kulichenko/Experiments/captions/dataset_internvl_2"
os.makedirs(dataset_dir, exist_ok=True)

def copy_files(src_dir, dest_dir, extensions):
    files_copied = 0
    for filename in os.listdir(src_dir):
        if any(filename.lower().endswith(ext) for ext in extensions):
            src = os.path.join(src_dir, filename)
            dst = os.path.join(dest_dir, filename)
            shutil.copy(src, dst)
            files_copied += 1
            print(f"Copied {src} -> {dst}")
    return files_copied

image_extensions = [".jpg", ".jpeg", ".png", ".webp", ".bmp"]
images_copied = copy_files(input_images_dir, dataset_dir, image_extensions)
text_extensions = [".txt"]
texts_copied = copy_files(output_prompts_dir, dataset_dir, text_extensions)

