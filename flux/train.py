#!/usr/bin/env python3
import os
import sys
from collections import OrderedDict
from PIL import Image

def prepare_dataset(dataset_path, caption_text):
    supported_extensions = ('.jpg', '.jpeg', '.png')
    for filename in os.listdir(dataset_path):
        if filename.lower().endswith(supported_extensions):
            base_name, _ = os.path.splitext(filename)
            caption_filepath = os.path.join(dataset_path, base_name + '.txt')
            if not os.path.exists(caption_filepath):
                with open(caption_filepath, 'w', encoding='utf-8') as f:
                    f.write(caption_text)
                print(f"Created caption file for {filename}")

def main():
    dataset_path = "/home/jovyan/shares/SR008.fs2/iana_kulichenko/Experiments/captions/dataset_internvl_2"
    output_dir = "/home/jovyan/shares/SR008.fs2/iana_kulichenko/Experiments/flux/output_internvl-3"          
    hf_token = "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"              
    ai_toolkit_path = "/home/jovyan/shares/SR008.fs2/iana_kulichenko/Experiments/flux/ai-toolkit"   
    #prepare_dataset(dataset_path, caption_text)

    os.environ['HF_TOKEN'] = hf_token
    os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
    sys.path.append(ai_toolkit_path)

    try:
        from toolkit.job import run_job
    except Exception as e:
        print("Error in import run_job.")

    prompt_variants = [
        "a top-down view from the center of the living room",
        "a top-down view from the center of the living room",
        "a top-down view from the center of the living room",
        "a top-down view from the center of the living room",
    ]

    job_to_run = OrderedDict([
        ('job', 'extension'),
        ('config', OrderedDict([
            ('name', 'living_room_top_view'),
            ('process', [
                OrderedDict([
                    ('type', 'sd_trainer'),
                    ('training_folder', output_dir),
                    ('device', 'cuda'),
                    ('network', OrderedDict([
                        ('type', 'lora'),
                        ('linear', 16),
                        ('linear_alpha', 16)
                    ])),
                    ('save', OrderedDict([
                        ('dtype', 'bf16'),
                        ('save_every', 250),
                        ('max_step_saves_to_keep', 4)
                    ])),
                    ('datasets', [
                        OrderedDict([
                            ('folder_path', dataset_path),
                            ('caption_ext', 'txt'),
                            ('caption_dropout_rate', 0.05),
                            ('shuffle_tokens', False),
                            ('cache_latents_to_disk', True),
                            ('resolution', [512, 768, 1024])
                        ])
                    ]),
                    ('train', OrderedDict([
                        ('batch_size', 8),
                        ('steps', 5000),
                        ('gradient_accumulation_steps', 2),
                        ('train_unet', True),
                        ('train_text_encoder', False),
                        ('content_or_style', 'balanced'),
                        ('gradient_checkpointing', True),
                        ('noise_scheduler', 'flowmatch'),
                        ('optimizer', 'adamw8bit'),
                        ('lr', 1e-4),
                        ('ema_config', OrderedDict([
                            ('use_ema', True),
                            ('ema_decay', 0.99)
                        ])),
                        ('dtype', 'bf16')
                    ])),
                    ('model', OrderedDict([
                        ('name_or_path', 'black-forest-labs/FLUX.1-dev'),
                        ('is_flux', True),
                        ('quantize', True),
                        ('dtype', 'bf16'),
                        ('force_download', True)
                    ])),
                    ('sample', OrderedDict([
                        ('sampler', 'flowmatch'),
                        ('sample_every', 100),
                        ('width', 1024),
                        ('height', 1024),
                        ('prompts', prompt_variants),
                        ('neg', ''),
                        ('seed', 0),  
                        ('walk_seed', True),
                        ('guidance_scale', 4),
                        ('sample_steps', 20)
                    ]))
                ])
            ])
        ])),
        ('meta', OrderedDict([
            ('name', '[name]'),
            ('version', '1.0')
        ]))
    ])

    run_job(job_to_run) 

if __name__ == "__main__":
    main()
