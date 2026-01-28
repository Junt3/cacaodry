#!/usr/bin/env python3
"""
Gestor unificado de base de datos para el Sistema de Secado de Cacao
Centraliza todas las operaciones: inicialización, migraciones, seed y pruebas
"""

import os
import sys
import json
import importlib.util
import argparse
import getpass
from datetime import datetime
from flask import Flask
from models import db, CalculoSecado, ConfiguracionSistema, RegistroError, init_db
from database_config import auto_configure_app, configure_postgresql, configure_sqlite
from auth_utils import establecer_password_configuracion, existe_password_configuracion


class DatabaseManager:
    """Gestor principal de operaciones de base de datos"""
    
    def __init__(self, db_type='postgresql'):
        self.db_type = db_type
        self.app = self._create_app()
        self.migration_manager = MigrationManager(self.app)
        self.seed_manager = SeedManager(self.app)
    
    def _create_app(self):
        """Crea una aplicación Flask configurada"""
        app = Flask(__name__)
        app.secret_key = 'cacao_secado_2023'
        
        if self.db_type == 'postgresql':
            configure_postgresql(app)
        else:
            configure_sqlite(app)
        
        init_db(app)
        return app
    
    def init_database(self, tables_only=False):
        """Inicializa la base de datos"""
        print(f"[INIT] Inicializando base de datos {self.db_type.upper()} del Sistema de Secado de Cacao...")
        
        with self.app.app_context():
            try:
                # Crear todas las tablas
                db.create_all()
                print("[OK] Tablas creadas exitosamente")
                
                if not tables_only:
                    # Inicializar configuración por defecto
                    self.seed_manager.load_default_config()
                    print("[OK] Configuración por defecto cargada")
                
                # Confirmar cambios
                db.session.commit()
                print("[OK] Cambios guardados exitosamente")
                
                # Mostrar resumen
                self._show_database_summary()
                
                print(f"\n[SUCCESS] Base de datos {self.db_type.upper()} inicializada correctamente!")
                return True
                
            except Exception as e:
                db.session.rollback()
                print(f"[ERROR] Error al inicializar la base de datos: {str(e)}")
                return False
    
    def reset_database(self, keep_config=False):
        """Resetea la base de datos"""
        print(f"[WARNING] ADVERTENCIA: Esto eliminará todos los datos de la base de datos {self.db_type.upper()}")
        
        if keep_config:
            print("Se mantendrá la configuración del sistema")
        
        confirmation = input("¿Está seguro que desea continuar? (s/N): ")
        if confirmation.lower() != 's':
            print("[CANCEL] Operación cancelada")
            return False
        
        with self.app.app_context():
            try:
                # Guardar configuración si se solicita
                config_data = []
                if keep_config:
                    config_data = ConfiguracionSistema.query.all()
                
                # Eliminar todas las tablas
                db.drop_all()
                print("[OK] Tablas eliminadas")
                
                # Recrear tablas
                db.create_all()
                print("[OK] Tablas recreadas")
                
                # Restaurar configuración si se solicita
                if keep_config:
                    for config in config_data:
                        new_config = ConfiguracionSistema(
                            clave=config.clave,
                            valor=config.valor,
                            descripcion=config.descripcion
                        )
                        db.session.add(new_config)
                    print("[OK] Configuración restaurada")
                
                db.session.commit()
                print("[SUCCESS] Base de datos reseteada correctamente")
                return True
                
            except Exception as e:
                db.session.rollback()
                print(f"[ERROR] Error al resetear la base de datos: {str(e)}")
                return False
    
    def show_info(self, detailed=False):
        """Muestra información de la base de datos"""
        print(f"[INFO] Información de la base de datos {self.db_type.upper()}:")
        print("-" * 50)
        
        with self.app.app_context():
            try:
                print(f"Tipo de base de datos: {self.db_type.upper()}")
                print(f"URL de conexión: {self.app.config['SQLALCHEMY_DATABASE_URI']}")
                
                if detailed:
                    print(f"Cálculos registrados: {CalculoSecado.query.count()}")
                    print(f"Errores registrados: {RegistroError.query.count()}")
                    print(f"Configuraciones: {ConfiguracionSistema.query.count()}")
                    
                    # Mostrar migraciones aplicadas
                    self.migration_manager.show_migration_status()
                
                return True
                
            except Exception as e:
                print(f"[ERROR] Error al obtener información: {str(e)}")
                return False
    
    def _show_database_summary(self):
        """Muestra un resumen de la base de datos"""
        print("\n[INFO] Resumen de la base de datos:")
        print(f"   - Cálculos registrados: {CalculoSecado.query.count()}")
        print(f"   - Errores registrados: {RegistroError.query.count()}")
        print(f"   - Configuraciones: {ConfiguracionSistema.query.count()}")


class MigrationManager:
    """Gestor de migraciones para la base de datos"""
    
    def __init__(self, app):
        self.app = app
        self.migrations_file = 'migrations.json'
        self.migrations = self._load_migrations()
    
    def _load_migrations(self):
        """Carga el historial de migraciones"""
        if os.path.exists(self.migrations_file):
            with open(self.migrations_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_migrations(self):
        """Guarda el historial de migraciones"""
        with open(self.migrations_file, 'w', encoding='utf-8') as f:
            json.dump(self.migrations, f, indent=2, ensure_ascii=False)
    
    def _add_migration(self, name, description):
        """Agrega una nueva migración al historial"""
        migration_id = f"migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.migrations[migration_id] = {
            'name': name,
            'description': description,
            'applied_at': datetime.now().isoformat(),
            'version': '1.0.0'
        }
        self._save_migrations()
        return migration_id
    
    def _is_applied(self, migration_id):
        """Verifica si una migración ya fue aplicada"""
        return migration_id in self.migrations
    
    def get_available_migrations(self):
        """Obtiene todas las migraciones disponibles desde el directorio de migraciones"""
        migrations_dir = 'migrations'
        if not os.path.exists(migrations_dir):
            return []
        
        migration_files = [f for f in os.listdir(migrations_dir) if f.endswith('.py') and not f.startswith('__')]
        migration_files.sort()
        
        migrations = []
        for file in migration_files:
            migration_id = file.replace('.py', '')
            try:
                module_path = os.path.join(migrations_dir, file)
                spec = importlib.util.spec_from_file_location(migration_id, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                description = module.__doc__.strip() if module.__doc__ else migration_id
                migrations.append((migration_id, description))
            except Exception as e:
                print(f"[WARNING] Error cargando migración {migration_id}: {str(e)}")
                migrations.append((migration_id, f"Error: {str(e)}"))
        
        return migrations
    
    def get_pending_migrations(self):
        """Obtiene las migraciones pendientes"""
        available_migrations = self.get_available_migrations()
        
        pending = []
        for migration_id, description in available_migrations:
            full_id = f"migration_{migration_id}"
            if not self._is_applied(full_id):
                pending.append((migration_id, description))
        
        return pending
    
    def apply_migration(self, migration_id, description):
        """Aplica una migración específica"""
        with self.app.app_context():
            try:
                migrations_dir = 'migrations'
                module_path = os.path.join(migrations_dir, f"{migration_id}.py")
                
                if not os.path.exists(module_path):
                    print(f"[ERROR] Archivo de migración no encontrado: {module_path}")
                    return False
                
                spec = importlib.util.spec_from_file_location(migration_id, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if hasattr(module, 'up'):
                    module.up(db)
                else:
                    print(f"[ERROR] La migración {migration_id} no tiene función 'up'")
                    return False
                
                full_id = f"migration_{migration_id}"
                self._add_migration(full_id, description)
                
                return True
                
            except Exception as e:
                print(f"[ERROR] Error aplicando migración {migration_id}: {str(e)}")
                return False
    
    def migrate(self):
        """Aplica todas las migraciones pendientes"""
        pending = self.get_pending_migrations()
        
        if not pending:
            print("[SUCCESS] No hay migraciones pendientes")
            return True
        
        print(f"[PROCESS] Aplicando {len(pending)} migración(es) pendiente(s)...")
        
        for migration_id, description in pending:
            print(f"\n[PROCESS] Aplicando: {migration_id} - {description}")
            if not self.apply_migration(migration_id, description):
                print(f"[ERROR] Falló la migración {migration_id}")
                return False
        
        print("\n[SUCCESS] Todas las migraciones aplicadas correctamente")
        return True
    
    def rollback(self, migration_id):
        """Revierte una migración específica"""
        print(f"[WARNING] Revertir migración {migration_id}")
        print("[WARNING] ADVERTENCIA: Esta funcionalidad es básica y puede no ser completa")
        
        with self.app.app_context():
            try:
                migrations_dir = 'migrations'
                module_path = os.path.join(migrations_dir, f"{migration_id}.py")
                
                if not os.path.exists(module_path):
                    print(f"[ERROR] Archivo de migración no encontrado: {module_path}")
                    return False
                
                spec = importlib.util.spec_from_file_location(migration_id, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if hasattr(module, 'down'):
                    module.down(db)
                else:
                    print(f"[WARNING] La migración {migration_id} no tiene función 'down'")
                
                full_id = f"migration_{migration_id}"
                if full_id in self.migrations:
                    del self.migrations[full_id]
                    self._save_migrations()
                    print(f"[OK] Migración {migration_id} eliminada del registro")
                else:
                    print(f"[ERROR] Migración {migration_id} no encontrada en el registro")
                    return False
                
                return True
                
            except Exception as e:
                print(f"[ERROR] Error revirtiendo migración: {str(e)}")
                return False
    
    def show_migration_status(self):
        """Muestra el estado de las migraciones"""
        print("[INFO] Estado de las migraciones:")
        print("-" * 50)
        
        pending = self.get_pending_migrations()
        
        if not self.migrations:
            print("[ERROR] No hay registro de migraciones aplicadas")
        else:
            print("[SUCCESS] Migraciones aplicadas:")
            for migration_id, info in self.migrations.items():
                print(f"   - {migration_id}: {info['name']} ({info['applied_at']})")
        
        if pending:
            print("\n[PENDING] Migraciones pendientes:")
            for migration_id, description in pending:
                print(f"   - {migration_id}: {description}")
        else:
            print("\n[SUCCESS] No hay migraciones pendientes")


class SeedManager:
    """Gestor de datos iniciales (seed)"""
    
    def __init__(self, app):
        self.app = app
    
    def load_default_config(self):
        """Carga la configuración por defecto del sistema"""
        configuraciones_default = [
            {
                'clave': 'version_sistema',
                'valor': '1.0.0',
                'descripcion': 'Versión actual del sistema de secado de cacao'
            },
            {
                'clave': 'temp_min_industrial',
                'valor': '40',
                'descripcion': 'Temperatura mínima permitida para secado industrial'
            },
            {
                'clave': 'temp_max_industrial',
                'valor': '100',
                'descripcion': 'Temperatura máxima permitida para secado industrial'
            },
            {
                'clave': 'temp_min_solar',
                'valor': '15',
                'descripcion': 'Temperatura mínima permitida para secado solar'
            },
            {
                'clave': 'temp_max_solar',
                'valor': '45',
                'descripcion': 'Temperatura máxima permitida para secado solar'
            },
            {
                'clave': 'humedad_min',
                'valor': '0',
                'descripcion': 'Humedad mínima permitida'
            },
            {
                'clave': 'humedad_max',
                'valor': '100',
                'descripcion': 'Humedad máxima permitida'
            },
            {
                'clave': 'humedad_advertencia_baja',
                'valor': '6',
                'descripcion': 'Umbral para advertencia de humedad baja (puede quebrar el grano)'
            },
            {
                'clave': 'humedad_advertencia_alta',
                'valor': '8',
                'descripcion': 'Umbral para advertencia de humedad alta (puede generar moho)'
            },
            {
                'clave': 'items_por_pagina',
                'valor': '10',
                'descripcion': 'Número de items a mostrar por página en el historial'
            },
            {
                'clave': 'precio_cacao',
                'valor': '6100',
                'descripcion': 'Precio del cacao en dólares por tonelada métrica'
            }
        ]
        
        with self.app.app_context():
            for config_data in configuraciones_default:
                existing = ConfiguracionSistema.query.filter_by(clave=config_data['clave']).first()
                if not existing:
                    config = ConfiguracionSistema(
                        clave=config_data['clave'],
                        valor=config_data['valor'],
                        descripcion=config_data['descripcion']
                    )
                    db.session.add(config)
                    print(f"[OK] Configuración agregada: {config_data['clave']}")
                else:
                    print(f"- Configuración ya existe: {config_data['clave']}")
    
    def setup_password(self, force=False):
        """Establece la contraseña de configuración"""
        with self.app.app_context():
            if existe_password_configuracion() and not force:
                print("[WARNING] Ya existe una contraseña configurada.")
                print("Si desea cambiarla, use la opción 'Cambiar Contraseña' en la configuración.")
                return False
            
            print("Por favor, ingrese una contraseña segura para proteger la configuración:")
            print("- Mínimo 8 caracteres")
            print("- Debe incluir letras y números")
            print("- No use información personal fácil de adivinar")
            
            while True:
                password = getpass.getpass("Nueva contraseña: ")
                
                if len(password) < 8:
                    print("[ERROR] La contraseña debe tener al menos 8 caracteres")
                    continue
                
                if not any(c.isdigit() for c in password):
                    print("[ERROR] La contraseña debe contener al menos un número")
                    continue
                
                if not any(c.isalpha() for c in password):
                    print("[ERROR] La contraseña debe contener al menos una letra")
                    continue
                
                password_confirm = getpass.getpass("Confirme la contraseña: ")
                
                if password != password_confirm:
                    print("[ERROR] Las contraseñas no coinciden")
                    continue
                
                break
            
            if establecer_password_configuracion(password):
                print("[SUCCESS] Contraseña establecida correctamente")
                return True
            else:
                print("[ERROR] Error al establecer la contraseña")
                return False


class TestManager:
    """Gestor de pruebas y diagnóstico de base de datos"""
    
    def __init__(self, app):
        self.app = app
    
    def test_connection(self):
        """Prueba la conexión a la base de datos"""
        print("[TEST] Probando conexión a la base de datos...")
        
        with self.app.app_context():
            try:
                db.engine.execute("SELECT 1")
                print("[SUCCESS] Conexión exitosa")
                return True
            except Exception as e:
                print(f"[ERROR] Error de conexión: {str(e)}")
                return False
    
    def test_operations(self):
        """Prueba operaciones básicas de CRUD"""
        print("\n[TEST] Probando operaciones básicas...")
        
        with self.app.app_context():
            try:
                # Probar inserción
                test_config = ConfiguracionSistema(
                    clave='test_connection',
                    valor='db_manager_test',
                    descripcion='Prueba de conexión db_manager'
                )
                db.session.add(test_config)
                db.session.commit()
                print("[SUCCESS] Inserción de datos exitosa")
                
                # Probar consulta
                retrieved = ConfiguracionSistema.query.filter_by(clave='test_connection').first()
                if retrieved and retrieved.valor == 'db_manager_test':
                    print("✅ Consulta de datos exitosa")
                else:
                    print("[ERROR] Error en consulta de datos")
                    return False
                
                # Probar actualización
                retrieved.valor = 'db_manager_test_updated'
                db.session.commit()
                updated = ConfiguracionSistema.query.filter_by(clave='test_connection').first()
                if updated and updated.valor == 'db_manager_test_updated':
                    print("[SUCCESS] Actualización de datos exitosa")
                else:
                    print("[ERROR] Error en actualización de datos")
                    return False
                
                # Probar eliminación
                db.session.delete(updated)
                db.session.commit()
                deleted = ConfiguracionSistema.query.filter_by(clave='test_connection').first()
                if deleted is None:
                    print("[SUCCESS] Eliminación de datos exitosa")
                else:
                    print("[ERROR] Error en eliminación de datos")
                    return False
                
                return True
            except Exception as e:
                print(f"[ERROR] Error en operaciones CRUD: {str(e)}")
                return False
    
    def run_all_tests(self):
        """Ejecuta todas las pruebas"""
        print("[TEST] Iniciando pruebas de base de datos...")
        print("=" * 60)
        
        tests = [
            ("Conexión a la base de datos", self.test_connection),
            ("Operaciones CRUD básicas", self.test_operations)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n[TEST] Ejecutando prueba: {test_name}")
            if test_func():
                passed += 1
                print(f"[SUCCESS] Prueba '{test_name}' superada")
            else:
                print(f"[ERROR] Prueba '{test_name}' fallida")
        
        print("\n" + "=" * 60)
        print(f"[RESULT] Resultados: {passed}/{total} pruebas superadas")
        
        return passed == total


def main():
    """Función principal del gestor de base de datos"""
    parser = argparse.ArgumentParser(
        description='Gestor unificado de base de datos para el Sistema de Secado de Cacao',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Comandos disponibles:
  init        Inicializa la base de datos
  migrate     Gestiona migraciones
  seed        Gestiona datos iniciales
  test        Ejecuta pruebas de diagnóstico
  reset       Resetea la base de datos
  info        Muestra información de la base de datos

Ejemplos:
  python db_manager.py init
  python db_manager.py migrate status
  python db_manager.py seed --password
  python db_manager.py test connection
        """
    )
    
    parser.add_argument('command', choices=['init', 'migrate', 'seed', 'test', 'reset', 'info'],
                       help='Comando a ejecutar')
    
    parser.add_argument('subcommand', nargs='?', 
                       help='Subcomando (para migrate, test, etc)')
    
    parser.add_argument('--db-type', choices=['postgresql', 'sqlite'], default='postgresql',
                       help='Tipo de base de datos (default: postgresql)')
    
    parser.add_argument('--tables-only', action='store_true',
                       help='Solo crear tablas (para init)')
    
    parser.add_argument('--config-only', action='store_true',
                       help='Solo cargar configuración (para seed)')
    
    parser.add_argument('--password', action='store_true',
                       help='Establecer contraseña (para seed)')
    
    parser.add_argument('--keep-config', action='store_true',
                       help='Mantener configuración al resetear')
    
    parser.add_argument('--detailed', action='store_true',
                       help='Mostrar información detallada (para info)')
    
    args = parser.parse_args()
    
    # Crear gestor de base de datos
    db_manager = DatabaseManager(args.db_type)
    
    # Ejecutar comando
    if args.command == 'init':
        success = db_manager.init_database(tables_only=args.tables_only)
    
    elif args.command == 'migrate':
        if args.subcommand == 'status':
            db_manager.migration_manager.show_migration_status()
            success = True
        elif args.subcommand == 'list':
            migrations = db_manager.migration_manager.get_available_migrations()
            print("[INFO] Migraciones disponibles:")
            for migration_id, description in migrations:
                print(f"   - {migration_id}: {description}")
            success = True
        elif args.subcommand == 'rollback' and len(sys.argv) > 3:
            migration_id = sys.argv[3]
            success = db_manager.migration_manager.rollback(migration_id)
        elif args.subcommand == 'rollback':
            print("[ERROR] Se requiere el ID de la migración para revertir")
            print("Uso: python db_manager.py migrate rollback <migration_id>")
            success = False
        else:
            success = db_manager.migration_manager.migrate()
    
    elif args.command == 'seed':
        if args.config_only:
            with db_manager.app.app_context():
                db_manager.seed_manager.load_default_config()
                db.session.commit()
            success = True
        elif args.password:
            success = db_manager.seed_manager.setup_password(force=True)
        else:
            with db_manager.app.app_context():
                db_manager.seed_manager.load_default_config()
                db.session.commit()
            success = True
    
    elif args.command == 'test':
        test_manager = TestManager(db_manager.app)
        if args.subcommand == 'connection':
            success = test_manager.test_connection()
        elif args.subcommand == 'operations':
            success = test_manager.test_operations()
        else:
            success = test_manager.run_all_tests()
    
    elif args.command == 'reset':
        success = db_manager.reset_database(keep_config=args.keep_config)
    
    elif args.command == 'info':
        success = db_manager.show_info(detailed=args.detailed)
    
    else:
        print(f"[ERROR] Comando desconocido: {args.command}")
        success = False
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()