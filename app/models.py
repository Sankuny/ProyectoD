from app import db
from flask_login import UserMixin
from datetime import date, datetime

# --------------------
# Usuario general (paciente o médico)
# --------------------
class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'paciente' o 'medico'

    paciente = db.relationship('Paciente', backref='user', uselist=False)

# --------------------
# Paciente (datos adicionales)
# --------------------
class Paciente(db.Model):
    __tablename__ = 'paciente'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    telefono = db.Column(db.String(20))
    domicilio = db.Column(db.String(200))

# --------------------
# Medicamento
# --------------------
class Medicamento(db.Model):
    __tablename__ = 'medicamento'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    ingrediente = db.Column(db.String(100), nullable=False)
    fecha_caducidad = db.Column(db.Date, default=date.today)

# --------------------
# Toma de medicamento
# --------------------
class TomaMedicamento(db.Model):
    __tablename__ = 'toma_medicamento'
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)
    medicamento_id = db.Column(db.Integer, db.ForeignKey('medicamento.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    fue_tomado = db.Column(db.Boolean, default=False)

  
    medicamento = db.relationship('Medicamento', backref='tomas')

# --------------------
# Signos vitales
# --------------------
class SignoVital(db.Model):
    __tablename__ = 'signo_vital'

    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)
    tipo = db.Column(db.String(50))  # presión, glucosa, etc.
    valor = db.Column(db.String(50))
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

# --------------------
# Cita médica
# --------------------
class Cita(db.Model):
    __tablename__ = 'cita'

    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    especialidad = db.Column(db.String(100))
    diagnostico = db.Column(db.Text)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
