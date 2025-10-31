"""
Flask Backend for Portfolio Chatbot
Handles API requests and keeps the HuggingFace token secure
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Get API key from environment variable (never commit this!)
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
API_URL = 'https://router.huggingface.co/v1/chat/completions'

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Endpoint to handle chat requests
    Expects JSON: { "messages": [...], "model": "...", "max_tokens": ..., ... }
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data or 'messages' not in data:
            return jsonify({'error': 'Invalid request format'}), 400
        
        # Prepare request to HuggingFace
        request_body = {
            "model": data.get("model", "meta-llama/Llama-3.1-8B-Instruct"),
            "messages": data.get("messages"),
            "max_tokens": data.get("max_tokens", 250),
            "temperature": data.get("temperature", 0.8),
            "top_p": data.get("top_p", 0.9)
        }
        
        # Make request to HuggingFace API
        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
                "Content-Type": "application/json",
            },
            json=request_body,
            timeout=30
        )
        
        if not response.ok:
            return jsonify({
                'error': f'HuggingFace API error: {response.status_code}',
                'details': response.text
            }), response.status_code
        
        # Return the response
        return jsonify(response.json())
    
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timeout'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Chatbot API is running'})

if __name__ == '__main__':
    # Check if API key is set
    if not HUGGINGFACE_API_KEY:
        print("⚠️  WARNING: HUGGINGFACE_API_KEY not set in environment!")
        print("   Create a .env file with: HUGGINGFACE_API_KEY=your_key_here")
    else:
        print("✅ HuggingFace API key loaded successfully")
    
    # Run the server
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)