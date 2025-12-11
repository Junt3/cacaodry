# Sistema Web de Secado de Cacao

Aplicación web para calcular tiempos de secado de cacao utilizando el Modelo de Page, desarrollada con Flask.

## Características

- **Dos modos de secado**: Industrial (gas/leña) y Solar (aire libre)
- **Cálculos precisos** basados en el Modelo Matemático de Page
- **Validación de datos** con advertencias para valores fuera de rango
- **Interfaz responsiva** que funciona en dispositivos móviles y escritorio
- **Resultados detallados** incluyendo balance de masa y tiempo estimado
- **Detección de sobrecarga** con penalización automática
- **Base de datos integrada** con SQLite y soporte para PostgreSQL
- **Historial de cálculos** con filtrado y paginación avanzada
- **Gestión de errores** con registro y visualización detallada
- **Sistema de configuración** personalizable desde la interfaz
- **API RESTful** para acceso programático a los datos
- **Sistema de migraciones** para evolución del esquema

## Requisitos

- Python 3.7 o superior
- Pip (gestor de paquetes de Python)
- PostgreSQL (opcional, para producción o entornos avanzados)

## Instalación

### Opción 1: SQLite (Desarrollo y pruebas rápidas)

1. Clonar o descargar este repositorio
2. Crear un entorno virtual (recomendado):
   ```
   python -m venv venv
   ```
   
3. Activar el entorno virtual:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
   
4. Instalar las dependencias:
   ```
   pip install -r requirements.txt
   ```

### Opción 2: PostgreSQL (Producción o entornos avanzados)

1. Instalar PostgreSQL en tu sistema:
   - Windows: Descargar desde https://www.postgresql.org/download/windows/
   - Linux: `sudo apt-get install postgresql postgresql-contrib` (Ubuntu/Debian)
   - Mac: `brew install postgresql`

2. Crear una base de datos para el proyecto:
   ```bash
   # Conectarse a PostgreSQL
   psql -U postgres
   
   # Crear base de datos
   CREATE DATABASE cacaodry;
   ```

3. Clonar o descargar este repositorio
4. Crear y activar un entorno virtual (como en la opción 1)
5. Instalar las dependencias:
   ```
   pip install -r requirements.txt
   ```

6. Inicializar la base de datos PostgreSQL:
   ```
   python init_postgresql.py
   ```

## Ejecución

### Con SQLite (configuración por defecto)
1. Asegúrate de estar en el directorio del proyecto
2. Ejecuta la aplicación:
   ```
   python app.py
   ```
3. Abre tu navegador web y visita: `http://localhost:5000`

### Con PostgreSQL
1. Asegúrate de que PostgreSQL esté en ejecución
2. La aplicación está configurada para usar PostgreSQL por defecto
3. Ejecuta la aplicación:
   ```
   python app.py
   ```
4. Abre tu navegador web y visita: `http://localhost:5000`

**Nota**: La configuración actual está optimizada para PostgreSQL. Si deseas usar SQLite, modifica la línea de conexión en `app.py`.

## Modelo Matemático

La aplicación utiliza el **Modelo de Page** para calcular el tiempo de secado:

```
MR = exp(-k * t^n)
```

Donde:
- MR: Razón de humedad (adimensional)
- k: Constante de velocidad (calculada con regresión exponencial)
- t: Tiempo (horas)
- n: Coeficiente de Page (0.70 para cacao)

La constante k se calcula dinámicamente según la temperatura:

```
k = 0.06 * exp(0.03 * T)
```

## Base de Datos

El sistema soporta tanto **SQLite** como **PostgreSQL** como motores de base de datos. La configuración actual está optimizada para PostgreSQL.

### Configuración de PostgreSQL

La aplicación está configurada para conectarse a PostgreSQL con las siguientes credenciales:
- Host: localhost
- Base de datos: cacaodry
- Usuario: postgres
- Contraseña: juniher2004

Para cambiar estas credenciales, modifica la línea de conexión en los archivos:
- `app.py`
- `init_db.py`
- `migrate.py`
- `init_postgresql.py`

### Modelos de Datos

### Modelos Principales
- **CalculoSecado**: Almacena todos los cálculos realizados
- **ConfiguracionSistema**: Parámetros configurables del sistema
- **RegistroError**: Registro de errores y excepciones

### Características de la BD
- **Persistencia automática** de todos los cálculos
- **Índices optimizados** para consultas frecuentes
- **Sistema de migraciones** para evolución del esquema
- **API endpoints** para acceso programático

### Inicialización

#### Para SQLite:
```bash
# Inicializar base de datos por primera vez
python init_db.py

# Aplicar migraciones pendientes
python migrate.py migrate

# Ver estado de migraciones
python migrate.py status
```

#### Para PostgreSQL:
```bash
# Inicializar base de datos PostgreSQL por primera vez
python init_postgresql.py

# Aplicar migraciones pendientes
python migrate.py migrate

# Ver estado de migraciones
python migrate.py status
```

### Vistas de Administración
- **/historial**: Historial completo con filtros y paginación
- **/errores**: Gestión de errores registrados
- **/configuracion**: Configuración personalizable del sistema

## Extensiones Futuras

La arquitectura está diseñada para facilitar futuras mejoras:

- ✅ **Almacenamiento de historial de cálculos en base de datos** (Implementado)
- ✅ **Sistema de configuración persistente** (Implementado)
- ✅ **Gestión avanzada de errores** (Implementado)
- ✅ **API RESTful** (Implementado)
- Integración con APIs de clima para obtener datos meteorológicos
- Autenticación de usuarios y perfiles personalizados
- Exportación de resultados a PDF/Excel
- Gráficos interactivos del proceso de secado
- Sistema de backup automático de la base de datos
- Análisis estadístico de cálculos históricos