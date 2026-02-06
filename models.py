from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class CalculoSecado(db.Model):
    __tablename__ = 'calculos_secado'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow)
    modo = db.Column(db.String(10), nullable=False)  # 'INDUSTRIAL' o 'SOLAR'
    
    # Parámetros de entrada
    temperatura_aire = db.Column(db.Float, nullable=False)
    superficie_tipo = db.Column(db.String(50))  # NULL para industrial
    humedad_inicial = db.Column(db.Float, nullable=False)
    humedad_final = db.Column(db.Float, nullable=False)
    peso_quintales = db.Column(db.Float, nullable=False)
    capacidad_maxima = db.Column(db.Float, nullable=False)
    
    # Parámetros calculados
    temperatura_efectiva = db.Column(db.Float, nullable=False)
    constante_k = db.Column(db.Float, nullable=False)
    constante_n = db.Column(db.Float, nullable=False)
    tiempo_base_horas = db.Column(db.Float, nullable=False)
    factor_penalizacion = db.Column(db.Float, nullable=False)
    tiempo_total_horas = db.Column(db.Float, nullable=False)
    
    # Resultados de masa
    peso_inicial_kg = db.Column(db.Float, nullable=False)
    peso_final_kg = db.Column(db.Float, nullable=False)
    agua_evaporada_litros = db.Column(db.Float, nullable=False)
    
    # Metadatos
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    
    def to_dict(self):
        """Convierte el objeto a un diccionario para fácil serialización"""
        return {
            'id': self.id,
            'fecha_hora': self.fecha_hora.strftime('%Y-%m-%d %H:%M:%S'),
            'modo': self.modo,
            'temperatura_aire': self.temperatura_aire,
            'superficie_tipo': self.superficie_tipo,
            'humedad_inicial': self.humedad_inicial,
            'humedad_final': self.humedad_final,
            'peso_quintales': self.peso_quintales,
            'capacidad_maxima': self.capacidad_maxima,
            'temperatura_efectiva': self.temperatura_efectiva,
            'constante_k': self.constante_k,
            'constante_n': self.constante_n,
            'tiempo_base_horas': self.tiempo_base_horas,
            'factor_penalizacion': self.factor_penalizacion,
            'tiempo_total_horas': self.tiempo_total_horas,
            'peso_inicial_kg': self.peso_inicial_kg,
            'peso_final_kg': self.peso_final_kg,
            'agua_evaporada_litros': self.agua_evaporada_litros,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent
        }

class ConfiguracionSistema(db.Model):
    __tablename__ = 'configuraciones_sistema'
    
    id = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(50), unique=True, nullable=False)
    valor = db.Column(db.Text, nullable=False)
    descripcion = db.Column(db.Text)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convierte el objeto a un diccionario para fácil serialización"""
        return {
            'id': self.id,
            'clave': self.clave,
            'valor': self.valor,
            'descripcion': self.descripcion,
            'fecha_actualizacion': self.fecha_actualizacion.strftime('%Y-%m-%d %H:%M:%S')
        }

class RegistroError(db.Model):
    __tablename__ = 'registros_errores'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow)
    tipo_error = db.Column(db.String(50), nullable=False)
    mensaje_error = db.Column(db.Text, nullable=False)
    datos_entrada = db.Column(db.Text)  # JSON con los datos que causaron el error
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    
    def to_dict(self):
        """Convierte el objeto a un diccionario para fácil serialización"""
        return {
            'id': self.id,
            'fecha_hora': self.fecha_hora.strftime('%Y-%m-%d %H:%M:%S'),
            'tipo_error': self.tipo_error,
            'mensaje_error': self.mensaje_error,
            'datos_entrada': self.datos_entrada,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent
        }

def init_db(app):
    """Inicializa la base de datos con la aplicación Flask"""
    db.init_app(app)
    
    with app.app_context():
        # Crea todas las tablas
        db.create_all()
        
        # Inserta configuraciones por defecto si no existen
        if not ConfiguracionSistema.query.filter_by(clave='version_sistema').first():
            config_default = ConfiguracionSistema(
                clave='version_sistema',
                valor='1.0.0',
                descripcion='Versión actual del sistema de secado de cacao'
            )
            db.session.add(config_default)
            db.session.commit()