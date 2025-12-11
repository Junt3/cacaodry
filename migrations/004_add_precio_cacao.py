"""
Migración 004: Añadir configuración del precio del cacao
"""

def up(db):
    """Aplica la migración"""
    from models import ConfiguracionSistema
    
    # Añadir configuración del precio del cacao
    precio_cacao = ConfiguracionSistema.query.filter_by(clave='precio_cacao').first()
    if not precio_cacao:
        nueva_config = ConfiguracionSistema(
            clave='precio_cacao',
            valor='6100',
            descripcion='Precio del cacao en dólares por tonelada métrica'
        )
        db.session.add(nueva_config)
        db.session.commit()
        print("✓ Configuración 'precio_cacao' añadida con valor por defecto de $6100/tonelada")
    else:
        print(f"✓ Configuración 'precio_cacao' ya existe con valor: ${precio_cacao.valor}/tonelada")

def down(db):
    """Revierte la migración"""
    from models import ConfiguracionSistema
    
    # Eliminar configuración del precio del cacao
    precio_cacao = ConfiguracionSistema.query.filter_by(clave='precio_cacao').first()
    if precio_cacao:
        db.session.delete(precio_cacao)
        db.session.commit()
        print("✓ Configuración 'precio_cacao' eliminada")
    else:
        print("✓ Configuración 'precio_cacao' no existe")