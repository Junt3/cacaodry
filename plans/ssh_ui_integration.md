# SSH Terminal UI Integration Design

## Configuration Page Layout with SSH Terminal Tab

### Current Configuration Page Structure
```
┌─────────────────────────────────────────────────────────────┐
│ Configuración del Sistema                    [Buttons]      │
├─────────────────────────────────────────────────────────────┤
│ Tab Navigation:                                            │
│ [Parámetros] [Humedad] [Visualización] [Económica] [SSH]   │
├─────────────────────────────────────────────────────────────┤
│ Tab Content Area                                           │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                                                         │ │
│ │   Current Tab Content                                   │ │
│ │                                                         │ │
│ │                                                         │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                     [Save] [Reset] [Change Password]       │
└─────────────────────────────────────────────────────────────┘
```

### New SSH Terminal Tab Layout
```
┌─────────────────────────────────────────────────────────────┐
│ Configuración del Sistema                    [Buttons]      │
├─────────────────────────────────────────────────────────────┤
│ Tab Navigation:                                            │
│ [Parámetros] [Humedad] [Visualización] [Económica] [SSH]   │
├─────────────────────────────────────────────────────────────┤
│ SSH Terminal Tab Content                                    │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Connection Form                                        │ │
│ │ Host: [________] Port: [__] User: [________]           │ │
│ │ Password: [________]                                   │ │
│ │ [Connect] [Disconnect] Status: Disconnected           │ │
│ └─────────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                                                         │ │
│ │                  TERMINAL WINDOW                        │ │
│ │                                                         │ │
│ │ user@server:~$ _                                        │ │
│ │                                                         │ │
│ │                                                         │ │
│ └─────────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Command Shortcuts:                                     │ │
│ │ [List Files] [Current Dir] [Who Am I] [Disk Usage]     │ │
│ │ [Memory] [Top Processes]                               │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                     [Save] [Reset] [Change Password]       │
└─────────────────────────────────────────────────────────────┘
```

## Tab Implementation Details

### HTML Structure Modifications
The existing configuracion.html will be modified to include:

1. **Tab Navigation Bar** - Added above the existing form
2. **Tab Content Containers** - Each existing section wrapped in a tab
3. **New SSH Terminal Tab** - Complete terminal interface

### JavaScript Tab Switching Logic
```javascript
// Tab switching functionality
document.addEventListener('DOMContentLoaded', function() {
    const tabs = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs and contents
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(tc => tc.classList.remove('active'));
            
            // Add active class to clicked tab and corresponding content
            tab.classList.add('active');
            const tabId = tab.getAttribute('data-tab');
            document.getElementById(`${tabId}-tab`).classList.add('active');
        });
    });
    
    // Initialize SSH terminal when SSH tab is first clicked
    document.querySelector('[data-tab="ssh"]').addEventListener('click', () => {
        if (!window.sshTerminal) {
            window.sshTerminal = new SSHTerminal();
        }
    });
});
```

### CSS for Tab System
```css
/* Tab Navigation */
.tab-navigation {
    display: flex;
    border-bottom: 2px solid #8B4513;
    margin-bottom: 1rem;
    gap: 0.5rem;
}

.tab-button {
    padding: 0.75rem 1.5rem;
    background: transparent;
    border: none;
    border-bottom: 3px solid transparent;
    cursor: pointer;
    font-weight: 600;
    color: #6c757d;
    transition: all 0.3s;
}

.tab-button:hover {
    color: #8B4513;
    background: rgba(139, 69, 19, 0.05);
}

.tab-button.active {
    color: #8B4513;
    border-bottom-color: #8B4513;
    background: rgba(139, 69, 19, 0.1);
}

/* Tab Content */
.tab-content {
    display: none;
    animation: fadeIn 0.3s;
}

.tab-content.active {
    display: block;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

/* SSH Terminal Specific Styles */
.ssh-terminal-container {
    background: white;
    border-radius: 10px;
    padding: 1.5rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.terminal-wrapper {
    background: #1e1e1e;
    border-radius: 8px;
    padding: 1rem;
    margin: 1rem 0;
    height: 400px;
    overflow: hidden;
}

#terminal {
    height: 100%;
    width: 100%;
}

.connection-status {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.875rem;
    font-weight: 600;
    margin-left: 1rem;
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
```

## Integration Points

### 1. Navigation Integration
- SSH tab added to existing navigation
- Maintains consistent styling with other tabs
- Only visible to authenticated users

### 2. Authentication Integration
- Uses existing Flask session authentication
- Respects the same `@requiere_autenticacion_config` decorator
- Maintains security level of configuration page

### 3. Form Integration
- SSH terminal operates independently of the configuration form
- Save/Reset buttons remain for other tabs
- Form submission only affects configuration tabs, not SSH

### 4. Styling Integration
- Uses existing color scheme (#8B4513 primary color)
- Maintains consistent button styles
- Follows responsive design patterns

## Responsive Design Considerations

### Desktop (>768px)
- Full terminal width with connection form above
- Command shortcuts in a horizontal row
- Terminal height: 400px

### Tablet (768px-480px)
- Stacked connection form fields
- Reduced terminal height: 300px
- Command shortcuts wrap to multiple rows

### Mobile (<480px)
- Full-width connection form
- Terminal height: 250px
- Command shortcuts in vertical list
- Simplified connection controls

## User Experience Flow

1. **Access Configuration Page**
   - User navigates to configuration page
   - Must be authenticated (existing requirement)

2. **Switch to SSH Tab**
   - Click SSH tab in navigation
   - Terminal interface initializes

3. **Configure Connection**
   - Enter server details
   - Click Connect button
   - Status indicator shows connection progress

4. **Use Terminal**
   - Terminal becomes active when connected
   - Can type commands directly
   - Use shortcut buttons for common commands

5. **Manage Session**
   - Disconnect button to close connection
   - Can reconnect with same or different credentials
   - Session automatically times out after inactivity

## Error Handling UI

### Connection Errors
- Status indicator turns red
- Error message displayed above terminal
- Terminal shows error message in red text

### Authentication Errors
- Highlight password field
- Show specific authentication error
- Allow retry without losing other form data

### Session Errors
- Notify when session times out
- Offer to reconnect
- Preserve connection details for easy reconnection