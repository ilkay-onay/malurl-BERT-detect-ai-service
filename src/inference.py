import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os
import sys

class URLAnalyzer:
    def __init__(self, model_path="outputs/production_model"):
        """
        Initializes the analyzer by loading the fine-tuned ModernBERT model.
        """
        print(f"📡 Loading ModernBERT model from {model_path}...")
        
        # 1. Hardware Selection
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # 2. Logic to determine the best attention implementation (Strict for ModernBERT)
        self.attn_implementation = "sdpa" # Default fast version
        if self.device.type == "cuda":
            try:
                import flash_attn
                if torch.cuda.get_device_capability()[0] >= 7:
                    self.attn_implementation = "flash_attention_2"
                    print("⚡ Inference: Flash Attention 2 & Unpadding Enabled!")
            except ImportError:
                print("🔹 Inference: Flash Attention 2 not found. Using SDPA.")
        else:
            print("💻 Inference: CPU detected. Using SDPA.")

        # 3. Load Assets
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        
        # 4. Determine Precision
        # BF16 for GPU (if supported), FP32 for CPU
        self.dtype = torch.bfloat16 if (torch.cuda.is_available() and torch.cuda.is_bf16_supported()) else torch.float32
        
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_path,
            dtype=self.dtype, # Fixed deprecation: torch_dtype -> dtype
            attn_implementation=self.attn_implementation
        ).to(self.device)
        
        self.model.eval() # Set to evaluation mode
        print(f"✅ Analyzer ready on {self.device} ({self.dtype})")

    def analyze(self, url: str):
        """
        Analyzes a single URL and returns a structured security report.
        """
        # Preprocess & Tokenize
        inputs = self.tokenizer(
            url,
            return_tensors="pt",
            truncation=True,
            max_length=256,
            padding=True
        ).to(self.device)

        # Inference
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = F.softmax(outputs.logits, dim=-1)
            
        # Extract Phishing Score (Index 1)
        phish_prob = probs[0][1].item()
        confidence = round(phish_prob * 100, 2)

        # Result Mapping
        if phish_prob > 0.85:
            risk, category = "high", "PHISHING"
            desc = "Critical Match: This URL structure matches verified malicious patterns."
        elif phish_prob > 0.50:
            risk, category = "medium", "SUSPICIOUS"
            desc = "Caution: Anomalies detected that are common in typosquatting attempts."
        else:
            risk, category = "low", "LEGITIMATE"
            desc = "Safe: No significant phishing characteristics were identified."

        return {
            "url": url,
            "risk": risk,
            "category": category,
            "confidence": f"{confidence}%",
            "description": desc,
            "raw_score": phish_prob
        }

if __name__ == "__main__":
    # Test block
    MODEL_DIR = "outputs/production_model"
    if not os.path.exists(MODEL_DIR):
        print(f"❌ Error: {MODEL_DIR} not found.")
    else:
        analyzer = URLAnalyzer(MODEL_DIR)
        print("\n🔍 Result for google.com:", analyzer.analyze("https://google.com")['category'])