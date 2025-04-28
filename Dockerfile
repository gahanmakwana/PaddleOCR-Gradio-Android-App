# 1. Use a slim Python image
FROM python:3.9-slim

# 2. Install OS-level deps (including setuptools) that PaddleOCR and OpenCV need
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libglib2.0-0 libsm6 libxrender1 libxext6 \
        python3-setuptools \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 3. Copy & install Python deps without pip cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy your whole app
COPY . .

# 5. Tell the container to listen on $PORT
ENV PORT 8080

# 6. Start via Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
