# malurl-BERT-detect-ai-service (malurl)

**malurl**, zararlı (malicious) ve oltalama (phishing) URL'lerini tespit etmek için geliştirilmiş, **ModernBERT** mimarisini kullanan yapay zeka tabanlı bir güvenlik aracıdır. Flash Attention 2 ve BF16 optimizasyonları ile donatılmış olup, URL yapısını analiz ederek saniyeler içinde güvenlik kararı verir.

Proje kod tabanı GitHub üzerinde barındırılmaktadır; ancak eğitim verileri, eğitilmiş model ağırlıkları ve analiz çıktıları harici olarak saklanmaktadır.

## Overview

The `malurl-BERT-detect-ai-service` project is a sophisticated AI-powered service designed for the real-time detection of malicious and phishing URLs. It leverages the power of the ModernBERT architecture, a transformer-based model optimized for understanding the nuances of URL structures. The service is engineered for high performance, incorporating advanced techniques such as Flash Attention 2 and BF16 (Brain Floating Point) precision to achieve rapid inference times, often within milliseconds. This allows for efficient integration into security workflows, web filtering systems, and threat intelligence platforms. The core functionality revolves around analyzing the lexical and structural properties of URLs to classify them as legitimate, suspicious, or outright malicious/phishing.

## Features

*   **ModernBERT Architecture:** Utilizes a fine-tuned ModernBERT model for deep understanding of URL patterns.
*   **High-Performance Inference:** Optimized with Flash Attention 2 and BF16 precision for low-latency predictions.
*   **Real-time Detection:** Capable of analyzing single URLs or batches of URLs with high throughput.
*   **Comprehensive Classification:** Categorizes URLs into `LEGITIMATE`, `SUSPICIOUS`, and `PHISHING` with associated risk levels (`low`, `medium`, `high`).
*   **Confidence Scoring:** Provides a confidence score for each prediction, indicating the model's certainty.
*   **FastAPI Web Service:** Exposes a robust RESTful API for easy integration with other applications.
*   **Interactive API Documentation:** Includes Swagger UI and ReDoc for seamless API exploration and testing.
*   **Batch Processing:** Supports analyzing multiple URLs in a single request for efficiency.
*   **Health Check Endpoint:** Allows monitoring of the service's operational status and model loading.
*   **Model Information Endpoint:** Provides details about the loaded model, including its path, device, and data type.
*   **Production-Ready Features:** Includes considerations for rate limiting, CORS, and HTTPS for secure deployment.
*   **Docker Support:** Provides Dockerfile and Docker Compose configurations for simplified deployment.

## Project Structure

```text
malurl-BERT-detect-ai-service/
├── analysis/          # Data analysis and auditing scripts
│   ├── audit_datasets.py
│   ├── check.py
│   ├── data_inspector.py
│   └── dataset_128or256.py
├── data/              # Processed training, validation, and test datasets
├── logs/              # Training logs and TensorBoard data
├── outputs/           # Trained model weights and artifacts (production_model)
├── plots/             # Performance graphs and reports
├── src/               # Core source code for training and inference
│   ├── config.py      # Configuration settings
│   ├── data_manager.py # Handles dataset loading and tokenization
│   ├── data_prep.py   # Script for data preprocessing and splitting
│   ├── inference.py   # Implements the URL analysis logic
│   ├── metrics.py     # Calculates and visualizes performance metrics
│   └── train.py       # The main training pipeline script
├── API_DOCUMENTATION.md
├── API_QUICKSTART.md
├── LICENSE
├── README.md
├── app.py             # FastAPI application entry point
├── deney-notları.txt  # Detailed project log and experimental notes
├── quick_test.py      # Script for quick manual testing of the model
├── requirements.txt   # Project dependencies
└── test_api.py        # Script for automated API endpoint testing
└── validate_external.py # Script for validating the model on external datasets
```

## Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the API Service

You can start the API using Python directly or via `uvicorn`.

**Method 1: Using Python**
```bash
python app.py
```

**Method 2: Using Uvicorn (Recommended for Production)**
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Access API Documentation

Once the API is running, you can access interactive documentation at:
*   **Swagger UI:** `http://localhost:8000/docs`
*   **ReDoc:** `http://localhost:8000/redoc`

## License

This project is licensed under the **GNU General Public License v3.0**. See the `LICENSE` file for more details.