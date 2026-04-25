# src/inference.py
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os

class URLAnalyzer:
    def __init__(self, model_path="outputs/production_model"):
        print(f"📡 Loading ModernBERT model from {model_path}...")
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # ModernBERT için optimize edilmiş attention seçimi
        self.attn_implementation = "sdpa"
        if self.device.type == "cuda":
            try:
                import flash_attn
                if torch.cuda.get_device_capability()[0] >= 7:
                    self.attn_implementation = "flash_attention_2"
            except ImportError:
                pass

        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        
        # Hassasiyet ayarı (BF16 veya FP32)
        self.dtype = torch.bfloat16 if (torch.cuda.is_available() and torch.cuda.is_bf16_supported()) else torch.float32
        
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_path,
            torch_dtype=self.dtype,
            attn_implementation=self.attn_implementation
        ).to(self.device)
        
        self.model.eval()
        print(f"✅ Analyzer ready on {self.device}")

    def analyze(self, url: str):
        inputs = self.tokenizer(
            url,
            return_tensors="pt",
            truncation=True,
            max_length=256,
            padding=True
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = F.softmax(outputs.logits, dim=-1)
            
        phish_prob = probs[0][1].item()
        confidence = round(phish_prob * 100, 2)

        if phish_prob > 0.85:
            risk, category = "high", "PHISHING"
            desc = "Critical Match: Malicious pattern detected."
        elif phish_prob > 0.60:
            risk, category = "medium", "SUSPICIOUS"
            desc = "Caution: Anomalous structure detected."
        else:
            risk, category = "low", "LEGITIMATE"
            desc = "Safe: No phishing characteristics identified."

        return {
            "url": url,
            "risk": risk,
            "category": category,
            "confidence": f"{confidence}%",
            "description": desc
        }