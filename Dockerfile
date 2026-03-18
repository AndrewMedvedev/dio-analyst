# syntax=docker/dockerfile:1.9-labs

# ─────────────────────────────
# STAGE 1 — deps
# ─────────────────────────────
FROM python:3.12-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# 👇 только если вдруг понадобится сборка (редко)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем uv
RUN pip install --no-cache-dir uv

# Копируем только зависимости (кэшируется!)
COPY pyproject.toml uv.lock requirements.txt* ./

# Устанавливаем зависимости
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# ─────────────────────────────
# STAGE 2 — runtime
# ─────────────────────────────
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# 👇 только runtime зависимости (если нужны)
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Копируем venv
COPY --from=builder /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"

# Копируем код (ПОСЛЕДНИМ!)
COPY . .

CMD ["python", "main.py"]
