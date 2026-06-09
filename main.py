"""
Main entry point for the LangChain Chatbot.
Run: python main.py
"""

from app import app

if __name__ == "__main__":
    print("\n*  LangChain Chatbot (Stateless) running at http://localhost:5000\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
