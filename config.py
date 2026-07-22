import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:

    SECRET_KEY = 'tu_clave_super_secreta'

    SQLALCHEMY_DATABASE_URI = (
        f'sqlite:///{os.path.join(BASE_DIR, "catalogo.db")}'
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(
        BASE_DIR,
        'static',
        'uploads'
    )