# Guía de Migración a PostgreSQL

## Resumen

Este documento describe los pasos necesarios para migrar el Sistema de Secado de Cacao de SQLite a PostgreSQL.

## Requisitos Previos

1. **PostgreSQL instalado** en el sistema local
2. **Base de datos creada** con el nombre `cacaodry`
3. **Python 3.7+** con pip instalado
4. **Entorno virtual** (recomendado)

## Instalación de PostgreSQL

### Windows
1. Descargar desde https://www.postgresql.org/download/windows/
2. Ejecutar el instalador y seguir las instrucciones
3. Anotar la contraseña del usuario `postgres`

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### macOS
```bash
brew install postgresql
brew services start postgresql
```

## Configuración de la Base de Datos

1. **Conectarse a PostgreSQL**:
   ```bash
   psql -U postgres
   ```

2. **Crear la base de datos**:
   ```sql
   CREATE DATABASE cacaodry;
   \q
   ```

3. **Verificar la conexión**:
   ```bash
   psql -U postgres -d cacaodry -c "SELECT version();"
   ```

## Instalación del Proyecto

1. **Clonar o descargar** el repositorio del proyecto

2. **Crear entorno virtual**:
   ```bash
   python -m venv venv
   ```

3. **Activar entorno virtual**:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuración de la Aplicación

La aplicación está configurada para usar PostgreSQL por defecto con las siguientes credenciales:
- **Host**: localhost
- **Base de datos**: cacaodry
- **Usuario**: postgres
- **Contraseña**: juniher2004

### Cambiar Credenciales

Si necesitas cambiar las credenciales, modifica el archivo `database_config.py`:

```python
'postgresql': {
    'SQLALCHEMY_DATABASE_URI': 'postgresql://usuario:password@localhost/cacaodry',
    # ... resto de la configuración
}
```

## Inicialización de la Base de Datos

1. **Ejecutar el script de inicialización**:
   ```bash
   python init_postgresql.py
   ```

2. **Verificar la inicialización**:
   ```bash
   python test_postgresql.py
   ```

## Ejecución de la Aplicación

1. **Iniciar la aplicación**:
   ```bash
   python app.py
   ```

2. **Acceder en el navegador**:
   ```
   http://localhost:5000
   ```

## Gestión de Migraciones

### Aplicar migraciones pendientes:
```bash
python migrate.py migrate
```

### Ver estado de migraciones:
```bash
python migrate.py status
```

### Revertir una migración:
```bash
python migrate.py rollback migration_id
```

## Pruebas de Funcionamiento

### Ejecutar pruebas completas:
```bash
python test_postgresql.py
```

### Pruebas manuales:
1. Acceder a `http://localhost:5000`
2. Realizar un cálculo de secado
3. Verificar que se guarde en el historial
4. Probar las vistas de administración

## Cambiar entre SQLite y PostgreSQL

### Usar PostgreSQL (por defecto):
```bash
# Sin cambios, usa PostgreSQL por defecto
python app.py
```

### Usar SQLite temporalmente:
```bash
# Establecer variable de entorno
set DB_TYPE=sqlite  # Windows
export DB_TYPE=sqlite  # Linux/Mac

# Ejecutar aplicación
python app.py
```

### Cambio permanente:
Modifica el archivo `database_config.py` y cambia la función `get_current_database_type()`.

## Solución de Problemas

### Error de conexión
- Verifica que PostgreSQL esté en ejecución
- Confirma que la base de datos `cacaodry` existe
- Verifica las credenciales de conexión

### Error de dependencias
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Error de permisos
Asegúrate de que el usuario `postgres` tenga permisos sobre la base de datos `cacaodry`.

### Error de puerto
Si PostgreSQL usa un puerto diferente, actualiza la cadena de conexión:
```python
'SQLALCHEMY_DATABASE_URI': 'postgresql://postgres:juniher2004@localhost:5433/cacaodry'
```

## Ventajas de PostgreSQL sobre SQLite

1. **Mejor rendimiento** en consultas complejas
2. **Soporte de concurrencia** para múltiples usuarios
3. **Mayor escalabilidad** para crecimiento futuro
4. **Características avanzadas** (triggers, procedimientos almacenados)
5. **Mejor seguridad** y gestión de permisos
6. **Herramientas de administración** más robustas

## Consideraciones de Producción

1. **Configurar backup automático** de la base de datos
2. **Monitorear el rendimiento** de las consultas
3. **Optimizar índices** según el uso real
4. **Configurar replicación** para alta disponibilidad
5. **Implementar logging** de consultas lentas

## Soporte

Si encuentras problemas durante la migración:

1. Revisa los mensajes de error carefully
2. Ejecuta las pruebas de diagnóstico
3. Verifica la configuración de PostgreSQL
4. Consulta la documentación oficial de PostgreSQL

---

**Nota**: Esta migración es opcional. SQLite sigue siendo perfectamente funcional para desarrollo y pequeñas implementaciones.