FROM python:3.10

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    GRADIO_SERVER_NAME="0.0.0.0" \
    GRADIO_SERVER_PORT=7860 \
    MPLCONFIGDIR=/tmp/matplotlib_cache \
    XDG_CACHE_HOME=/tmp

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    git-lfs \
    ffmpeg \
    libsm6 \
    libxext6 \
    cmake \
    rsync \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Pre-create cache directories and set permissions
RUN mkdir -p /tmp/matplotlib_cache && chmod -R 777 /tmp

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application with correct ownership
COPY --chown=1000:1000 . .

# Ensure user 1000 is used
USER 1000

# Expose the Gradio port
EXPOSE 7860

CMD ["python", "app.py"]
