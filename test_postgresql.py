#!/usr/bin/env python3
"""
Script para probar la conexión y funcionamiento básico con PostgreSQL
"""

import sys
import os
from flask import Flask
from models import db, CalculoSecado, ConfiguracionSistema, RegistroError, init_db
from database_config import configure_postgresql

def test_connection():
    """Prueba la conexión a PostgreSQL"""
    print("🔍 Probando conexión a PostgreSQL...")
    
    app = Flask(__name__)
    configure_postgresql(app)
    
    try:
        init_db(app)
        with app.app_context():
            # Intentar conectar
            db.engine.execute("SELECT 1")
            print("✅ Conexión a PostgreSQL exitosa")
            return True
    except Exception as e:
        print(f"❌ Error de conexión a PostgreSQL: {str(e)}")
        return False

def test_table_creation():
    """Prueba la creación de tablas"""
    print("\n🔍 Probando creación de tablas...")
    
    app = Flask(__name__)
    configure_postgresql(app)
    
    try:
        init_db(app)
        with app.app_context():
            # Crear tablas
            db.create_all()
            print("✅ Tablas creadas exitosamente")
            
            # Verificar que las tablas existan
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            expected_tables = ['calculos_secado', 'configuraciones_sistema', 'registros_errores']
            
            for table in expected_tables:
                if table in tables:
                    print(f"✅ Tabla '{table}' existe")
                else:
                    print(f"❌ Tabla '{table}' no encontrada")
                    return False
            
            return True
    except Exception as e:
        print(f"❌ Error al crear tablas: {str(e)}")
        return False

def test_basic_operations():
    """Prueba operaciones básicas de CRUD"""
    print("\n🔍 Probando operaciones básicas...")
    
    app = Flask(__name__)
    configure_postgresql(app)
    
    try:
        init_db(app)
        with app.app_context():
            # Probar inserción
            test_config = ConfiguracionSistema(
                clave='test_connection',
                valor='postgresql_test',
                descripcion='Prueba de conexión PostgreSQL'
            )
            db.session.add(test_config)
            db.session.commit()
            print("✅ Inserción de datos exitosa")
            
            # Probar consulta
            retrieved = ConfiguracionSistema.query.filter_by(clave='test_connection').first()
            if retrieved and retrieved.valor == 'postgresql_test':
                print("✅ Consulta de datos exitosa")
            else:
                print("❌ Error en consulta de datos")
                return False
            
            # Probar actualización
            retrieved.valor = 'postgresql_test_updated'
            db.session.commit()
            updated = ConfiguracionSistema.query.filter_by(clave='test_connection').first()
            if updated and updated.valor == 'postgresql_test_updated':
                print("✅ Actualización de datos exitosa")
            else:
                print("❌ Error en actualización de datos")
                return False
            
            # Probar eliminación
            db.session.delete(updated)
            db.session.commit()
            deleted = ConfiguracionSistema.query.filter_by(clave='test_connection').first()
            if deleted is None:
                print("✅ Eliminación de datos exitosa")
            else:
                print("❌ Error en eliminación de datos")
                return False
            
            return True
    except Exception as e:
        print(f"❌ Error en operaciones CRUD: {str(e)}")
        return False

def test_calculo_model():
    """Prueba el modelo CalculoSecado"""
    print("\n🔍 Probando modelo CalculoSecado...")
    
    app = Flask(__name__)
    configure_postgresql(app)
    
    try:
        init_db(app)
        with app.app_context():
            # Crear un cálculo de prueba
            test_calculo = CalculoSecado(
                modo='INDUSTRIAL',
                temperatura_aire=60.0,
                humedad_inicial=55.0,
                humedad_final=7.5,
                peso_quintales=10.0,
                capacidad_maxima=50.0,
                temperatura_efectiva=60.0,
                constante_k=0.5,
                constante_n=0.7,
                tiempo_base_horas=24.0,
                factor_penalizacion=1.0,
                tiempo_total_horas=24.0,
                peso_inicial_kg=460.0,
                peso_final_kg=400.0,
                agua_evaporada_litros=60.0,
                ip_address='127.0.0.1',
                user_agent='Test Agent'
            )
            db.session.add(test_calculo)
            db.session.commit()
            print("✅ Creación de CalculoSecado exitosa")
            
            # Probar consulta y conversión a diccionario
            retrieved = CalculoSecado.query.first()
            if retrieved:
                dict_data = retrieved.to_dict()
                if 'modo' in dict_data and dict_data['modo'] == 'INDUSTRIAL':
                    print("✅ Consulta y serialización de CalculoSecado exitosa")
                else:
                    print("❌ Error en serialización de CalculoSecado")
                    return False
            else:
                print("❌ Error en consulta de CalculoSecado")
                return False
            
            # Limpiar datos de prueba
            db.session.delete(retrieved)
            db.session.commit()
            
            return True
    except Exception as e:
        print(f"❌ Error en modelo CalculoSecado: {str(e)}")
        return False

def main():
    """Función principal de pruebas"""
    print("🧪 Iniciando pruebas de PostgreSQL para Sistema de Secado de Cacao...")
    print("=" * 60)
    
    tests = [
        ("Conexión a PostgreSQL", test_connection),
        ("Creación de tablas", test_table_creation),
        ("Operaciones CRUD básicas", test_basic_operations),
        ("Modelo CalculoSecado", test_calculo_model)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Ejecutando prueba: {test_name}")
        if test_func():
            passed += 1
            print(f"✅ Prueba '{test_name}' superada")
        else:
            print(f"❌ Prueba '{test_name}' fallida")
    
    print("\n" + "=" * 60)
    print(f"📊 Resultados: {passed}/{total} pruebas superadas")
    
    if passed == total:
        print("🎉 Todas las pruebas superadas. PostgreSQL está listo para usar!")
        return True
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa la configuración de PostgreSQL.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)