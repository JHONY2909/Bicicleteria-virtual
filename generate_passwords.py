from werkzeug.security import generate_password_hash

# Lista de contraseñas para los usuarios iniciales
passwords = {
    'admin': 'contraseña_admin123',
    'cliente1': 'contraseña_cliente123',
    'vendedor1': 'contraseña_vendedor123'
}

# Generar y mostrar las contraseñas hasheadas
for username, password in passwords.items():
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    print(f"Usuario: {username}, Contraseña hasheada: {hashed_password}")