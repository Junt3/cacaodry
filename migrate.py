#!/usr/bin/env python3
"""
Script de migraciones para el Sistema de Secado de Cacao
Permite gestionar cambios en el esquema de la base de datos
"""

import os
import sys
import json
import importlib.util
from datetime import datetime
from flask import Flask
from models import db, CalculoSecado, ConfiguracionSistema, RegistroError, init_db
from database_config import auto_configure_app

def crear_app():
    """Crea una aplicación Flask para migraciones"""
    app = Flask(__name__)
    
    # Configurar automáticamente la base de datos (PostgreSQL por defecto)
    auto_configure_app(app)
    
    # Inicializar la base de datos con esta aplicación
    init_db(app)
    return app

class MigrationManager:
    """Gestor de migraciones para la base de datos"""
    
    def __init__(self, app):
        self.app = app
        self.migrations_file = 'migrations.json'
        self.migrations = self.load_migrations()
    
    def load_migrations(self):
        """Carga el historial de migraciones"""
        if os.path.exists(self.migrations_file):
            with open(self.migrations_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_migrations(self):
        """Guarda el historial de migraciones"""
        with open(self.migrations_file, 'w', encoding='utf-8') as f:
            json.dump(self.migrations, f, indent=2, ensure_ascii=False)
    
    def add_migration(self, name, description):
        """Agrega una nueva migración al historial"""
        migration_id = f"migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.migrations[migration_id] = {
            'name': name,
            'description': description,
            'applied_at': datetime.now().isoformat(),
            'version': '1.0.0'
        }
        self.save_migrations()
        return migration_id
    
    def is_applied(self, migration_id):
        """Verifica si una migración ya fue aplicada"""
        return migration_id in self.migrations
    
    def get_available_migrations(self):
        """Obtiene todas las migraciones disponibles desde el directorio de migraciones"""
        migrations_dir = 'migrations'
        if not os.path.exists(migrations_dir):
            return []
        
        migration_files = [f for f in os.listdir(migrations_dir) if f.endswith('.py') and not f.startswith('__')]
        migration_files.sort()  # Ordenar por nombre para ejecutar en secuencia
        
        migrations = []
        for file in migration_files:
            migration_id = file.replace('.py', '')
            # Cargar el módulo para obtener la descripción
            try:
                module_path = os.path.join(migrations_dir, file)
                spec = importlib.util.spec_from_file_location(migration_id, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                description = module.__doc__.strip() if module.__doc__ else migration_id
                migrations.append((migration_id, description))
            except Exception as e:
                print(f"⚠️  Error cargando migración {migration_id}: {str(e)}")
                migrations.append((migration_id, f"Error: {str(e)}"))
        
        return migrations
    
    def get_pending_migrations(self):
        """Obtiene las migraciones pendientes"""
        available_migrations = self.get_available_migrations()
        
        pending = []
        for migration_id, description in available_migrations:
            full_id = f"migration_{migration_id}"
            if not self.is_applied(full_id):
                pending.append((migration_id, description))
        
        return pending
    
    def apply_migration(self, migration_id, description):
        """Aplica una migración específica"""
        with self.app.app_context():
            try:
                # Cargar el módulo de migración dinámicamente
                migrations_dir = 'migrations'
                module_path = os.path.join(migrations_dir, f"{migration_id}.py")
                
                if not os.path.exists(module_path):
                    print(f"❌ Archivo de migración no encontrado: {module_path}")
                    return False
                
                spec = importlib.util.spec_from_file_location(migration_id, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Ejecutar la migración
                if hasattr(module, 'up'):
                    module.up(db)
                else:
                    print(f"❌ La migración {migration_id} no tiene función 'up'")
                    return False
                
                # Registrar la migración como aplicada
                full_id = f"migration_{migration_id}"
                self.add_migration(full_id, description)
                
                return True
                
            except Exception as e:
                print(f"❌ Error aplicando migración {migration_id}: {str(e)}")
                return False
    
    def migrate(self):
        """Aplica todas las migraciones pendientes"""
        pending = self.get_pending_migrations()
        
        if not pending:
            print("✅ No hay migraciones pendientes")
            return True
        
        print(f"🔄 Aplicando {len(pending)} migración(es) pendiente(s)...")
        
        for migration_id, description in pending:
            print(f"\n📝 Aplicando: {migration_id} - {description}")
            if not self.apply_migration(migration_id, description):
                print(f"❌ Falló la migración {migration_id}")
                return False
        
        print("\n✅ Todas las migraciones aplicadas correctamente")
        return True
    
    def rollback(self, migration_id):
        """Revierte una migración específica"""
        print(f"⚠️  Revertir migración {migration_id}")
        print("⚠️  ADVERTENCIA: Esta funcionalidad es básica y puede no ser completa")
        print("⚠️  Se recomienda hacer backup de la base de datos antes de continuar")
        
        with self.app.app_context():
            try:
                # Cargar el módulo de migración dinámicamente
                migrations_dir = 'migrations'
                module_path = os.path.join(migrations_dir, f"{migration_id}.py")
                
                if not os.path.exists(module_path):
                    print(f"❌ Archivo de migración no encontrado: {module_path}")
                    return False
                
                spec = importlib.util.spec_from_file_location(migration_id, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Ejecutar el rollback si existe
                if hasattr(module, 'down'):
                    module.down(db)
                else:
                    print(f"⚠️  La migración {migration_id} no tiene función 'down', solo eliminando del registro")
                
                # Eliminar la migración del registro
                full_id = f"migration_{migration_id}"
                if full_id in self.migrations:
                    del self.migrations[full_id]
                    self.save_migrations()
                    print(f"✓ Migración {migration_id} eliminada del registro")
                else:
                    print(f"❌ Migración {migration_id} no encontrada en el registro")
                    return False
                
                return True
                
            except Exception as e:
                print(f"❌ Error revirtiendo migración: {str(e)}")
                return False
    
    def status(self):
        """Muestra el estado de las migraciones"""
        print("📊 Estado de las migraciones:")
        print("-" * 50)
        
        pending = self.get_pending_migrations()
        
        if not self.migrations:
            print("❌ No hay registro de migraciones aplicadas")
        else:
            print("✅ Migraciones aplicadas:")
            for migration_id, info in self.migrations.items():
                print(f"   - {migration_id}: {info['name']} ({info['applied_at']})")
        
        if pending:
            print("\n⏳ Migraciones pendientes:")
            for migration_id, description in pending:
                print(f"   - {migration_id}: {description}")
        else:
            print("\n✅ No hay migraciones pendientes")

def main():
    """Función principal"""
    app = crear_app()
    manager = MigrationManager(app)
    
    if len(sys.argv) < 2:
        print("Uso: python migrate.py [comando]")
        print("Comandos disponibles:")
        print("  migrate    - Aplica todas las migraciones pendientes")
        print("  status     - Muestra el estado de las migraciones")
        print("  rollback    - Revierte una migración específica")
        return
    
    command = sys.argv[1]
    
    if command == 'migrate':
        manager.migrate()
    elif command == 'status':
        manager.status()
    elif command == 'rollback':
        if len(sys.argv) < 3:
            print("Uso: python migrate.py rollback [migration_id]")
            return
        migration_id = sys.argv[2]
        manager.rollback(migration_id)
    else:
        print(f"Comando desconocido: {command}")

if __name__ == '__main__':
    main()