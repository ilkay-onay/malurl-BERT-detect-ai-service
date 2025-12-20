# src/config.py
import torch

class Config:
    MODEL_NAME = "answerdotai/ModernBERT-base" 
    MAX_LENGTH = 256
    
    OUTPUT_DIR = "outputs/"
    LOG_DIR = "logs/"
    PLOT_DIR = "plots/"
    
    BATCH_SIZE = 32 
    EPOCHS = 5 
    LEARNING_RATE = 5e-5 
    WEIGHT_DECAY = 0.01
    WARMUP_STEPS = 1000 
    PATIENCE = 3 
    
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    
    # NEW: Check if hardware supports BF16 (RTX 30/40/A-series)
    # This is the modern standard for 2025.
    USE_BF16 = torch.cuda.is_available() and torch.cuda.is_bf16_supported()
    USE_FP16 = torch.cuda.is_available() and not USE_BF16