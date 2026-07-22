from datetime import datetime
from . import db

class Pedido(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey('usuario.id')
    )

    fecha = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    estado = db.Column(
        db.String(20),
        default='pendiente'
    )

    total = db.Column(
        db.Float,
        default=0
    )

    # RELACIONES
    usuario = db.relationship(
        'Usuario',
        backref='pedidos'
    )

    items = db.relationship(
        'ItemPedido',
        backref='pedido',
        cascade='all, delete-orphan'
    )