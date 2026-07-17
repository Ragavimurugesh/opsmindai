# Production Dockerfile for OpsMind AI backend
# Multi‑stage build: builder installs system deps + Python packages, runtime is lean

# ---------- Builder stage ----------
FROM python:3.10-slim AS builder

# Install system libraries needed by XGBoost and Prophet (linear algebra, gcc)
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential gcc g++ libopenblas-dev && \
    rm -rf /var/lib/apt/lists/*

# Set up a virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ---------- Runtime stage ----------
FROM python:3.10-slim AS runtime

# Runtime system deps (no compiler)
RUN apt-get update && \
    apt-get install -y --no-install-recommends libgomp1 && \
    rm -rf /var/lib/apt/lists/*

# Copy virtualenv from builder
COPY --from=builder /opt/venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Set working directory and copy source code
WORKDIR /app
COPY backend/ ./backend/
COPY backend/models/ ./models/
COPY backend/services/ ./services/
COPY backend/routes/ ./routes/
COPY backend/dataset/ ./dataset/
COPY backend/utils/ ./utils/
COPY backend/database.py ./database.py
COPY backend/main.py ./main.py

# Expose the port Render will provide via $PORT (fallback 8000 for local testing)
EXPOSE ${PORT:-8000}

# Command to run FastAPI with uvicorn in production mode
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "${PORT:-8000}", "--workers", "4"]
