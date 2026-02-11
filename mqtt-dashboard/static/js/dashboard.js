// MQTT Dashboard Client-Side JavaScript

class MQTTDashboard {
    constructor() {
        this.activeBrokers = new Set();
        this.terminalUpdateInterval = null;
        this.dataUpdateInterval = null;
        this.init();
    }

    init() {
        this.setupNavigation();
        this.setupForms();
        this.setupTerminal();
        this.setupDataRefresh();
        this.setupExport();
        this.startAutoRefresh();
    }

    setupNavigation() {
        const navItems = document.querySelectorAll('.nav-item');
        const sections = document.querySelectorAll('.content-section');
        
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const targetSection = item.dataset.section;
                
                // Update active nav item
                navItems.forEach(nav => nav.classList.remove('active'));
                item.classList.add('active');
                
                // Update active section
                sections.forEach(section => section.classList.remove('active'));
                document.getElementById(`${targetSection}-section`).classList.add('active');
                
                // Update header title
                const titles = {
                    'connections': 'MQTT Connections',
                    'data': 'Data Points',
                    'terminal': 'Terminal',
                    'export': 'Export Data'
                };
                document.getElementById('section-title').textContent = titles[targetSection];
            });
        });
    }

    setupForms() {
        // Broker connection form
        document.getElementById('broker-connect-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.connectBroker();
        });

        // Subscribe form
        document.getElementById('subscribe-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.subscribeTopic();
        });

        // Publish form
        document.getElementById('publish-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.publishMessage();
        });

        // Clear data button
        document.getElementById('clear-data-btn').addEventListener('click', async () => {
            if (confirm('Are you sure you want to clear all data points?')) {
                await this.clearData();
            }
        });

        // Refresh data button
        document.getElementById('refresh-data-btn').addEventListener('click', async () => {
            await this.refreshData();
        });
    }

    setupTerminal() {
        const terminalInput = document.getElementById('terminal-input');
        const clearBtn = document.getElementById('clear-terminal-btn');

        terminalInput.addEventListener('keypress', async (e) => {
            if (e.key === 'Enter') {
                const command = terminalInput.value.trim();
                if (command) {
                    await this.executeCommand(command);
                    terminalInput.value = '';
                }
            }
        });

        clearBtn.addEventListener('click', async () => {
            await this.executeCommand('clear');
        });

        // Auto-refresh terminal
        this.terminalUpdateInterval = setInterval(() => {
            this.refreshTerminal();
        }, 2000);
    }

    setupDataRefresh() {
        // Auto-refresh data every 5 seconds
        this.dataUpdateInterval = setInterval(() => {
            const dataSection = document.getElementById('data-section');
            if (dataSection.classList.contains('active')) {
                this.refreshData();
            }
        }, 5000);
    }

    setupExport() {
        document.getElementById('export-sql-btn').addEventListener('click', async () => {
            await this.exportSQL();
        });

        document.getElementById('download-json-btn').addEventListener('click', () => {
            this.downloadJSON();
        });

        document.getElementById('copy-sql-btn').addEventListener('click', () => {
            this.copySQLToClipboard();
        });
    }

    async connectBroker() {
        const brokerId = document.getElementById('broker-id').value;
        const host = document.getElementById('broker-host').value;
        const port = document.getElementById('broker-port').value;
        const username = document.getElementById('broker-username').value;
        const password = document.getElementById('broker-password').value;

        try {
            const response = await fetch('/api/brokers/connect', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    broker_id: brokerId, 
                    host, 
                    port,
                    username: username || null,
                    password: password || null
                })
            });

            const data = await response.json();
            if (data.success) {
                this.showNotification('Broker connected successfully', 'success');
                this.activeBrokers.add(brokerId);
                this.updateBrokersList();
                document.getElementById('broker-connect-form').reset();
            } else {
                this.showNotification('Failed to connect: ' + data.message, 'error');
            }
        } catch (error) {
            this.showNotification('Connection error: ' + error.message, 'error');
        }
    }

    async subscribeTopic() {
        const brokerId = document.getElementById('sub-broker-id').value;
        const topic = document.getElementById('sub-topic').value;
        const qos = parseInt(document.getElementById('sub-qos').value);

        try {
            const response = await fetch('/api/topics/subscribe', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ broker_id: brokerId, topic, qos })
            });

            const data = await response.json();
            if (data.success) {
                this.showNotification(`Subscribed to ${topic}`, 'success');
                document.getElementById('subscribe-form').reset();
            } else {
                this.showNotification('Failed to subscribe: ' + data.message, 'error');
            }
        } catch (error) {
            this.showNotification('Subscription error: ' + error.message, 'error');
        }
    }

    async publishMessage() {
        const brokerId = document.getElementById('pub-broker-id').value;
        const topic = document.getElementById('pub-topic').value;
        const payload = document.getElementById('pub-payload').value;
        const qos = parseInt(document.getElementById('pub-qos').value);

        try {
            const response = await fetch('/api/topics/publish', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ broker_id: brokerId, topic, payload, qos })
            });

            const data = await response.json();
            if (data.success) {
                this.showNotification('Message published', 'success');
                document.getElementById('publish-form').reset();
            } else {
                this.showNotification('Failed to publish: ' + data.message, 'error');
            }
        } catch (error) {
            this.showNotification('Publish error: ' + error.message, 'error');
        }
    }

    async updateBrokersList() {
        try {
            const response = await fetch('/api/brokers');
            const brokers = await response.json();
            
            const brokersList = document.getElementById('active-brokers');
            if (brokers.length === 0) {
                brokersList.innerHTML = '<p class="empty-state">No active connections</p>';
            } else {
                brokersList.innerHTML = brokers.map(broker => `
                    <div class="broker-item">
                        <div class="broker-info">
                            <span class="broker-status"></span>
                            <span class="broker-name">${broker.id}</span>
                        </div>
                        <div class="broker-actions">
                            <button class="btn btn-danger btn-sm" onclick="dashboard.disconnectBroker('${broker.id}')">
                                Disconnect
                            </button>
                        </div>
                    </div>
                `).join('');
            }
        } catch (error) {
            console.error('Error updating brokers list:', error);
        }
    }

    async disconnectBroker(brokerId) {
        try {
            const response = await fetch('/api/brokers/disconnect', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ broker_id: brokerId })
            });

            const data = await response.json();
            if (data.success) {
                this.showNotification('Broker disconnected', 'success');
                this.activeBrokers.delete(brokerId);
                this.updateBrokersList();
            } else {
                this.showNotification('Failed to disconnect: ' + data.message, 'error');
            }
        } catch (error) {
            this.showNotification('Disconnect error: ' + error.message, 'error');
        }
    }

    async refreshData() {
        try {
            const response = await fetch('/api/data/points?limit=100');
            const dataPoints = await response.json();
            
            const tbody = document.getElementById('data-points-body');
            if (dataPoints.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="empty-state">No data points received</td></tr>';
            } else {
                tbody.innerHTML = dataPoints.reverse().map(dp => `
                    <tr>
                        <td>${new Date(dp.timestamp).toLocaleString()}</td>
                        <td>${dp.broker}</td>
                        <td>${dp.topic}</td>
                        <td>${dp.payload}</td>
                        <td>${dp.qos}</td>
                    </tr>
                `).join('');
            }
        } catch (error) {
            console.error('Error refreshing data:', error);
        }
    }

    async clearData() {
        try {
            const response = await fetch('/api/data/clear', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            const data = await response.json();
            if (data.success) {
                this.showNotification('Data cleared', 'success');
                await this.refreshData();
            }
        } catch (error) {
            this.showNotification('Error clearing data: ' + error.message, 'error');
        }
    }

    async refreshTerminal() {
        try {
            const response = await fetch('/api/terminal/logs');
            const logs = await response.json();
            
            const terminalOutput = document.getElementById('terminal-output');
            terminalOutput.innerHTML = logs.map(log => 
                `<div class="terminal-line">${this.escapeHtml(log)}</div>`
            ).join('');
            
            // Auto-scroll to bottom
            terminalOutput.scrollTop = terminalOutput.scrollHeight;
        } catch (error) {
            console.error('Error refreshing terminal:', error);
        }
    }

    async executeCommand(command) {
        try {
            const response = await fetch('/api/terminal/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command })
            });

            await response.json();
            // Terminal will auto-refresh with the result
            setTimeout(() => this.refreshTerminal(), 100);
        } catch (error) {
            console.error('Error executing command:', error);
        }
    }

    async exportSQL() {
        try {
            const response = await fetch('/api/data/export/sql');
            const data = await response.json();
            
            document.getElementById('sql-content').textContent = data.sql;
            document.getElementById('sql-output').style.display = 'block';
            this.showNotification('SQL export generated', 'success');
        } catch (error) {
            this.showNotification('Error generating SQL: ' + error.message, 'error');
        }
    }

    async downloadJSON() {
        try {
            const response = await fetch('/api/data/points?limit=10000');
            const data = await response.json();
            
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `mqtt_data_points_${new Date().toISOString()}.json`;
            a.click();
            URL.revokeObjectURL(url);
            
            this.showNotification('JSON downloaded', 'success');
        } catch (error) {
            this.showNotification('Error downloading JSON: ' + error.message, 'error');
        }
    }

    copySQLToClipboard() {
        const sqlContent = document.getElementById('sql-content').textContent;
        navigator.clipboard.writeText(sqlContent).then(() => {
            this.showNotification('SQL copied to clipboard', 'success');
        }).catch(err => {
            this.showNotification('Failed to copy: ' + err.message, 'error');
        });
    }

    showNotification(message, type) {
        const statusText = document.getElementById('status-text');
        const statusDot = document.querySelector('.status-dot');
        
        statusText.textContent = message;
        
        if (type === 'success') {
            statusDot.style.background = 'var(--success-color)';
        } else if (type === 'error') {
            statusDot.style.background = 'var(--danger-color)';
        } else {
            statusDot.style.background = 'var(--warning-color)';
        }
        
        setTimeout(() => {
            statusText.textContent = 'Ready';
            statusDot.style.background = 'var(--success-color)';
        }, 3000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    startAutoRefresh() {
        // Initial load
        this.updateBrokersList();
        this.refreshTerminal();
        this.refreshData();
    }
}

// Initialize dashboard when DOM is loaded
let dashboard;
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new MQTTDashboard();
});
