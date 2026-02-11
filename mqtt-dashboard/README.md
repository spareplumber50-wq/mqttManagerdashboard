# MQTT Dashboard

An open-source web-based MQTT connection manager with data logging, SQL export, and real-time terminal interface.

## Features

- 🔌 **Multi-Broker Support** - Connect to multiple MQTT brokers simultaneously
- 📊 **Data Point Logging** - Automatically log all incoming MQTT messages to a JSON file
- 💾 **SQL Export** - Convert logged data to SQL format for database import
- 💻 **Interactive Terminal** - Send commands and monitor MQTT activity in real-time
- 🔐 **Google Authentication** - Secure login with Google Sign-In
- 🎨 **Modern UI** - Sleek, dark-themed interface with responsive design
- 🌐 **Cloudflare Tunnel Ready** - Designed to work seamlessly with Cloudflare tunnels

## Quick Start

### Prerequisites

- Linux machine (Ubuntu 20.04+ recommended)
- Python 3.8 or higher
- pip package manager
- Google Cloud account (for OAuth)

### Installation

1. **Clone or download this project:**
   ```bash
   cd /path/to/mqtt-dashboard
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Google OAuth:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Google+ API
   - Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
   - Application type: Web application
   - Add authorized redirect URI: `http://your-domain/auth/callback`
   - Copy the Client ID and Client Secret

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   nano .env
   ```
   
   Fill in your values:
   ```
   SECRET_KEY=your-random-secret-key
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   ```

5. **Run the server:**
   ```bash
   sudo python3 app.py
   ```
   
   The server will start on port 80.

### Setting up Cloudflare Tunnel

1. **Install cloudflared:**
   ```bash
   wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
   sudo dpkg -i cloudflared-linux-amd64.deb
   ```

2. **Authenticate cloudflared:**
   ```bash
   cloudflared tunnel login
   ```

3. **Create a tunnel:**
   ```bash
   cloudflared tunnel create mqtt-dashboard
   ```

4. **Create config file:**
   ```bash
   nano ~/.cloudflared/config.yml
   ```
   
   Add:
   ```yaml
   tunnel: <tunnel-id>
   credentials-file: /home/<user>/.cloudflared/<tunnel-id>.json
   
   ingress:
     - hostname: your-domain.com
       service: http://localhost:80
     - service: http_status:404
   ```

5. **Run the tunnel:**
   ```bash
   cloudflared tunnel run mqtt-dashboard
   ```

## Usage

### Connecting to an MQTT Broker

1. Navigate to the **Connections** tab
2. Fill in the broker details:
   - **Broker ID**: A unique identifier (e.g., "main-broker")
   - **Host**: MQTT broker hostname or IP
   - **Port**: MQTT port (default: 1883)
   - **Username/Password**: Optional credentials
3. Click "Connect to Broker"

### Subscribing to Topics

1. Enter the Broker ID you connected to
2. Enter the topic pattern (e.g., `sensors/#` or `home/temperature`)
3. Select QoS level (0, 1, or 2)
4. Click "Subscribe"

### Publishing Messages

1. Enter the Broker ID
2. Enter the topic
3. Enter the message payload
4. Select QoS level
5. Click "Publish"

### Using the Terminal

The terminal accepts the following commands:

- `help` - Show available commands
- `clear` - Clear terminal output
- `status` - Show connection status
- `publish <broker_id> <topic> <message>` - Publish a message
- `subscribe <broker_id> <topic>` - Subscribe to a topic
- `disconnect <broker_id>` - Disconnect from a broker

Example:
```
$ publish main-broker sensors/temp 23.5
$ subscribe main-broker home/#
```

### Viewing Data Points

1. Navigate to the **Data Points** tab
2. View all received MQTT messages in a table
3. Click "Refresh" to update the data
4. Click "Clear All" to delete all logged data

### Exporting Data

1. Navigate to the **Export** tab
2. Click "Generate SQL Export" to create SQL INSERT statements
3. Click "Download JSON" to download the raw data file
4. Use "Copy to Clipboard" to copy SQL statements

## File Structure

```
mqtt-dashboard/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── mqtt_data_points.json      # Data storage (auto-created)
├── templates/
│   ├── login.html             # Login page
│   └── dashboard.html         # Main dashboard
└── static/
    ├── css/
    │   └── style.css          # All styling
    └── js/
        └── dashboard.js       # Client-side logic
```

## Data Storage

All MQTT data points are stored in `mqtt_data_points.json` with the following format:

```json
[
  {
    "timestamp": "2024-02-11T10:30:00",
    "broker": "main-broker",
    "topic": "sensors/temperature",
    "payload": "23.5",
    "qos": 0
  }
]
```

This file can be:
- Read back by the application
- Exported to SQL format
- Downloaded as JSON
- Manually edited or processed

## Customization

### Modifying Styles

All CSS is in `static/css/style.css`. The design uses CSS variables for easy theming:

```css
:root {
    --primary-color: #3b82f6;
    --dark-bg: #0f172a;
    /* ... modify as needed */
}
```

### Adding Features

The application is structured for easy modification:

1. **Backend (app.py)**: Add new API endpoints in the Flask app
2. **Frontend (dashboard.html)**: Add new UI sections
3. **Logic (dashboard.js)**: Add new JavaScript functionality
4. **Styling (style.css)**: Style your new components

## Security Considerations

- Change the `SECRET_KEY` in production
- Use HTTPS in production (Cloudflare Tunnel provides this)
- Restrict Google OAuth to specific domains
- Consider adding rate limiting for API endpoints
- Review user access and implement role-based access if needed

## Troubleshooting

### Port 80 Permission Error
```bash
# Run with sudo or use a higher port
sudo python3 app.py
```

### Google OAuth Redirect Error
- Make sure the redirect URI in Google Console matches your domain
- Check that `http://your-domain/auth/callback` is added

### MQTT Connection Failed
- Verify broker host and port
- Check if authentication is required
- Ensure firewall allows MQTT connections

### Cloudflare Tunnel Issues
- Verify tunnel configuration
- Check cloudflared logs: `cloudflared tunnel info mqtt-dashboard`
- Ensure tunnel is running: `ps aux | grep cloudflared`

## Contributing

This is an open-source project. Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - feel free to use and modify as needed.

## Support

For issues, questions, or suggestions:
- Open an issue on the repository
- Check existing documentation
- Review the terminal logs for debugging

## Roadmap

Potential future features:
- [ ] Multi-user support with roles
- [ ] MQTT over WebSocket support
- [ ] Data visualization with charts
- [ ] Automated backups
- [ ] Email notifications
- [ ] API key authentication
- [ ] Docker containerization
- [ ] Database storage option (PostgreSQL/MySQL)

---

Built with ❤️ for the MQTT community
