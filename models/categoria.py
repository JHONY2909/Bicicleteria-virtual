from flask_sqlalchemy import SQLAlchemy
from extensions import db  # Importar db desde extensions.py

class Categoria(db.Model):
    __tablename__ = 'categorias'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relación con Subcategoria
    subcategorias = db.relationship('Subcategoria', backref='categoria', lazy=True)

    def __repr__(self):
        return f'<Categoria {self.nombre}>'