
import requests
import json
import sys

API_BASE = "http://localhost:5000"

def test_health():
    """Test health check endpoint"""
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed!")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed! Is the backend running on port 5000?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_chat():
    """Test chat endpoint"""
    print("\n💬 Testing chat endpoint...")
    
    test_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say 'Hello, I am working!' and nothing else."}
    ]
    
    payload = {
        "messages": test_messages,
        "model": "meta-llama/Llama-3.1-8B-Instruct",
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    try:
        print("   Sending test message...")
        response = requests.post(
            f"{API_BASE}/api/chat",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            reply = data.get('choices', [{}])[0].get('message', {}).get('content', 'No content')
            print("✅ Chat endpoint passed!")
            print(f"   AI Response: {reply[:100]}...")
            return True
        else:
            print(f"❌ Chat failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout! HuggingFace might be slow or API key invalid")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_portfolio_context():
    """Test with portfolio-specific question"""
    print("\n🎯 Testing portfolio context...")
    
    payload = {
        "messages": [
            {"role": "system", "content": "You are Mariem's portfolio chatbot."},
            {"role": "user", "content": "What is Mariem's main role?"}
        ],
        "max_tokens": 100
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/chat",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            reply = data.get('choices', [{}])[0].get('message', {}).get('content', '')
            print("✅ Portfolio context test passed!")
            print(f"   Response: {reply[:150]}...")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("🧪 Portfolio Chatbot API Test Suite")
    print("=" * 60)
    
    # Run tests
    results = []
    results.append(("Health Check", test_health()))
    results.append(("Chat Endpoint", test_chat()))
    results.append(("Portfolio Context", test_portfolio_context()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your API is ready!")
        print("\nNext steps:")
        print("1. Open frontend/index.html in your browser")
        print("2. Click the chatbot button")
        print("3. Send a message to test the full integration")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        print("\nCommon fixes:")
        print("- Ensure Flask server is running: python backend/app.py")
        print("- Check HUGGINGFACE_API_KEY is set in backend/.env")
        print("- Verify your HuggingFace API key is valid")
        return 1

if __name__ == "__main__":
    sys.exit(main())