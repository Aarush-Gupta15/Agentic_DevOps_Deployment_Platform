# ════════════════════════════════════════════════════════════════
#  MULTI-STAGE DOCKERFILE — Phase 1
#  Why multi-stage? → Smaller final image, no build tools in prod
# ════════════════════════════════════════════════════════════════

# ── STAGE 1: Builder ──────────────────────────────────────────
# Use full Python image only for installing dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# Copy requirements first → Docker caches this layer
# If requirements.txt doesn't change, pip install is SKIPPED on rebuild (faster!)
COPY app/requirements.txt .

# Install to a custom prefix so we can copy just the packages later
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── STAGE 2: Runtime ──────────────────────────────────────────
# Fresh slim image — no pip, no build tools, just what we need
FROM python:3.11-slim

WORKDIR /app

# Copy ONLY installed packages from builder stage
# This is why final image is small — no leftover pip/gcc/etc.
COPY --from=builder /install /usr/local

# Copy app source code
COPY app/ .

# Security: run as non-root user (best practice)
RUN useradd -m appuser
USER appuser

# Document which port the app uses (doesn't actually publish it)
EXPOSE 5000

# ── HEALTHCHECK ───────────────────────────────────────────────
# Docker will run this every 30s to check if container is healthy
# Visible in: docker ps  (STATUS column → healthy / unhealthy)
HEALTHCHECK --interval=30s \
            --timeout=5s   \
            --start-period=10s \
            --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" \
  || exit 1

# ── START COMMAND ─────────────────────────────────────────────
# Gunicorn = production-grade WSGI server (better than flask dev server)
# --workers 2 → 2 worker processes (handles concurrent requests)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--access-logfile", "-", "main:app"]
