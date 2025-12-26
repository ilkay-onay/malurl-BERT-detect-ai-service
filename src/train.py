# src/train.py
import os
import sys
import torch
import numpy as np
from transformers import (
    AutoModelForSequenceClassification, 
    TrainingArguments, 
    Trainer, 
    EarlyStoppingCallback,
    DataCollatorWithPadding
)
from .config import Config
from .data_manager import URLDataManager
from .metrics import compute_metrics, generate_report_visuals

# ==========================================
# 🚩 MASTER CONTROLS
IS_BABY_RUN = False  # Set to False for the real 650k training!
# ==========================================

def train():
    print("\n" + "="*70)
    print(f"🚀 MODERN-BERT ULTIMATE PIPELINE (256-LENGTH / BF16 / COMPILED)")
    print(f"🛠️  MODE: {'BABY SMOKE TEST' if IS_BABY_RUN else 'PRODUCTION TRAINING'}")
    print("="*70)

    # --- 1. Infrastructure Setup ---
    for d in [Config.OUTPUT_DIR, Config.LOG_DIR, Config.PLOT_DIR]:
        if not os.path.exists(d): os.makedirs(d)
    
    # G�NCEL KONTROL: Fiziksel split dosyalar\u0131 var m\u0131?
    required_files = ["data/train.csv", "data/val.csv", "data/test.csv"]
    if not all(os.path.exists(f) for f in required_files) and not IS_BABY_RUN:
        print("\u274c ERROR: Physical split files (train/val/test.csv) missing. Run src/data_prep.py first.")
        sys.exit(1)

    # --- 2. Load Data ---
    dm = URLDataManager(Config.MODEL_NAME)
    tokenized_datasets = dm.get_hf_dataset(is_baby_run=IS_BABY_RUN)
    print(f"📊 Data ready. Train: {len(tokenized_datasets['train'])} samples.")

    # --- 3. Hardware & Precision Detection ---
    attn_implementation = "sdpa"
    try:
        import flash_attn
        if torch.cuda.is_available() and torch.cuda.get_device_capability()[0] >= 7:
            attn_implementation = "flash_attention_2"
            print("⚡ Flash Attention 2 & Unpadding Enabled!")
    except ImportError:
        print("🔹 Flash Attention 2 not found. Using SDPA.")

    dtype = torch.bfloat16 if Config.USE_BF16 else (torch.float16 if Config.USE_FP16 else torch.float32)
    print(f"💎 Precision Mode: {str(dtype).split('.')[-1].upper()}")

    # --- 4. Load Model ---
    print(f"📥 Loading {Config.MODEL_NAME}...")
    model = AutoModelForSequenceClassification.from_pretrained(
        Config.MODEL_NAME, 
        num_labels=2,
        attn_implementation=attn_implementation,
        dtype=dtype,  # <--- Change torch_dtype to just dtype
    ).to(Config.DEVICE)

    # --- 5. Training Arguments (ModernBERT Best Practices) ---
    eval_steps = 10 if IS_BABY_RUN else 2000
    save_steps = 10 if IS_BABY_RUN else 2000

    training_args = TrainingArguments(
        output_dir=Config.OUTPUT_DIR,
        overwrite_output_dir=not IS_BABY_RUN,
        
        # CRITICAL FIX FOR TORCH.COMPILE:
        remove_unused_columns=False, 
        
        num_train_epochs=1 if IS_BABY_RUN else Config.EPOCHS,
        per_device_train_batch_size=Config.BATCH_SIZE,
        per_device_eval_batch_size=Config.BATCH_SIZE,
        learning_rate=Config.LEARNING_RATE,
        weight_decay=Config.WEIGHT_DECAY,
        
        # BURAYI GÜNCELLEDİK: warmup_steps yerine warmup_ratio kullanıyoruz
        warmup_ratio=0.1 if not IS_BABY_RUN else 0.0, 
        lr_scheduler_type=Config.LR_SCHEDULER, # Config'e eklediğimiz cosine scheduler
        
        bf16=Config.USE_BF16,
        fp16=Config.USE_FP16,
        gradient_accumulation_steps=Config.GRADIENT_ACCUMULATION_STEPS, 
        
        eval_strategy="steps",
        eval_steps=eval_steps,
        save_strategy="steps",
        save_steps=save_steps,
        logging_steps=5 if IS_BABY_RUN else 50,
        
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        save_total_limit=2,
        report_to="tensorboard",
        logging_dir=Config.LOG_DIR,
        dataloader_num_workers=4 if not IS_BABY_RUN else 0,
    )

    # --- 6. Initialize Trainer ---
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["validation"],
        data_collator=DataCollatorWithPadding(tokenizer=dm.tokenizer),
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=Config.PATIENCE)]
    )

    # --- 7. TURBO: Torch Compile (After Trainer Init) ---
    if not IS_BABY_RUN and hasattr(torch, 'compile') and sys.platform != 'win32':
        try:
            print("🚀 Compiling Trainer model with TorchDynamo (Graph Capture)...")
            trainer.model = torch.compile(trainer.model)
        except Exception as e:
            print(f"⚠️  Compilation skipped (standard training will proceed): {e}")

    # --- 8. Auto-Resume Logic ---
    last_checkpoint = None
    if not IS_BABY_RUN and os.path.isdir(Config.OUTPUT_DIR):
        checkpoints = [os.path.join(Config.OUTPUT_DIR, d) for d in os.listdir(Config.OUTPUT_DIR) if d.startswith("checkpoint-")]
        if checkpoints:
            last_checkpoint = max(checkpoints, key=os.path.getmtime)
            print(f"🔄 Resuming from last checkpoint: {last_checkpoint}")

    # --- 9. Start Training ---
    print(f"▶️  Training Cycle Started. Best weights will be saved to end.")
    try:
        trainer.train(resume_from_checkpoint=last_checkpoint)
    except RuntimeError as e:
        if "out of memory" in str(e):
            print("\n❌ IDIOT-PROOF ERROR: GPU Out of Memory. Decrease BATCH_SIZE in config.py.")
            sys.exit(1)
        raise e

    # --- 10. Final Hold-out Evaluation & Reports ---
    print("\n🏁 Generating Final Production Analytics...")
    test_results = trainer.predict(tokenized_datasets["test"])
    
    y_true = test_results.label_ids
    # Convert logits to probabilities via Softmax
    y_probs = torch.nn.functional.softmax(torch.tensor(test_results.predictions), dim=-1)[:, 1].numpy()
    y_pred = np.argmax(test_results.predictions, axis=-1)

    generate_report_visuals(y_true, y_pred, y_probs, suffix="MODERN_BERT_FINAL")
    
    # --- 11. Final Save ---
    if not IS_BABY_RUN:
        final_path = os.path.join(Config.OUTPUT_DIR, "production_model")
        trainer.save_model(final_path)
        dm.tokenizer.save_pretrained(final_path)
        print(f"\n✅ TRAINING SUCCESSFUL! Model stored at: {final_path}")
    else:
        print("\n✅ Baby test success! Ready for full-scale production run.")

if __name__ == "__main__":
    train()