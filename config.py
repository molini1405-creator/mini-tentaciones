import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:

    SECRET_KEY = os.environ.get(
        'SECRET_KEY',
        'mini_tentaciones_super_secreta'
    )

    DATABASE_URL = os.environ.get('DATABASE_URL')

    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = (
            f'sqlite:///{os.path.join(BASE_DIR, "catalogo.db")}'
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(
        BASE_DIR,
        'static',
        'uploads'
    )

    # ===== EMAIL =====
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True

    # PONÉ TU GMAIL
    MAIL_USERNAME = 'mini.tentaciones.ok@gmail.com'

    # PONÉ LA CONTRASEÑA DE APLICACIÓN
    MAIL_PASSWORD = 'sgvf qxuz sxzg xcul'

    MAIL_DEFAULT_SENDER = 'mini.tentaciones.ok@gmail.com'