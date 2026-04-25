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
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## 📡 API Endpoints

### Single URL Analysis
`POST /analyze`
```bash
curl -X 'POST' \
  'http://localhost:8000/analyze' \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://secure-login-verify.suspicious-domain.tk/login"}'
```

### Batch Analysis
`POST /analyze/batch` (Analyzes up to 100 URLs simultaneously)

## 🧑‍💻 Authors & Contributors

**Ilkay ONAY**
* [LinkedIn](https://linkedin.com/in/ilkay-onay-391905254)
* [GitHub](https://github.com/ilkay-onay)

**Bayram BAYRAKTAR**
* [LinkedIn](https://tr.linkedin.com/in/bayram-bayraktar)
* [GitHub](https://github.com/Bayrak-tar)

*This project demonstrates applied AI research, bridging the gap between theoretical model training and real-world software engineering.*

*This project demonstrates applied AI research, bridging the gap between theoretical model training and real-world software engineering.*
