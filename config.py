class Config:
    SECRET_KEY = 'tu-clave-secreta'  # Cambia esto a una clave segura en producción
    SQLALCHEMY_DATABASE_URI = 'sqlite:///bicicleteria.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False