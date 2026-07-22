from . import db

class ItemPedido(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    pedido_id = db.Column(
        db.Integer,
        db.ForeignKey('pedido.id')
    )

    producto_id = db.Column(
        db.Integer,
        db.ForeignKey('producto.id')
    )

    cantidad = db.Column(
        db.Integer,
        default=1
    )

    precio_unitario = db.Column(db.Float)

    # RELACIÓN
    producto = db.relationship(
        'Producto',
        backref='items_pedido'
    )