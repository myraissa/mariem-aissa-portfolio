"""
Flask Backend for Portfolio Chatbot + serving index.html
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Flask app
app = Flask(__name__, static_folder=".", static_url_path="/")
CORS(app)

# HuggingFace API
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
API_URL = "https://router.huggingface.co/v1/chat/completions"

# ---------- API Endpoints ----------

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or "messages" not in data:
        return jsonify({"error": "Invalid request format"}), 400

    request_body = {
        "model": data.get("model", "meta-llama/Llama-3.1-8B-Instruct"),
        "messages": data.get("messages"),
        "max_tokens": data.get("max_tokens", 250),
        "temperature": data.get("temperature", 0.8),
        "top_p": data.get("top_p", 0.9)
    }

    try:
        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
                "Content-Type": "application/json"
            },
            json=request_body,
            timeout=30
        )
        if not response.ok:
            return jsonify({"error": f"HuggingFace API error: {response.status_code}", "details": response.text}), response.status_code
        return jsonify(response.json())

    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timeout"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "Chatbot API is running"})

# ---------- Serve Frontend ----------

@app.route("/")
def serve_index():
    return send_from_directory(".", "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(".", path)

# ---------- Run Server ----------

if __name__ == "__main__":
    if not HUGGINGFACE_API_KEY:
        print("⚠️  WARNING: HUGGINGFACE_API_KEY not set in environment!")
    else:
        print("✅ HuggingFace API key loaded successfully")

    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
