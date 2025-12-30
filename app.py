# app.py
"""
FastAPI Web Servisi - ModernBERT URL Phishing Detector
=======================================================
Bu servis, eğitilmiş ModernBERT modelini kullanarak URL'leri analiz eder
ve phishing/malicious içerik tespiti yapar.

Endpoint'ler:
    - POST /analyze - Tekli URL analizi
    - POST /analyze/batch - Toplu URL analizi
    - GET /health - Servis sağlık kontrolü
    - GET /model/info - Model bilgileri
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import List, Optional
import os
import sys
from contextlib import asynccontextmanager
import logging

from src.inference import URLAnalyzer

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global model instance
analyzer: Optional[URLAnalyzer] = None
MODEL_DIR = os.getenv("MODEL_DIR", "outputs/V3-hybrid/production_model")

# Pydantic Modelleri
class URLRequest(BaseModel):
    """Tekli URL analiz isteği"""
    url: str = Field(..., description="Analiz edilecek URL", min_length=3, max_length=2048)
    
    @validator('url')
    def validate_url(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('URL boş olamaz')
        # Basit URL format kontrolü
        if not any(v.startswith(prefix) for prefix in ['http://', 'https://', 'ftp://', 'www.']):
            # Eğer protokol yoksa http:// ekle
            v = 'http://' + v
        return v

    class Config:
        schema_extra = {
            "example": {
                "url": "https://secure-login-verify.suspicious-domain.tk/login"
            }
        }


class BatchURLRequest(BaseModel):
    """Toplu URL analiz isteği"""
    urls: List[str] = Field(..., description="Analiz edilecek URL listesi", min_items=1, max_items=100)
    
    @validator('urls')
    def validate_urls(cls, v):
        if len(v) > 100:
            raise ValueError('Maksimum 100 URL gönderilebilir')
        return [url.strip() for url in v if url.strip()]

    class Config:
        schema_extra = {
            "example": {
                "urls": [
                    "https://google.com",
                    "https://secure-login-verify.suspicious-domain.tk/login",
                    "http://paypal-verify-account.xyz/secure"
                ]
            }
        }


class AnalysisResponse(BaseModel):
    """URL analiz sonucu"""
    url: str = Field(..., description="Analiz edilen URL")
    risk: str = Field(..., description="Risk seviyesi: low, medium, high")
    category: str = Field(..., description="Kategori: LEGITIMATE, SUSPICIOUS, PHISHING")
    confidence: str = Field(..., description="Güven skoru (yüzde)")
    description: str = Field(..., description="Sonuç açıklaması")

    class Config:
        schema_extra = {
            "example": {
                "url": "https://secure-login-verify.suspicious-domain.tk/login",
                "risk": "high",
                "category": "PHISHING",
                "confidence": "94.23%",
                "description": "Critical Match: Malicious pattern detected."
            }
        }


class BatchAnalysisResponse(BaseModel):
    """Toplu URL analiz sonucu"""
    total: int = Field(..., description="Toplam analiz edilen URL sayısı")
    results: List[AnalysisResponse] = Field(..., description="Analiz sonuçları")
    summary: dict = Field(..., description="Özet istatistikler")


class HealthResponse(BaseModel):
    """Servis sağlık durumu"""
    status: str = Field(..., description="Servis durumu")
    model_loaded: bool = Field(..., description="Model yüklü mü?")
    model_path: str = Field(..., description="Model dizini")
    device: Optional[str] = Field(None, description="Kullanılan cihaz (CPU/CUDA)")


class ModelInfoResponse(BaseModel):
    """Model bilgileri"""
    model_path: str = Field(..., description="Model dizini")
    device: str = Field(..., description="Kullanılan cihaz")
    dtype: str = Field(..., description="Veri tipi (float32/bfloat16)")
    attention_implementation: str = Field(..., description="Attention implementasyonu")


# Lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama başlangıç ve kapanış işlemleri"""
    global analyzer
    
    # Startup
    logger.info(f"🚀 FastAPI servisi başlatılıyor...")
    logger.info(f"📁 Model dizini: {MODEL_DIR}")
    
    if not os.path.exists(MODEL_DIR):
        logger.error(f"❌ Model bulunamadı: {MODEL_DIR}")
        logger.error("⚠️ Servis model olmadan başlatılıyor (health endpoint hariç API çalışmayacak)")
    else:
        try:
            analyzer = URLAnalyzer(MODEL_DIR)
            logger.info("✅ Model başarıyla yüklendi")
        except Exception as e:
            logger.error(f"❌ Model yükleme hatası: {e}")
            analyzer = None
    
    yield
    
    # Shutdown
    logger.info("🛑 FastAPI servisi kapatılıyor...")
    analyzer = None


# FastAPI uygulaması
app = FastAPI(
    title="ModernBERT URL Phishing Detector API",
    description="URL'leri analiz ederek phishing/malicious içerik tespiti yapan AI destekli API servisi",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware (Frontend entegrasyonu için)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da spesifik domain'ler belirtilmeli
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Endpoint'ler
@app.get("/", tags=["Root"])
async def root():
    """Ana sayfa - API bilgileri"""
    return {
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


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Servis sağlık kontrolü"""
    return HealthResponse(
        status="healthy" if analyzer is not None else "degraded",
        model_loaded=analyzer is not None,
        model_path=MODEL_DIR,
        device=analyzer.device.type if analyzer else None
    )


@app.get("/model/info", response_model=ModelInfoResponse, tags=["Model"])
async def model_info():
    """Model detaylı bilgileri"""
    if analyzer is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model yüklenmedi. Lütfen model dosyalarını kontrol edin."
        )
    
    return ModelInfoResponse(
        model_path=MODEL_DIR,
        device=analyzer.device.type,
        dtype=str(analyzer.dtype),
        attention_implementation=analyzer.attn_implementation
    )


@app.post("/analyze", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_url(request: URLRequest):
    """
    Tekli URL analizi yapar
    
    - **url**: Analiz edilecek URL (zorunlu)
    
    Returns:
        AnalysisResponse: URL analiz sonucu
    """
    if analyzer is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model yüklenmedi. Servis şu an kullanılamıyor."
        )
    
    try:
        result = analyzer.analyze(request.url)
        return AnalysisResponse(**result)
    except Exception as e:
        logger.error(f"Analiz hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"URL analizi sırasında hata oluştu: {str(e)}"
        )


@app.post("/analyze/batch", response_model=BatchAnalysisResponse, tags=["Analysis"])
async def analyze_batch_urls(request: BatchURLRequest):
    """
    Toplu URL analizi yapar (maksimum 100 URL)
    
    - **urls**: Analiz edilecek URL listesi (zorunlu, max 100)
    
    Returns:
        BatchAnalysisResponse: Toplu analiz sonuçları ve özet istatistikler
    """
    if analyzer is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model yüklenmedi. Servis şu an kullanılamıyor."
        )
    
    results = []
    errors = []
    
    for url in request.urls:
        try:
            result = analyzer.analyze(url)
            results.append(AnalysisResponse(**result))
        except Exception as e:
            logger.error(f"URL analiz hatası ({url}): {e}")
            errors.append({"url": url, "error": str(e)})
    
    # Özet istatistikler
    summary = {
        "total_analyzed": len(results),
        "total_errors": len(errors),
        "legitimate": sum(1 for r in results if r.category == "LEGITIMATE"),
        "suspicious": sum(1 for r in results if r.category == "SUSPICIOUS"),
        "phishing": sum(1 for r in results if r.category == "PHISHING"),
        "high_risk": sum(1 for r in results if r.risk == "high"),
        "medium_risk": sum(1 for r in results if r.risk == "medium"),
        "low_risk": sum(1 for r in results if r.risk == "low")
    }
    
    if errors:
        summary["errors"] = errors
    
    return BatchAnalysisResponse(
        total=len(results),
        results=results,
        summary=summary
    )


# Hata yönetimi
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Validation hataları için özel handler"""
    return {
        "error": "Validation Error",
        "detail": str(exc)
    }


if __name__ == "__main__":
    import uvicorn
    
    # Komut satırı argümanları
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"🌐 Servis başlatılıyor: {host}:{port}")
    logger.info(f"📚 Dokümantasyon: http://{host}:{port}/docs")
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=True,  # Development için otomatik yeniden yükleme
        log_level="info"
    )
