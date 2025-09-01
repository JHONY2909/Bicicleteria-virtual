from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from models.wishlist import Wishlist
from models.product import Product
from extensions import db

wishlist_bp = Blueprint('wishlist', __name__)

@wishlist_bp.route('/wishlist')
@login_required
def wishlist():
    wishlist_items = Wishlist.query.filter_by(user_id=current_user.id).all()
    products_in_wishlist = []
    for item in wishlist_items:
        product = Product.query.get(item.product_id)
        if product:
            products_in_wishlist.append(product)
    return render_template('wishlist_page.html', products=products_in_wishlist)

@wishlist_bp.route('/add_to_wishlist/<int:product_id>', methods=['POST'])
@login_required
def add_to_wishlist(product_id):
    try:
        if current_user.rol not in ['cliente', 'vendedor']:
            return jsonify({'success': False, 'message': 'Acceso denegado'}), 403
        product = Product.query.get_or_404(product_id)
        wishlist_item = Wishlist.query.filter_by(user_id=current_user.id, product_id=product_id).first()
        if wishlist_item:
            return jsonify({'success': False, 'message': 'Ya está en tu lista de deseos', 'added': True})
        new_item = Wishlist(user_id=current_user.id, product_id=product_id)
        db.session.add(new_item)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Agregado a lista de deseos', 'added': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@wishlist_bp.route('/remove_from_wishlist/<int:product_id>', methods=['POST'])
@login_required
def remove_from_wishlist(product_id):
    try:
        wishlist_item = Wishlist.query.filter_by(user_id=current_user.id, product_id=product_id).first()
        if not wishlist_item:
            return jsonify({'success': False, 'message': 'No encontrado en lista de deseos'}), 404
        db.session.delete(wishlist_item)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Eliminado de lista de deseos', 'added': False})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500