# app.py
"""
FastAPI Web Service - ModernBERT URL Phishing Detector
=======================================================
This service uses the fine-tuned ModernBERT model to analyze URLs
and detect phishing/malicious content.

Endpoints:
    - POST /analyze       - Single URL analysis
    - POST /analyze/batch - Batch URL analysis
    - GET /health         - Service health check
    - GET /model/info     - Model metadata
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

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global model instance
analyzer: Optional[URLAnalyzer] = None
MODEL_DIR = os.getenv("MODEL_DIR", "outputs/V3-hybrid/production_model")

# Pydantic Models
class URLRequest(BaseModel):
    """Single URL analysis request"""
    url: str = Field(..., description="URL to be analyzed", min_length=3, max_length=2048)
    
    @validator('url')
    def validate_url(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('URL cannot be empty')
        if not any(v.startswith(prefix) for prefix in ['http://', 'https://', 'ftp://', 'www.']):
            v = 'http://' + v
        return v

    class Config:
        schema_extra = {
            "example": {
                "url": "https://secure-login-verify.suspicious-domain.tk/login"
            }
        }

class BatchURLRequest(BaseModel):
    """Batch URL analysis request"""
    urls: List[str] = Field(..., description="List of URLs to be analyzed", min_items=1, max_items=100)
    
    @validator('urls')
    def validate_urls(cls, v):
        if len(v) > 100:
            raise ValueError('Maximum 100 URLs can be sent at once')
        return [url.strip() for url in v if url.strip()]

class AnalysisResponse(BaseModel):
    """URL analysis response"""
    url: str = Field(..., description="Analyzed URL")
    risk: str = Field(..., description="Risk level: low, medium, high")
    category: str = Field(..., description="Category: LEGITIMATE, SUSPICIOUS, PHISHING")
    confidence: str = Field(..., description="Confidence score (percentage)")
    description: str = Field(..., description="Result description")

class BatchAnalysisResponse(BaseModel):
    """Batch URL analysis response"""
    total: int = Field(..., description="Total number of analyzed URLs")
    results: List[AnalysisResponse] = Field(..., description="Analysis results")
    summary: dict = Field(..., description="Summary statistics")

class HealthResponse(BaseModel):
    """Service health status"""
    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Is the model loaded?")
    model_path: str = Field(..., description="Model directory")
    device: Optional[str] = Field(None, description="Device used (CPU/CUDA)")

class ModelInfoResponse(BaseModel):
    """Model metadata"""
    model_path: str = Field(..., description="Model directory")
    device: str = Field(..., description="Device used")
    dtype: str = Field(..., description="Data type (float32/bfloat16)")
    attention_implementation: str = Field(..., description="Attention implementation")

# Lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle events"""
    global analyzer
    logger.info(f"🚀 Starting FastAPI service...")
    
    # Model yolu olarak Hugging Face reposunu ver (Kendi kullanıcı adını yaz)
    HF_MODEL_ID = os.getenv("MODEL_DIR", "ilkayO/modernbert-phishing-detector")
    logger.info(f"📁 Loading model: {HF_MODEL_ID}")
    
    try:
        # URLAnalyzer artık direkt Hugging Face'den indirecek!
        analyzer = URLAnalyzer(HF_MODEL_ID)
        logger.info("✅ Model loaded successfully from Hugging Face / Cache")
    except Exception as e:
        logger.error(f"❌ Error loading model: {e}")
        analyzer = None
        
    yield
    logger.info("🛑 Shutting down FastAPI service...")
    analyzer = None

app = FastAPI(
    title="ModernBERT URL Phishing Detector API",
    description="AI-powered API service for analyzing URLs and detecting phishing/malicious content",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Root"])
async def root():
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
    return HealthResponse(
        status="healthy" if analyzer is not None else "degraded",
        model_loaded=analyzer is not None,
        model_path=MODEL_DIR,
        device=analyzer.device.type if analyzer else None
    )

@app.get("/model/info", response_model=ModelInfoResponse, tags=["Model"])
async def model_info():
    if analyzer is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Model not loaded.")
    return ModelInfoResponse(
        model_path=MODEL_DIR,
        device=analyzer.device.type,
        dtype=str(analyzer.dtype),
        attention_implementation=analyzer.attn_implementation
    )

@app.post("/analyze", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_url(request: URLRequest):
    if analyzer is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Model not loaded.")
    try:
        result = analyzer.analyze(request.url)
        return AnalysisResponse(**result)
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/analyze/batch", response_model=BatchAnalysisResponse, tags=["Analysis"])
async def analyze_batch_urls(request: BatchURLRequest):
    if analyzer is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Model not loaded.")
    results, errors = [], []
    for url in request.urls:
        try:
            result = analyzer.analyze(url)
            results.append(AnalysisResponse(**result))
        except Exception as e:
            logger.error(f"Batch Analysis error ({url}): {e}")
            errors.append({"url": url, "error": str(e)})
    
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
    if errors: summary["errors"] = errors
    return BatchAnalysisResponse(total=len(results), results=results, summary=summary)

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return {"error": "Validation Error", "detail": str(exc)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    logger.info(f"🌐 Service starting: {host}:{port}")
    uvicorn.run("app:app", host=host, port=port, reload=True, log_level="info")
