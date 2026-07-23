from flask import Flask, render_template, session, redirect, url_for, request, flash
from config import Config
from models import db


from models.usuario import Usuario
from models.producto import Producto
from models.pedido import Pedido
from models.item_pedido import ItemPedido

from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.security import generate_password_hash, check_password_hash

import os
import webbrowser
from threading import Timer
from urllib.parse import quote

from flask_mail import Mail, Message
from threading import Thread
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

mail = Mail(app)
def enviar_email_async(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
            print('EMAIL ENVIADO CORRECTAMENTE')
        except Exception as e:
            print('ERROR AL ENVIAR EMAIL:', e)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])


# =========================
# FLASK LOGIN
# =========================

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = 'login'


@login_manager.user_loader
def cargar_usuario(id):
    return Usuario.query.get(int(id))


# =========================
# ABRIR NAVEGADOR
# =========================

def abrir_navegador():
    webbrowser.open(
        'http://127.0.0.1:5000'
    )


# =========================
# CARRITO
# =========================

def obtener_carrito():

    if 'carrito' not in session:
        session.pop('carrito', None)
        session.modified = True

    return session['carrito']

# =========================
# MIS PEDIDOS (CLIENTE)
# =========================

@app.route('/mis-pedidos')
@login_required
def mis_pedidos():

    pedidos = Pedido.query.filter_by(
        usuario_id=current_user.id
    ).order_by(
        Pedido.fecha.desc()
    ).all()

    return render_template(
        'mis_pedidos.html',
        pedidos=pedidos
    )
# =========================
# REGISTRO CLIENTES
# =========================

@app.route('/registro', methods=['GET', 'POST'])
def registro():

    if request.method == 'POST':

        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        confirmar = request.form['confirmar_password']

        # Validar que coincidan
        if password != confirmar:
            flash(
                'Las contraseñas no coinciden',
                'danger'
            )
            return redirect(url_for('registro'))

        # Validar longitud
        if len(password) < 6:
            flash(
                'La contraseña debe tener al menos 6 caracteres',
                'danger'
            )
            return redirect(url_for('registro'))

        # Verificar email existente
        usuario_existente = Usuario.query.filter_by(
            email=email
        ).first()

        if usuario_existente:
            flash(
                'Ya existe una cuenta con ese email',
                'danger'
            )
            return redirect(url_for('registro'))

        # Crear usuario
        nuevo_usuario = Usuario(
            nombre=nombre,
            email=email,
            password=generate_password_hash(password)
        )

        db.session.add(nuevo_usuario)
        db.session.commit()

        flash(
            'Cuenta creada correctamente. Ahora podés iniciar sesión.',
            'success'
        )

        return redirect(url_for('login'))

    return render_template('registro.html')

# =========================
# CAMBIAR CONTRASEÑA
# =========================

@app.route('/cambiar-password', methods=['GET', 'POST'])
@login_required
def cambiar_password():

    if request.method == 'POST':

        actual = request.form['actual']
        nueva = request.form['nueva']
        confirmar = request.form['confirmar']

        # Verificar contraseña actual
        if not check_password_hash(current_user.password, actual):
            flash(
                'La contraseña actual es incorrecta',
                'danger'
            )
            return redirect(url_for('cambiar_password'))

        # Verificar coincidencia
        if nueva != confirmar:
            flash(
                'Las nuevas contraseñas no coinciden',
                'danger'
            )
            return redirect(url_for('cambiar_password'))

        # Verificar longitud
        if len(nueva) < 6:
            flash(
                'La nueva contraseña debe tener al menos 6 caracteres',
                'danger'
            )
            return redirect(url_for('cambiar_password'))

        # Guardar nueva contraseña
        current_user.password = generate_password_hash(nueva)

        db.session.commit()

        flash(
            'Contraseña actualizada correctamente',
            'success'
        )

        return redirect(url_for('catalogo'))

    return render_template('cambiar_password.html')

# =========================
# OLVIDÉ MI CONTRASEÑA
# =========================

@app.route('/olvide-password', methods=['GET', 'POST'])
def olvide_password():

    if request.method == 'POST':

        email = request.form['email']

        usuario = Usuario.query.filter_by(
            email=email
        ).first()

        print()
        print('EMAIL INGRESADO:', email)
        print('USUARIO ENCONTRADO:', usuario)
        print()

        if usuario:

            try:

                token = serializer.dumps(
                    usuario.email,
                    salt='reset-password'
                )

                enlace = url_for(
                    'reset_password',
                    token=token,
                    _external=True
                )

                print('ENLACE:', enlace)

                msg = Message(
                    'Recuperar contraseña - Mini Tentaciones',
                    recipients=[usuario.email]
                )

                msg.body = f'''
Hola {usuario.nombre}

Hacé clic en este enlace para restablecer tu contraseña en Mini tentaciones 🍩:

{enlace}
'''

                Thread(
    target=enviar_email_async,
    args=(app, msg)
).start()

                print('EMAIL ENVIADO CORRECTAMENTE')

            except Exception as e:

                print('ERROR AL ENVIAR EMAIL:')
                print(e)

        flash(
            'Si el correo existe, enviamos un enlace de recuperación.',
            'success'
        )

        return redirect(url_for('login'))

    return render_template('olvide_password.html')

@app.route('/debug-mail')
def debug_mail():

    return {
        'server': app.config.get('MAIL_SERVER'),
        'port': app.config.get('MAIL_PORT'),
        'tls': app.config.get('MAIL_USE_TLS'),
        'ssl': app.config.get('MAIL_USE_SSL'),
        'username': app.config.get('MAIL_USERNAME'),
        'password_loaded': bool(app.config.get('MAIL_PASSWORD'))
    }

# =========================
# RESET PASSWORD
# =========================

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):

    try:

        email = serializer.loads(
            token,
            salt='reset-password',
            max_age=3600
        )

    except:
        flash(
            'El enlace es inválido o ya venció',
            'danger'
        )
        return redirect(url_for('login'))

    usuario = Usuario.query.filter_by(
        email=email
    ).first_or_404()

    if request.method == 'POST':

        password = request.form['password']
        confirmar = request.form['confirmar']

        if password != confirmar:
            flash(
                'Las contraseñas no coinciden',
                'danger'
            )
            return redirect(request.url)

        usuario.password = generate_password_hash(password)

        db.session.commit()

        flash(
            'Contraseña actualizada correctamente',
            'success'
        )

        return redirect(url_for('login'))

    return render_template('reset_password.html')
# =========================
# LOGIN
# =========================

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        usuario = Usuario.query.filter_by(
            email=email
        ).first()


        if usuario and check_password_hash(
            usuario.password,
            password
        ):

            login_user(usuario)

            if usuario.es_admin:
                return redirect(
                    url_for('admin')
                )

            return redirect(
                url_for('catalogo')
            )


        return "Usuario o contraseña incorrectos"


    return render_template(
        'login.html'
    )


@app.route('/logout')
@login_required
def logout():

    logout_user()

    return redirect(url_for('catalogo', agregado=1))




# =========================
# CATÁLOGO
# =========================

@app.route('/')
def catalogo():

    productos = Producto.query.all()

    return render_template(
        'catalogo.html',
        productos=productos
    )

# =========================
# VER CARRITO
# =========================

@app.route('/carrito')
def carrito():

    carrito = obtener_carrito()

    productos_carrito = []
    total = 0


    for producto_id, cantidad in carrito.items():

        producto = Producto.query.get(
            int(producto_id)
        )

        if producto:

            subtotal = producto.precio * cantidad

            total += subtotal


            productos_carrito.append({
                'producto': producto,
                'cantidad': cantidad,
                'subtotal': subtotal
            })


    return render_template(
        'carrito.html',
        productos_carrito=productos_carrito,
        total=total
    )


# =========================
# AGREGAR AL CARRITO
# =========================

@app.route('/agregar-carrito/<int:id>', methods=['POST'])
def agregar_carrito(id):

    carrito = obtener_carrito()

    id_str = str(id)


    if id_str in carrito:
        carrito[id_str] += 1

    else:
        carrito[id_str] = 1


    session['carrito'] = carrito

    session.modified = True


    return redirect(
        url_for('catalogo')
    )


# =========================
# SUMAR
# =========================

@app.route('/sumar/<int:id>')
def sumar(id):

    carrito = obtener_carrito()

    id_str = str(id)


    if id_str in carrito:
        carrito[id_str] += 1


    session.modified = True


    return redirect(
        url_for('carrito')
    )


# =========================
# RESTAR
# =========================

@app.route('/restar/<int:id>')
def restar(id):

    carrito = obtener_carrito()

    id_str = str(id)


    if id_str in carrito:

        carrito[id_str] -= 1


        if carrito[id_str] <= 0:
            carrito.pop(id_str)


    session.modified = True


    return redirect(
        url_for('carrito')
    )


# =========================
# ELIMINAR
# =========================

@app.route('/eliminar/<int:id>')
def eliminar(id):

    carrito = obtener_carrito()

    carrito.pop(
        str(id),
        None
    )


    session.modified = True


    return redirect(
        url_for('carrito')
    )


# =========================
# CONFIRMAR PEDIDO
# =========================

@app.route('/confirmar-pedido', methods=['POST'])
@login_required
def confirmar_pedido():

    carrito = obtener_carrito()

    if not carrito:
        return redirect(url_for('carrito'))

    total = 0

    # Crear pedido
    pedido = Pedido(
        usuario_id=current_user.id,
        estado='pendiente'
    )

    db.session.add(pedido)
    db.session.flush()

    # Texto para WhatsApp
    mensaje = f"Hola Mini Tentaciones 🍩%0A%0A"
    mensaje += f"Quiero confirmar mi pedido #{pedido.id}%0A%0A"

    # Guardar items
    for producto_id, cantidad in carrito.items():

        producto = Producto.query.get(int(producto_id))

        if producto and producto.stock >= cantidad:

            subtotal = producto.precio * cantidad
            total += subtotal

            # Descontar stock
            producto.stock -= cantidad

            item = ItemPedido(
                pedido_id=pedido.id,
                producto_id=producto.id,
                cantidad=cantidad,
                precio_unitario=producto.precio
            )

            db.session.add(item)

            # Agregar al mensaje
            mensaje += f"🍩 {producto.nombre} x{cantidad} - ${subtotal:,.0f}%0A"

    pedido.total = total

    db.session.commit()

    # Vaciar carrito
    session['carrito'] = {}

    # Final del mensaje
    mensaje += f"%0ATotal: ${total:,.0f}%0A"
    mensaje += f"Cliente: {current_user.nombre}"

    # TU NÚMERO DE WHATSAPP
    numero = "5492612070017"

    # URL de WhatsApp
    whatsapp_url = f"https://wa.me/{numero}?text={mensaje}"

    return redirect(whatsapp_url)

# =========================
# ADMIN PRODUCTOS
# =========================

@app.route('/admin')
@login_required
def admin():

    if not current_user.es_admin:

        return "Acceso denegado"


    productos = Producto.query.all()


    return render_template(
        'admin_productos.html',
        productos=productos
    )


@app.route('/admin/agregar', methods=['POST'])
@login_required
def admin_agregar():

    if not current_user.es_admin:

        return "Acceso denegado"


    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio = request.form['precio']
    stock = request.form['stock']


    imagen = request.files['imagen']

    nombre_imagen = None


    if imagen and imagen.filename:

        nombre_imagen = imagen.filename

        ruta = os.path.join(
            app.config['UPLOAD_FOLDER'],
            nombre_imagen
        )

        imagen.save(ruta)



    producto = Producto(
        nombre=nombre,
        descripcion=descripcion,
        precio=float(precio),
        stock=int(stock),
        imagen=nombre_imagen
    )


    db.session.add(producto)

    db.session.commit()


    return redirect(
        url_for('admin')
    )
# =========================
# VER PEDIDOS ADMIN
# =========================

@app.route('/admin/pedidos')
@login_required
def admin_pedidos():

    if not current_user.es_admin:
        return "Acceso denegado"


    pedidos = Pedido.query.order_by(
        Pedido.fecha.desc()
    ).all()


    return render_template(
        'admin_pedidos.html',
        pedidos=pedidos
    )

@app.route('/admin/pedido/<int:id>/estado', methods=['POST'])
@login_required
def cambiar_estado_pedido(id):

    if not current_user.es_admin:
        return 'Acceso denegado'

    pedido = Pedido.query.get_or_404(id)

    nuevo_estado = request.form['estado']

    pedido.estado = nuevo_estado

    db.session.commit()

    return redirect(url_for('admin_pedidos'))

# =========================
# EDITAR PRODUCTO
# =========================

@app.route('/admin/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_editar(id):

    if not current_user.es_admin:
        return 'Acceso denegado'

    producto = Producto.query.get_or_404(id)

    if request.method == 'POST':

        producto.nombre = request.form['nombre']
        producto.descripcion = request.form['descripcion']
        producto.precio = float(request.form['precio'])
        producto.stock = int(request.form['stock'])

        # Si sube una nueva imagen
        imagen = request.files['imagen']

        if imagen and imagen.filename:

            nombre_imagen = imagen.filename

            ruta = os.path.join(
                app.config['UPLOAD_FOLDER'],
                nombre_imagen
            )

            imagen.save(ruta)

            producto.imagen = nombre_imagen

        db.session.commit()

        return redirect(url_for('admin'))

    return render_template(
        'editar_producto.html',
        producto=producto
    )
# =========================
# ELIMINAR PRODUCTO ADMIN
# =========================

@app.route('/admin/eliminar/<int:id>')
@login_required
def admin_eliminar(id):

    if not current_user.es_admin:

        return "Acceso denegado"


    producto = Producto.query.get(id)


    if producto:

        db.session.delete(producto)

        db.session.commit()


    return redirect(
        url_for('admin')
    )



# =========================
# CREAR BASE Y ADMIN INICIAL
# =========================

with app.app_context():

    db.create_all()


    # Crear carpeta de imágenes si no existe

    if not os.path.exists(
        app.config['UPLOAD_FOLDER']
    ):

        os.makedirs(
            app.config['UPLOAD_FOLDER']
        )


    # Crear administrador inicial

    admin_existente = Usuario.query.filter_by(
        email='admin@catalogo.com'
    ).first()


    if not admin_existente:

        admin = Usuario(

            nombre='Administrador',

            email='admin@catalogo.com',

            password=generate_password_hash(
                'admin123'
            ),

            es_admin=True
        )


        db.session.add(admin)

        db.session.commit()

with app.app_context():
    db.create_all()

# =========================
# INICIAR APP
# =========================

if __name__ == '__main__':

    Timer(
        1,
        abrir_navegador
    ).start()


    app.run(

        debug=True,

        use_reloader=False,

        host='127.0.0.1',

        port=5000

    )

