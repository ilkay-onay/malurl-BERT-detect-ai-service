# src/config.py
import torch

class Config:
    # --- Model Ayarları ---
    MODEL_NAME = "answerdotai/ModernBERT-base" 
    MAX_LENGTH = 256 # URL'lerin %99'u için yeterli.
    
    # --- Dosya Yolları ---
    EXP_NAME = "V3-hybrid" # Her yeni denemede burayı değiştir
    OUTPUT_DIR = f"outputs/{EXP_NAME}/"
    LOG_DIR = f"logs/{EXP_NAME}/"
    PLOT_DIR = f"plots/{EXP_NAME}/"
    
    # --- Hiperparametreler (KRİTİK GÜNCELLEMELER) ---
    BATCH_SIZE = 32 
    GRADIENT_ACCUMULATION_STEPS = 2 # Effective Batch Size = 64 olur. Daha stabil eğitim sağlar.
    
    EPOCHS = 5 
    # Learning Rate'i düşürdük (5e-5 çok hızlıydı, ezberletiyordu)
    LEARNING_RATE = 2e-5 
    
    # Weight Decay'i artırdık (0.01'den 0.1'e - Ezberlemeyi zorlaştıran en önemli ayar!)
    WEIGHT_DECAY = 0.1 
    
    # Warmup ratio kullanmak daha profesyoneldir (Toplam adımın %10'u)
    WARMUP_RATIO = 0.1 
    
    LR_SCHEDULER = "cosine" # Linear yerine Cosine daha yumuşak bir iniş sağlar
    
    PATIENCE = 3 
    
    # --- Donanım ---
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    USE_BF16 = torch.cuda.is_available() and torch.cuda.is_bf16_supported()
    USE_FP16 = torch.cuda.is_available() and not USE_BF16