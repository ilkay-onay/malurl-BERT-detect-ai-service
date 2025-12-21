from src.inference import URLAnalyzer

# 1. Initialize (This loads the model into your GPU/RAM)
analyzer = URLAnalyzer("outputs/production_model")

# 2. Get input from user
while True:
    user_url = input("\n🔗 Enter a URL to check (or 'q' to quit): ")
    if user_url.lower() == 'q': break
    
    # 3. Predict
    result = analyzer.analyze(user_url)
    
    # 4. Print pretty output
    print(f"VERDICT: {result['category']}")
    print(f"CONFIDENCE: {result['confidence']}")
    print(f"DESCRIPTION: {result['description']}")