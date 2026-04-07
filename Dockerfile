FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p vectorstore/db data/raw data/processed

# Run ingestion during build (optional - can also run at startup)
# RUN python ingest.py

# Expose port
EXPOSE 8501

# Set environment variables
ENV PYTHONPATH=/app
ENV KMP_DUPLICATE_LIB_OK=TRUE

# Run the application
CMD ["streamlit", "run", "app_web.py", "--server.port=8501", "--server.address=0.0.0.0"]
