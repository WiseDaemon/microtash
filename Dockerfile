# Production Dockerfile for Microstash (Optimized for Google Cloud Run, Render, Fly.io)
FROM python:3.11-slim

# Prevent python from writing pyc files to disk and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Ensure data directories exist
RUN mkdir -p /app/data/audio

# Expose default HTTP port
EXPOSE 8000

# Healthcheck for container orchestrators
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:${PORT}/api/ideas?limit=1 || exit 1

# Launch uvicorn
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
