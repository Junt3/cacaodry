"""
Módulo de configuración del Sistema de Secado de Cacao
"""

from models import ConfiguracionSistema
from flask import current_app

def obtener_configuracion(clave, default=None):
    """
    Obtiene un valor de configuración desde la base de datos
    
    Args:
        clave (str): Clave de la configuración
        default: Valor por defecto si no se encuentra
        
    Returns:
        str: Valor de la configuración o el valor por defecto
    """
    try:
        with current_app.app_context():
            config = ConfiguracionSistema.query.filter_by(clave=clave).first()
            return config.valor if config else default
    except:
        return default

def guardar_configuracion(clave, valor, descripcion=None):
    """
    Guarda un valor de configuración en la base de datos
    
    Args:
        clave (str): Clave de la configuración
        valor (str): Valor a guardar
        descripcion (str): Descripción opcional
    """
    try:
        with current_app.app_context():
            config = ConfiguracionSistema.query.filter_by(clave=clave).first()
            if config:
                config.valor = valor
                if descripcion:
                    config.descripcion = descripcion
            else:
                nueva_config = ConfiguracionSistema(
                    clave=clave,
                    valor=valor,
                    descripcion=descripcion or ''
                )
                current_app.extensions['sqlalchemy'].db.session.add(nueva_config)
            
            current_app.extensions['sqlalchemy'].db.session.commit()
            return True
    except:
        return False