"""
Phase 1: Dockerized Flask App
Features: Health endpoint, Structured Logging
"""

from flask import Flask, jsonify, request
import logging
import socket
import os
import time

# ── Logging Setup ──────────────────────────────────────────────
# Structured log format: timestamp | level | message
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# ── App Setup ──────────────────────────────────────────────────
app = Flask(__name__)
START_TIME = time.time()


# ── Middleware: Log every request ──────────────────────────────
@app.before_request
def log_request():
    logger.info(f"Incoming → {request.method} {request.path} | IP: {request.remote_addr}")

@app.after_request
def log_response(response):
    logger.info(f"Outgoing ← {request.method} {request.path} | Status: {response.status_code}")
    return response


# ── Routes ─────────────────────────────────────────────────────

@app.route("/")
def home():
    """Main route — returns app info."""
    logger.info("Home endpoint hit")
    return jsonify({
        "app": "Agentic DevOps - Phase 1",
        "status": "running",
        "host": socket.gethostname(),       # Shows container hostname in Docker
        "environment": os.getenv("APP_ENV", "development"),
        "message": "Phase 1 complete! Flask app is Dockerized ✅"
    })


@app.route("/health")
def health():
    """
    Health endpoint — used by Docker HEALTHCHECK and Kubernetes liveness probe.
    Always returns 200 if app is alive.
    """
    logger.info("Health check passed")
    return jsonify({
        "status": "healthy",
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "host": socket.gethostname()
    }), 200


@app.route("/ready")
def ready():
    """
    Readiness endpoint — used by Kubernetes readiness probe.
    In real apps: check DB connection, cache, etc.
    """
    logger.info("Readiness check passed")
    return jsonify({"status": "ready"}), 200


@app.route("/info")
def info():
    """Returns app environment info — useful for debugging."""
    return jsonify({
        "python_env": os.getenv("APP_ENV", "development"),
        "host": socket.gethostname(),
        "port": os.getenv("PORT", "5000"),
        "uptime_seconds": round(time.time() - START_TIME, 2)
    })


# ── Run ────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    logger.info(f"Starting app on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
