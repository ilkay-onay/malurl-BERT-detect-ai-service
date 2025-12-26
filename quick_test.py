# quick_test.py
import os
import sys
from src.inference import URLAnalyzer

# Modelin nerede olduğunu belirt (Eğitim bittikten sonra buraya kaydedilir)
MODEL_DIR = "outputs/V3-hybrid/production_model"

if not os.path.exists(MODEL_DIR):
    print(f"❌ HATA: Model bulunamadı! Lütfen önce eğitimi tamamlayın.")
    print(f"Aranan dizin: {MODEL_DIR}")
    sys.exit(1)

try:
    analyzer = URLAnalyzer(MODEL_DIR)
    
    print("\n" + "="*50)
    print("🚀 MODERN-BERT QUICK TEST")
    print("="*50)

    while True:
        url = input("\n🔗 Test edilecek URL (çıkış: q): ")
        if url.lower() == 'q': break
        
        res = analyzer.analyze(url)
        
        print(f"---")
        print(f"VERDICT: {res['category']}")
        print(f"CONFIDENCE: {res['confidence']}")
        print(f"DESC: {res['description']}")

except Exception as e:
    print(f"❌ Bir hata oluştu: {e}")