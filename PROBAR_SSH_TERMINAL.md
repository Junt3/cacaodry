# Cómo Probar el Terminal SSH

## Pasos para depurar el problema del botón de conectar:

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Ejecutar la aplicación
```bash
python app.py
```

### 3. Abrir la aplicación en el navegador
- Navegar a: http://localhost:5000
- Hacer clic en "Configuración" en el menú de navegación
- Iniciar sesión con la contraseña de configuración

### 4. Probar el terminal SSH
- Hacer clic en la pestaña "SSH Terminal"
- Llenar los campos:
  - Host: localhost (o cualquier servidor SSH)
  - Port: 22
  - Username: tu nombre de usuario
  - Password: tu contraseña
- Hacer clic en el botón "Connect"

### 5. Verificar la consola del navegador
- Abrir las herramientas de desarrollador (F12)
- Ir a la pestaña "Console"
- Buscar mensajes de error o advertencia

### 6. Verificar los logs del servidor
- En la terminal donde se ejecutó `python app.py`
- Buscar mensajes como:
  - "Received connect_ssh request"
  - "Attempting to connect to"
  - Cualquier mensaje de error

## Si el botón no funciona:

### Opción 1: Probar WebSocket básico
```bash
python test_websocket.py
```
Luego abrir http://localhost:5001 en el navegador para probar si WebSocket funciona.

### Opción 2: Verificar JavaScript
- En la consola del navegador, ejecutar:
  ```javascript
  console.log('SSH Terminal object:', window.sshTerminal);
  console.log('Socket object:', window.sshTerminal ? window.sshTerminal.socket : null);
  ```

### Opción 3: Verificar elementos del DOM
- En la consola del navegador, ejecutar:
  ```javascript
  console.log('Connect button:', document.getElementById('ssh-connect'));
  console.log('Form inputs:', {
    host: document.getElementById('ssh-host')?.value,
    port: document.getElementById('ssh-port')?.value,
    username: document.getElementById('ssh-username')?.value,
    password: document.getElementById('ssh-password')?.value
  });
  ```

## Problemas comunes y soluciones:

1. **El terminal no se inicializa**:
   - Asegurarse de hacer clic primero en la pestaña SSH
   - Verificar que no haya errores de JavaScript en la consola

2. **WebSocket no se conecta**:
   - Verificar que el servidor esté corriendo con SocketIO
   - Revisar el firewall del navegador y del sistema

3. **Error de autenticación**:
   - Asegurarse de haber iniciado sesión en la página de configuración
   - Verificar que la sesión de Flask esté activa

4. **La conexión SSH falla**:
   - Verificar que el servidor SSH sea alcanzable
   - Probar con un cliente SSH normal: `ssh usuario@host`

## Para revertir a la versión completa:
Si la versión simplificada funciona, se puede volver a la versión completa modificando `app.py`:

```python
# Cambiar esta línea:
from ssh_terminal import create_simple_ssh_namespace
create_simple_ssh_namespace(socketio)

# Por esta:
from ssh_terminal import create_ssh_namespace
create_ssh_namespace(socketio)