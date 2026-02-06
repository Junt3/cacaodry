"""
Módulo para manejar conexiones SSH desde la consola web.
Utiliza paramiko para establecer conexiones SSH seguras.
"""

import paramiko
import socket
import threading
import time
from typing import Optional, Callable
import json


class SSHSession:
    """Clase para manejar una sesión SSH individual"""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.client: Optional[paramiko.SSHClient] = None
        self.channel: Optional[paramiko.Channel] = None
        self.connected = False
        self.hostname: Optional[str] = None
        self.username: Optional[str] = None
        self.port = 22
        self.last_activity = time.time()
        self.output_buffer = ""
        self.lock = threading.Lock()

    def connect(self, hostname: str, username: str, password: str, port: int = 22,
                timeout: int = 10) -> tuple[bool, str]:
        """
        Establece conexión SSH con el servidor remoto.

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            self.client.connect(
                hostname=hostname,
                port=port,
                username=username,
                password=password,
                timeout=timeout,
                allow_agent=False,
                look_for_keys=False
            )

            # Crear canal interactivo
            self.channel = self.client.invoke_shell(
                term='xterm-256color',
                width=120,
                height=30
            )

            self.hostname = hostname
            self.username = username
            self.port = port
            self.connected = True
            self.last_activity = time.time()

            # Leer banner inicial
            time.sleep(0.5)
            initial_output = self._read_output()
            self.output_buffer = initial_output

            return True, "Conexión establecida correctamente"

        except paramiko.AuthenticationException:
            return False, "Error de autenticación: Usuario o contraseña incorrectos"
        except paramiko.SSHException as e:
            return False, f"Error SSH: {str(e)}"
        except socket.timeout:
            return False, "Error: Tiempo de conexión agotado"
        except socket.error as e:
            return False, f"Error de conexión: {str(e)}"
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"

    def execute_command(self, command: str) -> tuple[bool, str]:
        """
        Ejecuta un comando en la sesión SSH.

        Returns:
            tuple: (success: bool, output: str)
        """
        if not self.connected or not self.channel:
            return False, "No hay conexión activa"

        try:
            with self.lock:
                # Limpiar buffer anterior
                self._read_output()

                # Enviar comando
                self.channel.send(command + '\n')
                self.last_activity = time.time()

                # Esperar y leer salida
                time.sleep(0.3)
                output = self._read_output()

                return True, output

        except Exception as e:
            return False, f"Error al ejecutar comando: {str(e)}"

    def _read_output(self) -> str:
        """Lee la salida disponible del canal"""
        output = ""
        if self.channel and self.channel.recv_ready():
            try:
                while self.channel.recv_ready():
                    data = self.channel.recv(4096).decode('utf-8', errors='replace')
                    if not data:
                        break
                    output += data
            except Exception:
                pass
        return output

    def get_output(self) -> str:
        """Obtiene la salida acumulada y limpia el buffer"""
        with self.lock:
            new_output = self._read_output()
            if new_output:
                self.output_buffer += new_output
            output = self.output_buffer
            self.output_buffer = ""
            return output

    def disconnect(self):
        """Cierra la conexión SSH"""
        self.connected = False

        if self.channel:
            try:
                self.channel.close()
            except Exception:
                pass
            self.channel = None

        if self.client:
            try:
                self.client.close()
            except Exception:
                pass
            self.client = None

    def is_active(self) -> bool:
        """Verifica si la conexión sigue activa"""
        if not self.connected:
            return False

        if self.channel and self.client:
            try:
                # Verificar transporte
                transport = self.client.get_transport()
                if not transport or not transport.is_active():
                    self.connected = False
                    return False
                return True
            except Exception:
                self.connected = False
                return False

        return False

    def send_special_key(self, key: str) -> bool:
        """Envía teclas especiales (Ctrl+C, Tab, etc.)"""
        if not self.connected or not self.channel:
            return False

        special_keys = {
            'ctrl_c': '\x03',
            'ctrl_d': '\x04',
            'ctrl_z': '\x1a',
            'tab': '\t',
            'escape': '\x1b',
            'up': '\x1b[A',
            'down': '\x1b[B',
            'right': '\x1b[C',
            'left': '\x1b[D',
            'enter': '\r',
            'backspace': '\x7f',
            'ctrl_l': '\x0c',  # Limpiar pantalla
        }

        try:
            if key in special_keys:
                self.channel.send(special_keys[key])
            else:
                self.channel.send(key)
            self.last_activity = time.time()
            return True
        except Exception:
            return False


class SSHSessionManager:
    """Gestor de sesiones SSH para la aplicación Flask"""

    def __init__(self):
        self.sessions: dict[str, SSHSession] = {}
        self.lock = threading.Lock()
        self._start_cleanup_thread()

    def _start_cleanup_thread(self):
        """Inicia hilo para limpiar sesiones inactivas"""
        def cleanup():
            while True:
                time.sleep(60)  # Cada minuto
                self._cleanup_inactive_sessions()

        thread = threading.Thread(target=cleanup, daemon=True)
        thread.start()

    def _cleanup_inactive_sessions(self):
        """Elimina sesiones inactivas o expiradas"""
        with self.lock:
            current_time = time.time()
            expired = []

            for session_id, session in self.sessions.items():
                # Cerrar sesiones inactivas por más de 30 minutos
                if current_time - session.last_activity > 1800:
                    expired.append(session_id)
                elif not session.is_active():
                    expired.append(session_id)

            for session_id in expired:
                session = self.sessions.pop(session_id)
                session.disconnect()

    def create_session(self, session_id: str) -> SSHSession:
        """Crea una nueva sesión SSH"""
        with self.lock:
            # Cerrar sesión existente si hay una
            if session_id in self.sessions:
                old_session = self.sessions.pop(session_id)
                old_session.disconnect()

            session = SSHSession(session_id)
            self.sessions[session_id] = session
            return session

    def get_session(self, session_id: str) -> Optional[SSHSession]:
        """Obtiene una sesión existente"""
        with self.lock:
            session = self.sessions.get(session_id)
            if session and session.is_active():
                return session
            return None

    def remove_session(self, session_id: str):
        """Elimina una sesión"""
        with self.lock:
            if session_id in self.sessions:
                session = self.sessions.pop(session_id)
                session.disconnect()

    def get_session_status(self, session_id: str) -> dict:
        """Obtiene el estado de una sesión"""
        session = self.get_session(session_id)

        if not session:
            return {
                'connected': False,
                'hostname': None,
                'username': None,
                'message': 'No hay sesión activa'
            }

        return {
            'connected': session.is_active(),
            'hostname': session.hostname,
            'username': session.username,
            'message': 'Sesión activa'
        }


# Instancia global del gestor de sesiones
ssh_manager = SSHSessionManager()
