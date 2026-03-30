# ============================================================
# Dockerfile — HoneyTrap (multi-stage build)
# Stage 1 : builder (dépendances)
# Stage 2 : runtime léger + optimisé
# ============================================================

# ── Stage 1 : Builder ────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Installer les dépendances système minimales
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copier requirements et installer en mode wheel
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt


# ── Stage 2 : Runtime ────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Dépendances système runtime uniquement
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl \
    && rm -rf /var/lib/apt/lists/*

# Copier les wheels depuis le builder
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Copier le code source
COPY . .

# Créer utilisateur non-root pour la sécurité
RUN useradd -m honeytrap && chown -R honeytrap:honeytrap /app
USER honeytrap

# Variables d'environnement par défaut
ENV FLASK_ENV=production
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_VERSION=1.0.0

EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/health/ || exit 1

# Gunicorn en production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "60", "run:app"]
