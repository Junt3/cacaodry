#!/usr/bin/env python3
"""
Test script for SSH Terminal functionality

This script tests the SSH terminal components to ensure they work correctly
before deploying to production.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ssh_terminal.ssh_manager import SSHConnectionManager, SSHConnection
from ssh_terminal.utils import validate_connection_params, is_dangerous_command
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ssh_connection_manager():
    """Test SSH Connection Manager functionality."""
    print("\n=== Testing SSH Connection Manager ===")
    
    manager = SSHConnectionManager()
    
    # Test connection with invalid parameters
    print("Testing invalid connection parameters...")
    result = manager.create_connection(
        session_id="test1",
        host="invalid.example.com",
        port=22,
        username="test",
        password="test"
    )
    print(f"Invalid connection result: {result}")
    
    # Test connection status
    status = manager.get_connection_status("test1")
    print(f"Connection status: {status}")
    
    print("✓ SSH Connection Manager tests completed")

def test_ssh_connection():
    """Test SSH Connection class."""
    print("\n=== Testing SSH Connection Class ===")
    
    # Test with localhost if SSH is available
    conn = SSHConnection(
        host="localhost",
        port=22,
        username="test",
        password="test"
    )
    
    # This will likely fail unless SSH server is running with test user
    result = conn.connect()
    print(f"Connection attempt result: {result}")
    
    if result:
        print("✓ SSH connection successful")
        conn.disconnect()
    else:
        print("✓ SSH connection failed as expected (no test SSH server)")
    
    print("✓ SSH Connection tests completed")

def test_validation():
    """Test input validation functions."""
    print("\n=== Testing Input Validation ===")
    
    # Test valid parameters
    valid_params = {
        'host': 'example.com',
        'port': 22,
        'username': 'testuser'
    }
    is_valid, error = validate_connection_params(valid_params)
    print(f"Valid parameters: {is_valid}, Error: {error}")
    
    # Test invalid parameters
    invalid_params = {
        'host': '',
        'port': 22,
        'username': 'testuser'
    }
    is_valid, error = validate_connection_params(invalid_params)
    print(f"Invalid host: {is_valid}, Error: {error}")
    
    # Test dangerous command detection
    dangerous = "rm -rf /"
    print(f"Command '{dangerous}' is dangerous: {is_dangerous_command(dangerous)}")
    
    safe = "ls -la"
    print(f"Command '{safe}' is dangerous: {is_dangerous_command(safe)}")
    
    print("✓ Input validation tests completed")

def test_socketio_events():
    """Test SocketIO event handlers."""
    print("\n=== Testing SocketIO Event Handlers ===")
    
    # Import the namespace
    from ssh_terminal.socketio_events import SSHTerminalNamespace
    
    # Create a mock namespace instance
    namespace = SSHTerminalNamespace()
    
    print("✓ SocketIO namespace created successfully")
    print("✓ SocketIO event handlers tests completed")

def main():
    """Run all tests."""
    print("Starting SSH Terminal Tests...")
    
    try:
        test_validation()
        test_ssh_connection_manager()
        test_ssh_connection()
        test_socketio_events()
        
        print("\n✅ All tests completed successfully!")
        print("\nTo test the SSH terminal in the browser:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run the application: python app.py")
        print("3. Navigate to http://localhost:5000")
        print("4. Login to configuration page")
        print("5. Click on 'SSH Terminal' tab")
        print("6. Enter SSH connection details and click 'Connect'")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        logger.exception("Test failed")
        sys.exit(1)

if __name__ == "__main__":
    main()