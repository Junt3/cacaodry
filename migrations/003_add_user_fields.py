"""
Migración 003: Campos adicionales para tracking de usuario
"""

def up(db):
    """Aplica la migración"""
    # Ejemplo de cómo agregar nuevos campos
    # Nota: En SQLite, ALTER TABLE tiene limitaciones
    # Para producción, considerar usar una base de datos más robusta
    print("✓ Campos de usuario agregados (ejemplo)")

def down(db):
    """Revierte la migración"""
    print("✓ Campos de usuario eliminados (ejemplo)")