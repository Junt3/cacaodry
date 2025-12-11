#!/usr/bin/env python3
"""
Módulo de configuración de base de datos para el Sistema de Secado de Cacao
Permite cambiar fácilmente entre SQLite y PostgreSQL
"""

import os

# Configuración de bases de datos disponibles
DATABASE_CONFIGS = {
    'sqlite': {
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///cacaodry.db',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'description': 'SQLite - Ideal para desarrollo y pruebas rápidas'
    },
    'postgresql': {
        'SQLALCHEMY_DATABASE_URI': 'postgresql://postgres:juniher2004@localhost/cacaodry',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SQLALCHEMY_ENGINE_OPTIONS': {
            'pool_size': 10,
            'pool_recycle': 120,
            'pool_pre_ping': True
        },
        'description': 'PostgreSQL - Recomendado para producción y entornos avanzados'
    }
}

def get_database_config(db_type='postgresql'):
    """
    Obtiene la configuración de base de datos según el tipo especificado
    
    Args:
        db_type (str): Tipo de base de datos ('sqlite' o 'postgresql')
        
    Returns:
        dict: Configuración de la base de datos
    """
    if db_type not in DATABASE_CONFIGS:
        raise ValueError(f"Tipo de base de datos no soportado: {db_type}")
    
    return DATABASE_CONFIGS[db_type]

def configure_app(app, db_type='postgresql'):
    """
    Configura una aplicación Flask con la base de datos especificada
    
    Args:
        app: Aplicación Flask
        db_type (str): Tipo de base de datos ('sqlite' o 'postgresql')
    """
    config = get_database_config(db_type)
    
    for key, value in config.items():
        if key != 'description':
            app.config[key] = value
    
    print(f"🔧 Aplicación configurada para usar: {config['description']}")

def get_current_database_type():
    """
    Obtiene el tipo de base de datos actual desde variable de entorno
    
    Returns:
        str: Tipo de base de datos ('sqlite' o 'postgresql')
    """
    return os.environ.get('DB_TYPE', 'postgresql')

def auto_configure_app(app):
    """
    Configura automáticamente la aplicación según la variable de entorno DB_TYPE
    
    Args:
        app: Aplicación Flask
    """
    db_type = get_current_database_type()
    configure_app(app, db_type)
    return db_type

# Funciones de conveniencia para configurar rápidamente
def configure_sqlite(app):
    """Configura la aplicación para usar SQLite"""
    configure_app(app, 'sqlite')

def configure_postgresql(app):
    """Configura la aplicación para usar PostgreSQL"""
    configure_app(app, 'postgresql')

# Información sobre las bases de datos
def print_database_info():
    """Imprime información sobre las configuraciones de base de datos disponibles"""
    print("📊 Configuraciones de base de datos disponibles:")
    print("-" * 50)
    for db_type, config in DATABASE_CONFIGS.items():
        print(f"• {db_type.upper()}: {config['description']}")

if __name__ == '__main__':
    print_database_info()