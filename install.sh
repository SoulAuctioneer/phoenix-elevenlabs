#!/bin/bash

# Installation script for Voice Assistant
# Handles system dependencies and Python virtual environment setup

set -e  # Exit on any error

# Function to log messages with timestamps
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS setup
    log "Detected macOS system"
    
    if ! command_exists brew; then
        log "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    log "Installing system dependencies..."
    brew install portaudio
    
elif [[ "$OSTYPE" == "linux"* ]]; then
    # Raspberry Pi / Linux setup
    log "Detected Linux system"
    
    log "Updating package lists..."
    sudo apt-get update
    
    log "Installing system dependencies..."
    sudo apt-get install -y python3-pip portaudio19-dev python3-pyaudio
    
    # Add user to audio group
    if ! groups | grep -q audio; then
        log "Adding user to audio group..."
        sudo usermod -a -G audio $USER
        log "Note: You may need to log out and back in for audio group changes to take effect"
    fi
else
    log "Unsupported operating system: $OSTYPE"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    log "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
log "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
log "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
log "Installing Python dependencies..."
pip install "elevenlabs[pyaudio]" python-dotenv

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    log "Creating .env file..."
    cat > .env << EOL
# ElevenLabs Configuration
AGENT_ID=your_agent_id_here
ELEVENLABS_API_KEY=your_api_key_here  # Optional for public agents
EOL
    log "Please update .env file with your credentials"
fi

# Add these lines after creating the .env file
log "Creating logs directory..."
mkdir -p logs

# Install from requirements.txt
log "Installing Python dependencies from requirements.txt..."
pip install -r requirements.txt

# Create example conversation directory
log "Creating logs directory..."
mkdir -p logs

# Make run script executable
chmod +x run.sh

log "Installation complete!"
log "You can now run the application using: ./run.sh" 