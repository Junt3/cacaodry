# Sistema de Protección por Contraseña para Configuración

## Overview

Se ha implementado un sistema de protección por contraseña simple para restringir el acceso a la página de configuración del Sistema de Secado de Cacao. Esta solución proporciona seguridad adecuada sin la complejidad de un sistema de roles completo.

## Características

### 🔐 Seguridad
- **Hash de contraseña**: Usa `werkzeug.security` para almacenar contraseñas de forma segura
- **Sesiones seguras**: Las sesiones expiran después de 2 horas de inactividad
- **Validación de fortaleza**: Requiere contraseñas con mínimo 8 caracteres, letras y números
- **Protección CSRF**: Los formularios incluyen protección CSRF

### 🎯 Funcionalidades
- **Login simple**: Interfaz amigable para autenticarse
- **Cambio de contraseña**: Los usuarios autenticados pueden cambiar su contraseña
- **Indicadores visuales**: Muestra el estado de autenticación en la navegación
- **Cierre de sesión**: Opción explícita para cerrar sesión

## Instalación y Configuración

### 1. Inicializar la Contraseña

Ejecute el script `init_password.py` para establecer la contraseña inicial:

```bash
python init_password.py
```

El script le guiará para establecer una contraseña segura con las siguientes validaciones:
- Mínimo 8 caracteres
- Al menos un número
- Al menos una letra

### 2. Acceder a la Configuración

1. Inicie la aplicación: `python app.py`
2. Haga clic en "🔒 Configuración" en el menú de navegación
3. Ingrese la contraseña cuando se le solicite
4. Tendrá acceso a todas las opciones de configuración

## Flujo de Usuario

### Autenticación
```
Usuario → /configuracion → Verificar sesión → Redirigir a /login-config
Login → Verificar contraseña → Crear sesión → Acceder a /configuracion
```

### Cambio de Contraseña
```
Configuración → "Cambiar Contraseña" → Verificar contraseña actual → 
Establecer nueva contraseña → Confirmar cambio
```

### Cierre de Sesión
```
Configuración → "Cerrar Sesión" → Eliminar sesión → Redirigir a inicio
```

## Estructura de Archivos

### Archivos Nuevos
- `auth_utils.py` - Utilidades de autenticación
- `templates/login_config.html` - Formulario de login
- `templates/cambiar_password.html` - Formulario de cambio de contraseña
- `init_password.py` - Script de inicialización

### Archivos Modificados
- `app.py` - Rutas de autenticación y protección
- `templates/base.html` - Navegación con indicadores de estado
- `templates/configuracion.html` - Opciones de sesión

## Rutas Implementadas

| Ruta | Método | Descripción | Protección |
|------|--------|-------------|------------|
| `/configuracion` | GET | Página de configuración | 🔒 Requiere autenticación |
| `/login-config` | GET | Formulario de login | ✅ Pública |
| `/verificar-login-config` | POST | Procesar login | ✅ Pública |
| `/logout-config` | GET | Cerrar sesión | ✅ Pública |
| `/cambiar-password-config` | GET/POST | Cambiar contraseña | 🔒 Requiere autenticación |

## Seguridad Implementada

### Almacenamiento de Contraseña
- **Hash**: `werkzeug.security.generate_password_hash()`
- **Verificación**: `werkzeug.security.check_password_hash()`
- **Ubicación**: Tabla `ConfiguracionSistema` con clave `password_configuracion`

### Gestión de Sesiones
- **Duración**: 2 horas de inactividad
- **Almacenamiento**: Sesiones de Flask
- **Variables**: `config_authenticated`, `config_auth_time`

### Validaciones
- **Fortaleza de contraseña**: Mínimo 8 caracteres, letras y números
- **Coincidencia**: Verificación que nueva contraseña y confirmación coincidan
- **Contraseña actual**: Requerida para cambiar la contraseña

## Consideraciones de Mantenimiento

### Cambio de Contraseña
- Los usuarios pueden cambiar su contraseña desde la configuración
- Se requiere la contraseña actual para verificar identidad
- La nueva contraseña debe cumplir con los requisitos de fortaleza

### Recuperación de Contraseña
- Si olvida la contraseña, debe ejecutar `init_password.py` nuevamente
- Esto restablecerá la contraseña completamente

### Monitoreo
- Los intentos de acceso se registran en los logs de la aplicación
- Los errores de autenticación muestran mensajes genéricos por seguridad

## Personalización

### Tiempo de Sesión
Para cambiar el tiempo de expiración de la sesión, modifique el valor en `auth_utils.py`:

```python
if time.time() - ultimo_acceso > 7200:  # 2 horas en segundos
```

### Requisitos de Contraseña
Para ajustar los requisitos de fortaleza, modifique la función `validar_fortaleza_password()` en `auth_utils.py`.

## Solución de Problemas

### Problemas Comunes

1. **"No hay contraseña configurada"**
   - Solución: Ejecute `python init_password.py`

2. **"La sesión ha expirado"**
   - Solución: Inicie sesión nuevamente

3. **"Contraseña incorrecta"**
   - Solución: Verifique la contraseña o restablézcala con `init_password.py`

### Logs y Depuración

Los errores de autenticación se registran en los logs de la aplicación. Para habilitar modo debug:

```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

## Mejoras Futuras

Posibles mejoras para el sistema:

1. **Intentos fallidos**: Límite de intentos fallidos antes de bloquear
2. **Recuperación por email**: Sistema de recuperación de contraseña
3. **Logs de auditoría**: Registro de cambios en configuración
4. **Autenticación de dos factores**: Capa adicional de seguridad

## Conclusión

Este sistema de protección por contraseña simple proporciona una solución efectiva y segura para proteger la configuración del sistema sin la complejidad de un sistema de roles completo. Es fácil de mantener y proporciona la seguridad necesaria para las operaciones críticas de configuración.