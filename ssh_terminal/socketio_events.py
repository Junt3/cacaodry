"""
WebSocket Event Handlers for SSH Terminal

This module defines the WebSocket events for handling SSH terminal
communication between the frontend and backend.
"""

from flask import request, session
from flask_socketio import Namespace, emit, disconnect
from ssh_terminal.ssh_manager import SSHConnectionManager
import logging

logger = logging.getLogger(__name__)

# Global SSH connection manager
ssh_manager = SSHConnectionManager()


class SSHTerminalNamespace(Namespace):
    """WebSocket namespace for SSH terminal events."""
    
    def on_connect(self):
        """Handle client connection to SSH terminal namespace."""
        # Verify user is authenticated
        if not session.get('config_authenticated'):
            logger.warning(f"Unauthenticated connection attempt from {request.remote_addr}")
            disconnect()
            return
        
        logger.info(f"SSH terminal client connected: {request.sid}")
        emit('connection_status', {
            'status': 'connected',
            'message': 'WebSocket connected. Ready to establish SSH connection.'
        })
    
    def on_disconnect(self):
        """Handle client disconnection."""
        logger.info(f"SSH terminal client disconnected: {request.sid}")
        # Clean up any SSH connection for this session
        ssh_manager.close_connection(request.sid)
    
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
            key_auth = data.get('key_auth', False)
            
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
            
            # Create SSH connection
            success = ssh_manager.create_connection(
                session_id=request.sid,
                host=host,
                port=port,
                username=username,
                password=password if not key_auth else None,
                key=None  # TODO: Implement key-based authentication
            )
            
            if success:
                emit('connection_status', {
                    'status': 'connected',
                    'message': f'Connected to {username}@{host}:{port}'
                })
                
                # Start reading output from SSH connection
                self._start_output_reader()
            else:
                emit('error', {
                    'type': 'connection',
                    'message': 'Failed to establish SSH connection. Please check your credentials.'
                })
                
        except ValueError as e:
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
        try:
            if 'data' not in data:
                return
            
            input_data = data['data']
            success = ssh_manager.send_input(request.sid, input_data)
            
            if not success:
                emit('error', {
                    'type': 'connection',
                    'message': 'No active SSH connection'
                })
                
        except Exception as e:
            logger.error(f"Error in terminal_input: {str(e)}")
            emit('error', {
                'type': 'command',
                'message': 'Error sending input to terminal'
            })
    
    def on_resize_terminal(self, data):
        """Handle terminal resize request."""
        try:
            if 'cols' not in data or 'rows' not in data:
                return
            
            cols = int(data['cols'])
            rows = int(data['rows'])
            
            if cols < 1 or rows < 1:
                return
            
            success = ssh_manager.resize_terminal(request.sid, cols, rows)
            
            if not success:
                logger.warning(f"Failed to resize terminal for session {request.sid}")
                
        except (ValueError, KeyError) as e:
            logger.error(f"Error in resize_terminal: {str(e)}")
    
    def on_disconnect_ssh(self):
        """Handle SSH disconnection request."""
        try:
            ssh_manager.close_connection(request.sid)
            emit('connection_status', {
                'status': 'disconnected',
                'message': 'SSH connection closed'
            })
        except Exception as e:
            logger.error(f"Error in disconnect_ssh: {str(e)}")
    
    def on_get_status(self):
        """Handle status request."""
        try:
            status = ssh_manager.get_connection_status(request.sid)
            emit('connection_status', status)
        except Exception as e:
            logger.error(f"Error in get_status: {str(e)}")
            emit('error', {
                'type': 'status',
                'message': 'Error getting connection status'
            })
    
    def _start_output_reader(self):
        """Start reading output from SSH connection and emit to client."""
        def output_reader():
            while True:
                try:
                    output = ssh_manager.read_output(request.sid)
                    if output:
                        emit('terminal_output', {'data': output})
                    else:
                        # Check if connection is still active
                        status = ssh_manager.get_connection_status(request.sid)
                        if status['status'] != 'connected':
                            break
                    
                    # Small delay to prevent excessive CPU usage
                    import time
                    time.sleep(0.05)
                    
                except Exception as e:
                    logger.error(f"Error in output reader: {str(e)}")
                    break
        
        # Start output reader in a background thread
        import threading
        thread = threading.Thread(target=output_reader, daemon=True)
        thread.start()


def create_ssh_namespace(socketio):
    """Register the SSH terminal namespace with SocketIO."""
    socketio.on_namespace(SSHTerminalNamespace('/ssh-terminal'))
    logger.info("SSH terminal namespace registered")