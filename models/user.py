from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from extensions import db  # Importar db desde extensions.py
from werkzeug.security import check_password_hash

from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(50), unique=True, nullable=False)
    contrasena = db.Column(db.String(128), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    apellido = db.Column(db.String(50))
    rol = db.Column(db.String(20), nullable=False, default='cliente')

    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.contrasena, password)

    def get_id(self):
        return str(self.id)  # Debe devolver una cadena