from models import db
from datetime import datetime


class Resena(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id"),
        nullable=False
    )

    estrellas = db.Column(
        db.Integer,
        nullable=False
    )

    comentario = db.Column(
        db.String(500),
        nullable=False
    )

    fecha = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    usuario = db.relationship("Usuario")