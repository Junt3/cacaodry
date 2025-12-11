#!/usr/bin/env python3
"""
Script para inicializar la contraseña de configuración del sistema
Ejecutar este script solo una vez para establecer la contraseña inicial
"""

import sys
import getpass
from models import db, ConfiguracionSistema
from auth_utils import establecer_password_configuracion, existe_password_configuracion
from database_config import configure_postgresql
from flask import Flask

def main():
    """Función principal para inicializar la contraseña"""
    
    # Crear aplicación Flask mínima para configuración
    app = Flask(__name__)
    app.secret_key = 'cacao_secado_2023'
    
    # Configurar base de datos
    configure_postgresql(app)
    db.init_app(app)
    
    with app.app_context():
        print("🔐 Inicialización de Contraseña de Configuración")
        print("=" * 50)
        
        # Verificar si ya existe una contraseña
        if existe_password_configuracion():
            print("⚠️  Ya existe una contraseña configurada.")
            print("Si desea cambiarla, use la opción 'Cambiar Contraseña' en la configuración.")
            response = input("¿Desea restablecer la contraseña de todas formas? (s/N): ")
            if response.lower() != 's':
                print("❌ Operación cancelada.")
                return
        
        # Solicitar nueva contraseña
        print("\nPor favor, ingrese una contraseña segura para proteger la configuración:")
        print("- Mínimo 8 caracteres")
        print("- Debe incluir letras y números")
        print("- No use información personal fácil de adivinar")
        
        while True:
            password = getpass.getpass("Nueva contraseña: ")
            
            if len(password) < 8:
                print("❌ La contraseña debe tener al menos 8 caracteres")
                continue
            
            if not any(c.isdigit() for c in password):
                print("❌ La contraseña debe contener al menos un número")
                continue
            
            if not any(c.isalpha() for c in password):
                print("❌ La contraseña debe contener al menos una letra")
                continue
            
            password_confirm = getpass.getpass("Confirme la contraseña: ")
            
            if password != password_confirm:
                print("❌ Las contraseñas no coinciden")
                continue
            
            break
        
        # Establecer la contraseña
        print("\n🔄 Estableciendo contraseña...")
        
        if establecer_password_configuracion(password):
            print("✅ Contraseña establecida correctamente")
            print("\n📋 Información importante:")
            print("- La página de configuración ahora está protegida")
            print("- Para acceder, visite /configuracion e ingrese la contraseña")
            print("- Puede cambiar la contraseña en cualquier momento desde la configuración")
            print("- La sesión expirará después de 2 horas de inactividad")
            print("\n🚀 ¡El sistema está listo para usar!")
        else:
            print("❌ Error al establecer la contraseña")
            print("Por favor, revise los logs para más información")
            sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)