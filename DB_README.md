# Base de Datos - Sistema de Secado de Cacao

## Overview

Este documento describe la implementación de la base de datos del Sistema de Secado de Cacao, incluyendo modelos, inicialización y migraciones.

## Modelos de Datos

### 1. CalculoSecado
Almacena los cálculos de secado realizados por los usuarios.

**Campos:**
- `id`: Identificador único (Primary Key)
- `fecha_hora`: Fecha y hora del cálculo
- `modo`: Modo de secado ('INDUSTRIAL' o 'SOLAR')
- `temperatura_aire`: Temperatura del aire ingresada
- `superficie_tipo`: Tipo de superficie (para modo solar)
- `humedad_inicial`: Humedad inicial del grano
- `humedad_final`: Humedad final deseada
- `peso_quintales`: Peso en quintales
- `capacidad_maxima`: Capacidad máxima del sistema
- `temperatura_efectiva`: Temperatura efectiva calculada
- `constante_k`: Constante k del modelo de Page
- `constante_n`: Constante n del modelo de Page
- `tiempo_base_horas`: Tiempo base de secado
- `factor_penalizacion`: Factor por sobrecarga
- `tiempo_total_horas`: Tiempo total de secado
- `peso_inicial_kg`: Peso inicial en kg
- `peso_final_kg`: Peso final en kg
- `agua_evaporada_litros`: Agua evaporada en litros
- `ip_address`: Dirección IP del cliente
- `user_agent`: User Agent del navegador

### 2. ConfiguracionSistema
Almacena la configuración del sistema.

**Campos:**
- `id`: Identificador único (Primary Key)
- `clave`: Clave de configuración (única)
- `valor`: Valor de la configuración
- `descripcion`: Descripción del parámetro
- `fecha_actualizacion`: Fecha de última actualización

### 3. RegistroError
Almacena los errores ocurridos en el sistema.

**Campos:**
- `id`: Identificador único (Primary Key)
- `fecha_hora`: Fecha y hora del error
- `tipo_error`: Tipo de error ('VALIDACION', 'CALCULO')
- `mensaje_error`: Mensaje del error
- `datos_entrada`: Datos que causaron el error (JSON)
- `ip_address`: Dirección IP del cliente
- `user_agent`: User Agent del navegador

## Inicialización

### Script de Inicialización

Para inicializar la base de datos desde cero:

```bash
python init_db.py
```

Este script:
- Crea todas las tablas necesarias
- Inserta configuraciones por defecto
- Muestra un resumen de la base de datos

### Configuraciones por Defecto

El sistema incluye las siguientes configuraciones iniciales:

- `version_sistema`: Versión actual del sistema
- `temp_min_industrial`: Temperatura mínima para secado industrial (40°C)
- `temp_max_industrial`: Temperatura máxima para secado industrial (100°C)
- `temp_min_solar`: Temperatura mínima para secado solar (15°C)
- `temp_max_solar`: Temperatura máxima para secado solar (45°C)
- `humedad_min`: Humedad mínima permitida (0%)
- `humedad_max`: Humedad máxima permitida (100%)
- `humedad_advertencia_baja`: Umbral de advertencia baja (6%)
- `humedad_advertencia_alta`: Umbral de advertencia alta (8%)
- `items_por_pagina`: Items por página en el historial (10)

## Migraciones

### Sistema de Migraciones

El sistema incluye un gestor de migraciones para manejar cambios en el esquema:

```bash
# Aplicar migraciones pendientes
python migrate.py migrate

# Ver estado de las migraciones
python migrate.py status

# Revertir una migración específica
python migrate.py rollback migration_id
```

### Migraciones Disponibles

1. **001_initial_schema**: Crea el esquema inicial de la base de datos
2. **002_add_indexes**: Agrega índices para mejorar rendimiento
3. **003_add_user_fields**: Campos adicionales para tracking de usuario

## API Endpoints

### Cálculos
- `GET /api/calculos`: Obtiene todos los cálculos (límite 50)
- `GET /api/calculo/<id>`: Obtiene detalles de un cálculo específico

### Errores
- `GET /api/error/<id>`: Obtiene detalles de un error específico

## Vistas de Administración

### Historial de Cálculos
- URL: `/historial`
- Funcionalidades:
  - Paginación configurable
  - Filtrado por modo y fechas
  - Selección múltiple para eliminación
  - Exportación a JSON

### Gestión de Errores
- URL: `/errores`
- Funcionalidades:
  - Visualización de errores registrados
  - Eliminación individual o masiva
  - Inspección de datos que causaron el error

### Configuración del Sistema
- URL: `/configuracion`
- Funcionalidades:
  - Modificación de parámetros del sistema
  - Validación de rangos permitidos
  - Persistencia en base de datos

## Consideraciones de Rendimiento

### Índices
Se han agregado índices en:
- `calculos_secado(fecha_hora)`: Para ordenamiento por fecha
- `registros_errores(fecha_hora)`: Para consultas de errores
- `calculos_secado(modo)`: Para filtrado por modo

### Optimizaciones
- Paginación para evitar cargar grandes volúmenes de datos
- Consultas filtradas para reducir transferencia
- Índices compuestos para búsquedas comunes

## Backup y Recuperación

### Backup Manual
```bash
# Copia de seguridad de la base de datos
cp cacaodry.db backup_cacaodry_$(date +%Y%m%d).db
```

### Recuperación
```bash
# Restaurar desde backup
cp backup_cacaodry_YYYYMMDD.db cacaodry.db
```

## Seguridad

### Consideraciones
- Los datos de usuario (IP, User Agent) se almacenan para auditoría
- No se almacenan datos personales sensibles
- Los errores se registran sin exponer información interna crítica

### Recomendaciones
- Realizar backups periódicos
- Limitar el acceso a la base de datos en producción
- Monitorear el tamaño de la base de datos y limpiar registros antiguos

## Troubleshooting

### Problemas Comunes

1. **Error: "database is locked"**
   - Cerrar todas las conexiones a la base de datos
   - Verificar que no haya procesos usando el archivo .db

2. **Error: "no such table"**
   - Ejecutar `python init_db.py` para crear las tablas
   - Verificar que el archivo de base de datos exista

3. **Migración fallida**
   - Verificar el estado con `python migrate.py status`
   - Revertir la última migración si es necesario
   - Revisar el log de errores específicos

### Logs
Los errores de la aplicación se registran en:
- Base de datos (tabla `registros_errores`)
- Logs de Flask (si está configurado)
- Consola (en modo desarrollo)

## Futuras Mejoras

1. **Migraciones automáticas**: Integrar con el inicio de la aplicación
2. **Backup programado**: Script para backups automáticos
3. **Replicación**: Para alta disponibilidad
4. **Análisis de datos**: Vistas para estadísticas y tendencias
5. **Optimización de consultas**: Para grandes volúmenes de datos