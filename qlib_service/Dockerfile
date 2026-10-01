# Use official Python runtime as a parent image
FROM --platform=linux/amd64 python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV QLIB_SERVICE_HOST=0.0.0.0
ENV QLIB_SERVICE_PORT=8386

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        make \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create storage directories
RUN mkdir -p storage qlib_data models_storage logs

# Create a non-root user
RUN groupadd -r qlib && useradd -r -g qlib qlib

# Change ownership
RUN chown -R qlib:qlib /app

# Switch to non-root user
USER qlib

# Expose port
EXPOSE 8386

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8386/health')" || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8386"]
