from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .usuario import Usuario
from .producto import Producto
from .pedido import Pedido
from .item_pedido import ItemPedido
from .resena import Resena