from flask import Blueprint, render_template, request
from models.product import Product
from models.categoria import Categoria
from models.subcategoria import Subcategoria
from extensions import db
from sqlalchemy import or_

products_bp = Blueprint('products', __name__)

@products_bp.route('/catalog')
def catalog():
    search_query = request.args.get('search', '').strip()
    selected_category_id = request.args.get('category_id', '')
    selected_subcategory_id = request.args.get('subcategory_id', '')

    query = Product.query

    # Aplicar filtro de búsqueda
    if search_query:
        query = query.filter(or_(
            Product.nombre.ilike(f'%{search_query}%'),
            Product.descripcion.ilike(f'%{search_query}%')
        ))

    # Aplicar filtro de categoría/subcategoría
    if selected_subcategory_id:
        query = query.filter_by(subcategoria_id=selected_subcategory_id)
    elif selected_category_id:
        query = query.join(Product.subcategoria).join(Subcategoria.categoria).filter(Categoria.id == selected_category_id)

    products = query.all()
    categories = Categoria.query.all()
    subcategories = Subcategoria.query.all()

    return render_template('catalog.html', products=products, categories=categories, subcategories=subcategories, selected_category_id=selected_category_id, selected_subcategory_id=selected_subcategory_id)