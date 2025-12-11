#!/usr/bin/env python3
"""
Script para inicializar la base de datos PostgreSQL del Sistema de Secado de Cacao
"""

import os
import sys
from flask import Flask
from models import db, CalculoSecado, ConfiguracionSistema, RegistroError, init_db
from database_config import configure_postgresql

def crear_app():
    """Crea una aplicación Flask para inicialización con PostgreSQL"""
    app = Flask(__name__)
    
    # Configurar específicamente para PostgreSQL
    configure_postgresql(app)
    
    # Inicializar la base de datos con esta aplicación
    init_db(app)
    return app

def inicializar_configuracion():
    """Inicializa la configuración por defecto del sistema para PostgreSQL"""
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
    
    for config_data in configuraciones_default:
        # Verificar si ya existe
        existing = ConfiguracionSistema.query.filter_by(clave=config_data['clave']).first()
        if not existing:
            config = ConfiguracionSistema(
                clave=config_data['clave'],
                valor=config_data['valor'],
                descripcion=config_data['descripcion']
            )
            db.session.add(config)
            print(f"✓ Configuración agregada: {config_data['clave']}")
        else:
            print(f"- Configuración ya existe: {config_data['clave']}")

def main():
    """Función principal de inicialización para PostgreSQL"""
    print("🐘 Inicializando base de datos PostgreSQL del Sistema de Secado de Cacao...")
    
    # Crear aplicación Flask
    app = crear_app()
    
    # Inicializar base de datos
    with app.app_context():
        try:
            # Crear todas las tablas
            db.create_all()
            print("✓ Tablas creadas exitosamente en PostgreSQL")
            
            # Inicializar configuración por defecto
            inicializar_configuracion()
            
            # Confirmar cambios
            db.session.commit()
            print("✓ Configuración guardada exitosamente")
            
            # Mostrar resumen
            print("\n📊 Resumen de la base de datos PostgreSQL:")
            print(f"   - Cálculos registrados: {CalculoSecado.query.count()}")
            print(f"   - Errores registrados: {RegistroError.query.count()}")
            print(f"   - Configuraciones: {ConfiguracionSistema.query.count()}")
            
            print("\n✅ Base de datos PostgreSQL inicializada correctamente!")
            print("🚀 El sistema está listo para usar con PostgreSQL")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al inicializar la base de datos PostgreSQL: {str(e)}")
            print("\n💡 Posibles soluciones:")
            print("   1. Verifique que PostgreSQL esté en ejecución")
            print("   2. Confirme que la base de datos 'cacaodry' existe")
            print("   3. Verifique las credenciales de conexión")
            print("   4. Asegúrese de tener psycopg2-binary instalado")
            sys.exit(1)

if __name__ == '__main__':
    main()