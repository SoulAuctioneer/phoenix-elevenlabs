#!/bin/bash

# Run script for Voice Assistant
# Activates virtual environment if needed and runs the application

set -e  # Exit on any error

# Function to log messages with timestamps
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    # Check if venv exists
    if [ ! -d "venv" ]; then
        log "Virtual environment not found. Please run ./install.sh first"
        exit 1
    fi
    
    log "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if .env file exists and has required variables
if [ ! -f ".env" ]; then
    log "Error: .env file not found"
    exit 1
fi

if ! grep -q "AGENT_ID" .env || ! grep -q "ELEVENLABS_API_KEY" .env; then
    log "Error: Please configure your AGENT_ID and ELEVENLABS_API_KEY in .env file"
    exit 1
fi

# Run the application
log "Starting Voice Assistant..."
python3 voice_assistant.py 