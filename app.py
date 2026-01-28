from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, session
from flask_socketio import SocketIO
from calculos_secado import simular_secado, validar_entradas, obtener_ajuste_superficie
from models import db, CalculoSecado, RegistroError, ConfiguracionSistema, init_db
from configuracion import obtener_configuracion
from database_config import auto_configure_app
from auth_utils import (
    requiere_autenticacion_config, verificar_password_configuracion,
    crear_sesion_config, cerrar_sesion_config, establecer_password_configuracion,
    existe_password_configuracion, validar_fortaleza_password
)
from datetime import datetime, timedelta
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'cacao_secado_2023'  # Clave secreta para mensajes flash

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True, async_mode='threading')

# Configuración automática de la base de datos (PostgreSQL por defecto)
auto_configure_app(app)

# Inicializar la base de datos
init_db(app)

# Import and register SSH terminal
from ssh_terminal import create_simple_ssh_namespace
create_simple_ssh_namespace(socketio)

@app.route('/')
def index():
    """Página principal con el formulario de entrada"""
    return render_template('index.html')

@app.route('/historial')
def historial():
    """Página para mostrar el historial de cálculos"""
    pagina = request.args.get('pagina', 1, type=int)
    
    # Obtener el valor de configuración y convertir explícitamente a entero
    # para evitar TypeError cuando paginate() compara con enteros
    try:
        por_pagina = int(request.args.get('por_pagina', obtener_configuracion('items_por_pagina', 10)))
    except (ValueError, TypeError):
        por_pagina = 10
    modo_filtro = request.args.get('modo', '')
    fecha_inicio = request.args.get('fecha_inicio', '')
    fecha_fin = request.args.get('fecha_fin', '')
    
    # Construir consulta base
    query = CalculoSecado.query
    
    # Aplicar filtros
    if modo_filtro:
        query = query.filter(CalculoSecado.modo == modo_filtro)
    
    if fecha_inicio:
        try:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            query = query.filter(CalculoSecado.fecha_hora >= fecha_inicio_dt)
        except ValueError:
            pass  # Ignorar si el formato es inválido
    
    if fecha_fin:
        try:
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
            # Agregar un día para incluir todo el día seleccionado
            fecha_fin_dt = fecha_fin_dt + timedelta(days=1)
            query = query.filter(CalculoSecado.fecha_hora < fecha_fin_dt)
        except ValueError:
            pass  # Ignorar si el formato es inválido
    
    # Ordenar y paginar
    calculos = query.order_by(CalculoSecado.fecha_hora.desc()).paginate(
        page=pagina, per_page=por_pagina, error_out=False
    )
    
    return render_template('historial.html', calculos=calculos,
                        modo_filtro=modo_filtro, fecha_inicio=fecha_inicio,
                        fecha_fin=fecha_fin, por_pagina=por_pagina)

@app.route('/api/calculos')
def api_calculos():
    """API para obtener cálculos en formato JSON"""
    calculos = CalculoSecado.query.order_by(CalculoSecado.fecha_hora.desc()).limit(50).all()
    return jsonify([calculo.to_dict() for calculo in calculos])

@app.route('/api/calculo/<int:id>')
def api_calculo_detalle(id):
    """API para obtener detalles de un cálculo específico"""
    calculo = CalculoSecado.query.get_or_404(id)
    return jsonify(calculo.to_dict())

@app.route('/api/error/<int:id>')
def api_error_detalle(id):
    """API para obtener detalles de un error específico"""
    error = RegistroError.query.get_or_404(id)
    return jsonify(error.to_dict())

@app.route('/eliminar/calculo/<int:id>', methods=['POST'])
def eliminar_calculo(id):
    """Elimina un cálculo específico del historial"""
    calculo = CalculoSecado.query.get_or_404(id)
    try:
        db.session.delete(calculo)
        db.session.commit()
        flash('Cálculo eliminado correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error al eliminar cálculo: {str(e)}")
        flash('Error al eliminar el cálculo', 'danger')
    
    return redirect(url_for('historial'))

@app.route('/eliminar/calculos', methods=['POST'])
def eliminar_calculos_seleccionados():
    """Elimina múltiples cálculos seleccionados"""
    ids = request.form.getlist('seleccionados')
    if not ids:
        flash('No se seleccionaron cálculos para eliminar', 'warning')
        return redirect(url_for('historial'))
    
    try:
        # Convertir IDs a integers
        ids_int = [int(id) for id in ids]
        # Eliminar todos los cálculos seleccionados
        CalculoSecado.query.filter(CalculoSecado.id.in_(ids_int)).delete(synchronize_session=False)
        db.session.commit()
        flash(f'{len(ids_int)} cálculos eliminados correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error al eliminar cálculos: {str(e)}")
        flash('Error al eliminar los cálculos seleccionados', 'danger')
    
    return redirect(url_for('historial'))

@app.route('/errores')
def ver_errores():
    """Vista para ver y gestionar errores registrados"""
    pagina = request.args.get('pagina', 1, type=int)
    
    # Convertir explícitamente a entero para evitar TypeError cuando paginate() compara con enteros
    try:
        por_pagina = int(obtener_configuracion('items_por_pagina', 20))
    except (ValueError, TypeError):
        por_pagina = 20
    
    errores = RegistroError.query.order_by(RegistroError.fecha_hora.desc()).paginate(
        page=pagina, per_page=por_pagina, error_out=False
    )
    
    return render_template('errores.html', errores=errores)

@app.route('/eliminar/error/<int:id>', methods=['POST'])
def eliminar_error(id):
    """Elimina un registro de error específico"""
    error = RegistroError.query.get_or_404(id)
    try:
        db.session.delete(error)
        db.session.commit()
        flash('Error eliminado correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error al eliminar registro de error: {str(e)}")
        flash('Error al eliminar el registro', 'danger')
    
    return redirect(url_for('ver_errores'))

@app.route('/limpiar/errores', methods=['POST'])
def limpiar_errores():
    """Elimina todos los registros de errores"""
    try:
        RegistroError.query.delete()
        db.session.commit()
        flash('Todos los registros de errores han sido eliminados', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error al limpiar registros de errores: {str(e)}")
        flash('Error al eliminar los registros', 'danger')
    
    return redirect(url_for('ver_errores'))

@app.route('/configuracion')
@requiere_autenticacion_config
def configuracion():
    """Vista para gestionar la configuración del sistema (protegida)"""
    configuraciones = ConfiguracionSistema.query.all()
    return render_template('configuracion.html',
                         configuraciones=configuraciones,
                         autenticado=session.get('config_authenticated', False),
                         ssh_tab=True)

@app.route('/login-config')
def login_config():
    """Vista para autenticarse y acceder a la configuración"""
    # Si ya está autenticado, redirigir a configuración
    if session.get('config_authenticated'):
        return redirect(url_for('configuracion'))
    
    return render_template('login_config.html')

@app.route('/verificar-login-config', methods=['POST'])
def verificar_login_config():
    """Verifica las credenciales para acceder a la configuración"""
    password = request.form.get('password', '')
    
    if not password:
        flash('Por favor ingrese una contraseña', 'danger')
        return redirect(url_for('login_config'))
    
    # Verificar si existe contraseña configurada
    if not existe_password_configuracion():
        flash('No hay contraseña configurada. Contacte al administrador', 'danger')
        return redirect(url_for('login_config'))
    
    # Verificar contraseña
    if verificar_password_configuracion(password):
        crear_sesion_config()
        flash('Acceso concedido correctamente', 'success')
        return redirect(url_for('configuracion'))
    else:
        flash('Contraseña incorrecta. Por favor intente nuevamente', 'danger')
        return redirect(url_for('login_config'))

@app.route('/logout-config')
def logout_config():
    """Cierra la sesión de configuración"""
    cerrar_sesion_config()
    return redirect(url_for('index'))


@app.route('/guardar/configuracion', methods=['POST'])
@requiere_autenticacion_config
def guardar_configuracion():
    """Guarda la configuración del sistema"""
    claves = request.form.getlist('clave')
    valores = request.form.getlist('valor')
    descripciones = request.form.getlist('descripcion')
    
    try:
        for i, clave in enumerate(claves):
            config = ConfiguracionSistema.query.filter_by(clave=clave).first()
            if config:
                config.valor = valores[i]
                if i < len(descripciones):
                    config.descripcion = descripciones[i]
            else:
                nueva_config = ConfiguracionSistema(
                    clave=clave,
                    valor=valores[i],
                    descripcion=descripciones[i] if i < len(descripciones) else ''
                )
                db.session.add(nueva_config)
        
        db.session.commit()
        flash('Configuración guardada correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error al guardar configuración: {str(e)}")
        flash('Error al guardar la configuración', 'danger')
    
    return redirect(url_for('configuracion'))

@app.route('/cambiar-password-config', methods=['GET', 'POST'])
@requiere_autenticacion_config
def cambiar_password_config():
    """Cambia la contraseña de acceso a la configuración"""
    if request.method == 'GET':
        return render_template('cambiar_password.html')
    
    # Procesar formulario POST
    password_actual = request.form.get('password_actual', '')
    password_nuevo = request.form.get('password_nuevo', '')
    password_confirmar = request.form.get('password_confirmar', '')
    
    # Validaciones
    if not password_actual or not password_nuevo or not password_confirmar:
        flash('Todos los campos son obligatorios', 'danger')
        return render_template('cambiar_password.html')
    
    # Verificar contraseña actual
    if not verificar_password_configuracion(password_actual):
        flash('La contraseña actual es incorrecta', 'danger')
        return render_template('cambiar_password.html')
    
    # Validar que las nuevas contraseñas coincidan
    if password_nuevo != password_confirmar:
        flash('Las nuevas contraseñas no coinciden', 'danger')
        return render_template('cambiar_password.html')
    
    # Validar fortaleza de la nueva contraseña
    es_valida, mensaje = validar_fortaleza_password(password_nuevo)
    if not es_valida:
        flash(mensaje, 'danger')
        return render_template('cambiar_password.html')
    
    # Establecer nueva contraseña
    if establecer_password_configuracion(password_nuevo):
        flash('Contraseña cambiada correctamente', 'success')
        return redirect(url_for('configuracion'))
    else:
        flash('Error al cambiar la contraseña. Por favor intente nuevamente', 'danger')
        return render_template('cambiar_password.html')

@app.route('/calcular', methods=['POST'])
def calcular():
    """Procesa los datos del formulario y muestra los resultados"""
    
    # Obtener datos del formulario
    modo = request.form.get('modo')
    
    # Obtener temperatura según el modo
    if modo == "1":  # Industrial
        temp_aire = request.form.get('temp_aire')
        sel_superficie = None
    else:  # Solar
        temp_aire = request.form.get('temp_aire_solar')
        sel_superficie = request.form.get('sel_superficie')
    
    h_inicial = request.form.get('h_inicial')
    h_final = request.form.get('h_final')
    peso_quintales = request.form.get('peso_quintales')
    capacidad_max = request.form.get('capacidad_max')
    
    # Validar entradas
    mensajes = validar_entradas(modo, temp_aire, sel_superficie, h_inicial, h_final, peso_quintales, capacidad_max)
    
    # Separar errores de advertencias
    errores = [msg for msg in mensajes if not msg.startswith('ADVERTENCIA:')]
    advertencias = [msg for msg in mensajes if msg.startswith('ADVERTENCIA:')]
    
    if errores:
        # Registrar errores en la base de datos
        try:
            error_registro = RegistroError(
                tipo_error='VALIDACION',
                mensaje_error='; '.join(errores),
                datos_entrada=json.dumps({
                    'modo': modo,
                    'temp_aire': temp_aire,
                    'sel_superficie': sel_superficie,
                    'h_inicial': h_inicial,
                    'h_final': h_final,
                    'peso_quintales': peso_quintales,
                    'capacidad_max': capacidad_max
                }),
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            db.session.add(error_registro)
            db.session.commit()
        except Exception as e:
            app.logger.error(f"Error al registrar error: {str(e)}")
        
        for error in errores:
            flash(error, 'danger')
        return redirect(url_for('index'))
    
    # Convertir a tipos numéricos
    temp_aire = float(temp_aire)
    h_inicial = float(h_inicial)
    h_final = float(h_final)
    peso_quintales = float(peso_quintales)
    capacidad_max = float(capacidad_max)
    
    # Realizar cálculos
    try:
        resultados = simular_secado(modo, temp_aire, sel_superficie, h_inicial, h_final, peso_quintales, capacidad_max)
        
        # Preparar datos de entrada para mostrar en resultados
        datos_entrada = {
            'modo': modo,
            'modo_nombre': 'Secadora Industrial (Gas/Leña)' if modo == '1' else 'Secado al Aire Libre (Solar)',
            'temp_aire': temp_aire,
            'h_inicial': h_inicial,
            'h_final': h_final,
            'peso_quintales': peso_quintales,
            'capacidad_max': capacidad_max
        }
        
        if modo == '2' and sel_superficie:
            _, superficie_nombre = obtener_ajuste_superficie(sel_superficie)
            datos_entrada['superficie_nombre'] = superficie_nombre
        
        # Guardar el cálculo en la base de datos
        try:
            calculo_guardado = CalculoSecado(
                modo=resultados['modo'],
                temperatura_aire=temp_aire,
                superficie_tipo=datos_entrada.get('superficie_nombre'),
                humedad_inicial=h_inicial,
                humedad_final=h_final,
                peso_quintales=peso_quintales,
                capacidad_maxima=capacidad_max,
                temperatura_efectiva=resultados['temp_efectiva'],
                constante_k=resultados['k_calculado'],
                constante_n=resultados['n_calculado'],
                tiempo_base_horas=resultados['tiempo_base_horas'],
                factor_penalizacion=resultados['factor_penalizacion'],
                tiempo_total_horas=resultados['tiempo_total_horas_calor'],
                peso_inicial_kg=resultados['peso_kg_inicial'],
                peso_final_kg=resultados['peso_kg_final'],
                agua_evaporada_litros=resultados['agua_eliminada'],
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            db.session.add(calculo_guardado)
            db.session.commit()
        except Exception as e:
            app.logger.error(f"Error al guardar cálculo: {str(e)}")
            flash('El cálculo se realizó pero no pudo guardarse en el historial', 'warning')
        
        # Pasar advertencias a la plantilla
        return render_template('resultados.html', resultados=resultados, datos_entrada=datos_entrada, advertencias=advertencias)
        
    except Exception as e:
        # Registrar error crítico
        try:
            error_registro = RegistroError(
                tipo_error='CALCULO',
                mensaje_error=str(e),
                datos_entrada=json.dumps({
                    'modo': modo,
                    'temp_aire': temp_aire,
                    'sel_superficie': sel_superficie,
                    'h_inicial': h_inicial,
                    'h_final': h_final,
                    'peso_quintales': peso_quintales,
                    'capacidad_max': capacidad_max
                }),
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            db.session.add(error_registro)
            db.session.commit()
        except Exception as db_error:
            app.logger.error(f"Error al registrar error crítico: {str(db_error)}")
        
        flash(f'Error en el cálculo: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    """Manejo de errores 404"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Manejo de errores 500"""
    flash('Ha ocurrido un error en el servidor. Por favor, inténtelo nuevamente.', 'danger')
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Ejecutar la aplicación con SocketIO en modo debug para desarrollo
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)