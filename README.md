# malurl-BERT-detect-ai-service (malurl)

**malurl**, zararlı (malicious) ve oltalama (phishing) URL'lerini tespit etmek için geliştirilmiş, **ModernBERT** mimarisini kullanan yapay zeka tabanlı bir güvenlik aracıdır. Flash Attention 2 ve BF16 optimizasyonları ile donatılmış olup, URL yapısını analiz ederek saniyeler içinde güvenlik kararı verir.

Proje kod tabanı GitHub üzerinde barındırılmaktadır; ancak eğitim verileri, eğitilmiş model ağırlıkları ve analiz çıktıları harici olarak saklanmaktadır.

---

## 📂 Kurulum ve Veri Hazırlığı (ÖNEMLİ)

Projeyi klonladıktan sonra çalıştırabilmek için **Google Drive** üzerindeki gerekli klasörleri indirip proje ana dizinine yerleştirmeniz gerekmektedir.

### 1. Dosyaları İndirin
Aşağıdaki Google Drive linkine gidin:
🔗 **[Proje Veri ve Model Dosyaları (Google Drive)](https://drive.google.com/drive/folders/1SwNtfp3z6KRtk3iFAtfsmxAfMUEvi6Q8?usp=sharing)**

### 2. Klasörleri Yerleştirin
Drive içerisindeki şu **4 klasörü** indirin ve projenin **ana dizinine (root)** yapıştırın:
*   `data/` (İşlenmiş eğitim ve test verileri)
*   `outputs/` (Eğitilmiş model ağırlıkları - production_model burada bulunur)
*   `logs/` (TensorBoard eğitim kayıtları)
*   `plots/` (Performans grafikleri ve raporlar)

### 3. Klasör Yapısı Doğrulama
İşlem bittiğinde dosya yapınız tam olarak şöyle görünmelidir:

```text
malurl-BERT-detect-ai-service/
├── analysis/          # Veri seti analiz scriptleri
├── data/              <-- Drive'dan geldi
├── logs/              <-- Drive'dan geldi
├── outputs/           <-- Drive'dan geldi (İçinde production_model var)
├── plots/             <-- Drive'dan geldi
├── src/               # Eğitim ve Inference kaynak kodları
├── quick_test.py      # Hızlı test aracı
├── validate_external.py # Harici veri doğrulama aracı
├── requirements.txt
└── README.md
```

---

## 🚀 Python Ortamı Kurulumu

Python 3.10 veya üzeri önerilir.

1.  **Sanal Ortam Oluşturun:**
    ```bash
    python -m venv venv
    
    # Windows
    .\venv\Scripts\activate
    
    # Mac/Linux
    source venv/bin/activate
    ```

2.  **Bağımlılıkları Yükleyin:**
    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```
    *(Not: NVIDIA GPU kullanıyorsanız, PyTorch'un CUDA sürümünü yüklediğinizden emin olun.)*

---

## 🛠️ Kullanım

Bu projeyi üç farklı şekilde kullanabilirsiniz:

### 1. Hızlı Test (Quick Test)
Modeli manuel olarak test etmek ve URL'leri tek tek denemek için:
```bash
python quick_test.py
```
*Bu script, `outputs/` klasöründeki modeli yükler ve konsol üzerinden interaktif bir test ortamı sunar.*

### 2. Harici Doğrulama (External Validation)
Modelin görmediği harici bir veri seti (örn. Kaggle verisi) üzerinde toplu performansını ölçmek için:
```bash
python validate_external.py
```
*Bu script `data/raw/malicious_phish.csv` (veya belirtilen harici dosya) üzerinde toplu tahmin yapar ve başarı raporu sunar.*

### 3. Yeniden Eğitim (Training Pipeline)
Eğer `data/` klasöründeki verilerle modeli sıfırdan eğitmek isterseniz:

```bash
# 1. Veri Hazırlığı (Opsiyonel - ham veriden csv üretir)
python -m src.data_prep

# 2. Eğitimi Başlat
python -m src.train
```

---

## 📊 Model Mimarisi ve Performans

*   **Model:** ModernBERT-base (Encoder-only)
*   **Context Window:** 256 Token
*   **Optimizasyon:** Flash Attention 2, Unpadding, BF16
*   **Eğitim Verisi:** ~650.000+ dengelenmiş URL

Detaylı performans grafikleri (Confusion Matrix, ROC Curve) `plots/` klasöründe yer almaktadır.

---

## 🛡️ Yasal Uyarı
Bu proje eğitim ve araştırma amaçlı geliştirilmiştir. Model sadece URL'nin sözdizimsel (lexical) yapısını analiz eder. Prodüksiyon ortamında Domain Reputation ve WHOIS sorguları ile birlikte kullanılması önerilir.