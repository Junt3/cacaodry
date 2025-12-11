"""
Migración 002: Agregar índices para mejorar rendimiento
"""

def up(db):
    """Aplica la migración"""
    from sqlalchemy import text
    db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_calculos_fecha ON calculos_secado(fecha_hora)'))
    db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_errores_fecha ON registros_errores(fecha_hora)'))
    db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_calculos_modo ON calculos_secado(modo)'))
    db.session.commit()
    print("✓ Índices agregados")

def down(db):
    """Revierte la migración"""
    from sqlalchemy import text
    db.session.execute(text('DROP INDEX IF EXISTS idx_calculos_fecha'))
    db.session.execute(text('DROP INDEX IF EXISTS idx_errores_fecha'))
    db.session.execute(text('DROP INDEX IF EXISTS idx_calculos_modo'))
    db.session.commit()
    print("✓ Índices eliminados")