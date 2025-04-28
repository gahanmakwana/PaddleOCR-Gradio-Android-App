# Use official Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Set environment variable for port
ENV PORT=8080

# Expose the port (optional, Railway handles it)
EXPOSE 8080

# Start the app using Gunicorn, binding to 0.0.0.0:$PORT
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
