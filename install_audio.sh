#!/bin/bash
# Installation script for PyAudio (required for voice chat)

echo "=== Installing PyAudio for Voice Chat ==="

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add Homebrew to PATH for Apple Silicon Macs
    if [[ -f "/opt/homebrew/bin/brew" ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
fi

echo "Installing portaudio..."
brew install portaudio

echo "Installing PyAudio via pip..."
pip install pyaudio

echo "=== Installation Complete ==="
echo "Verify installation with: python3 -c 'import pyaudio; print(\"PyAudio installed successfully\")'"


