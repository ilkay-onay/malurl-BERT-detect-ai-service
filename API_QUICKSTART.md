# 🚀 FastAPI Hızlı Başlangıç Kılavuzu

ModernBERT URL Phishing Detector API'yi hızlıca çalıştırmak için bu kılavuzu takip edin.

## ⚡ 3 Adımda Başlayın

### 1️⃣ Gereksinimleri Yükleyin

```bash
pip install -r requirements.txt
```

**Yüklenen paketler:**
- FastAPI - Web framework
- Uvicorn - ASGI server
- Pydantic - Data validation
- Transformers, PyTorch - ML modeli için

### 2️⃣ Model Kontrolü

API'nin çalışması için eğitilmiş model dosyalarının olması gerekir:

```bash
# Varsayılan model dizini
outputs/V3-hybrid/production_model/
```

Model yoksa şu mesajı alırsınız:
```
⚠️ Servis model olmadan başlatılıyor (health endpoint hariç API çalışmayacak)
```

### 3️⃣ API'yi Başlatın

**Yöntem 1: Python ile**
```bash
python app.py
```

**Yöntem 2: Uvicorn ile (önerilen)**
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

**Yöntem 3: Farklı port ile**
```bash
# Windows CMD
set PORT=9000
python app.py

# Linux/Mac
export PORT=9000
python app.py
```

### ✅ Doğrulama

API başarıyla başladığında şu çıktıyı göreceksiniz:

```
INFO:     Started server process
INFO:     Waiting for application startup.
🚀 FastAPI servisi başlatılıyor...
📁 Model dizini: outputs/V3-hybrid/production_model
📡 Loading ModernBERT model from outputs/V3-hybrid/production_model...
✅ Analyzer ready on cuda
✅ Model başarıyla yüklendi
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Tarayıcınızdan şu adreslere gidin:
- 📚 **API Docs (Swagger)**: http://localhost:8000/docs
- 📖 **ReDoc**: http://localhost:8000/redoc
- 💚 **Health Check**: http://localhost:8000/health

---

## 🧪 İlk Testiniz

### Test 1: Health Check

```bash
curl http://localhost:8000/health
```

**Beklenen yanıt:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_path": "outputs/V3-hybrid/production_model",
  "device": "cuda"
}
```

### Test 2: Tekli URL Analizi

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://google.com"}'
```

**Beklenen yanıt:**
```json
{
  "url": "https://google.com",
  "risk": "low",
  "category": "LEGITIMATE",
  "confidence": "2.34%",
  "description": "Safe: No phishing characteristics identified."
}
```

### Test 3: Şüpheli URL Testi

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "http://paypal-verify-account.xyz/secure/login.php"}'
```

**Beklenen yanıt:**
```json
{
  "url": "http://paypal-verify-account.xyz/secure/login.php",
  "risk": "high",
  "category": "PHISHING",
  "confidence": "89.45%",
  "description": "Critical Match: Malicious pattern detected."
}
```

### Test 4: Toplu Analiz

```bash
curl -X POST http://localhost:8000/analyze/batch \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://google.com",
      "https://github.com",
      "http://suspicious-login.tk"
    ]
  }'
```

### Test 5: Otomatik Test Script'i

```bash
python test_api.py
```

Bu script tüm endpoint'leri otomatik olarak test eder ve detaylı rapor sunar.

---

## 🔧 Sorun Giderme

### ❌ Problem: "Model bulunamadı"

**Çözüm:**
```bash
# Model dizinini kontrol edin
ls outputs/V3-hybrid/production_model/

# veya farklı bir model dizini belirtin
export MODEL_DIR="outputs/phiusiil_v1/production_model"
python app.py
```

### ❌ Problem: "Port already in use"

**Çözüm:**
```bash
# Farklı bir port kullanın
export PORT=9000
python app.py

# veya mevcut işlemi durdurun (Linux/Mac)
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F
```

### ❌ Problem: "Module not found"

**Çözüm:**
```bash
# Tüm gereksinimleri yeniden yükleyin
pip install -r requirements.txt --force-reinstall

# Veya tek tek yükleyin
pip install fastapi uvicorn pydantic
```

### ❌ Problem: CUDA hatası

**Çözüm:**
API otomatik olarak CPU'ya geçer. Ancak GPU kullanmak isterseniz:
```bash
# CUDA kurulumu kontrolü
python -c "import torch; print(torch.cuda.is_available())"

# CPU'da çalıştırma (GPU olmadan)
# API otomatik olarak CPU'yu algılar, ekstra bir şey yapmanıza gerek yok
```

---

## 💡 Kullanım İpuçları

### Python ile Kullanım

```python
import requests

# API base URL
API_URL = "http://localhost:8000"

# Tekli analiz
def analyze_url(url):
    response = requests.post(
        f"{API_URL}/analyze",
        json={"url": url}
    )
    return response.json()

# Kullanım
result = analyze_url("https://suspicious-site.tk")
print(f"Category: {result['category']}")
print(f"Risk: {result['risk']}")
print(f"Confidence: {result['confidence']}")
```

### JavaScript/Node.js ile Kullanım

```javascript
// fetch API ile
async function analyzeURL(url) {
    const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url })
    });
    return await response.json();
}

// Kullanım
analyzeURL('https://suspicious-site.tk')
    .then(result => {
        console.log('Category:', result.category);
        console.log('Risk:', result.risk);
    });
```

### cURL Örnekleri (Daha Fazla)

```bash
# Pretty print ile
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://test.com"}' | python -m json.tool

# Dosyadan URL listesi okuma
curl -X POST http://localhost:8000/analyze/batch \
  -H "Content-Type: application/json" \
  -d @urls.json

# urls.json içeriği:
# {
#   "urls": [
#     "https://site1.com",
#     "https://site2.com"
#   ]
# }
```

---

## 📱 Frontend Entegrasyonu

### React Örneği

```jsx
import React, { useState } from 'react';

function URLChecker() {
    const [url, setUrl] = useState('');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);

    const checkURL = async () => {
        setLoading(true);
        try {
            const response = await fetch('http://localhost:8000/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });
            const data = await response.json();
            setResult(data);
        } catch (error) {
            console.error('Error:', error);
        }
        setLoading(false);
    };

    return (
        <div>
            <input 
                value={url} 
                onChange={(e) => setUrl(e.target.value)}
                placeholder="Enter URL to check"
            />
            <button onClick={checkURL} disabled={loading}>
                {loading ? 'Checking...' : 'Check URL'}
            </button>
            
            {result && (
                <div className={`result ${result.risk}`}>
                    <h3>{result.category}</h3>
                    <p>Risk: {result.risk}</p>
                    <p>Confidence: {result.confidence}</p>
                    <p>{result.description}</p>
                </div>
            )}
        </div>
    );
}
```

---

## 🎯 Sonraki Adımlar

1. ✅ API'yi başarıyla çalıştırdınız
2. 📖 [Detaylı API Dokümantasyonunu](API_DOCUMENTATION.md) okuyun
3. 🔧 Kendi uygulamanıza entegre edin
4. 🚀 Production'a deploy edin

**Detaylı bilgi için:**
- API Dokümantasyonu: `API_DOCUMENTATION.md`
- Interactive Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📊 Performans Beklentileri

| Cihaz | Tek URL | 10 URL (Batch) | 100 URL (Batch) |
|-------|---------|----------------|-----------------|
| CUDA GPU | ~50ms | ~200ms | ~1.5s |
| CPU | ~200ms | ~800ms | ~6s |

---

## ✨ Özellikler

- ✅ Otomatik GPU/CPU algılama
- ✅ Batch processing (100 URL'ye kadar)
- ✅ Interactive API documentation (Swagger)
- ✅ CORS desteği (Frontend entegrasyonu için)
- ✅ Validation ve error handling
- ✅ Health check endpoint
- ✅ Model bilgileri endpoint
- ✅ Production-ready mimari

---

**🎉 Tebrikler! API'niz hazır ve çalışıyor.**

Sorularınız için: http://localhost:8000/docs adresindeki interaktif dokümantasyonu kullanın.
