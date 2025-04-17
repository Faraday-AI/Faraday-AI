# Build stage
FROM python:3.10.13-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
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
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage caching
COPY requirements.txt .

# Create virtual environment and install dependencies with retry logic
RUN python -m venv /opt/venv \
    && . /opt/venv/bin/activate \
    && pip install --no-cache-dir --timeout=1000 --retries=5 pip setuptools wheel \
    && pip install --no-cache-dir --timeout=1000 --retries=5 -r requirements.txt || \
    (echo "Retrying pip install..." && pip install --no-cache-dir --timeout=1000 --retries=5 -r requirements.txt)

# Copy the application code
COPY . .

# Create data and models directories and set permissions
RUN mkdir -p /app/data /app/services/physical_education/models/movement_analysis /app/models \
    && chmod -R 777 /app/data /app/services/physical_education/models /app/models

# Generate models
RUN . /opt/venv/bin/activate \
    && python -c "from app.services.physical_education.models.generate_models import generate_models; generate_models()"

# Final stage
FROM python:3.10.13-slim

WORKDIR /app

# Install runtime dependencies in a single layer
RUN apt-get update && apt-get install -y \
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
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user and required directories in a single layer
RUN useradd -m -u 1000 appuser \
    && mkdir -p /opt/venv/lib/python3.10/site-packages/mediapipe/modules/pose_landmark \
    && mkdir -p /app/services/physical_education/models/movement_analysis /app/static /app/logs /app/exports /app/models \
    && chown -R appuser:appuser /opt/venv /app \
    && chmod -R 755 /opt/venv /app \
    && chmod -R 777 /app/logs /app/exports /app/data /app/services/physical_education/models /app/models

# Copy only necessary files
COPY --chown=appuser:appuser . .

# Copy generated models and data from builder stage
COPY --from=builder --chown=appuser:appuser /app/services/physical_education/models/movement_analysis/movement_models.json
COPY --from=builder --chown=appuser:appuser /app/data /app/data
COPY --from=builder --chown=appuser:appuser /app/models /app/models

USER appuser

# Set environment variables in a single layer
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    APP_ENVIRONMENT=production \
    LOG_LEVEL=info \
    LOG_DIR=/app/logs \
    MODEL_DIR=/app/models \
    STATIC_DIR=/app/static \
    EXPORTS_DIR=/app/exports

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose ports
EXPOSE 8000 9091 9100

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 