"""
SSH Connection Manager for Terminal Emulator

This module handles SSH connections, authentication, and command execution
for the web-based terminal emulator.
"""

import paramiko
import threading
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class SSHConnection:
    """Represents a single SSH connection with an interactive shell."""
    
    def __init__(self, host: str, port: int, username: str, password: str = None, key: str = None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.key = key
        self.client = None
        self.channel = None
        self.connected = False
        self.last_activity = datetime.utcnow()
        self._lock = threading.Lock()
        
    def connect(self) -> bool:
        """Establish SSH connection and open interactive shell."""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Authentication
            if self.key:
                # Key-based authentication
                key_obj = paramiko.RSAKey.from_private_key_file(self.key)
                self.client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    pkey=key_obj,
                    timeout=10,
                    look_for_keys=False,
                    allow_agent=False
                )
            else:
                # Password-based authentication
                self.client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    password=self.password,
                    timeout=10,
                    look_for_keys=False,
                    allow_agent=False
                )
            
            # Open interactive shell
            self.channel = self.client.invoke_shell(term='xterm-256color')
            self.channel.setblocking(0)
            self.connected = True
            self.last_activity = datetime.utcnow()
            
            logger.info(f"SSH connection established to {self.username}@{self.host}:{self.port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to {self.username}@{self.host}:{self.port}: {str(e)}")
            self._cleanup()
            return False
    
    def send_input(self, data: str) -> bool:
        """Send input to the SSH shell."""
        if not self.connected or not self.channel:
            return False
            
        try:
            with self._lock:
                self.channel.send(data)
                self.last_activity = datetime.utcnow()
            return True
        except Exception as e:
            logger.error(f"Error sending input to SSH: {str(e)}")
            self._cleanup()
            return False
    
    def read_output(self) -> str:
        """Read output from the SSH channel."""
        if not self.connected or not self.channel:
            return ""
            
        try:
            with self._lock:
                if self.channel.recv_ready():
                    data = self.channel.recv(4096).decode('utf-8', errors='ignore')
                    self.last_activity = datetime.utcnow()
                    return data
                elif self.channel.recv_stderr_ready():
                    data = self.channel.recv_stderr(4096).decode('utf-8', errors='ignore')
                    self.last_activity = datetime.utcnow()
                    return data
        except Exception as e:
            logger.error(f"Error reading from SSH: {str(e)}")
            self._cleanup()
        
        return ""
    
    def resize_terminal(self, cols: int, rows: int) -> bool:
        """Resize the terminal window."""
        if not self.connected or not self.channel:
            return False
            
        try:
            with self._lock:
                self.channel.resize_pty(width=cols, height=rows)
            return True
        except Exception as e:
            logger.error(f"Error resizing terminal: {str(e)}")
            return False
    
    def is_active(self) -> bool:
        """Check if the connection is still active."""
        if not self.connected or not self.client or not self.channel:
            return False
            
        try:
            # Check if channel is still open
            if self.channel.closed:
                return False
                
            # Check timeout (30 minutes of inactivity)
            if datetime.utcnow() - self.last_activity > timedelta(minutes=30):
                logger.info("SSH connection timed out due to inactivity")
                return False
                
            return True
        except Exception:
            return False
    
    def disconnect(self):
        """Close the SSH connection."""
        self._cleanup()
        logger.info(f"SSH connection closed for {self.username}@{self.host}:{self.port}")
    
    def _cleanup(self):
        """Clean up connection resources."""
        with self._lock:
            self.connected = False
            if self.channel:
                try:
                    self.channel.close()
                except:
                    pass
                self.channel = None
            if self.client:
                try:
                    self.client.close()
                except:
                    pass
                self.client = None


class SSHConnectionManager:
    """Manages multiple SSH connections with session isolation."""
    
    def __init__(self):
        self.connections: Dict[str, SSHConnection] = {}
        self._lock = threading.Lock()
        self._cleanup_thread = None
        self._start_cleanup_thread()
    
    def create_connection(self, session_id: str, host: str, port: int, 
                         username: str, password: str = None, key: str = None) -> bool:
        """Create a new SSH connection for a session."""
        with self._lock:
            # Close existing connection for this session if any
            if session_id in self.connections:
                self.connections[session_id].disconnect()
                del self.connections[session_id]
            
            # Create new connection
            conn = SSHConnection(host, port, username, password, key)
            if conn.connect():
                self.connections[session_id] = conn
                logger.info(f"Created SSH connection for session: {session_id}")
                return True
            else:
                return False
    
    def get_connection(self, session_id: str) -> Optional[SSHConnection]:
        """Get existing SSH connection for a session."""
        with self._lock:
            return self.connections.get(session_id)
    
    def send_input(self, session_id: str, data: str) -> bool:
        """Send input to SSH connection."""
        conn = self.get_connection(session_id)
        if conn and conn.is_active():
            return conn.send_input(data)
        return False
    
    def read_output(self, session_id: str) -> str:
        """Read output from SSH connection."""
        conn = self.get_connection(session_id)
        if conn and conn.is_active():
            return conn.read_output()
        return ""
    
    def resize_terminal(self, session_id: str, cols: int, rows: int) -> bool:
        """Resize terminal for SSH connection."""
        conn = self.get_connection(session_id)
        if conn and conn.is_active():
            return conn.resize_terminal(cols, rows)
        return False
    
    def close_connection(self, session_id: str):
        """Close SSH connection for a session."""
        with self._lock:
            if session_id in self.connections:
                self.connections[session_id].disconnect()
                del self.connections[session_id]
                logger.info(f"Closed SSH connection for session: {session_id}")
    
    def _start_cleanup_thread(self):
        """Start background thread to clean up inactive connections."""
        def cleanup():
            while True:
                time.sleep(60)  # Check every minute
                with self._lock:
                    inactive_sessions = []
                    for session_id, conn in self.connections.items():
                        if not conn.is_active():
                            inactive_sessions.append(session_id)
                    
                    for session_id in inactive_sessions:
                        conn = self.connections[session_id]
                        conn.disconnect()
                        del self.connections[session_id]
                        logger.info(f"Cleaned up inactive SSH connection: {session_id}")
        
        self._cleanup_thread = threading.Thread(target=cleanup, daemon=True)
        self._cleanup_thread.start()
    
    def get_connection_status(self, session_id: str) -> Dict[str, Any]:
        """Get status information for a connection."""
        conn = self.get_connection(session_id)
        if not conn:
            return {"status": "disconnected", "message": "No active connection"}
        
        if not conn.is_active():
            return {"status": "disconnected", "message": "Connection inactive"}
        
        return {
            "status": "connected",
            "message": f"Connected to {conn.username}@{conn.host}:{conn.port}",
            "host": conn.host,
            "port": conn.port,
            "username": conn.username,
            "last_activity": conn.last_activity.isoformat()
        }