#!/bin/bash

# Create necessary directories
mkdir -p ~/.streamlit/

# Create Streamlit config
echo "\
[general]\n\
email = \"\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS = false\n\
port = \$PORT\n\
" > ~/.streamlit/config.toml

# Run ingestion if vector DB doesn't exist
if [ ! -f "vectorstore/db/index.faiss" ]; then
    echo "Running document ingestion..."
    python ingest.py
fi
