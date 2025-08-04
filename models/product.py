from extensions import db
from models.subcategoria import Subcategoria

class Product(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255))
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    url_imagen = db.Column(db.String(255))
    subcategoria_id = db.Column(db.Integer, db.ForeignKey('subcategorias.id'), nullable=False)

    subcategoria = db.relationship('Subcategoria', back_populates='productos')

    def __repr__(self):
        return f'<Product {self.nombre}>'