from . import db

class Producto(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nombre = db.Column(
        db.String(150),
        nullable=False
    )

    descripcion = db.Column(
        db.Text
    )

    precio = db.Column(
        db.Float,
        nullable=False
    )

    stock = db.Column(
        db.Integer,
        default=0
    )

    imagen = db.Column(
        db.String(200)
    )


    resenas = db.relationship(
        "Resena",
        backref="producto",
        cascade="all, delete-orphan"
    )