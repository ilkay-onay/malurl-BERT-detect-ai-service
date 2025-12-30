# test_api.py
"""
FastAPI endpoint'lerini test etmek için basit script
"""

import requests
import json
import time

# API Base URL
BASE_URL = "http://localhost:8000"

def print_section(title):
    """Bölüm başlığı yazdır"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_health():
    """Health endpoint'i test et"""
    print_section("🏥 HEALTH CHECK")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False

def test_root():
    """Root endpoint'i test et"""
    print_section("🏠 ROOT ENDPOINT")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False

def test_model_info():
    """Model info endpoint'i test et"""
    print_section("ℹ️ MODEL INFO")
    try:
        response = requests.get(f"{BASE_URL}/model/info")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        else:
            print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False

def test_single_url():
    """Tekli URL analizi test et"""
    print_section("🔍 SINGLE URL ANALYSIS")
    
    test_urls = [
        "https://www.google.com",
        "https://secure-login-verify.suspicious-domain.tk/login",
        "http://paypal-verify-account.xyz/secure/login.php",
        "https://github.com",
        "http://free-iphone-winner.click/claim"
    ]
    
    for url in test_urls:
        print(f"\n🔗 Test URL: {url}")
        try:
            payload = {"url": url}
            response = requests.post(f"{BASE_URL}/analyze", json=payload)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ├─ Risk: {result['risk']}")
                print(f"  ├─ Category: {result['category']}")
                print(f"  ├─ Confidence: {result['confidence']}")
                print(f"  └─ Description: {result['description']}")
            else:
                print(f"  └─ Error: {response.text}")
            
            time.sleep(0.5)  # Rate limiting
        except Exception as e:
            print(f"  └─ ❌ Hata: {e}")

def test_batch_urls():
    """Toplu URL analizi test et"""
    print_section("📦 BATCH URL ANALYSIS")
    
    test_batch = {
        "urls": [
            "https://www.google.com",
            "https://www.amazon.com",
            "https://secure-login-verify.suspicious-domain.tk/login",
            "http://paypal-verify-account.xyz/secure/login.php",
            "https://github.com",
            "http://banking-update.ml/verify",
            "https://www.microsoft.com",
            "http://free-iphone-winner.click/claim"
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/analyze/batch", json=test_batch)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n📊 SUMMARY:")
            print(f"  ├─ Total Analyzed: {result['total']}")
            print(f"  ├─ Legitimate: {result['summary']['legitimate']}")
            print(f"  ├─ Suspicious: {result['summary']['suspicious']}")
            print(f"  ├─ Phishing: {result['summary']['phishing']}")
            print(f"  ├─ High Risk: {result['summary']['high_risk']}")
            print(f"  ├─ Medium Risk: {result['summary']['medium_risk']}")
            print(f"  └─ Low Risk: {result['summary']['low_risk']}")
            
            print(f"\n📋 DETAILED RESULTS:")
            for idx, res in enumerate(result['results'], 1):
                print(f"\n  {idx}. {res['url'][:50]}...")
                print(f"     ├─ Category: {res['category']}")
                print(f"     ├─ Risk: {res['risk']}")
                print(f"     └─ Confidence: {res['confidence']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Hata: {e}")

def test_invalid_requests():
    """Geçersiz istekleri test et"""
    print_section("❌ INVALID REQUEST TESTS")
    
    # Boş URL
    print("\n1️⃣ Test: Boş URL")
    try:
        response = requests.post(f"{BASE_URL}/analyze", json={"url": ""})
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json() if response.status_code != 200 else 'Unexpected success'}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Eksik URL field
    print("\n2️⃣ Test: Eksik URL field")
    try:
        response = requests.post(f"{BASE_URL}/analyze", json={})
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json() if response.status_code != 200 else 'Unexpected success'}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Çok fazla URL (batch limit test)
    print("\n3️⃣ Test: Batch limit (>100 URLs)")
    try:
        response = requests.post(
            f"{BASE_URL}/analyze/batch", 
            json={"urls": [f"https://test{i}.com" for i in range(101)]}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json() if response.status_code != 200 else 'Unexpected success'}")
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Ana test fonksiyonu"""
    print("\n" + "🚀 " + "="*56)
    print("  FastAPI URL Phishing Detector - API Test Suite")
    print("="*60)
    print(f"📡 Base URL: {BASE_URL}")
    print(f"⏰ Test Start Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Servis çalışıyor mu kontrol et
    try:
        requests.get(f"{BASE_URL}/", timeout=2)
    except requests.exceptions.ConnectionError:
        print("\n❌ HATA: API servisi çalışmıyor!")
        print("Lütfen önce API'yi başlatın: python app.py")
        return
    
    # Testleri çalıştır
    tests = [
        ("Root Endpoint", test_root),
        ("Health Check", test_health),
        ("Model Info", test_model_info),
        ("Single URL Analysis", test_single_url),
        ("Batch URL Analysis", test_batch_urls),
        ("Invalid Requests", test_invalid_requests)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result if isinstance(result, bool) else True))
        except Exception as e:
            print(f"\n❌ Test hatası ({test_name}): {e}")
            results.append((test_name, False))
    
    # Özet rapor
    print_section("📊 TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n🎯 Total: {passed}/{total} tests passed")
    print(f"⏰ Test End Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

if __name__ == "__main__":
    main()
