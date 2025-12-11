# Inicio Rápido - Sistema de Secado de Cacao

## Requisitos
- Python 3.7+
- PostgreSQL (recomendado) o SQLite

## Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/Junt3/cacaodry.git
cd cacaodry

# 2. Crear entorno virtual, hacer 'sudo apt install python3.13-venv' si falla
python -m venv venv


# 3. Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt
```

## Configuración de Base de Datos

### Opción 1: PostgreSQL (Recomendado)

```bash
# 1. Crear base de datos en PostgreSQL
CREATE TABLE IF NOT EXISTS 'cacaodry'

# 2. Inicializar base de datos
python db_manager.py init --db-type=postgresql

# 3. Establecer contraseña de configuración
python db_manager.py seed --password

# 4. Verificar instalación
python db_manager.py test
```

## Ejecutar Aplicación

```bash
python app.py
```

Abrir navegador en: http://localhost:5000

## Comandos Útiles

### Mantenimiento de Base de Datos
```bash
# Ver estado de la base de datos
python db_manager.py info

# Aplicar migraciones (actualizaciones)
python db_manager.py migrate

# Ver estado de migraciones
python db_manager.py migrate status

# Ejecutar pruebas de diagnóstico
python db_manager.py test
```

### Resolución de Problemas
```bash
# Si hay problemas de conexión
python db_manager.py test connection

# Si hay problemas con datos
python db_manager.py test operations

# Para resetear todo (¡cuidado! pierde datos)
python db_manager.py reset

# Para resetear manteniendo configuración
python db_manager.py reset --keep-config
```

## Flujo de Trabajo Típico

### Proyecto Nuevo
```bash
python db_manager.py init
python db_manager.py seed --password
python db_manager.py test
python app.py
```

### Actualización del Sistema
```bash
python db_manager.py migrate
python app.py
```

### Diagnóstico de Problemas
```bash
python db_manager.py test
python db_manager.py info --detailed
```

## Más Información

- Documentación completa: [`README.md`](README.md)
- Guía del gestor de BD: [`DB_MANAGER_GUIDE.md`](DB_MANAGER_GUIDE.md)
- Ayuda del gestor: `python db_manager.py --help`

## Vistas Principales

- `/` - Calculadora de secado
- `/historial` - Historial de cálculos
- `/configuracion` - Configuración del sistema (requiere contraseña)
- `/errores` - Gestión de errores