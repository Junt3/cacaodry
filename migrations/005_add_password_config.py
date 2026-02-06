"""
Migración 005: Agregar configuración de contraseña para protección
"""

def up(db):
    """Aplica la migración"""
    from models import ConfiguracionSistema
    
    # Verificar si ya existe la configuración de contraseña
    password_config = ConfiguracionSistema.query.filter_by(clave='password_configuracion').first()
    
    if not password_config:
        # Insertar configuración por defecto para contraseña (vacía, se establecerá después)
        config = ConfiguracionSistema(
            clave='password_configuracion',
            valor='',
            descripcion='Contraseña para proteger el acceso a la configuración del sistema'
        )
        db.session.add(config)
        print("✓ Configuración 'password_configuracion' añadida")
    else:
        print("✓ Configuración 'password_configuracion' ya existe")

def down(db):
    """Revierte la migración"""
    from models import ConfiguracionSistema
    
    # Eliminar configuración de contraseña
    password_config = ConfiguracionSistema.query.filter_by(clave='password_configuracion').first()
    if password_config:
        db.session.delete(password_config)
        print("✓ Configuración 'password_configuracion' eliminada")
    else:
        print("✓ Configuración 'password_configuracion' no existía")