# MQTT Dashboard - Quick Start Guide

## What You Have

A complete, production-ready MQTT dashboard web application with:

✅ **Multi-broker MQTT connections**  
✅ **Real-time data logging to JSON file** (mqtt_data_points.json)  
✅ **SQL export functionality**  
✅ **Interactive terminal for MQTT commands**  
✅ **Google OAuth authentication**  
✅ **Sleek, modern dark UI with separate CSS**  
✅ **Cloudflare Tunnel support**  
✅ **Port 80 hosting**  
✅ **Docker support**  
✅ **Open-source (MIT License)**  

## File Overview

```
mqtt-dashboard/
├── app.py                      # Main Flask server (Python)
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── setup.sh                   # Automated setup script
├── Dockerfile                 # Docker containerization
├── docker-compose.yml         # Docker Compose configuration
├── mqtt-dashboard.service     # Systemd service file
├── README.md                  # Full documentation
├── CONTRIBUTING.md            # Contribution guidelines
├── LICENSE                    # MIT License
├── .gitignore                # Git ignore rules
├── templates/
│   ├── login.html            # Google OAuth login page
│   └── dashboard.html        # Main dashboard interface
└── static/
    ├── css/
    │   └── style.css         # All styling (separate file)
    └── js/
        └── dashboard.js      # Client-side functionality
```

## Installation (3 Options)

### Option 1: Quick Setup (Recommended)

```bash
cd mqtt-dashboard
chmod +x setup.sh
sudo ./setup.sh
```

Then edit `.env` with your Google OAuth credentials and run:
```bash
sudo python3 app.py
```

### Option 2: Manual Setup

```bash
cd mqtt-dashboard

# Install dependencies
pip3 install -r requirements.txt --break-system-packages

# Configure environment
cp .env.example .env
nano .env  # Add your Google OAuth credentials

# Run server
sudo python3 app.py
```

### Option 3: Docker

```bash
cd mqtt-dashboard

# Edit .env with your credentials
cp .env.example .env
nano .env

# Run with Docker Compose
docker-compose up -d
```

## Google OAuth Setup (Required)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URI: `http://your-domain/auth/callback`
6. Copy Client ID and Secret to `.env`

## Cloudflare Tunnel Setup

```bash
# Install cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Authenticate
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create mqtt-dashboard

# Configure (edit ~/.cloudflared/config.yml)
tunnel: <your-tunnel-id>
credentials-file: /home/user/.cloudflared/<tunnel-id>.json
ingress:
  - hostname: yourdomain.com
    service: http://localhost:80
  - service: http_status:404

# Run tunnel
cloudflared tunnel run mqtt-dashboard
```

## Key Features

### 1. Connect to MQTT Brokers
- Supports multiple simultaneous connections
- Optional username/password authentication
- Automatic reconnection

### 2. Subscribe & Publish
- Subscribe to topics with wildcards (#, +)
- Publish messages with QoS 0, 1, or 2
- Real-time message reception

### 3. Data Logging
- All messages saved to `mqtt_data_points.json`
- Readable JSON format
- Persistent across restarts

### 4. SQL Export
- Convert JSON data to SQL INSERT statements
- Ready for database import
- One-click export and copy

### 5. Terminal Interface
Commands:
- `help` - Show available commands
- `status` - Show connection status
- `publish <broker_id> <topic> <message>` - Publish
- `subscribe <broker_id> <topic>` - Subscribe
- `disconnect <broker_id>` - Disconnect
- `clear` - Clear terminal

## Customization

### Change Colors (static/css/style.css)
```css
:root {
    --primary-color: #3b82f6;  /* Change this */
    --dark-bg: #0f172a;        /* And this */
}
```

### Add Features (app.py)
```python
@app.route('/api/your-endpoint', methods=['POST'])
@login_required
def your_function():
    # Your code here
    return jsonify({'success': True})
```

### Modify UI (templates/dashboard.html)
Add new sections to the dashboard by following the existing pattern.

## Security Checklist

- [ ] Change SECRET_KEY in .env
- [ ] Set up Google OAuth with correct redirect URI
- [ ] Use HTTPS in production (Cloudflare provides this)
- [ ] Restrict OAuth to specific domains
- [ ] Review firewall rules
- [ ] Keep dependencies updated

## Troubleshooting

**Can't bind to port 80:**
```bash
sudo python3 app.py  # Run with sudo
```

**Google OAuth fails:**
- Check redirect URI matches exactly
- Verify Client ID and Secret in .env
- Ensure Google+ API is enabled

**MQTT connection fails:**
- Verify broker host and port
- Check firewall rules
- Test broker connectivity: `mosquitto_sub -h broker -t test`

**Terminal not updating:**
- Check browser console for errors
- Refresh the page
- Verify WebSocket connections aren't blocked

## File Locations

- **Data file:** `mqtt_data_points.json` (auto-created)
- **Logs:** Check terminal output or systemd journal
- **Configuration:** `.env` file

## Next Steps

1. ✅ Install and configure
2. ✅ Set up Google OAuth
3. ✅ Connect to your MQTT broker
4. ✅ Subscribe to topics
5. ✅ View incoming data
6. ✅ Export to SQL
7. ✅ (Optional) Set up Cloudflare Tunnel
8. ✅ (Optional) Customize the design

## Support

- Read the full README.md for detailed documentation
- Check CONTRIBUTING.md if you want to modify the code
- Open an issue on GitHub for bugs or questions

---

**You're ready to go! Start the server and open http://localhost in your browser.**

For production deployment with Cloudflare Tunnel, your dashboard will be accessible worldwide with HTTPS automatically enabled.
