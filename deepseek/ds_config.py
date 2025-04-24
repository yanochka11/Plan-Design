{
  "bf16": {
    "enabled": true,
    "loss_scale": 0,
    "loss_scale_window": 1000,
    "initial_scale_power": 16,
    "hysteresis": 2,
    "min_loss_scale": 1
  },
  "optimizer": {
    "type": "AdamW",
    "params": {
      "lr": 5e-5,
      "betas": [0.9, 0.99],
      "weight_decay": 0.1
    }
  },
  "scheduler": {
    "type": "CosineAnnealingLR",
    "params": {
      "warmup_min_lr": 0,
      "warmup_max_lr": 5e-5,
      "warmup_num_steps": "auto",
      "total_num_steps": "auto"
    }
  },
  "zero_optimization": {
    "stage": 3,
    "offload_optimizer": {
      "device": "none"
    },
    "offload_param": {
      "device": "cpu",
      "pin_memory": true
    },
    "overlap_comm": true,
    "contiguous_gradients": true,
    "reduce_bucket_size": "auto",
    "stage3_prefetch_bucket_size": "auto",
    "stage3_param_persistence_threshold": "auto"
  },
  "gradient_accumulation_steps": 2,
  "gradient_clipping": 1.0,
  "train_micro_batch_size_per_gpu": 2,
  "train_batch_size": "auto",
  "steps_per_print": 15,
  "wall_clock_breakdown": false
}
