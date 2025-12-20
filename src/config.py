# src/config.py
import torch

class Config:
    MODEL_NAME = "google-bert/bert-base-uncased"
    MAX_LENGTH = 256
    
    OUTPUT_DIR = "outputs/"
    LOG_DIR = "logs/"
    PLOT_DIR = "plots/"
    
    # Hyperparameters
    BATCH_SIZE = 16 
    EPOCHS = 5 # BERT usually converges in 3-5 epochs on 600k rows
    LEARNING_RATE = 2e-5
    WEIGHT_DECAY = 0.01
    WARMUP_STEPS = 500
    PATIENCE = 3 # Early stopping patience
    
    # Hardware
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    FP16 = True if torch.cuda.is_available() else False # Mixed precision only for Nvidia GPUs