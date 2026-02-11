"""
MQTT Dashboard Web Server
An open-source MQTT connection manager with data logging and SQL export
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from authlib.integrations.flask_client import OAuth
import paho.mqtt.client as mqtt
import json
import sqlite3
import os
from datetime import datetime
import threading
import logging
from werkzeug.security import generate_password_hash, check_password_hash

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# OAuth Configuration for Google Sign-In
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID', 'YOUR_GOOGLE_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET', 'YOUR_GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User class
class User(UserMixin):
    def __init__(self, id, email, name):
        self.id = id
        self.email = email
        self.name = name

# In-memory user storage (replace with database in production)
users_db = {}

@login_manager.user_loader
def load_user(user_id):
    return users_db.get(user_id)

# MQTT Configuration
MQTT_DATA_FILE = 'mqtt_data_points.json'
mqtt_clients = {}
mqtt_subscriptions = {}
terminal_logs = []

class MQTTManager:
    def __init__(self):
        self.clients = {}
        self.data_points = self.load_data_points()
        
    def load_data_points(self):
        """Load MQTT data points from file"""
        if os.path.exists(MQTT_DATA_FILE):
            try:
                with open(MQTT_DATA_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading data points: {e}")
                return []
        return []
    
    def save_data_points(self):
        """Save MQTT data points to file"""
        try:
            with open(MQTT_DATA_FILE, 'w') as f:
                json.dump(self.data_points, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving data points: {e}")
    
    def add_data_point(self, broker, topic, payload, qos=0):
        """Add a new data point"""
        data_point = {
            'timestamp': datetime.now().isoformat(),
            'broker': broker,
            'topic': topic,
            'payload': payload,
            'qos': qos
        }
        self.data_points.append(data_point)
        self.save_data_points()
        self.add_terminal_log(f"[DATA] Received on {topic}: {payload}")
        return data_point
    
    def export_to_sql(self):
        """Export data points to SQL format"""
        sql_statements = []
        
        # Create table statement
        create_table = """
CREATE TABLE IF NOT EXISTS mqtt_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    broker TEXT NOT NULL,
    topic TEXT NOT NULL,
    payload TEXT,
    qos INTEGER
);
"""
        sql_statements.append(create_table)
        
        # Insert statements
        for dp in self.data_points:
            insert = f"""INSERT INTO mqtt_data (timestamp, broker, topic, payload, qos) 
VALUES ('{dp['timestamp']}', '{dp['broker']}', '{dp['topic']}', '{dp['payload']}', {dp['qos']});"""
            sql_statements.append(insert)
        
        return '\n'.join(sql_statements)
    
    def add_terminal_log(self, message):
        """Add a log message to the terminal"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        terminal_logs.append(log_entry)
        # Keep only last 100 logs
        if len(terminal_logs) > 100:
            terminal_logs.pop(0)
        logger.info(message)
    
    def create_mqtt_client(self, broker_id, broker_host, broker_port, username=None, password=None):
        """Create and connect MQTT client"""
        try:
            client = mqtt.Client(client_id=f"dashboard_{broker_id}")
            
            # Set callbacks
            def on_connect(client, userdata, flags, rc):
                if rc == 0:
                    self.add_terminal_log(f"[SUCCESS] Connected to broker {broker_host}:{broker_port}")
                else:
                    self.add_terminal_log(f"[ERROR] Connection failed with code {rc}")
            
            def on_message(client, userdata, msg):
                payload = msg.payload.decode('utf-8')
                self.add_data_point(broker_id, msg.topic, payload, msg.qos)
            
            def on_disconnect(client, userdata, rc):
                self.add_terminal_log(f"[DISCONNECT] Lost connection to {broker_host}:{broker_port}")
            
            client.on_connect = on_connect
            client.on_message = on_message
            client.on_disconnect = on_disconnect
            
            if username and password:
                client.username_pw_set(username, password)
            
            client.connect(broker_host, int(broker_port), 60)
            client.loop_start()
            
            self.clients[broker_id] = client
            self.add_terminal_log(f"[INFO] Attempting to connect to {broker_host}:{broker_port}")
            
            return True
        except Exception as e:
            self.add_terminal_log(f"[ERROR] Failed to create client: {str(e)}")
            logger.error(f"MQTT client creation error: {e}")
            return False
    
    def subscribe_topic(self, broker_id, topic, qos=0):
        """Subscribe to a topic"""
        if broker_id in self.clients:
            try:
                self.clients[broker_id].subscribe(topic, qos)
                self.add_terminal_log(f"[SUBSCRIBE] Subscribed to {topic} on {broker_id}")
                return True
            except Exception as e:
                self.add_terminal_log(f"[ERROR] Failed to subscribe: {str(e)}")
                return False
        return False
    
    def publish_message(self, broker_id, topic, payload, qos=0):
        """Publish a message to a topic"""
        if broker_id in self.clients:
            try:
                self.clients[broker_id].publish(topic, payload, qos)
                self.add_terminal_log(f"[PUBLISH] Published to {topic}: {payload}")
                return True
            except Exception as e:
                self.add_terminal_log(f"[ERROR] Failed to publish: {str(e)}")
                return False
        return False
    
    def disconnect_broker(self, broker_id):
        """Disconnect from a broker"""
        if broker_id in self.clients:
            try:
                self.clients[broker_id].loop_stop()
                self.clients[broker_id].disconnect()
                del self.clients[broker_id]
                self.add_terminal_log(f"[DISCONNECT] Disconnected from {broker_id}")
                return True
            except Exception as e:
                self.add_terminal_log(f"[ERROR] Failed to disconnect: {str(e)}")
                return False
        return False

# Initialize MQTT Manager
mqtt_manager = MQTTManager()

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/auth/google')
def google_login():
    redirect_uri = url_for('google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/auth/callback')
def google_callback():
    try:
        token = google.authorize_access_token()
        user_info = token.get('userinfo')
        
        if user_info:
            user_id = user_info['sub']
            user = User(
                id=user_id,
                email=user_info['email'],
                name=user_info.get('name', user_info['email'])
            )
            users_db[user_id] = user
            login_user(user)
            mqtt_manager.add_terminal_log(f"[AUTH] User {user.email} logged in")
            return redirect(url_for('dashboard'))
    except Exception as e:
        logger.error(f"Google authentication error: {e}")
        mqtt_manager.add_terminal_log(f"[ERROR] Authentication failed: {str(e)}")
    
    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    mqtt_manager.add_terminal_log(f"[AUTH] User {current_user.email} logged out")
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

# API Routes
@app.route('/api/brokers', methods=['GET'])
@login_required
def get_brokers():
    brokers = [{'id': broker_id, 'connected': True} for broker_id in mqtt_manager.clients.keys()]
    return jsonify(brokers)

@app.route('/api/brokers/connect', methods=['POST'])
@login_required
def connect_broker():
    data = request.json
    broker_id = data.get('broker_id')
    host = data.get('host')
    port = data.get('port', 1883)
    username = data.get('username')
    password = data.get('password')
    
    if mqtt_manager.create_mqtt_client(broker_id, host, port, username, password):
        return jsonify({'success': True, 'message': 'Broker connected'})
    return jsonify({'success': False, 'message': 'Failed to connect'}), 400

@app.route('/api/brokers/disconnect', methods=['POST'])
@login_required
def disconnect_broker():
    data = request.json
    broker_id = data.get('broker_id')
    
    if mqtt_manager.disconnect_broker(broker_id):
        return jsonify({'success': True, 'message': 'Broker disconnected'})
    return jsonify({'success': False, 'message': 'Failed to disconnect'}), 400

@app.route('/api/topics/subscribe', methods=['POST'])
@login_required
def subscribe_topic():
    data = request.json
    broker_id = data.get('broker_id')
    topic = data.get('topic')
    qos = data.get('qos', 0)
    
    if mqtt_manager.subscribe_topic(broker_id, topic, qos):
        return jsonify({'success': True, 'message': f'Subscribed to {topic}'})
    return jsonify({'success': False, 'message': 'Failed to subscribe'}), 400

@app.route('/api/topics/publish', methods=['POST'])
@login_required
def publish_message():
    data = request.json
    broker_id = data.get('broker_id')
    topic = data.get('topic')
    payload = data.get('payload')
    qos = data.get('qos', 0)
    
    if mqtt_manager.publish_message(broker_id, topic, payload, qos):
        return jsonify({'success': True, 'message': 'Message published'})
    return jsonify({'success': False, 'message': 'Failed to publish'}), 400

@app.route('/api/data/points', methods=['GET'])
@login_required
def get_data_points():
    limit = request.args.get('limit', 100, type=int)
    return jsonify(mqtt_manager.data_points[-limit:])

@app.route('/api/data/export/sql', methods=['GET'])
@login_required
def export_sql():
    sql_content = mqtt_manager.export_to_sql()
    return jsonify({'sql': sql_content})

@app.route('/api/data/clear', methods=['POST'])
@login_required
def clear_data():
    mqtt_manager.data_points = []
    mqtt_manager.save_data_points()
    mqtt_manager.add_terminal_log("[INFO] Data points cleared")
    return jsonify({'success': True, 'message': 'Data cleared'})

@app.route('/api/terminal/logs', methods=['GET'])
@login_required
def get_terminal_logs():
    return jsonify(terminal_logs)

@app.route('/api/terminal/command', methods=['POST'])
@login_required
def execute_command():
    data = request.json
    command = data.get('command', '')
    
    # Parse and execute commands
    parts = command.strip().split()
    if not parts:
        return jsonify({'success': False, 'message': 'Empty command'})
    
    cmd = parts[0].lower()
    
    if cmd == 'help':
        help_text = """
Available commands:
  help - Show this help message
  clear - Clear terminal logs
  status - Show connection status
  publish <broker_id> <topic> <message> - Publish a message
  subscribe <broker_id> <topic> - Subscribe to a topic
  disconnect <broker_id> - Disconnect from broker
        """
        mqtt_manager.add_terminal_log(help_text)
        return jsonify({'success': True})
    
    elif cmd == 'clear':
        terminal_logs.clear()
        mqtt_manager.add_terminal_log("[INFO] Terminal cleared")
        return jsonify({'success': True})
    
    elif cmd == 'status':
        status = f"Connected brokers: {len(mqtt_manager.clients)}"
        mqtt_manager.add_terminal_log(status)
        for broker_id in mqtt_manager.clients.keys():
            mqtt_manager.add_terminal_log(f"  - {broker_id}")
        return jsonify({'success': True})
    
    elif cmd == 'publish' and len(parts) >= 4:
        broker_id = parts[1]
        topic = parts[2]
        message = ' '.join(parts[3:])
        mqtt_manager.publish_message(broker_id, topic, message)
        return jsonify({'success': True})
    
    elif cmd == 'subscribe' and len(parts) >= 3:
        broker_id = parts[1]
        topic = parts[2]
        mqtt_manager.subscribe_topic(broker_id, topic)
        return jsonify({'success': True})
    
    elif cmd == 'disconnect' and len(parts) >= 2:
        broker_id = parts[1]
        mqtt_manager.disconnect_broker(broker_id)
        return jsonify({'success': True})
    
    else:
        mqtt_manager.add_terminal_log(f"[ERROR] Unknown command: {command}")
        return jsonify({'success': False, 'message': 'Unknown command'})

if __name__ == '__main__':
    mqtt_manager.add_terminal_log("[INFO] MQTT Dashboard Server starting...")
    mqtt_manager.add_terminal_log("[INFO] Server running on port 80")
    app.run(host='0.0.0.0', port=80, debug=False)
