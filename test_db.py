from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

# Definir un modelo simple para la tabla de prueba
class PruebaUsuario(db.Model):
    __tablename__ = 'prueba_usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    correo = db.Column(db.String(100), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())

def test_connection():
    with app.app_context():
        try:
            # Crear las tablas definidas en los modelos
            db.create_all()
            print("Tablas creadas correctamente.")

            # Insertar un usuario de prueba
            new_user = PruebaUsuario(
                nombre='Usuario Nuevo',
                correo='nuevo@bicicleteria.com'
            )
            db.session.add(new_user)
            db.session.commit()
            print("Usuario de prueba insertado correctamente.")

            # Consultar todos los usuarios
            users = PruebaUsuario.query.all()
            print("Usuarios en la base de datos:")
            for user in users:
                print(f"ID: {user.id}, Nombre: {user.nombre}, Correo: {user.correo}, Fecha: {user.fecha_creacion}")

        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == '__main__':
    test_connection()