from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    load_dotenv()  # Carga variables desde .env

    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'devkey')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///medicamentos.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Importar modelos (para Flask-Migrate)
    from app import models

    # Registrar rutas con Blueprints
    from app.routes.public import public_bp
    from app.routes.auth import auth_bp
    from app.routes.medico import medico_bp
    from app.routes.api_paciente import api_paciente_bp
    
    app.register_blueprint(api_paciente_bp, url_prefix='/api/paciente')
    app.register_blueprint(public_bp)  # Sin prefijo: maneja "/"
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(medico_bp, url_prefix='/medico')

    return app
