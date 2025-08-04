from flask import Flask, redirect, request, url_for, render_template, jsonify
from flask_login import LoginManager, current_user
from extensions import db, migrate
from routes.auth import auth_bp
from routes.products import products_bp
from routes.cart import cart_bp
from routes.dashboard import dashboard_bp
from models.product import Product
from models.categoria import Categoria
from models.subcategoria import Subcategoria
from models.user import User
from datetime import timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bicicleteria.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)

db.init_app(app)
migrate.init_app(app, db)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(products_bp, url_prefix='/products')
app.register_blueprint(cart_bp, url_prefix='/cart')
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')


@app.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        if current_user.rol == 'administrador':
            return redirect(url_for('dashboard.admin_panel'))
        elif current_user.rol in ['cliente', 'vendedor']:
            return redirect(url_for('dashboard.client_dashboard'))
    categories = Categoria.query.all()
    subcategories = Subcategoria.query.all()
    products = Product.query.all()
    selected_category_id = request.form.get('category_id') if request.method == 'POST' else None
    selected_subcategory_id = request.form.get('subcategory_id') if request.method == 'POST' else None
    if request.method == 'POST':
        print(f"Received category_id: {selected_category_id}, subcategory_id: {selected_subcategory_id}")
        if selected_subcategory_id and selected_subcategory_id != "":
            products = Product.query.filter_by(subcategoria_id=selected_subcategory_id).all()
        elif selected_category_id and selected_category_id != "":
            products = Product.query.join(Product.subcategoria).join(Subcategoria.categoria).filter(Categoria.id == selected_category_id).all()
        else:
            products = Product.query.all()
    return render_template('catalog.html', products=products, categories=categories, subcategories=subcategories, selected_category_id=selected_category_id, selected_subcategory_id=selected_subcategory_id)

@app.route('/subcategories/<int:category_id>')
def get_subcategories(category_id):
    subcategories = Subcategoria.query.filter_by(categoria_id=category_id).all()
    return jsonify([{'id': subcat.id, 'nombre': subcat.nombre} for subcat in subcategories])

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

if __name__ == '__main__':
    app.run(debug=True)