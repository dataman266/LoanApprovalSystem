FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src src/
COPY scripts scripts/

# Create data directory
RUN mkdir -p data logs

# Expose ports
EXPOSE 8000 8501 8001 8002 8003 8004

# Set environment
ENV PYTHONUNBUFFERED=1
ENV ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}

# Default command
CMD ["python3", "scripts/run_api.py"]
