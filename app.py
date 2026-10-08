import os
import json
import requests
from flask import Flask, request, jsonify, send_from_directory
from filters import extract_filters

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "static"))

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
SYSTEM_PROMPT = "You are a helpful shopping assistant. Be concise."

if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY is not set; /api/chat will return an error until it is.")

sessions = {}  # in-memory: lost on restart, so run a single worker

MERCHANTS = ["Amazon", "eBay", "Walmart", "BestBuy", "Newegg"]
PRODUCTS = ["Logitech MX Master 3S", "Logitech MX Keys", "Razer DeathAdder V3",
            "Corsair K95 RGB", "SteelSeries Arctis 7"]


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.post("/api/chat")
def chat():
    if not GEMINI_API_KEY:
        return jsonify(error="Server is missing GEMINI_API_KEY"), 500

    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify(error="Message is required"), 400

    links = [l for l in data.get("links", []) if isinstance(l, str)][:5]
    sid = str(data.get("session_id") or "anonymous")
    if sid not in sessions and len(sessions) > 500:
        sessions.pop(next(iter(sessions)))  # drop the oldest session
    session = sessions.setdefault(sid, {"memory": [], "filters": {}})

    # The browser owns the filter list (users can remove chips); new message wins
    if isinstance(data.get("filters"), dict):
        session["filters"] = data["filters"]
    session["filters"].update(extract_filters(message))

    context = build_context(message, links, session["memory"], session["filters"])

    try:
        resp = requests.post(
            GEMINI_URL,
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {GEMINI_API_KEY}"},
            json={"model": MODEL,
                  "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                               {"role": "user", "content": context}],
                  "max_tokens": 1000},  # Gemini 2.5 may spend some on reasoning
            timeout=60,
        )
    except requests.exceptions.RequestException as e:
        print(f"Error calling Gemini: {e}")
        return jsonify(error="Could not reach Gemini. Try again."), 502

    if not resp.ok:
        print(f"Gemini error: {resp.status_code} {resp.text}")
        if resp.status_code == 429:
            return jsonify(error="Gemini rate limit reached. Wait a minute and try again."), 429
        return jsonify(error=f"Gemini returned status {resp.status_code}"), 502

    reply = (resp.json().get("choices", [{}])[0].get("message", {}).get("content")
             or "No response from model")

    session["memory"] = (session["memory"] + [{"user": message, "assistant": reply}])[-3:]

    return jsonify(assistant_reply=reply,
                   offers=generate_mock_offers(links, session["filters"]),
                   filters=session["filters"])


def build_context(message, links, memory, filters):
    parts = []
    if memory:
        parts.append("Conversation history:")
        for turn in memory[-2:]:
            parts.append(f"User: {turn['user']}")
            parts.append(f"Assistant: {turn['assistant'][:100]}...")
        parts.append("")
    if filters:
        parts += [f"Active filters: {json.dumps(filters)}", ""]
    if links:
        parts += [f"Product links to analyze: {', '.join(links)}", ""]
    parts.append(f"Current request: {message}")
    return "\n".join(parts)


def generate_mock_offers(links, filters):
    """Placeholder data. Replace with real scraping or a price API."""
    max_price = filters.get("max_price")
    items = ([(f"Product {i + 1}", l) for i, l in enumerate(links)] if links else
             [(p, f"https://example.com/product/{i}") for i, p in enumerate(PRODUCTS)])
    offers = []
    for i, (title, src) in enumerate(items):
        price = 79.99 + i * 10 if links else 69.99 + i * 15
        if max_price and price > max_price:
            if not links:
                continue
            price = max(max_price - 10, 1)
        shipping = (5.99 if i % 2 == 0 else 0) if links else (0 if i == 0 else 4.99)
        offers.append({
            "id": f"offer-{i}", "title": title, "merchant": MERCHANTS[i % 5],
            "price": round(price, 2), "shipping": shipping,
            "total": round(price + shipping, 2), "currency": "$",
            "rating": round(4.0 + i * 0.2, 1) if links else round(4.5 - i * 0.1, 1),
            "score": (85 if links else 95) - i * 5, "sources": [src],
        })
    return sorted(offers, key=lambda o: o["score"], reverse=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 4000))
    print(f"Running on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")
