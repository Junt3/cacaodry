# SSH Terminal Feature Documentation

## Overview

The SSH Terminal feature provides a web-based SSH client integrated into the Cacao Drying System's configuration page. It allows authenticated administrators to access the server hosting this service directly through the web interface using a full terminal emulator.

## Features

- **Full Terminal Emulator**: Complete xterm.js-based terminal with ANSI support
- **Real-time Communication**: WebSocket-based bidirectional communication
- **Session Management**: Isolated SSH sessions per user
- **Command Shortcuts**: Quick access buttons for common commands
- **Security Features**: Authentication validation, command logging, and session timeout
- **Responsive Design**: Works on desktop and mobile devices

## Architecture

### Backend Components

1. **SSH Connection Manager** (`ssh_terminal/ssh_manager.py`)
   - Manages SSH connections using paramiko
   - Handles authentication (password-based)
   - Manages session isolation and cleanup

2. **WebSocket Events** (`ssh_terminal/socketio_events.py`)
   - Handles real-time communication with frontend
   - Manages connection lifecycle
   - Implements security checks

3. **Utilities** (`ssh_terminal/utils.py`)
   - Input validation and sanitization
   - Dangerous command detection
   - Common command definitions

### Frontend Components

1. **Terminal Interface** (`static/js/ssh_terminal.js`)
   - xterm.js terminal emulator
   - WebSocket client implementation
   - Command history and shortcuts

2. **UI Integration** (`templates/configuracion.html`)
   - Tab-based interface
   - Connection form
   - Terminal container

## Installation and Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

The following new dependencies are required:
- Flask-SocketIO==5.3.6
- python-socketio==5.8.0
- paramiko==3.3.1
- eventlet==0.33.3

### 2. Run the Application

```bash
python app.py
```

The application will now run with SocketIO support at `http://localhost:5000`

### 3. Access the SSH Terminal

1. Navigate to the configuration page
2. Click on the "SSH Terminal" tab
3. Enter connection details:
   - Host: Server hostname or IP
   - Port: SSH port (default: 22)
   - Username: SSH username
   - Password: SSH password
4. Click "Connect" to establish the connection

## Usage Guide

### Connecting to a Server

1. Ensure you have valid SSH credentials
2. Enter the connection details in the form
3. Click "Connect" or press Enter in any field
4. The terminal will display the SSH login prompt
5. Enter your password when prompted

### Using the Terminal

- The terminal supports all standard SSH operations
- Use arrow keys for command history
- Terminal automatically resizes with the window
- Use Ctrl+C to interrupt commands

### Command Shortcuts

The following quick-access buttons are available:
- **List Files**: `ls -la`
- **Current Dir**: `pwd`
- **Who Am I**: `whoami`
- **Disk Usage**: `df -h`
- **Memory**: `free -m`
- **Top Processes**: `top -n 1`
- **All Processes**: `ps aux`
- **Listening Ports**: `netstat -tlnp`
- **Service Status**: `systemctl status`
- **Recent Logs**: `tail -n 50 /var/log/syslog`
- **System Info**: `uname -a`
- **Date & Time**: `date`

## Security Considerations

### Authentication
- Only authenticated users can access the SSH terminal
- SSH credentials are transmitted over encrypted WebSocket connections
- Sessions are isolated per user

### Session Management
- Automatic timeout after 30 minutes of inactivity
- Connections are cleaned up when users disconnect
- One SSH connection per user session

### Command Logging
- All commands are logged for audit purposes
- Dangerous commands are detected and blocked
- Input is sanitized to prevent injection attacks

### Network Security
- WebSocket connections use the same security as the main application
- Consider using HTTPS/WSS in production
- SSH connections use the system's SSH configuration

## Troubleshooting

### Connection Issues

1. **"Connection failed" Error**
   - Verify the host and port are correct
   - Check if the server is reachable
   - Ensure SSH service is running on the target server

2. **"Authentication failed" Error**
   - Verify username and password are correct
   - Check if password authentication is enabled
   - Ensure the account is not locked

3. **"Timeout" Error**
   - Check network connectivity
   - Verify firewall settings
   - Try connecting with a standalone SSH client

### Terminal Issues

1. **Terminal Not Responding**
   - Refresh the page and reconnect
   - Check browser console for errors
   - Ensure JavaScript is enabled

2. **Display Issues**
   - Try resizing the browser window
   - Check if xterm.js loaded correctly
   - Verify CSS is not blocked

### Performance Issues

1. **Slow Response**
   - Check server load
   - Verify network latency
   - Consider reducing terminal scrollback

## Development Notes

### Adding New Commands

To add new command shortcuts:

1. Update `get_common_commands()` in `ssh_terminal/utils.py`
2. Add buttons in `templates/configuracion.html`
3. The command will be automatically available

### Extending Authentication

To add key-based authentication:

1. Modify `SSHConnection.connect()` in `ssh_terminal/ssh_manager.py`
2. Update the connection form in the template
3. Add key file upload handling

### Custom Terminal Themes

To customize the terminal appearance:

1. Modify the theme options in `static/js/ssh_terminal.js`
2. Update CSS variables in the template
3. Test with different color schemes

## API Reference

### WebSocket Events

#### Client to Server

- `connect_ssh`: Establish SSH connection
- `terminal_input`: Send command/input
- `resize_terminal`: Resize terminal dimensions
- `disconnect_ssh`: Close SSH connection
- `get_status`: Get connection status

#### Server to Client

- `connection_status`: Update connection state
- `terminal_output`: Stream terminal output
- `error`: Error messages

### Python Classes

#### SSHConnectionManager

```python
create_connection(session_id, host, port, username, password)
send_input(session_id, data)
read_output(session_id)
resize_terminal(session_id, cols, rows)
close_connection(session_id)
get_connection_status(session_id)
```

#### SSHConnection

```python
connect()
send_input(data)
read_output()
resize_terminal(cols, rows)
disconnect()
is_active()
```

## Testing

Run the test script to verify functionality:

```bash
python test_ssh_terminal.py
```

This will test:
- SSH connection management
- Input validation
- Dangerous command detection
- SocketIO event handlers

## Production Deployment

### Environment Variables

Consider setting these environment variables:

```bash
FLASK_ENV=production
FLASK_SECRET_KEY=your-secret-key
SSH_TIMEOUT=1800  # 30 minutes
```

### Reverse Proxy Configuration

For Nginx with WebSocket support:

```nginx
location /socket.io/ {
    proxy_pass http://localhost:5000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
}
```

### Monitoring

Monitor:
- SSH connection counts
- WebSocket connections
- Command execution logs
- Resource usage

## License

This SSH terminal feature is part of the Cacao Drying System and follows the same license terms.