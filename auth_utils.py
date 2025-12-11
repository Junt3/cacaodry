"""
Módulo de utilidades de autenticación para la protección de configuración
"""

from flask import session, flash, redirect, url_for
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from models import ConfiguracionSistema
from datetime import timedelta
import time

def establecer_password_configuracion(password):
    """
    Establece la contraseña para proteger la configuración
    
    Args:
        password (str): Contraseña a establecer
        
    Returns:
        bool: True si se estableció correctamente, False si hubo error
    """
    try:
        password_hash = generate_password_hash(password)
        
        config = ConfiguracionSistema.query.filter_by(clave='password_configuracion').first()
        if config:
            config.valor = password_hash
        else:
            nueva_config = ConfiguracionSistema(
                clave='password_configuracion',
                valor=password_hash,
                descripcion='Contraseña para proteger el acceso a la configuración del sistema'
            )
            db.session.add(nueva_config)
        
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error al establecer contraseña: {str(e)}")
        return False

def verificar_password_configuracion(password):
    """
    Verifica si la contraseña proporcionada es correcta
    
    Args:
        password (str): Contraseña a verificar
        
    Returns:
        bool: True si la contraseña es correcta, False si no
    """
    try:
        config = ConfiguracionSistema.query.filter_by(clave='password_configuracion').first()
        if not config:
            # Si no hay contraseña configurada, no se permite el acceso
            return False
            
        return check_password_hash(config.valor, password)
    except Exception as e:
        print(f"Error al verificar contraseña: {str(e)}")
        return False

def existe_password_configuracion():
    """
    Verifica si ya existe una contraseña configurada
    
    Returns:
        bool: True si existe contraseña, False si no
    """
    try:
        config = ConfiguracionSistema.query.filter_by(clave='password_configuracion').first()
        return config is not None
    except Exception as e:
        print(f"Error al verificar existencia de contraseña: {str(e)}")
        return False

def requiere_autenticacion_config(f):
    """
    Decorador para proteger rutas que requieren autenticación de configuración
    
    Args:
        f: Función a proteger
        
    Returns:
        Función decorada que verifica autenticación
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar si el usuario está autenticado para configuración
        if not session.get('config_authenticated'):
            flash('Debe autenticarse para acceder a la configuración', 'warning')
            return redirect(url_for('login_config'))
        
        # Verificar tiempo de expiración de sesión (2 horas)
        ultimo_acceso = session.get('config_auth_time', 0)
        if time.time() - ultimo_acceso > 7200:  # 2 horas en segundos
            session.pop('config_authenticated', None)
            session.pop('config_auth_time', None)
            flash('Su sesión ha expirado, por favor inicie sesión nuevamente', 'warning')
            return redirect(url_for('login_config'))
        
        # Actualizar tiempo de último acceso
        session['config_auth_time'] = time.time()
        
        return f(*args, **kwargs)
    
    return decorated_function

def crear_sesion_config():
    """
    Crea una sesión de autenticación para configuración
    
    Returns:
        None
    """
    session['config_authenticated'] = True
    session['config_auth_time'] = time.time()

def cerrar_sesion_config():
    """
    Cierra la sesión de autenticación para configuración
    
    Returns:
        None
    """
    session.pop('config_authenticated', None)
    session.pop('config_auth_time', None)
    flash('Sesión cerrada correctamente', 'info')

def validar_fortaleza_password(password):
    """
    Valida la fortaleza de una contraseña
    
    Args:
        password (str): Contraseña a validar
        
    Returns:
        tuple: (bool es_valida, str mensaje_error)
    """
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    
    if not any(c.isdigit() for c in password):
        return False, "La contraseña debe contener al menos un número"
    
    if not any(c.isalpha() for c in password):
        return False, "La contraseña debe contener al menos una letra"
    
    return True, ""

# Importar db aquí para evitar importación circular
from models import db