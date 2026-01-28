# SSH Terminal Technical Specification

## 1. WebSocket Events Specification

### Client to Server Events
- `connect_ssh`: Initialize SSH connection with credentials
  ```json
  {
    "host": "server.example.com",
    "port": 22,
    "username": "user",
    "password": "password", // or use key_auth
    "key_auth": false
  }
  ```

- `terminal_input`: Send command/input to SSH
  ```json
  {
    "data": "ls -la\n"
  }
  ```

- `disconnect_ssh`: Close SSH connection
  ```json
  {}
  ```

- `resize_terminal`: Resize terminal dimensions
  ```json
  {
    "cols": 80,
    "rows": 24
  }
  ```

### Server to Client Events
- `connection_status`: Update on connection state
  ```json
  {
    "status": "connecting|connected|disconnected|error",
    "message": "Connection established"
  }
  ```

- `terminal_output`: Stream terminal output
  ```json
  {
    "data": "user@server:~$ "
  }
  ```

- `error`: Error messages
  ```json
  {
    "type": "auth|connection|command",
    "message": "Authentication failed"
  }
  ```

## 2. SSH Manager Module Design

### Class: SSHConnectionManager
```python
class SSHConnectionManager:
    def __init__(self):
        self.active_sessions = {}  # session_id -> SSHConnection
        
    def create_connection(self, session_id, host, port, username, password=None, key=None):
        """Create new SSH connection"""
        
    def get_connection(self, session_id):
        """Retrieve existing connection"""
        
    def execute_command(self, session_id, command):
        """Execute command and return output"""
        
    def resize_terminal(self, session_id, cols, rows):
        """Resize terminal dimensions"""
        
    def close_connection(self, session_id):
        """Close SSH connection"""
```

### Class: SSHConnection
```python
class SSHConnection:
    def __init__(self, host, port, username, password=None, key=None):
        self.client = paramiko.SSHClient()
        self.channel = None
        self.host = host
        self.port = port
        self.username = username
        
    def connect(self):
        """Establish SSH connection"""
        
    def open_shell(self):
        """Open interactive shell channel"""
        
    def send_input(self, data):
        """Send input to shell"""
        
    def resize(self, cols, rows):
        """Resize terminal"""
        
    def disconnect(self):
        """Close connection"""
```

## 3. Frontend Implementation Details

### HTML Structure (to be added to configuracion.html)
```html
<div id="ssh-terminal-tab" class="tab-content">
    <div class="ssh-connection-form">
        <div class="form-row">
            <div class="form-group">
                <label for="ssh-host">Host:</label>
                <input type="text" id="ssh-host" placeholder="server.example.com">
            </div>
            <div class="form-group">
                <label for="ssh-port">Port:</label>
                <input type="number" id="ssh-port" value="22">
            </div>
            <div class="form-group">
                <label for="ssh-username">Username:</label>
                <input type="text" id="ssh-username" placeholder="username">
            </div>
            <div class="form-group">
                <label for="ssh-password">Password:</label>
                <input type="password" id="ssh-password" placeholder="password">
            </div>
        </div>
        <div class="form-actions">
            <button id="ssh-connect" class="btn btn-primary">Connect</button>
            <button id="ssh-disconnect" class="btn btn-secondary" disabled>Disconnect</button>
            <span id="ssh-status" class="status-indicator">Disconnected</span>
        </div>
    </div>
    
    <div class="terminal-container">
        <div id="terminal"></div>
    </div>
    
    <div class="command-shortcuts">
        <button class="btn btn-sm btn-secondary" data-command="ls -la">List Files</button>
        <button class="btn btn-sm btn-secondary" data-command="pwd">Current Dir</button>
        <button class="btn btn-sm btn-secondary" data-command="whoami">Who Am I</button>
        <button class="btn btn-sm btn-secondary" data-command="df -h">Disk Usage</button>
        <button class="btn btn-sm btn-secondary" data-command="free -m">Memory</button>
        <button class="btn btn-sm btn-secondary" data-command="top">Top Processes</button>
    </div>
</div>
```

### JavaScript Implementation (ssh_terminal.js)
```javascript
class SSHTerminal {
    constructor() {
        this.term = null;
        this.socket = null;
        this.connected = false;
        this.initTerminal();
        this.initSocket();
        this.bindEvents();
    }
    
    initTerminal() {
        this.term = new Terminal({
            cols: 80,
            rows: 24,
            fontSize: 14,
            fontFamily: 'Consolas, monospace',
            theme: {
                background: '#1e1e1e',
                foreground: '#ffffff'
            }
        });
        
        const fitAddon = new FitAddon.FitAddon();
        this.term.loadAddon(fitAddon);
        this.term.open(document.getElementById('terminal'));
        fitAddon.fit();
        
        this.term.onData(data => {
            if (this.connected) {
                this.socket.emit('terminal_input', { data });
            }
        });
    }
    
    initSocket() {
        this.socket = io('/ssh-terminal');
        
        this.socket.on('connection_status', data => {
            this.updateStatus(data.status, data.message);
        });
        
        this.socket.on('terminal_output', data => {
            this.term.write(data.data);
        });
        
        this.socket.on('error', data => {
            this.showError(data.type, data.message);
        });
    }
    
    connect(host, port, username, password) {
        this.socket.emit('connect_ssh', {
            host, port, username, password
        });
    }
    
    disconnect() {
        this.socket.emit('disconnect_ssh');
    }
    
    updateStatus(status, message) {
        const statusEl = document.getElementById('ssh-status');
        statusEl.textContent = message;
        statusEl.className = `status-indicator status-${status}`;
        this.connected = (status === 'connected');
        
        document.getElementById('ssh-connect').disabled = this.connected;
        document.getElementById('ssh-disconnect').disabled = !this.connected;
    }
    
    showError(type, message) {
        // Display error in terminal or modal
        this.term.write(`\r\n\x1b[31mError: ${message}\x1b[0m\r\n`);
    }
}
```

## 4. CSS Styling

```css
/* SSH Terminal Tab Styles */
.tab-content {
    display: none;
}

.tab-content.active {
    display: block;
}

.ssh-connection-form {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
}

.terminal-container {
    background: #1e1e1e;
    border-radius: 8px;
    padding: 1rem;
    height: 400px;
    overflow: hidden;
}

#terminal {
    height: 100%;
}

.status-indicator {
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-weight: 600;
    font-size: 0.875rem;
}

.status-connected {
    background: #d4edda;
    color: #155724;
}

.status-disconnected {
    background: #f8d7da;
    color: #721c24;
}

.status-connecting {
    background: #fff3cd;
    color: #856404;
}

.command-shortcuts {
    margin-top: 1rem;
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.btn-sm {
    padding: 0.25rem 0.5rem;
    font-size: 0.875rem;
}
```

## 5. Security Considerations

### Session Management
- Use Flask session ID to track SSH connections
- Automatically disconnect after 30 minutes of inactivity
- Limit to one SSH connection per authenticated user

### Command Logging
```python
def log_command(session_id, command, output, user_id):
    log_entry = {
        'timestamp': datetime.utcnow(),
        'user_id': user_id,
        'session_id': session_id,
        'command': command,
        'output_length': len(output)
    }
    # Store in database or log file
```

### Input Validation
- Sanitize terminal input to prevent injection attacks
- Limit command length
- Optional: Implement command blacklist for dangerous operations

## 6. Error Handling

### Connection Errors
- Host unreachable
- Authentication failure
- Timeout
- Connection lost

### Command Errors
- Permission denied
- Command not found
- Shell errors

### Recovery Mechanisms
- Auto-reconnect on connection loss
- Clear error messages
- Graceful degradation

## 7. Performance Considerations

### Output Buffering
- Buffer terminal output to reduce WebSocket messages
- Implement flow control for large outputs

### Resource Limits
- Limit terminal size (cols/rows)
- Set timeout for command execution
- Monitor memory usage per session

## 8. Testing Strategy

### Unit Tests
- SSH connection manager
- WebSocket event handlers
- Command execution

### Integration Tests
- Full SSH workflow
- Error scenarios
- Session management

### Manual Tests
- Different SSH servers
- Various authentication methods
- Command execution
- Terminal resizing
- Connection stability