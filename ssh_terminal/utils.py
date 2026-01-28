"""
Utility functions for SSH Terminal module

This module provides helper functions for logging, validation,
and security measures for the SSH terminal feature.
"""

import re
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

# Dangerous commands that should be restricted
DANGEROUS_COMMANDS = [
    r'rm\s+-rf\s+/',  # Remove root directory
    r'format\s+',     # Format disk
    r'fdisk\s+',      # Disk partitioning
    r'mkfs\.',        # Make filesystem
    r'dd\s+if=/dev/zero',  # Zero out disk
    r':\(\)\{\s*:\|:&\s*\}\;',  # Fork bomb
    r'shutdown\s+',   # Shutdown system
    r'reboot\s+',     # Reboot system
    r'poweroff\s+',   # Power off system
    r'halt\s+',       # Halt system
]

# Compile regex patterns for dangerous commands
DANGEROUS_PATTERNS = [re.compile(cmd, re.IGNORECASE) for cmd in DANGEROUS_COMMANDS]


def is_dangerous_command(command: str) -> bool:
    """
    Check if a command contains potentially dangerous operations.
    
    Args:
        command: The command string to check
        
    Returns:
        True if the command is dangerous, False otherwise
    """
    for pattern in DANGEROUS_PATTERNS:
        if pattern.search(command):
            return True
    return False


def sanitize_input(input_str: str) -> str:
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        input_str: The input string to sanitize
        
    Returns:
        Sanitized input string
    """
    # Remove null bytes
    input_str = input_str.replace('\x00', '')
    
    # Limit command length
    if len(input_str) > 1000:
        input_str = input_str[:1000] + '... (truncated)'
    
    return input_str


def validate_connection_params(params: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate SSH connection parameters.
    
    Args:
        params: Dictionary containing connection parameters
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ['host', 'port', 'username']
    
    for field in required_fields:
        if field not in params or not params[field]:
            return False, f"Missing required field: {field}"
    
    # Validate host
    host = params['host'].strip()
    if not host:
        return False, "Host cannot be empty"
    
    # Basic hostname/IP validation
    if not re.match(r'^[a-zA-Z0-9.-]+$', host) and not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', host):
        return False, "Invalid host format"
    
    # Validate port
    try:
        port = int(params['port'])
        if port < 1 or port > 65535:
            return False, "Port must be between 1 and 65535"
    except ValueError:
        return False, "Port must be a number"
    
    # Validate username
    username = params['username'].strip()
    if not username:
        return False, "Username cannot be empty"
    
    if not re.match(r'^[a-zA-Z0-9._-]+$', username):
        return False, "Invalid username format"
    
    return True, None


def log_ssh_command(session_id: str, user_id: Optional[str], command: str, 
                   output_length: int = 0, success: bool = True):
    """
    Log SSH command execution for audit trail.
    
    Args:
        session_id: WebSocket session ID
        user_id: User ID from Flask session (if available)
        command: The command that was executed
        output_length: Length of command output
        success: Whether the command was successful
    """
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'session_id': session_id,
        'user_id': user_id,
        'command': command[:100],  # Truncate long commands
        'output_length': output_length,
        'success': success,
        'ip_address': None  # Will be set by caller
    }
    
    # Log to file or database
    logger.info(f"SSH Command: {log_entry}")
    
    # In production, you might want to store this in a database
    # or send to a centralized logging system


def format_error_message(error_type: str, details: str) -> str:
    """
    Format user-friendly error messages.
    
    Args:
        error_type: Type of error (auth, connection, command, etc.)
        details: Technical details of the error
        
    Returns:
        User-friendly error message
    """
    messages = {
        'auth': "Authentication failed. Please check your username and password.",
        'connection': "Connection failed. Please verify the host and port.",
        'timeout': "Connection timed out. The server may be unreachable.",
        'forbidden': "Access denied. You don't have permission to connect.",
        'unknown': "An unexpected error occurred. Please try again."
    }
    
    base_message = messages.get(error_type, messages['unknown'])
    
    # Add specific details for certain error types (in production, be careful not to expose sensitive info)
    if error_type in ['auth', 'connection']:
        # Don't expose too many details for security reasons
        return base_message
    
    return f"{base_message} ({details})"


def get_system_info_command() -> str:
    """
    Get a command to retrieve basic system information.
    
    Returns:
        Command string for system info
    """
    return "uname -a && echo '---' && df -h && echo '---' && free -m && echo '---' && uptime"


def get_common_commands() -> List[Dict[str, str]]:
    """
    Get a list of common SSH commands with descriptions.
    
    Returns:
        List of dictionaries with 'command' and 'description' keys
    """
    return [
        {'command': 'ls -la', 'description': 'List files in detail'},
        {'command': 'pwd', 'description': 'Print working directory'},
        {'command': 'whoami', 'description': 'Show current user'},
        {'command': 'df -h', 'description': 'Show disk usage'},
        {'command': 'free -m', 'description': 'Show memory usage'},
        {'command': 'top -n 1', 'description': 'Show running processes'},
        {'command': 'ps aux', 'description': 'Show all processes'},
        {'command': 'netstat -tlnp', 'description': 'Show listening ports'},
        {'command': 'systemctl status', 'description': 'Show service status'},
        {'command': 'tail -n 50 /var/log/syslog', 'description': 'Show recent logs'},
        {'command': 'cat /proc/version', 'description': 'Show kernel version'},
        {'command': 'date', 'description': 'Show current date and time'},
    ]