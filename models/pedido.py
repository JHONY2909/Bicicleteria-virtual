from extensions import db  # Importar db desde extensions.py

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    direccion_id = db.Column(db.Integer, db.ForeignKey('direcciones.id'))
    monto_total = db.Column(db.Numeric(10, 2), nullable=False)
    metodo_pago = db.Column(db.String(20), nullable=False)
    estado = db.Column(db.String(20), default='pendiente')
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())

    usuario = db.relationship('User', backref='pedidos')
    detalles = db.relationship('DetallePedido', back_populates='pedido', lazy=True)
    direccion = db.relationship('Direccion', backref='pedidos')
