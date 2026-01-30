from __future__ import annotations

import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import requests


OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/chat")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma3:4b")
DEFAULT_SYSTEM = os.environ.get(
    "OLLAMA_SYSTEM",
    "You are an NPC in a town simulation. Respond briefly and stay in character.",
)

app = Flask(__name__)
CORS(app)


@app.get("/")
def index():
    return send_from_directory(os.path.join(os.path.dirname(__file__), ".."), "index.html")


@app.get("/<path:filename>")
def serve_static(filename):
    return send_from_directory(os.path.join(os.path.dirname(__file__), ".."), filename)


@app.get("/health")
def health() -> tuple[dict, int]:
    return {"status": "ok"}, 200


@app.post("/api/chat")
def chat() -> tuple[dict, int]:
    data = request.get_json(silent=True) or {}
    prompt = data.get("prompt", "")
    system = data.get("system", DEFAULT_SYSTEM)
    model = data.get("model", OLLAMA_MODEL)

    if not prompt:
        return {"error": "Missing prompt"}, 400

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        content = data.get("message", {}).get("content", "")
        return {"content": content}, 200
    except requests.RequestException as exc:
        return {"error": str(exc)}, 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=True)
