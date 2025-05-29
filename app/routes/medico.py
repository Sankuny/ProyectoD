from flask import Blueprint, render_template, request, redirect, url_for, make_response,flash
from app import db
from app.models import User, Paciente, Medicamento, TomaMedicamento, SignoVital, Cita
from datetime import datetime, date, time 
from weasyprint import HTML
from werkzeug.security import generate_password_hash
from flask_login import login_required


medico_bp = Blueprint('medico', __name__)

# 📄 Ver todos los pacientes
@medico_bp.route('/pacientes', methods=['GET', 'POST'])
def pacientes():
    if request.method == 'POST':
        data = request.form
        nuevo_user = User(
            name=data['name'],
            email=data['email'],
            password = generate_password_hash("1234"),
            role='paciente'
        )
        db.session.add(nuevo_user)
        db.session.flush()

        nuevo_paciente = Paciente(
            user_id=nuevo_user.id,
            telefono=data.get('telefono'),
            domicilio=data.get('domicilio')
        )
        db.session.add(nuevo_paciente)
        db.session.commit()

        return redirect(url_for('medico.pacientes'))

    pacientes = Paciente.query.all()
    return render_template('medico/pacientes.html', pacientes=pacientes)

# 📄 Ver detalle del paciente
@medico_bp.route('/pacientes/<int:paciente_id>')
def ver_paciente(paciente_id):
    paciente = Paciente.query.get_or_404(paciente_id)
    tomas = TomaMedicamento.query.filter_by(paciente_id=paciente_id).all()
    signos = SignoVital.query.filter_by(paciente_id=paciente_id).all()
    return render_template('medico/ver_paciente.html', paciente=paciente, tomas=tomas, signos=signos)

# ➕ Asignar medicamento a paciente
@medico_bp.route('/pacientes/<int:paciente_id>/asignar', methods=['POST'])
def asignar_medicamento(paciente_id):
    nombre = request.form['nombre']
    ingrediente = request.form['ingrediente']
    fecha_caducidad = request.form['fecha_caducidad']
    hora_str = request.form['hora']

    # Crear el medicamento
    medicamento = Medicamento(
        nombre=nombre,
        ingrediente=ingrediente,
        fecha_caducidad=datetime.strptime(fecha_caducidad, "%Y-%m-%d").date()
    )
    db.session.add(medicamento)
    db.session.flush()  # Para obtener su ID

    # Crear una toma para hoy
    toma = TomaMedicamento(
        paciente_id=paciente_id,
        medicamento_id=medicamento.id,
        fecha=date.today(),
        hora=datetime.strptime(hora_str, "%Y-%m-%dT%H:%M").time(),
        fue_tomado=False
    )
    db.session.add(toma)
    db.session.commit()

    return redirect(url_for('medico.ver_paciente', paciente_id=paciente_id))

# 📅 Ver citas médicas
@medico_bp.route('/citas')
def citas():
    citas = Cita.query.all()
    return render_template('medico/citas.html', citas=citas)

@medico_bp.route('/pacientes/<int:paciente_id>/pdf')
def generar_pdf(paciente_id):
    paciente = Paciente.query.get_or_404(paciente_id)
    tomas = TomaMedicamento.query.filter_by(paciente_id=paciente_id).all()
    signos = SignoVital.query.filter_by(paciente_id=paciente_id).all()

    html = render_template('medico/pdf_paciente.html', paciente=paciente, tomas=tomas, signos=signos)
    pdf = HTML(string=html).write_pdf()

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=paciente_{paciente_id}.pdf'
    return response


@medico_bp.route('/citas/nueva', methods=['GET', 'POST'])
@login_required
def nueva_cita():
    if request.method == 'POST':
        paciente_id = request.form['paciente_id']
        especialidad = request.form['especialidad']
        doctor = request.form['doctor']
        fecha = request.form['fecha']
        hora = request.form['hora']
        diagnostico = request.form.get('diagnostico')

        nueva_cita = Cita(
            paciente_id=paciente_id,
            especialidad=especialidad,
            doctor=doctor,
            fecha=fecha,
            hora=hora,
            diagnostico=diagnostico
        )
        db.session.add(nueva_cita)
        db.session.commit()
        flash('Cita creada exitosamente.', 'success')
        return redirect(url_for('medico.citas'))

    pacientes = Paciente.query.all()
    return render_template('medico/nueva_cita.html', pacientes=pacientes)
