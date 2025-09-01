from extensions import db

class DetallePedido(db.Model):
    __tablename__ = 'detalles_pedidos'
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    
    producto = db.relationship('Product', backref='detalles_pedidos')
    pedido = db.relationship('Pedido', back_populates='detalles')
