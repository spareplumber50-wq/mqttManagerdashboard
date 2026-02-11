#!/bin/bash

# MQTT Dashboard Setup Script
echo "=========================================="
echo "MQTT Dashboard Installation Script"
echo "=========================================="
echo ""

# Check if running as root for port 80
if [ "$EUID" -ne 0 ] && [ "$1" != "--no-root" ]; then 
    echo "Note: Running on port 80 requires root privileges."
    echo "Run with sudo or use --no-root flag to skip this check."
fi

# Check Python version
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Found Python $PYTHON_VERSION"

# Install pip if not available
if ! command -v pip3 &> /dev/null; then
    echo "Installing pip..."
    sudo apt-get update
    sudo apt-get install -y python3-pip
fi

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip3 install -r requirements.txt --break-system-packages

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env file with your Google OAuth credentials."
fi

# Create data file if it doesn't exist
if [ ! -f mqtt_data_points.json ]; then
    echo "[]" > mqtt_data_points.json
    echo "Created mqtt_data_points.json"
fi

# Optional: Setup systemd service
echo ""
read -p "Do you want to install as a system service? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    CURRENT_DIR=$(pwd)
    CURRENT_USER=$(whoami)
    
    # Update service file with current directory
    sed -i "s|/path/to/mqtt-dashboard|$CURRENT_DIR|g" mqtt-dashboard.service
    sed -i "s|User=www-data|User=$CURRENT_USER|g" mqtt-dashboard.service
    
    # Copy service file
    sudo cp mqtt-dashboard.service /etc/systemd/system/
    
    # Reload systemd
    sudo systemctl daemon-reload
    
    # Enable and start service
    sudo systemctl enable mqtt-dashboard
    
    echo "Service installed. To start: sudo systemctl start mqtt-dashboard"
    echo "To view logs: sudo journalctl -u mqtt-dashboard -f"
fi

echo ""
echo "=========================================="
echo "Installation complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Google OAuth credentials"
echo "2. Run: sudo python3 app.py"
echo "3. Access the dashboard at http://localhost"
echo ""
echo "For Cloudflare Tunnel setup, see README.md"
echo ""
