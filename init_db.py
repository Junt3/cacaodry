#!/usr/bin/env python3
"""
Script para inicializar la base de datos del Sistema de Secado de Cacao
"""

import os
import sys
from flask import Flask
from models import db, CalculoSecado, ConfiguracionSistema, RegistroError, init_db
from database_config import auto_configure_app

def crear_app():
    """Crea una aplicación Flask para inicialización"""
    app = Flask(__name__)
    
    # Configurar automáticamente la base de datos (PostgreSQL por defecto)
    auto_configure_app(app)
    
    # Inicializar la base de datos con esta aplicación
    init_db(app)
    return app

def inicializar_configuracion():
    """Inicializa la configuración por defecto del sistema"""
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
    """Función principal de inicialización"""
    print("🌱 Inicializando base de datos del Sistema de Secado de Cacao...")
    
    # Crear aplicación Flask
    app = crear_app()
    
    # Inicializar base de datos
    with app.app_context():
        try:
            # Crear todas las tablas
            db.create_all()
            print("✓ Tablas creadas exitosamente")
            
            # Inicializar configuración por defecto
            inicializar_configuracion()
            
            # Confirmar cambios
            db.session.commit()
            print("✓ Configuración guardada exitosamente")
            
            # Mostrar resumen
            print("\n📊 Resumen de la base de datos:")
            print(f"   - Cálculos registrados: {CalculoSecado.query.count()}")
            print(f"   - Errores registrados: {RegistroError.query.count()}")
            print(f"   - Configuraciones: {ConfiguracionSistema.query.count()}")
            
            print("\n✅ Base de datos inicializada correctamente!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al inicializar la base de datos: {str(e)}")
            sys.exit(1)

if __name__ == '__main__':
    main()