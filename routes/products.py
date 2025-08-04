from flask import Blueprint, render_template
from models.product import Product
from extensions import db

products_bp = Blueprint('products', __name__)

@products_bp.route('/catalog')
def catalog():
    products = Product.query.all()
    return render_template('catalog.html', products=products)