/**
 * SSH Terminal Interface for Cacao Drying System
 * 
 * This module provides a web-based SSH terminal using xterm.js and Socket.IO
 * for real-time communication with the backend SSH service.
 */

class SSHTerminal {
    constructor() {
        this.term = null;
        this.socket = null;
        this.connected = false;
        this.fitAddon = null;
        this.outputBuffer = '';
        this.commandHistory = [];
        this.historyIndex = -1;
        this.currentLine = '';
        
        this.init();
    }
    
    init() {
        this.initTerminal();
        this.initSocket();
        this.bindEvents();
        this.resizeTerminal();
    }
    
    initTerminal() {
        // Initialize xterm.js terminal
        this.term = new Terminal({
            cols: 80,
            rows: 24,
            fontSize: 14,
            fontFamily: 'Consolas, "Courier New", monospace',
            theme: {
                background: '#1e1e1e',
                foreground: '#ffffff',
                cursor: '#ffffff',
                selection: '#264f78',
                black: '#000000',
                red: '#cd3131',
                green: '#0dbc79',
                yellow: '#e5e510',
                blue: '#2472c8',
                magenta: '#bc3fbc',
                cyan: '#11a8cd',
                white: '#e5e5e5',
                brightBlack: '#666666',
                brightRed: '#f14c4c',
                brightGreen: '#23d18b',
                brightYellow: '#f5f543',
                brightBlue: '#3b8eea',
                brightMagenta: '#d670d6',
                brightCyan: '#29b8db',
                brightWhite: '#e5e5e5'
            },
            cursorBlink: true,
            cursorStyle: 'block',
            scrollback: 1000,
            tabStopWidth: 4
        });
        
        // Load and apply fit addon
        if (typeof FitAddon !== 'undefined') {
            this.fitAddon = new FitAddon.FitAddon();
            this.term.loadAddon(this.fitAddon);
        }
        
        // Open terminal in the container
        const terminalContainer = document.getElementById('terminal');
        if (terminalContainer) {
            this.term.open(terminalContainer);
            if (this.fitAddon) {
                this.fitAddon.fit();
            }
        }
        
        // Handle terminal data (user input)
        this.term.onData(data => {
            this.handleTerminalInput(data);
        });
        
        // Handle terminal resize
        this.term.onResize(size => {
            this.handleTerminalResize(size.cols, size.rows);
        });
        
        // Handle keyboard events for command history
        this.term.onKey(e => {
            this.handleKeyEvents(e);
        });
    }
    
    initSocket() {
        // Initialize Socket.IO connection
        this.socket = io('/ssh-terminal', {
            transports: ['websocket', 'polling'],
            upgrade: true,
            rememberUpgrade: true
        });
        
        // Socket event handlers
        this.socket.on('connect', () => {
            this.updateStatus('connected', 'WebSocket connected. Ready to establish SSH connection.');
        });
        
        this.socket.on('disconnect', () => {
            this.updateStatus('disconnected', 'WebSocket disconnected');
            this.connected = false;
        });
        
        this.socket.on('connection_status', (data) => {
            this.updateStatus(data.status, data.message);
            this.connected = (data.status === 'connected');
        });
        
        this.socket.on('terminal_output', (data) => {
            this.term.write(data.data);
        });
        
        this.socket.on('error', (data) => {
            this.handleError(data.type, data.message);
        });
        
        this.socket.on('connect_error', (error) => {
            this.handleError('connection', 'Failed to connect to server: ' + error.message);
        });
    }
    
    bindEvents() {
        // Connect button
        const connectBtn = document.getElementById('ssh-connect');
        if (connectBtn) {
            connectBtn.addEventListener('click', () => this.connect());
        }
        
        // Disconnect button
        const disconnectBtn = document.getElementById('ssh-disconnect');
        if (disconnectBtn) {
            disconnectBtn.addEventListener('click', () => this.disconnect());
        }
        
        // Command shortcut buttons
        const shortcutBtns = document.querySelectorAll('.command-shortcut');
        shortcutBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const command = e.target.getAttribute('data-command');
                if (command && this.connected) {
                    this.term.write(command + '\n');
                }
            });
        });
        
        // Form submission on Enter key
        const formInputs = document.querySelectorAll('#ssh-host, #ssh-port, #ssh-username, #ssh-password');
        formInputs.forEach(input => {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.connect();
                }
            });
        });
        
        // Window resize
        window.addEventListener('resize', () => {
            this.resizeTerminal();
        });
    }
    
    connect() {
        console.log('SSH connect() called');
        
        // Get connection parameters
        const host = document.getElementById('ssh-host').value.trim();
        const port = document.getElementById('ssh-port').value || '22';
        const username = document.getElementById('ssh-username').value.trim();
        const password = document.getElementById('ssh-password').value;
        
        console.log('Connection params:', { host, port, username: username + '***' });
        
        // Validate inputs
        if (!host || !username) {
            console.log('Validation failed: missing host or username');
            this.showError('validation', 'Please enter host and username');
            return;
        }
        
        // Clear terminal
        this.term.clear();
        this.term.focus();
        
        console.log('Emitting connect_ssh event...');
        // Emit connection request
        this.socket.emit('connect_ssh', {
            host: host,
            port: parseInt(port),
            username: username,
            password: password,
            key_auth: false  // TODO: Implement key-based authentication
        });
    }
    
    disconnect() {
        this.socket.emit('disconnect_ssh');
    }
    
    handleTerminalInput(data) {
        if (!this.connected) {
            return;
        }
        
        // Buffer the input for command history
        if (data === '\r' || data === '\n') {
            if (this.currentLine.trim()) {
                this.commandHistory.push(this.currentLine);
                this.historyIndex = this.commandHistory.length;
            }
            this.currentLine = '';
        } else if (data === '\u007f') { // Backspace
            if (this.currentLine.length > 0) {
                this.currentLine = this.currentLine.slice(0, -1);
            }
        } else if (data >= ' ') {
            this.currentLine += data;
        }
        
        // Send input to server
        this.socket.emit('terminal_input', { data: data });
    }
    
    handleKeyEvents(e) {
        // Handle arrow keys for command history
        if (e.key === 'ArrowUp') {
            e.domEvent.preventDefault();
            if (this.historyIndex > 0) {
                this.historyIndex--;
                // Clear current line and replace with history
                // Note: This is a simplified implementation
                // A full implementation would need to track cursor position
            }
        } else if (e.key === 'ArrowDown') {
            e.domEvent.preventDefault();
            if (this.historyIndex < this.commandHistory.length - 1) {
                this.historyIndex++;
                // Clear current line and replace with history
            }
        }
    }
    
    handleTerminalResize(cols, rows) {
        if (this.socket && this.connected) {
            this.socket.emit('resize_terminal', { cols: cols, rows: rows });
        }
    }
    
    resizeTerminal() {
        if (this.fitAddon) {
            this.fitAddon.fit();
        }
    }
    
    updateStatus(status, message) {
        const statusEl = document.getElementById('ssh-status');
        if (statusEl) {
            statusEl.textContent = message;
            statusEl.className = `connection-status status-${status}`;
        }
        
        // Update button states
        const connectBtn = document.getElementById('ssh-connect');
        const disconnectBtn = document.getElementById('ssh-disconnect');
        
        if (connectBtn && disconnectBtn) {
            connectBtn.disabled = this.connected;
            disconnectBtn.disabled = !this.connected;
        }
    }
    
    handleError(type, message) {
        // Show error in terminal
        this.term.write(`\r\n\x1b[31mError: ${message}\x1b[0m\r\n`);
        
        // Update status
        this.updateStatus('error', message);
        
        // Show error in modal for critical errors
        if (type === 'connection' || type === 'auth') {
            if (typeof showAlerta === 'function') {
                showAlerta('SSH Error', message, 'error');
            } else {
                alert(message);
            }
        }
    }
    
    showError(type, message) {
        // Show error message
        if (typeof showAlerta === 'function') {
            showAlerta('Validation Error', message, 'error');
        } else {
            alert(message);
        }
    }
    
    focus() {
        if (this.term) {
            this.term.focus();
        }
    }
}

// Initialize SSH terminal when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Check if SSH terminal tab exists
    const sshTab = document.querySelector('[data-tab="ssh"]');
    if (sshTab) {
        sshTab.addEventListener('click', function() {
            // Initialize terminal on first tab click
            if (!window.sshTerminal) {
                window.sshTerminal = new SSHTerminal();
            } else {
                // Focus existing terminal
                window.sshTerminal.focus();
            }
        });
        
        // Also initialize if we're starting on the SSH tab
        if (sshTab.classList.contains('active')) {
            window.sshTerminal = new SSHTerminal();
        }
    }
    
    // Also check if we need to initialize immediately
    // This handles the case where the page loads with SSH tab active
    const activeTab = document.querySelector('.tab-button.active');
    if (activeTab && activeTab.getAttribute('data-tab') === 'ssh') {
        if (!window.sshTerminal) {
            window.sshTerminal = new SSHTerminal();
        }
    }
});

// Export for global access
window.SSHTerminal = SSHTerminal;