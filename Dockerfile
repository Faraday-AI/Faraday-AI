# Build stage
FROM python:3.10-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.10-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    libmagic1 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user and set permissions
RUN useradd -m -u 1000 appuser && \
    mkdir -p /opt/venv/lib/python3.10/site-packages/mediapipe/modules/pose_landmark && \
    chown -R appuser:appuser /opt/venv && \
    chmod -R 755 /opt/venv

# Create models directory and set permissions
RUN mkdir -p /app/models && \
    chown -R appuser:appuser /app/models && \
    chmod -R 755 /app/models

# Copy application code
COPY . .

# Set ownership of application files
RUN chown -R appuser:appuser /app

USER appuser

# Create initial models using the virtual environment
RUN /opt/venv/bin/python -c "import tensorflow as tf; \
    model = tf.keras.Sequential([ \
        tf.keras.layers.Dense(10, activation='relu', input_shape=(10,)), \
        tf.keras.layers.Dense(1, activation='sigmoid') \
    ]); \
    tf.keras.models.save_model(model, '/app/models/movement_analysis_model.h5', save_format='h5')"

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Run the application
CMD ["/opt/venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 