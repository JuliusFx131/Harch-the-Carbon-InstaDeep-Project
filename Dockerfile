FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgdal-dev \
    libexpat1 \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch (CPU-only) - use the correct version
RUN pip install --no-cache-dir torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu

# Install other dependencies
RUN pip install --no-cache-dir \
    segmentation-models-pytorch==0.3.3 \
    rasterio==1.4.3 \
    tqdm==4.67.1 \
    six

COPY . .

CMD ["python", "app.py"]