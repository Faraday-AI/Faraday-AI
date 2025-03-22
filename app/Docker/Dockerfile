# Build stage
FROM python:3.9-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1

# Set working directory
WORKDIR /build

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt

# Final stage
FROM python:3.9-slim

# Create non-root user
RUN useradd -m -u 1000 appuser

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PATH="/home/appuser/.local/bin:$PATH"

# Set working directory
WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels and requirements from builder
COPY --from=builder /build/wheels /wheels
COPY requirements.txt .

# Install Python packages from wheels and allow PyPI fallback
RUN pip install --no-cache-dir --find-links=/wheels -r requirements.txt \
    && rm -rf /wheels

# Copy project files
COPY --chown=appuser:appuser . .

# Create necessary directories with proper permissions
RUN mkdir -p logs static/images \
    && chown -R appuser:appuser logs static

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Set environment variables for production
ENV ENVIRONMENT=production \
    WORKERS=4

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/test || exit 1

# Run the application with Gunicorn
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app.main:app"] 
