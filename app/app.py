from flask import Flask, jsonify, request, Response
from prometheus_client import Counter, Histogram, CONTENT_TYPE_LATEST, generate_latest
import os
import socket
import time

app = Flask(__name__)

APP_ENV = os.getenv("APP_ENV", "dev")
API_KEY = os.getenv("API_KEY", "not-set")
PORT = int(os.getenv("PORT", "5000"))

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "http_status"]
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["endpoint"]
)

transactions = [
    {"id": 1, "account": "CHK-1001", "amount": 250.75, "status": "approved"},
    {"id": 2, "account": "SVG-2002", "amount": 1200.00, "status": "pending"},
    {"id": 3, "account": "BUS-3003", "amount": 89.99, "status": "declined"},
]

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    endpoint = request.endpoint or "unknown"
    REQUEST_COUNT.labels(request.method, endpoint, response.status_code).inc()
    if hasattr(request, "start_time"):
        REQUEST_LATENCY.labels(endpoint).observe(time.time() - request.start_time)
    return response

def is_authorized(req):
    return req.headers.get("X-API-KEY") == API_KEY

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Secure Transaction API running",
        "environment": APP_ENV,
        "host": socket.gethostname(),
    }), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route("/ready", methods=["GET"])
def ready():
    return jsonify({"status": "ready"}), 200

@app.route("/metrics", methods=["GET"])
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route("/transactions", methods=["GET"])
def get_transactions():
    if not is_authorized(request):
        return jsonify({"error": "unauthorized"}), 401
    return jsonify(transactions), 200

@app.route("/transactions/<int:tx_id>", methods=["GET"])
def get_transaction(tx_id):
    if not is_authorized(request):
        return jsonify({"error": "unauthorized"}), 401
    tx = next((t for t in transactions if t["id"] == tx_id), None)
    if not tx:
        return jsonify({"error": "transaction not found"}), 404
    return jsonify(tx), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
