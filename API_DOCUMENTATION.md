# ModernBERT URL Phishing Detector - API Dokümantasyonu

## 📖 Genel Bakış

Bu API, ModernBERT tabanlı derin öğrenme modelini kullanarak URL'leri analiz eder ve phishing/malicious içerik tespiti yapar.

**Base URL:** `http://localhost:8000`

**API Version:** `1.0.0`

---

## 🚀 Hızlı Başlangıç

### 1. Gereksinimleri Yükleyin

```bash
pip install -r requirements.txt
```

### 2. API'yi Başlatın

```bash
python app.py
```

Alternatif olarak doğrudan uvicorn ile:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### 3. API Dokümantasyonuna Erişin

API başlatıldıktan sonra şu adreslerde interaktif dokümantasyona erişebilirsiniz:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 📋 Endpoint'ler

### 1. Root Endpoint

**GET** `/`

API hakkında genel bilgi döner.

#### Örnek İstek

```bash
curl http://localhost:8000/
```

#### Örnek Yanıt

```json
{
  "message": "ModernBERT URL Phishing Detector API",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health",
  "endpoints": {
    "analyze": "POST /analyze",
    "batch_analyze": "POST /analyze/batch",
    "model_info": "GET /model/info"
  }
}
```

---

### 2. Health Check

**GET** `/health`

Servis sağlık durumunu kontrol eder.

#### Örnek İstek

```bash
curl http://localhost:8000/health
```

#### Örnek Yanıt

```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_path": "outputs/V3-hybrid/production_model",
  "device": "cuda"
}
```

#### Yanıt Alanları

| Alan | Tip | Açıklama |
|------|-----|----------|
| `status` | string | `healthy` veya `degraded` |
| `model_loaded` | boolean | Model başarıyla yüklendiyse `true` |
| `model_path` | string | Model dosyalarının bulunduğu dizin |
| `device` | string | Kullanılan cihaz (`cuda` veya `cpu`) |

---

### 3. Model Bilgileri

**GET** `/model/info`

Yüklenmiş model hakkında detaylı bilgi döner.

#### Örnek İstek

```bash
curl http://localhost:8000/model/info
```

#### Örnek Yanıt

```json
{
  "model_path": "outputs/V3-hybrid/production_model",
  "device": "cuda",
  "dtype": "torch.bfloat16",
  "attention_implementation": "flash_attention_2"
}
```

#### Yanıt Alanları

| Alan | Tip | Açıklama |
|------|-----|----------|
| `model_path` | string | Model dizini |
| `device` | string | Kullanılan cihaz |
| `dtype` | string | Veri tipi (float32/bfloat16) |
| `attention_implementation` | string | Attention mekanizması implementasyonu |

---

### 4. Tekli URL Analizi

**POST** `/analyze`

Tek bir URL'yi analiz eder ve phishing riski değerlendirmesi yapar.

#### İstek Gövdesi

```json
{
  "url": "https://secure-login-verify.suspicious-domain.tk/login"
}
```

#### Örnek İstek (cURL)

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://secure-login-verify.suspicious-domain.tk/login"}'
```

#### Örnek İstek (Python)

```python
import requests

response = requests.post(
    "http://localhost:8000/analyze",
    json={"url": "https://secure-login-verify.suspicious-domain.tk/login"}
)
result = response.json()
print(result)
```

#### Örnek Yanıt

```json
{
  "url": "https://secure-login-verify.suspicious-domain.tk/login",
  "risk": "high",
  "category": "PHISHING",
  "confidence": "94.23%",
  "description": "Critical Match: Malicious pattern detected."
}
```

#### Yanıt Alanları

| Alan | Tip | Açıklama |
|------|-----|----------|
| `url` | string | Analiz edilen URL |
| `risk` | string | Risk seviyesi: `low`, `medium`, `high` |
| `category` | string | Kategori: `LEGITIMATE`, `SUSPICIOUS`, `PHISHING` |
| `confidence` | string | Model güven skoru (yüzde) |
| `description` | string | Sonuç açıklaması |

#### Risk Seviyeleri

- **`low`** (Düşük Risk): Phishing olasılığı < %50
- **`medium`** (Orta Risk): Phishing olasılığı %50-85 arası
- **`high`** (Yüksek Risk): Phishing olasılığı > %85

#### Hata Kodları

| Kod | Açıklama |
|-----|----------|
| `200` | Başarılı |
| `422` | Geçersiz istek (validation hatası) |
| `500` | Sunucu hatası |
| `503` | Model yüklenmemiş |

---

### 5. Toplu URL Analizi

**POST** `/analyze/batch`

Birden fazla URL'yi toplu olarak analiz eder (maksimum 100 URL).

#### İstek Gövdesi

```json
{
  "urls": [
    "https://google.com",
    "https://secure-login-verify.suspicious-domain.tk/login",
    "http://paypal-verify-account.xyz/secure"
  ]
}
```

#### Örnek İstek (cURL)

```bash
curl -X POST http://localhost:8000/analyze/batch \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://google.com",
      "https://secure-login-verify.suspicious-domain.tk/login",
      "http://paypal-verify-account.xyz/secure"
    ]
  }'
```

#### Örnek İstek (Python)

```python
import requests

urls = [
    "https://google.com",
    "https://secure-login-verify.suspicious-domain.tk/login",
    "http://paypal-verify-account.xyz/secure"
]

response = requests.post(
    "http://localhost:8000/analyze/batch",
    json={"urls": urls}
)
result = response.json()
print(f"Total Analyzed: {result['total']}")
print(f"Phishing Detected: {result['summary']['phishing']}")
```

#### Örnek Yanıt

```json
{
  "total": 3,
  "results": [
    {
      "url": "https://google.com",
      "risk": "low",
      "category": "LEGITIMATE",
      "confidence": "2.34%",
      "description": "Safe: No phishing characteristics identified."
    },
    {
      "url": "https://secure-login-verify.suspicious-domain.tk/login",
      "risk": "high",
      "category": "PHISHING",
      "confidence": "94.23%",
      "description": "Critical Match: Malicious pattern detected."
    },
    {
      "url": "http://paypal-verify-account.xyz/secure",
      "risk": "high",
      "category": "PHISHING",
      "confidence": "89.45%",
      "description": "Critical Match: Malicious pattern detected."
    }
  ],
  "summary": {
    "total_analyzed": 3,
    "total_errors": 0,
    "legitimate": 1,
    "suspicious": 0,
    "phishing": 2,
    "high_risk": 2,
    "medium_risk": 0,
    "low_risk": 1
  }
}
```

#### Yanıt Alanları

| Alan | Tip | Açıklama |
|------|-----|----------|
| `total` | integer | Başarıyla analiz edilen URL sayısı |
| `results` | array | Her URL için analiz sonuçları |
| `summary` | object | Özet istatistikler |

#### Summary (Özet) Alanları

| Alan | Tip | Açıklama |
|------|-----|----------|
| `total_analyzed` | integer | Toplam analiz edilen URL |
| `total_errors` | integer | Hata sayısı |
| `legitimate` | integer | Güvenli URL sayısı |
| `suspicious` | integer | Şüpheli URL sayısı |
| `phishing` | integer | Phishing URL sayısı |
| `high_risk` | integer | Yüksek riskli URL sayısı |
| `medium_risk` | integer | Orta riskli URL sayısı |
| `low_risk` | integer | Düşük riskli URL sayısı |

#### Limitler

- **Maksimum URL sayısı:** 100
- **Minimum URL sayısı:** 1

---

## 🔒 Güvenlik ve En İyi Pratikler

### Rate Limiting

Production ortamında rate limiting uygulamanız önerilir:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/analyze")
@limiter.limit("10/minute")
async def analyze_url(request: Request, url_request: URLRequest):
    # ...
```

### CORS

Production'da CORS ayarlarını özelleştirin:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Spesifik domainler
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### HTTPS

Production'da mutlaka HTTPS kullanın:

```bash
uvicorn app:app --host 0.0.0.0 --port 443 --ssl-keyfile key.pem --ssl-certfile cert.pem
```

---

## 🧪 Test Etme

### Test Script'i Çalıştırma

```bash
# Önce API'yi başlatın (ayrı bir terminal)
python app.py

# Sonra test script'ini çalıştırın
python test_api.py
```

### Manuel Test (cURL)

```bash
# Health check
curl http://localhost:8000/health

# Tek URL testi
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://google.com"}'

# Toplu test
curl -X POST http://localhost:8000/analyze/batch \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://google.com", "http://suspicious-site.tk"]}'
```

### Postman Collection

API'yi test etmek için Postman koleksiyonu:

1. Postman'i açın
2. Import → Raw text
3. Aşağıdaki JSON'u yapıştırın:

```json
{
  "info": {
    "name": "URL Phishing Detector API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "http://localhost:8000/health",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["health"]
        }
      }
    },
    {
      "name": "Analyze Single URL",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\"url\": \"https://google.com\"}"
        },
        "url": {
          "raw": "http://localhost:8000/analyze",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["analyze"]
        }
      }
    },
    {
      "name": "Analyze Batch URLs",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\"urls\": [\"https://google.com\", \"http://suspicious-site.tk\"]}"
        },
        "url": {
          "raw": "http://localhost:8000/analyze/batch",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["analyze", "batch"]
        }
      }
    }
  ]
}
```

---

## 🌍 Ortam Değişkenleri

API'yi özelleştirmek için aşağıdaki ortam değişkenlerini kullanabilirsiniz:

| Değişken | Açıklama | Varsayılan |
|----------|----------|-----------|
| `MODEL_DIR` | Model dosyalarının bulunduğu dizin | `outputs/V3-hybrid/production_model` |
| `HOST` | API host adresi | `0.0.0.0` |
| `PORT` | API port numarası | `8000` |

### Kullanım

```bash
# Linux/Mac
export MODEL_DIR="path/to/your/model"
export PORT=9000
python app.py

# Windows (CMD)
set MODEL_DIR=path\to\your\model
set PORT=9000
python app.py

# Windows (PowerShell)
$env:MODEL_DIR="path\to\your\model"
$env:PORT=9000
python app.py
```

---

## 🐳 Docker Desteği

### Dockerfile Örneği

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Gereksinimleri yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarını kopyala
COPY . .

# Port aç
EXPOSE 8000

# Uygulamayı başlat
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./outputs:/app/outputs
    environment:
      - MODEL_DIR=/app/outputs/V3-hybrid/production_model
    restart: unless-stopped
```

### Çalıştırma

```bash
# Build
docker build -t url-phishing-detector .

# Run
docker run -p 8000:8000 -v $(pwd)/outputs:/app/outputs url-phishing-detector

# Docker Compose ile
docker-compose up -d
```

---

## 📊 Performans

### Beklenen Yanıt Süreleri

| Endpoint | Ortalama Süre | Notlar |
|----------|---------------|--------|
| `/health` | < 10ms | Basit durum kontrolü |
| `/analyze` | 50-200ms | GPU ile ~50ms, CPU ile ~200ms |
| `/analyze/batch` (10 URL) | 200-800ms | GPU ile daha hızlı |

### Optimizasyon İpuçları

1. **GPU Kullanımı**: CUDA destekli GPU kullanımı 3-4x hızlandırma sağlar
2. **Batch Processing**: Birden fazla URL için batch endpoint'i kullanın
3. **Model Caching**: Model yalnızca startup'ta yüklenir, sonraki istekler hızlıdır
4. **Connection Pooling**: Yüksek trafikte connection pooling kullanın

---

## ❓ Sık Sorulan Sorular

### Q: Model dosyaları nerede olmalı?

**A:** Model dosyaları `MODEL_DIR` ortam değişkeninde belirtilen dizinde olmalıdır. Varsayılan: `outputs/V3-hybrid/production_model`

### Q: API çalışmıyor, ne yapmalıyım?

**A:** Şu adımları izleyin:
1. Model dosyalarının doğru dizinde olduğunu kontrol edin
2. `/health` endpoint'ini kontrol edin
3. Logları inceleyin
4. Gereksinimlerin yüklü olduğunu doğrulayın

### Q: Batch işlemde 100'den fazla URL gönderebilir miyim?

**A:** Hayır, batch endpoint'i maksimum 100 URL kabul eder. Daha fazla URL için istekleri bölün.

### Q: API production'da nasıl deploy edilir?

**A:** 
- Gunicorn/Uvicorn workers ile çalıştırın
- Nginx reverse proxy kullanın
- HTTPS sertifikası ekleyin
- Rate limiting uygulayın
- Docker container'da deploy edin

---

## 📞 Destek

Sorularınız veya sorunlarınız için:
- GitHub Issues
- Email: support@example.com
- Documentation: http://localhost:8000/docs

---

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.
