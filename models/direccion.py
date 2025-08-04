from flask_sqlalchemy import SQLAlchemy
from extensions import db  # Importar db desde extensions.py

class Direccion(db.Model):
    __tablename__ = 'direcciones'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    calle = db.Column(db.String(100), nullable=False)
    ciudad = db.Column(db.String(100), nullable=False)
    codigo_postal = db.Column(db.String(20))
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())