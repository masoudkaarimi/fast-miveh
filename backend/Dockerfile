# --- Stage 1: Build stage ---
FROM python:3.11-slim AS builder

WORKDIR /app

# --- Install build dependencies ---
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev

# --- Install python dependencies ---
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt


# --- Stage 2: Final stage ---
FROM python:3.11-slim

# --- Create a non-root user ---
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /home/appuser/app

# --- Install runtime dependencies ---
RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev && rm -rf /var/lib/apt/lists/*

# --- Copy wheels from builder stage and install ---
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# --- Copy application code ---
COPY . .

# --- Create log directory and change ownership before switching user ---
RUN mkdir -p /var/log/django && \
    chown -R appuser:appuser /var/log/django

# --- Change ownership of the app directory to the non-root user ---
RUN chown -R appuser:appuser /home/appuser

# --- Switch to the non-root user ---
USER appuser

# --- Expose port for the app ---
EXPOSE 8000
