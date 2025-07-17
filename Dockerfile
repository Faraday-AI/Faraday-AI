# Use an official Python runtime as a parent image
FROM python:3.10.17-slim AS builder

# Set basic environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    MINIO_ROOT_USER=faraday \
    MINIO_ROOT_PASSWORD=faraday_secure_password_2025 \
    PYTHONIOENCODING=utf-8 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        wget \
        git \
        cmake \
        libgl1-mesa-glx \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        libgl1-mesa-dev \
        libgstreamer1.0-dev \
        libgstreamer-plugins-base1.0-dev \
        libgtk2.0-dev \
        libtbb-dev \
        libatlas-base-dev \
        libswscale-dev \
        libavcodec-dev \
        libavformat-dev \
        libavutil-dev \
        libavdevice-dev \
        libavfilter-dev \
        iputils-ping \
        gcc \
        python3-dev \
        g++ \
        postgresql-client \
        locales && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    locale-gen C.UTF-8 && \
    update-locale LANG=C.UTF-8

# Copy only requirements first to leverage caching
COPY requirements.txt .

# Create virtual environment and install dependencies with retry logic
RUN python -m venv /opt/venv \
    && . /opt/venv/bin/activate \
    && pip install --no-cache-dir --timeout=1000 --retries=5 --upgrade pip==25.1.1 \
    && pip install --no-cache-dir --timeout=1000 --retries=5 setuptools wheel \
    && pip install --no-cache-dir --timeout=1000 --retries=5 -r requirements.txt \
    && pip install --no-cache-dir --timeout=1000 --retries=5 gunicorn pyotp authlib qrcode || \
    (echo "Retrying pip install..." && pip install --no-cache-dir --timeout=1000 --retries=5 -r requirements.txt \
    && pip install --no-cache-dir --timeout=1000 --retries=5 gunicorn pyotp authlib qrcode)

# Create data and models directories and set permissions
RUN mkdir -p /app/data /app/services/physical_education/models/movement_analysis /app/models /app/scripts \
    && chmod -R 777 /app/data /app/services/physical_education/models /app/models /app/scripts

# Copy the application code
COPY . .

# Final stage
FROM python:3.10.17-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y \
        libpq5 \
        curl \
        libmagic1 \
        libgl1-mesa-glx \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        libgstreamer1.0-0 \
        libgstreamer-plugins-base1.0-0 \
        libgtk2.0-0 \
        libtbbmalloc2 \
        libatlas-base-dev \
        libswscale6 \
        libavcodec59 \
        libavformat59 \
        libavutil57 \
        libavdevice59 \
        libavfilter8 \
        iputils-ping \
        gcc \
        python3-dev \
        g++ \
        postgresql-client \
        netcat-traditional \
        locales && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    locale-gen C.UTF-8 && \
    update-locale LANG=C.UTF-8

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Create all required directories first
RUN mkdir -p \
    /opt/venv/lib/python3.10/site-packages/mediapipe/modules/pose_landmark \
    /app/services/physical_education/models/movement_analysis \
    /app/static \
    /app/logs \
    /app/exports \
    /app/models \
    /app/data \
    /app/scripts

# Create non-root user and set permissions
RUN useradd -m -u 1000 appuser \
    && chown -R appuser:appuser /opt/venv /app \
    && chmod -R 755 /opt/venv /app \
    && chmod -R 777 /app/logs /app/exports /app/data /app/services/physical_education/models /app/models /app/scripts

# Copy everything from builder stage
COPY --from=builder --chown=appuser:appuser /app /app

# Copy and set up startup script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

USER appuser

# Set environment variables in a single layer after Python is fully installed
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONHOME=/opt/venv \
    PYTHONPATH=/app:/app/models:/app/models/physical_education:/app/models/physical_education/pe_enums:/app/models/core:/app/models/movement_analysis \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    APP_ENVIRONMENT=production \
    LOG_LEVEL=info \
    LOG_DIR=/app/logs \
    MODEL_DIR=/app/models \
    STATIC_DIR=/app/static \
    EXPORTS_DIR=/app/exports \
    PYTHONHASHSEED=0

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose ports
EXPOSE 8000 9091 9100

# Start the application
CMD ["/app/start.sh"] 