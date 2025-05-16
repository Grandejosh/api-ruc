from flask import Flask, request, jsonify, abort
import mysql.connector
from mysql.connector import Error
from functools import wraps

app = Flask(__name__)

# Configuración MySQL
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '12345AracodePeru',
    'database': 'api_ruc'
}

# Decorador para restringir acceso solo a localhost
def local_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.remote_addr != '127.0.0.1':
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None

def determinar_tipo_persona(ruc):
    """Determina el tipo de persona basado en los primeros dígitos del RUC"""
    if not ruc or len(ruc) < 2:
        return "DESCONOCIDO"
    
    primeros_digitos = ruc[:2]
    
    if primeros_digitos == "10":
        return "PERSONA NATURAL"
    elif primeros_digitos == "20":
        return "PERSONA JURÍDICA"
    elif primeros_digitos == "15":
        return "PERSONA NATURAL EXTRANJERA"
    elif primeros_digitos == "16":
        return "PERSONA JURÍDICA EXTRANJERA"
    elif primeros_digitos == "17":
        return "EMBAJADAS Y ORGANISMOS INTERNACIONALES"
    else:
        return "OTRO TIPO"

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar el estado del servicio"""
    return jsonify({
        'status': 'active',
        'service': 'API de Consulta RUC/DNI',
        'version': '1.0.0',
        'database': 'connected' if get_db_connection() else 'disconnected'
    })

@app.route('/help', methods=['GET'])
def api_help():
    """Endpoint de ayuda con documentación de la API"""
    help_info = {
        'api_name': 'API de Consulta RUC/DNI',
        'description': 'API para consultar información de contribuyentes peruanos',
        'endpoints': [
            {
                'path': '/health',
                'method': 'GET',
                'description': 'Verifica el estado del servicio',
                'example_response': {
                    'status': 'active',
                    'service': 'API de Consulta RUC/DNI',
                    'version': '1.0.0',
                    'database': 'connected'
                }
            },
            {
                'path': '/help',
                'method': 'GET',
                'description': 'Muestra esta ayuda con documentación de la API',
                'example_response': 'Documentación completa de todos los endpoints'
            },
            {
                'path': '/consulta-ruc',
                'method': 'GET',
                'description': 'Consulta información por RUC',
                'parameters': {
                    'ruc': 'Número de RUC a consultar (11 dígitos)'
                },
                'example_request': '/consulta-ruc?ruc=20123456789',
                'example_response': {
                    'ruc': '20123456789',
                    'nombre_o_razon_social': 'EMPRESA EJEMPLO SAC',
                    'estado_contribuyente': 'ACTIVO',
                    'tipo_persona': 'PERSONA JURÍDICA'
                }
            },
            {
                'path': '/consulta-dni',
                'method': 'GET',
                'description': 'Consulta información por DNI',
                'parameters': {
                    'dni': 'Número de DNI a consultar (8 dígitos)'
                },
                'example_request': '/consulta-dni?dni=12345678',
                'example_response': {
                    'dni': '12345678',
                    'ruc': '10123456789',
                    'nombre_completo': 'PEREZ GOMEZ JUAN CARLOS',
                    'estado_contribuyente': 'ACTIVO',
                    'tipo_persona': 'PERSONA NATURAL'
                }
            }
        ],
        'tipos_persona': {
            '10': 'PERSONA NATURAL',
            '15': 'PERSONA NATURAL EXTRANJERA',
            '20': 'PERSONA JURÍDICA',
            '16': 'PERSONA JURÍDICA EXTRANJERA',
            '17': 'EMBAJADAS Y ORGANISMOS INTERNACIONALES',
            'otros': 'OTRO TIPO'
        },
        'notes': [
            'Todas las rutas (excepto /health y /help) requieren acceso desde localhost',
            'Los códigos de estado HTTP indican el resultado de la operación'
        ]
    }
    return jsonify(help_info)

@app.route('/consulta-ruc', methods=['GET'])
################################################################@local_only
def consulta_ruc():
    ruc = request.args.get('ruc')
    
    if not ruc:
        return jsonify({'error': 'El parámetro RUC es requerido'}), 400
    
    # Validar que el RUC tenga 11 dígitos
    if not ruc.isdigit() or len(ruc) != 11:
        return jsonify({'error': 'RUC debe tener exactamente 11 dígitos numéricos'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Error de conexión a la base de datos'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT c.ruc, c.nombre_o_razon_social, e.descripcion as estado_contribuyente
        FROM contribuyentes c
        JOIN estados_contribuyente e ON c.estado_del_contribuyente = e.id
        WHERE c.ruc = %s
        """
        cursor.execute(query, (ruc,))
        empresa = cursor.fetchone()
        
        if empresa is None:
            return jsonify({'error': 'RUC no encontrado'}), 404
        
        # Determinar tipo de persona
        tipo_persona = determinar_tipo_persona(empresa['ruc'])
        
        response = {
            'ruc': empresa['ruc'],
            'nombre_o_razon_social': empresa['nombre_o_razon_social'],
            'estado_contribuyente': empresa['estado_contribuyente'],
            'tipo_persona': tipo_persona
        }
        
        return jsonify(response)
        
    except Error as e:
        return jsonify({'error': f'Error en la base de datos: {str(e)}'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/consulta-dni', methods=['GET'])
###############################################################@local_only
def consulta_dni():
    dni = request.args.get('dni')
    
    if not dni:
        return jsonify({'error': 'El parámetro DNI es requerido'}), 400
    
    # Validar que el DNI tenga 8 dígitos
    if not dni.isdigit() or len(dni) != 8:
        return jsonify({'error': 'DNI debe tener exactamente 8 dígitos numéricos'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Error de conexión a la base de datos'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Consulta para buscar el DNI (prefijo 10 + DNI)
        query = """
        SELECT c.ruc, c.nombre_o_razon_social, e.descripcion as estado_contribuyente
        FROM contribuyentes c
        JOIN estados_contribuyente e ON c.estado_del_contribuyente = e.id
        WHERE c.ruc LIKE %s
        LIMIT 1
        """
        cursor.execute(query, (f"10{dni}%",))
        persona = cursor.fetchone()
        
        if persona is None:
            return jsonify({'error': 'DNI no encontrado'}), 404
        
        # Determinar tipo de persona (siempre será PERSONA NATURAL para DNI)
        tipo_persona = determinar_tipo_persona(persona['ruc'])
        
        response = {
            'dni': dni,
            'ruc': persona['ruc'],
            'nombre_completo': persona['nombre_o_razon_social'],
            'estado_contribuyente': persona['estado_contribuyente'],
            'tipo_persona': tipo_persona
        }
        
        return jsonify(response)
        
    except Error as e:
        return jsonify({'error': f'Error en la base de datos: {str(e)}'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5002, debug=True)