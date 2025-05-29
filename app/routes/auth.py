from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import User
from app import db, login_manager

auth_bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if not user:
            flash('Correo no encontrado', 'error')
            return redirect(url_for('auth.login'))

        if user.role != 'medico':
            flash('Acceso no autorizado', 'error')
            return redirect(url_for('auth.login'))

        if not check_password_hash(user.password, password):
            flash('Contraseña incorrecta', 'error')
            return redirect(url_for('auth.login'))

        login_user(user)
        return redirect(url_for('medico.pacientes'))

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

# 🆕 Registro exclusivo para médicos
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        existente = User.query.filter_by(email=email).first()
        if existente:
            flash('Este correo ya está registrado.', 'error')
            return redirect(url_for('auth.register'))

        user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            role='medico'
        )
        db.session.add(user)
        db.session.commit()
        flash('Médico registrado con éxito. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')
