"""
Simplified WebSocket Event Handlers for SSH Terminal

This is a simplified version to help debug issues with the SSH terminal.
"""

from flask import request, session
from flask_socketio import Namespace, emit, disconnect
import logging

logger = logging.getLogger(__name__)


class SimpleSSHTerminalNamespace(Namespace):
    """Simplified WebSocket namespace for SSH terminal events."""
    
    def on_connect(self):
        """Handle client connection to SSH terminal namespace."""
        logger.info(f"Client connected: {request.sid}")
        
        # Verify user is authenticated
        if not session.get('config_authenticated'):
            logger.warning(f"Unauthenticated connection attempt from {request.remote_addr}")
            disconnect()
            return
        
        emit('connection_status', {
            'status': 'connected',
            'message': 'WebSocket connected. Ready to establish SSH connection.'
        })
    
    def on_disconnect(self):
        """Handle client disconnection."""
        logger.info(f"Client disconnected: {request.sid}")
    
    def on_connect_ssh(self, data):
        """Handle SSH connection request."""
        logger.info(f"Received connect_ssh request: {data}")
        
        try:
            # Validate required fields
            required_fields = ['host', 'port', 'username']
            for field in required_fields:
                if field not in data or not data[field]:
                    logger.error(f"Missing required field: {field}")
                    emit('error', {
                        'type': 'validation',
                        'message': f'Missing required field: {field}'
                    })
                    return
            
            host = data['host'].strip()
            port = int(data['port'])
            username = data['username'].strip()
            password = data.get('password', '').strip()
            
            logger.info(f"Attempting to connect to {username}@{host}:{port}")
            
            # Validate port range
            if port < 1 or port > 65535:
                emit('error', {
                    'type': 'validation',
                    'message': 'Port must be between 1 and 65535'
                })
                return
            
            emit('connection_status', {
                'status': 'connecting',
                'message': f'Connecting to {username}@{host}:{port}...'
            })
            
            # For now, just simulate a connection
            # In production, this would use the SSH manager
            import time
            time.sleep(1)
            
            emit('connection_status', {
                'status': 'connected',
                'message': f'Connected to {username}@{host}:{port}'
            })
            
            # Send a welcome message to terminal
            emit('terminal_output', {
                'data': f'\r\nConnected to {username}@{host}:{port}\r\n'
            })
            
            # Send a prompt
            emit('terminal_output', {
                'data': f'{username}@{host}:~$ '
            })
                
        except ValueError as e:
            logger.error(f"ValueError in connect_ssh: {str(e)}")
            emit('error', {
                'type': 'validation',
                'message': f'Invalid input: {str(e)}'
            })
        except Exception as e:
            logger.error(f"Error in connect_ssh: {str(e)}")
            emit('error', {
                'type': 'connection',
                'message': 'An unexpected error occurred while connecting.'
            })
    
    def on_terminal_input(self, data):
        """Handle terminal input from client."""
        logger.info(f"Received terminal input: {data}")
        
        try:
            if 'data' not in data:
                return
            
            input_data = data['data']
            
            # Echo the input back for testing
            if input_data == '\r' or input_data == '\n':
                emit('terminal_output', {
                    'data': '\r\n'
                })
                emit('terminal_output', {
                    'data': '$ '
                })
            else:
                emit('terminal_output', {
                    'data': input_data
                })
                
        except Exception as e:
            logger.error(f"Error in terminal_input: {str(e)}")
            emit('error', {
                'type': 'command',
                'message': 'Error sending input to terminal'
            })
    
    def on_disconnect_ssh(self):
        """Handle SSH disconnection request."""
        logger.info("Received disconnect_ssh request")
        emit('connection_status', {
            'status': 'disconnected',
            'message': 'SSH connection closed'
        })


def create_simple_ssh_namespace(socketio):
    """Register simplified SSH terminal namespace with SocketIO."""
    socketio.on_namespace(SimpleSSHTerminalNamespace('/ssh-terminal'))
    logger.info("Simple SSH terminal namespace registered")