from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
from extensions import db
from werkzeug.security import generate_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        nombre_usuario = request.form['username']
        contrasena = request.form['password']
        correo = request.form['email']
        telefono = request.form.get('telefono')
        apellido = request.form.get('apellido')
        user = User.query.filter_by(nombre_usuario=nombre_usuario).first()
        if user:
            flash('El nombre de usuario ya existe', 'error')
            return redirect(url_for('auth.register'))
        user = User(
            nombre_usuario=nombre_usuario,
            contrasena=generate_password_hash(contrasena),
            correo=correo,
            telefono=telefono,
            apellido=apellido
        )
        db.session.add(user)
        db.session.commit()
        flash('Registro exitoso. Por favor, inicia sesión.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.rol == 'administrador':
            return redirect(url_for('dashboard.admin_panel'))
        elif current_user.rol in ['cliente', 'vendedor']:
            return redirect(url_for('dashboard.client_dashboard'))
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            flash('Por favor, completa todos los campos.', 'error')
            return redirect(url_for('auth.login'))
        user = User.query.filter_by(nombre_usuario=username).first()
        if user and user.check_password(password):
            login_user(user)
            if user.rol == 'administrador':
                return redirect(url_for('dashboard.admin_panel'))
            elif user.rol in ['cliente', 'vendedor']:
                return redirect(url_for('dashboard.client_dashboard'))
            return redirect(url_for('index'))
        flash('Credenciales inválidas', 'error')
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    from flask import session
    session.clear()  # Limpia toda la sesión
    return redirect(url_for('index'))