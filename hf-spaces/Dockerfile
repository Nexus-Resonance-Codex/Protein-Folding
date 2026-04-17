FROM python:3.12-slim

# Institutional environment variables
ENV PYTHONUNBUFFERED=1 \
    GRADIO_SERVER_NAME=0.0.0.0 \
    GRADIO_SERVER_PORT=7860 \
    APP_HOME=/app

WORKDIR $APP_HOME

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
# We copy the entire directory structure needed
COPY . .

# Institutional port exposure
EXPOSE 7860

# Execute resonance entrypoint
CMD ["python", "-m", "nrc_protein_folder_live.app"]
