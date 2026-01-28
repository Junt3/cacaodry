#!/usr/bin/env python3
"""
Simple test script to verify WebSocket functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.secret_key = 'test-secret-key'

# Initialize SocketIO with threading mode
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('test_response', {'message': 'WebSocket connected successfully!'})

@socketio.on('test_message')
def handle_test_message(data):
    print(f'Received test message: {data}')
    emit('test_response', {'message': f'Received: {data}'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@app.route('/')
def index():
    return """
    <html>
    <head>
        <title>WebSocket Test</title>
        <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    </head>
    <body>
        <h1>WebSocket Test</h1>
        <button onclick="testConnection()">Test Connection</button>
        <div id="output"></div>
        
        <script>
            const socket = io();
            
            socket.on('connect', () => {
                console.log('Connected to WebSocket');
                document.getElementById('output').innerHTML += '<p>Connected to WebSocket</p>';
            });
            
            socket.on('test_response', (data) => {
                console.log('Received response:', data);
                document.getElementById('output').innerHTML += '<p>Response: ' + data.message + '</p>';
            });
            
            function testConnection() {
                console.log('Sending test message');
                socket.emit('test_message', {data: 'Hello WebSocket!'});
            }
        </script>
    </body>
    </html>
    """

if __name__ == '__main__':
    print("Starting WebSocket test server on http://localhost:5001")
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)