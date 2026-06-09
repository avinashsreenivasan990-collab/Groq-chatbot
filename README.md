# LangChain Chatbot

A stateless chatbot built with Flask and LangChain. Each request is handled independently, with support for Groq, Google Gemini, and OpenAI models.

## Features

- Stateless chat responses with no conversation memory
- Streaming responses over Server-Sent Events
- Web UI served from Flask static files
- Provider switching between Groq, Gemini, and OpenAI
- Config endpoint for frontend defaults

## Tech Stack

- Python
- Flask
- Flask-CORS
- LangChain
- Groq, Gemini, and OpenAI LangChain integrations

## Project Structure

- `app.py` - Flask app, routes, and LLM factory
- `main.py` - Alternate entry point for running the server
- `static/index.html` - Frontend chat interface
- `static/style.css` - Frontend styling
- `requirements.txt` - Python dependencies

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment variables by copying `.env.example` to `.env` and setting your values.

## Environment Variables

- `PROVIDER` - `groq`, `gemini`, or `openai`
- `API_KEY` - Your provider API key
- `MODEL_NAME` - Model name for the selected provider
- `TEMPERATURE` - Sampling temperature from `0.0` to `1.0`

## Run Locally

Start the server with either entry point:

```bash
python app.py
```

or

```bash
python main.py
```

Then open `http://localhost:5000` in your browser.

## API Endpoints

- `GET /` - Serves the chat UI
- `POST /chat` - Stateless streaming chat endpoint
- `GET /config` - Returns server defaults for the frontend
- `GET /health` - Health check endpoint

## Chat Request Shape

```json
{
  "provider": "groq",
  "api_key": "your-api-key",
  "model": "llama-3.3-70b-versatile",
  "temperature": 0.7,
  "prompt": "Hello!",
  "system_prompt": "You are a helpful assistant."
}
```

## Notes

- The app is stateless by design, so each request is processed independently.
- If you switch providers in the UI, make sure the model name matches that provider.