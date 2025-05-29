from flask import Blueprint, jsonify, request, current_app
from app.models import Medicamento, TomaMedicamento as Toma, SignoVital, Cita, User
from app import db
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta
import jwt
from functools import wraps

api_paciente_bp = Blueprint('api_paciente', __name__)

# 🔐 Decorador para validar el token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            bearer = request.headers['Authorization']
            token = bearer.split(" ")[1] if " " in bearer else bearer

        if not token:
            return jsonify({'error': 'Token requerido'}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            user = User.query.get(data['user_id'])
            if not user or not user.paciente:
                return jsonify({'error': 'Usuario inválido'}), 401
            request.current_user = user
        except Exception:
            return jsonify({'error': 'Token inválido o expirado'}), 401

        return f(*args, **kwargs)
    return decorated

@api_paciente_bp.route('/login', methods=['POST'])
def login_paciente():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No se recibió JSON válido'}), 400

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Faltan datos'}), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 401

        if not check_password_hash(user.password, password):
            return jsonify({'error': 'Contraseña incorrecta'}), 401

        if not hasattr(user, 'paciente') or not user.paciente:
            return jsonify({'error': 'El usuario no es un paciente'}), 401

        payload = {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email
            }
        })

    except Exception as e:
        current_app.logger.error(f"Error en login_paciente: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500


# 📄 Ver perfil del paciente
@api_paciente_bp.route('/perfil', methods=['GET'])
@token_required
def perfil():
    user = request.current_user
    return jsonify({
        'name': user.name,
        'email': user.email,
        'telefono': user.paciente.telefono,
        'domicilio': user.paciente.domicilio
    })

# 💊 Ver medicamentos activos del paciente
@api_paciente_bp.route('/medicamentos', methods=['GET'])
@token_required
def get_medicamentos():
    user = request.current_user
    medicamentos = Medicamento.query.filter_by(paciente_id=user.paciente.id).all()
    return jsonify([
        {
            "id": m.id,
            "nombre": m.nombre,
            "ingrediente": m.ingrediente,
            "fecha_caducidad": m.fecha_caducidad.isoformat() if m.fecha_caducidad else None
        } for m in medicamentos
    ])

# ⏰ Ver historial de tomas
@api_paciente_bp.route('/tomas', methods=['GET'])
@token_required
def get_tomas():
    user = request.current_user
    tomas = Toma.query.filter_by(paciente_id=user.paciente.id).order_by(Toma.fecha.desc()).all()
    return jsonify([
        {
            "medicamento": toma.medicamento.nombre,
            "fecha": toma.fecha.isoformat(),
            "hora": toma.hora.strftime('%H:%M'),
            "fue_tomado": toma.fue_tomado
        } for toma in tomas
    ])

# 📅 Ver citas médicas
@api_paciente_bp.route('/citas', methods=['GET'])
@token_required
def get_citas():
    user = request.current_user
    citas = Cita.query.filter_by(paciente_id=user.paciente.id).order_by(Cita.fecha.desc()).all()
    return jsonify([
        {
            "fecha": cita.fecha.isoformat(),
            "descripcion": cita.descripcion or ""
        } for cita in citas
    ])

# ❤️ Ver signos vitales
@api_paciente_bp.route('/signos', methods=['GET'])
@token_required
def get_signos():
    user = request.current_user
    signos = SignoVital.query.filter_by(paciente_id=user.paciente.id).order_by(SignoVital.fecha.desc()).all()
    return jsonify([
        {
            "tipo": s.tipo,
            "valor": s.valor,
            "fecha": s.fecha.isoformat()
        } for s in signos
    ])

# ➕ Registrar nuevo signo vital
@api_paciente_bp.route('/signos', methods=['POST'])
@token_required
def registrar_signos():
    user = request.current_user
    data = request.json
    tipo = data.get('tipo')
    valor = data.get('valor')

    if not tipo or not valor:
        return jsonify({"error": "Faltan datos"}), 400

    nuevo_signo = SignoVital(
        paciente_id=user.paciente.id,
        tipo=tipo,
        valor=valor,
        fecha=datetime.utcnow()
    )
    db.session.add(nuevo_signo)
    db.session.commit()

    return jsonify({"mensaje": "Signo vital registrado exitosamente."}), 201
