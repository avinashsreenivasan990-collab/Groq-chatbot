"""
LangChain Stateless Chatbot — Python Backend
=============================================
Flask server with /chat endpoint using LangChain.
Each request is independent (no memory / no conversation history).
Supports streaming via Server-Sent Events (SSE).

Providers: Groq (default), Google Gemini, OpenAI
"""

import os
import json
import traceback

from dotenv import load_dotenv
from flask import Flask, request, Response, jsonify, send_from_directory
from flask_cors import CORS
from langchain_core.messages import HumanMessage, SystemMessage

# Load environment variables from .env
load_dotenv()

# Read defaults from .env
DEFAULT_PROVIDER    = os.getenv("PROVIDER", "groq")
DEFAULT_API_KEY     = os.getenv("API_KEY", "")
DEFAULT_MODEL       = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
DEFAULT_TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

# ---------------------------------------------------------------------------
# App Setup
# ---------------------------------------------------------------------------
app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)


# ---------------------------------------------------------------------------
# LLM Factory — creates the right model based on provider
# ---------------------------------------------------------------------------
def create_llm(provider, api_key, model_name, temperature):
    """
    Create a LangChain chat model for the given provider.
    Groq is optimized for speed with ultra-low latency inference.
    """
    if provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=model_name,
            api_key=api_key,
            temperature=temperature,
            max_retries=1,
        )
    elif provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=temperature,
            max_retries=1,
        )
    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model_name,
            api_key=api_key,
            temperature=temperature,
            max_retries=1,
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")


# ---------------------------------------------------------------------------
# Routes — Static Files
# ---------------------------------------------------------------------------
@app.route("/")
def serve_index():
    """Serve the chat frontend."""
    return send_from_directory("static", "index.html")


# ---------------------------------------------------------------------------
# Routes — Chat API (Stateless, Streaming)
# ---------------------------------------------------------------------------
@app.route("/chat", methods=["POST"])
def chat():
    """
    Stateless chat endpoint.

    Expects JSON:
        {
            "provider":      "groq" | "gemini" | "openai",
            "api_key":       "<your-api-key>",
            "model":         "llama-3.3-70b-versatile",
            "temperature":   0.7,
            "prompt":        "Hello!",
            "system_prompt": ""          (optional)
        }

    Returns: text/event-stream with SSE chunks.
    """
    data = request.get_json(silent=True) or {}

    provider = data.get("provider", DEFAULT_PROVIDER)
    api_key = data.get("api_key", "") or DEFAULT_API_KEY
    model_name = data.get("model", DEFAULT_MODEL)
    temperature = float(data.get("temperature", DEFAULT_TEMPERATURE))
    prompt = data.get("prompt", "").strip()
    system_prompt = data.get("system_prompt", "").strip()

    # --- Validation ---
    if not api_key:
        return jsonify({"error": "API key is required. Set it in .env or send it in the request."}), 400
    if not prompt:
        return jsonify({"error": "Prompt cannot be empty."}), 400

    try:
        # --- Build LLM (no memory, fresh each request) ---
        llm = create_llm(provider, api_key, model_name, temperature)

        # --- Build message list (stateless — only current prompt) ---
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))

        # --- Stream response via SSE ---
        def generate():
            try:
                for chunk in llm.stream(messages):
                    token = chunk.content
                    if token:
                        yield f"data: {json.dumps({'content': token})}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as stream_err:
                yield f"data: {json.dumps({'error': str(stream_err)})}\n\n"

        return Response(
            generate(),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------------
# Config Endpoint (frontend auto-populate, hides API key)
# ---------------------------------------------------------------------------
@app.route("/config")
def config():
    """Return server defaults so the frontend can auto-populate fields."""
    return jsonify({
        "provider": DEFAULT_PROVIDER,
        "model": DEFAULT_MODEL,
        "temperature": DEFAULT_TEMPERATURE,
        "has_api_key": bool(DEFAULT_API_KEY),
    })


# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------
@app.route("/health")
def health():
    return jsonify({"status": "ok", "mode": "stateless", "provider": DEFAULT_PROVIDER})


# ---------------------------------------------------------------------------
# Entry Point (also runnable via main.py)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("\n*  LangChain Chatbot (Stateless) running at http://localhost:5000\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
