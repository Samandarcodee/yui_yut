FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (no gcc needed for prebuilt wheels)
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install with specific versions to avoid Rust compilation
RUN pip install --no-cache-dir --only-binary=all -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY main.py .

# Create data directory for SQLite
RUN mkdir -p /app/data

# Create non-root user
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.path.insert(0, '.'); from src.config import get_settings; print('OK')" || exit 1

# Set environment
ENV PYTHONPATH=/app
ENV DB_PATH=/app/data/uyin.sqlite3

CMD ["python", "main.py"]
