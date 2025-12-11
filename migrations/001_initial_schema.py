"""
Migración 001: Esquema inicial de la base de datos
"""

def up(db):
    """Aplica la migración"""
    # Crear todas las tablas
    db.create_all()
    print("✓ Esquema inicial creado")

def down(db):
    """Revierte la migración"""
    # Esta migración no se puede revertir fácilmente en SQLite
    print("⚠️  Revertir esquema inicial no es recomendable")