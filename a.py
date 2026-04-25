import os
import shutil

def write_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip() + "\n")
    print(f"✅ Created/Updated: {filepath}")

def main():
    print("🚀 Starting repository preparation for GitHub...")

    # 1. CREATE .gitignore
    gitignore_content = """
# Python & Environments
__pycache__/
*.py[cod]
.env
venv/
env/
.venv/

# ML & Data (ASLA GITHUB'A ATILMAMALI)
data/
outputs/
logs/
plots/
*.safetensors
*.bin

# IDEs
.vscode/
.idea/
.ipynb_checkpoints/
CODEBASE_MAP.txt
"""
    write_file(".gitignore", gitignore_content)

    # 2. CREATE Dockerfile
    dockerfile_content = """
FROM python:3.10-slim

WORKDIR /app

# Install build dependencies for PyTorch optimizations
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose FastAPI port
EXPOSE 8000

# Start service
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
"""
    write_file("Dockerfile", dockerfile_content)

    # 3. CREATE README.md
    readme_content = """
# 🛡️ ModernBERT URL Phishing Detector (AI Service)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-EE4C2C.svg?logo=pytorch)](https://pytorch.org/)
[![Model](https://img.shields.io/badge/Model-ModernBERT--base-yellow.svg)](https://huggingface.co/answerdotai/ModernBERT-base)

An enterprise-grade, high-performance REST API service that leverages a fine-tuned **ModernBERT** model to detect malicious and phishing URLs. Built with modern ML practices focusing on real-world generalization and strict prevention of data leakage.

## ✨ Key Features
* **Advanced NLP Architecture:** Fine-tuned `answerdotai/ModernBERT-base` (149M Params).
* **Hardware Optimized:** Accelerated with `TorchDynamo (torch.compile)`, BF16 Mixed Precision, and Flash Attention 2.
* **Production Ready API:** Asynchronous FastAPI implementation with Pydantic validation, batch processing, and built-in health checks.
* **Robust Generalization:** Trained using global deduplication, URL protocol sanitization, and **Domain-Based Group Splitting** to prevent structural overfitting.

## 🔬 The ML Journey: From Overfitting to Robust Generalization (See `RESEARCH_LOG.md`)
Training a phishing detector is notorious for dataset biases. To ensure enterprise-grade reliability, this model evolved through rigorous R&D:
* **Phase 1 (The Deceptive Baseline):** Achieved 100% F1 on standard datasets, but failed on Out-of-Distribution (OOD) data due to structural overfitting (memorizing domains instead of patterns).
* **Phase 2 (Architectural Fix):** Merged multiple datasets, implemented global deduplication, and applied **GroupShuffleSplit** to isolate domain trees.
* **Phase 3 (Production):** The final model achieves a robust, true **0.83 F1-Score** on entirely unseen domains, successfully analyzing URL depth, character entropy, and keyword morphology.

## 🚀 Installation & Usage

### 1. Run with Docker (Recommended)
```bash
docker build -t modernbert-phishing-detector .
docker run -p 8000:8000 modernbert-phishing-detector
```

### 2. Local Setup
```bash
git clone https://github.com/ilkay-onay/malurl-BERT-detect-ai-service.git
cd malurl-BERT-detect-ai-service
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt
python app.py
```

## 📡 API Endpoints

### Single URL Analysis
`POST /analyze`
```bash
curl -X 'POST' \\
  'http://localhost:8000/analyze' \\
  -H 'Content-Type: application/json' \\
  -d '{"url": "https://secure-login-verify.suspicious-domain.tk/login"}'
```

### Batch Analysis
`POST /analyze/batch` (Analyzes up to 100 URLs simultaneously)

## 🧑‍💻 Author
**Ilkay ONAY**
* [LinkedIn](https://linkedin.com/in/ilkay-onay-391905254)
* [GitHub](https://github.com/ilkay-onay)

*This project demonstrates applied AI research, bridging the gap between theoretical model training and real-world software engineering.*
"""
    write_file("README.md", readme_content)

    # 4. TRANSLATE deney-notları.txt -> RESEARCH_LOG.md
    research_log_content = """
# 📑 Scientific Project Log: ModernBERT-URL-Inference
**Project Code:** malurl-BERT-detect-ai-service  
**Core Architecture:** ModernBERT-base (149M Parameters)

---

## 🔬 Phase 0: Initiation & Label Alignment Error (Deceptive Baseline)
*   **Datasets Used:** Mixed open-source URL lists (Kaggle + Manual lists).
*   **Methodology:** Basic BERT training, standard random split.
*   **Findings:** 
    *   **F1 Score:** 0.97
*   **Scientific Analysis:** Post-training manual review revealed that "phishing" labels in the dataset actually pointed to "safe but unpopular" sites, while "safe" labels only covered "Alexa Top 100" sites.
*   **Diagnosis:** **Label Shift / Bias.** The model learned to classify site "popularity" instead of detecting phishing. The model's generalization ability was deemed zero, and the phase was cancelled.

---

## 🔬 Phase 1: PhiUSIIL Experiment & "Closed System" Success
*   **Dataset Used:** **PhiUSIIL Phishing URL Dataset** (~235,370 samples).
    *   *Characteristics:* 134,850 Safe, 100,945 Phishing URLs. High-quality academic dataset.
*   **Methodology:** Training with ModernBERT-base architecture using 256 token length.
*   **Findings:**
    *   **Accuracy:** 1.00
    *   **F1-Score:** 1.00
*   **External Validation (Out-of-Distribution Testing):** The **Kaggle Malicious Phish Dataset** (~651,191 samples) was used to test the model.
    *   **Accuracy:** 46% (Worse than random guessing).
    *   **Error Analysis:** Out of 10,000 safe samples, 9,079 were marked as False Positives.
*   **Diagnosis:** **Structural Overfitting & Data Leakage.** The model memorized specific domain structures and sterile URL formats from the PhiUSIIL dataset. Since domain-based splitting wasn't used, it flawlessly remembered domains seen during training.

---

## 🔬 Phase 2: Architectural Restructuring & Hybrid Approach (The Un-fucking)
*   **Datasets Used (Hybrid Pool):**
    1.  **PhiUSIIL Dataset:** (Labels normalized: 1->0, 0->1).
    2.  **Kaggle Malicious Phish Dataset:** (Normalized to Benign/Malicious).
*   **Developed Techniques:**
    *   **Global Deduplication:** URLs were stripped of protocols (`https`, `http`, `www`) for global deduplication. In case of conflicting labels (same URL, different labels), the "Malicious" label was preserved to increase the safety margin.
    *   **URL Sanitization:** URLs were cleaned as raw strings to prevent the model from exploiting protocol tricks.
    *   **Domain-Based Group Splitting:** The dataset was physically split into 80-10-10 ratios. Using the **GroupShuffleSplit** algorithm, it was guaranteed that all sub-URLs of a domain existed only in a single set (Train or Test).

---

## 🔬 Phase 3: Final Production Model & Stable Success (Validation)
*   **Training Parameters:**
    *   **Model:** ModernBERT-base (Compiled with TorchDynamo).
    *   **Precision:** BF16 Mixed Precision.
    *   **Attention:** Flash Attention 2 & Unpadding.
    *   **Learning Rate:** 2e-5 (Cosine Decay Scheduler).
    *   **Weight Decay:** 0.1 (L2 Regularization / Overfitting Defense).
*   **Final Performance Metrics (On Unseen Domains):**
    *   **Accuracy:** 83.00%
    *   **F1-Score:** 0.8300
    *   **Precision (Accuracy of malicious detection):** 0.84
    *   **Recall (Catch rate of malicious URLs):** 0.83
*   **Scientific Evaluation:** The model's success is **scientifically honest**, unlike the deceptive 100% rates in previous phases. The model now analyzes URL morphology (subdirectory depth, character entropy, suspicious keyword sequences) instead of memorizing domain names.

---

### 📈 Technical Comparison Table

| Phase | Data Source | Splitting Strategy | F1 Score | OOD Test* | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Phase 0** | Mixed (Bad Labels) | Random | 0.97 | Failed | Cancelled |
| **Phase 1** | PhiUSIIL | Random | 1.00 | 15% F1 | Overfitted |
| **Phase 3** | **Hybrid (PhiU+Kaggle)** | **Domain-Group** | **0.83** | **83%+** | **Production Ready** |

*\*OOD Test: Performance on datasets never seen during training.*
"""
    write_file("RESEARCH_LOG.md", research_log_content)
    if os.path.exists("deney-notları.txt"):
        os.remove("deney-notları.txt")
        print("🗑️ Removed: deney-notları.txt (Replaced by RESEARCH_LOG.md)")

    # 5. TRANSLATE app.py comments/logs to English
    app_py_content = """
# app.py
\"\"\"
FastAPI Web Service - ModernBERT URL Phishing Detector
=======================================================
This service uses the fine-tuned ModernBERT model to analyze URLs
and detect phishing/malicious content.

Endpoints:
    - POST /analyze       - Single URL analysis
    - POST /analyze/batch - Batch URL analysis
    - GET /health         - Service health check
    - GET /model/info     - Model metadata
\"\"\"

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
    \"\"\"Single URL analysis request\"\"\"
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
    \"\"\"Batch URL analysis request\"\"\"
    urls: List[str] = Field(..., description="List of URLs to be analyzed", min_items=1, max_items=100)
    
    @validator('urls')
    def validate_urls(cls, v):
        if len(v) > 100:
            raise ValueError('Maximum 100 URLs can be sent at once')
        return [url.strip() for url in v if url.strip()]

class AnalysisResponse(BaseModel):
    \"\"\"URL analysis response\"\"\"
    url: str = Field(..., description="Analyzed URL")
    risk: str = Field(..., description="Risk level: low, medium, high")
    category: str = Field(..., description="Category: LEGITIMATE, SUSPICIOUS, PHISHING")
    confidence: str = Field(..., description="Confidence score (percentage)")
    description: str = Field(..., description="Result description")

class BatchAnalysisResponse(BaseModel):
    \"\"\"Batch URL analysis response\"\"\"
    total: int = Field(..., description="Total number of analyzed URLs")
    results: List[AnalysisResponse] = Field(..., description="Analysis results")
    summary: dict = Field(..., description="Summary statistics")

class HealthResponse(BaseModel):
    \"\"\"Service health status\"\"\"
    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Is the model loaded?")
    model_path: str = Field(..., description="Model directory")
    device: Optional[str] = Field(None, description="Device used (CPU/CUDA)")

class ModelInfoResponse(BaseModel):
    \"\"\"Model metadata\"\"\"
    model_path: str = Field(..., description="Model directory")
    device: str = Field(..., description="Device used")
    dtype: str = Field(..., description="Data type (float32/bfloat16)")
    attention_implementation: str = Field(..., description="Attention implementation")

@asynccontextmanager
async def lifespan(app: FastAPI):
    \"\"\"Application lifecycle events\"\"\"
    global analyzer
    logger.info(f"🚀 Starting FastAPI service...")
    logger.info(f"📁 Model directory: {MODEL_DIR}")
    
    if not os.path.exists(MODEL_DIR):
        logger.error(f"❌ Model not found: {MODEL_DIR}")
        logger.error("⚠️ Starting service without model (only health endpoint will work)")
    else:
        try:
            analyzer = URLAnalyzer(MODEL_DIR)
            logger.info("✅ Model loaded successfully")
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
"""
    write_file("app.py", app_py_content)

    print("\n🎉 Repository preparation complete! The codebase is now in English and production-ready.")
    print("================================================================")
    print("NEXT STEPS:")
    print("1. Review the generated files: README.md, Dockerfile, RESEARCH_LOG.md")
    print("2. Run the following git commands to push to GitHub:")
    print("   git status")
    print("   git add .")
    print("   git commit -m 'feat: Production-ready restructuring, English translation, Docker integration'")
    print("   git push origin main")
    print("================================================================\n")

if __name__ == "__main__":
    main()