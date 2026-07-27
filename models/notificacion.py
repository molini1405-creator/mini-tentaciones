from datetime import datetime
from . import db


class Notificacion(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey('usuario.id'),
        nullable=False
    )

    pedido_id = db.Column(
        db.Integer,
        db.ForeignKey('pedido.id'),
        nullable=False
    )

    mensaje = db.Column(
        db.String(255),
        nullable=False
    )

    leida = db.Column(
        db.Boolean,
        default=False
    )

    fecha = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    usuario = db.relationship(
        'Usuario',
        backref='notificaciones'
    )

    pedido = db.relationship(
        'Pedido',
        backref='notificaciones'
    )