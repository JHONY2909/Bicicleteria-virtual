from extensions import db

class Subcategoria(db.Model):
    __tablename__ = 'subcategorias'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    productos = db.relationship('Product', back_populates='subcategoria')

    def __repr__(self):
        return f'<Subcategoria {self.nombre}>'