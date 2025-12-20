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
# 🚩 TOGGLE THIS FOR TESTING
IS_BABY_RUN = False  # Set to False for real training
# ==========================================

def train():
    print("\n" + "="*60)
    print(f"🚀 {'BABY SMOKE TEST' if IS_BABY_RUN else 'FULL PRODUCTION TRAINING'}")
    print("="*60)

    # idiot Proofing: Directories
    for d in [Config.OUTPUT_DIR, Config.LOG_DIR, Config.PLOT_DIR]:
        if not os.path.exists(d): os.makedirs(d)
    
    if not os.path.exists("data/processed_dataset.csv"):
        print("❌ ERROR: data/processed_dataset.csv missing. Run data_manager first.")
        sys.exit(1)

    # 1. Load Data
    dm = URLDataManager(Config.MODEL_NAME)
    tokenized_datasets = dm.get_hf_dataset(is_baby_run=IS_BABY_RUN)
    
    # 2. Adjust intervals for Baby Run
    eval_steps = 10 if IS_BABY_RUN else 500
    save_steps = 10 if IS_BABY_RUN else 500
    epochs = 1 if IS_BABY_RUN else Config.EPOCHS

    # 3. Load Model
    print(f"📥 Loading {Config.MODEL_NAME}...")
    model = AutoModelForSequenceClassification.from_pretrained(
        Config.MODEL_NAME, num_labels=2
    ).to(Config.DEVICE)

# 4. Define Training Arguments
    training_args = TrainingArguments(
        output_dir=Config.OUTPUT_DIR,
        overwrite_output_dir=not IS_BABY_RUN,
        
        num_train_epochs=epochs,
        per_device_train_batch_size=Config.BATCH_SIZE,
        per_device_eval_batch_size=Config.BATCH_SIZE,
        learning_rate=Config.LEARNING_RATE,
        weight_decay=Config.WEIGHT_DECAY,
        warmup_steps=10 if IS_BABY_RUN else Config.WARMUP_STEPS,
        fp16=Config.FP16,
        gradient_accumulation_steps=1 if IS_BABY_RUN else 2,
        
        eval_strategy="steps",
        eval_steps=2000,    # <--- CHANGE THIS from 500 to 2000
        save_steps=2000,    # <--- CHANGE THIS from 500 to 2000
        
        logging_steps=50,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        save_total_limit=2,
        report_to="tensorboard",
        logging_dir=Config.LOG_DIR,
    )

    # 5. Initialize Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["validation"],
        data_collator=DataCollatorWithPadding(tokenizer=dm.tokenizer),
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=Config.PATIENCE)]
    )

    # 6. Train with Auto-Resume (Only if NOT baby run)
    last_checkpoint = None
    if not IS_BABY_RUN and os.path.isdir(Config.OUTPUT_DIR):
        checkpoints = [os.path.join(Config.OUTPUT_DIR, d) for d in os.listdir(Config.OUTPUT_DIR) if d.startswith("checkpoint-")]
        if checkpoints:
            last_checkpoint = max(checkpoints, key=os.path.getmtime)
            print(f"🔄 Resuming from {last_checkpoint}")

    print(f"▶️  Starting Loop...")
    try:
        trainer.train(resume_from_checkpoint=last_checkpoint)
    except RuntimeError as e:
        if "out of memory" in str(e):
            print("\n❌ OOM ERROR: Lower BATCH_SIZE in config.py")
            sys.exit(1)
        raise e

    # 7. Final Evaluation & Technical Visuals
    print("\n🏁 Generating Reports...")
    test_results = trainer.predict(tokenized_datasets["test"])
    y_true = test_results.label_ids
    y_probs = torch.nn.functional.softmax(torch.tensor(test_results.predictions), dim=-1)[:, 1].numpy()
    y_pred = np.argmax(test_results.predictions, axis=-1)

    generate_report_visuals(y_true, y_pred, y_probs, suffix="BABY" if IS_BABY_RUN else "FINAL")
    
    if not IS_BABY_RUN:
        final_path = os.path.join(Config.OUTPUT_DIR, "production_model")
        trainer.save_model(final_path)
        dm.tokenizer.save_pretrained(final_path)
        print(f"✅ Model saved at {final_path}")
    else:
        print("✅ Baby test complete! No errors found. Set IS_BABY_RUN = False for real training.")

if __name__ == "__main__":
    train()