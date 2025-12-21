# malurl-BERT-detect-ai-service (malurl)

**malurl** is a state-of-the-art AI service for detecting malicious and phishing URLs. It leverages the **ModernBERT** (2025) architecture, featuring hardware-level optimizations like Flash Attention 2 and unpadding to provide near-instant security verdicts.

---

## 📁 Model Setup (Critical)

The brain of the service is a fine-tuned ModernBERT model. Because the weights are large, they are hosted externally.

1.  **Download** the `production_model` folder from this [Google Drive Link](https://drive.google.com/drive/folders/1DqY4mCzpK4aDcvMQVeN3sISxCg3JOKXs?usp=sharing).
2.  **Move** the entire `production_model` folder into the `Flask-API/Bert-model-files/` directory.
3.  **Verification**: Your file tree must look like this:
    ```text
    malurl-BERT-detect-ai-service/
    ├── Flask-API/
    │   ├── app.py
    │   └── Bert-model-files/
    │       └── production_model/  <-- Folder from Google Drive
    │           ├── config.json
    │           ├── model.safetensors
    │           └── tokenizer.json
    ├── src/
    ├── data/
    └── quick_test.py
    ```

---

## 🚀 Python Environment Setup

The following steps will guide you through setting up a native Python environment for inference and training.

### 1. Create & Activate Virtual Environment
```bash
# From the project root
python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
# .\venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install --upgrade pip

# Core AI Stack (Optimized for CUDA 12.1 - adjust if using different CUDA)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# ModernBERT & Data Processing
pip install transformers==4.48.0 datasets accelerate evaluate scikit-learn pandas

# Flash Attention 2 (Optional but recommended for RTX 30/40 series GPUs)
pip install flash-attn --no-build-isolation

# API Dependencies
pip install flask flask-cors flask-sqlalchemy flask-jwt-extended flask-bcrypt python-dotenv
```

---

## 🛠️ Usage

### 🔍 Quick Test (CLI)
Run a local check to verify the model is loaded correctly:
```bash
python quick_test.py
```

### 🌐 Launch the API Service
Start the backend that powers external integrations (like the browser extension):
```bash
cd Flask-API
python app.py
```
*The service runs on `http://localhost:5001` by default.*

### 🧠 Training & Data Pipeline
If you want to retrain the model with fresh data:
1.  **Merge & Whitelist**: `python -m src.data_manager` (Resolves label conflicts and protects high-trust domains).
2.  **Full Train**: `python -m src.train` (Runs the ModernBERT training pipeline).

---

## 📊 Technical Specifications (2025 Update)

| Spec | Value |
| :--- | :--- |
| **Model Type** | ModernBERT-base (Encoder-only) |
| **Context Window** | 256 Tokens |
| **Optimizations** | Flash Attention 2, Unpadding, BF16 |
| **Inference Speed** | ~10ms per URL (GPU), ~50ms (CPU) |
| **Training Dataset** | 650,000+ unique balanced URLs |
| **Metric (F1)** | ~0.97 (Validation/Test) |

---

## 🛡️ Professional Methodology
*   **Conflict Resolution**: Automatically resolves nearly 100,000 conflicting labels by prioritizing live feeds (PhishTank) over historical CSVs.
*   **Safe Domain Whitelisting**: Implements a hard whitelist for global root domains (Google, Apple, Microsoft) to eliminate false positives on safe infrastructure.
*   **Advanced Tracking**: Full TensorBoard logging and technical report generation (ROC/PR curves) included in the `src/` logic.

**Disclaimer**: This model analyzes URL structure only. For production deployments, it is recommended to combine this with domain age and reputation lookups.