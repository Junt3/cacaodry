#!/usr/bin/env python3
"""
Script para ejecutar migraciones de la base de datos
"""

import sys
import os
from flask import Flask
from models import db
from database_config import configure_postgresql

def run_migration(migration_number):
    """Ejecuta una migración específica"""
    
    # Crear aplicación Flask mínima
    app = Flask(__name__)
    app.secret_key = 'cacao_secado_2023'
    
    # Configurar base de datos
    configure_postgresql(app)
    db.init_app(app)
    
    with app.app_context():
        try:
            # Importar la migración
            migration_module = __import__(f'migrations.{migration_number}', fromlist=['up', 'down'])
            
            print(f"🔄 Ejecutando migración {migration_number}...")
            migration_module.up(db)
            
            # Confirmar cambios
            db.session.commit()
            print(f"✅ Migración {migration_number} completada exitosamente")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error en migración {migration_number}: {str(e)}")
            sys.exit(1)

def main():
    """Función principal"""
    
    print("🗄️  Sistema de Migraciones - Base de Datos")
    print("=" * 50)
    
    if len(sys.argv) != 2:
        print("Uso: python run_migrations.py <numero_migracion>")
        print("Ejemplo: python run_migrations.py 005_add_password_config")
        sys.exit(1)
    
    migration_number = sys.argv[1]
    
    # Verificar que el archivo de migración existe
    migration_file = f"migrations/{migration_number}.py"
    if not os.path.exists(migration_file):
        print(f"❌ No se encuentra el archivo de migración: {migration_file}")
        sys.exit(1)
    
    # Ejecutar migración
    run_migration(migration_number)

if __name__ == '__main__':
    main()