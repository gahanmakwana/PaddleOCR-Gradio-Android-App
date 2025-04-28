# Use a slim Python image
FROM python:3.9-slim

# Install OS-level dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1 \
    python3-setuptools \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Set environment port (Railway uses it)
ENV PORT=8080

# Start the app
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
