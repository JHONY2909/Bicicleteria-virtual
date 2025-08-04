from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_required, current_user
from models.cart import Cart
from models.product import Product
from extensions import db

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/cart')
@login_required
def cart():
    # Obtener los productos del carrito para el usuario actual
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    products_in_cart = []
    total = 0
    for item in cart_items:
        product = Product.query.get(item.product_id)
        if product:
            products_in_cart.append({
                'id': item.id,  # ID del ítem del carrito
                'product': product,
                'quantity': item.quantity,
                'subtotal': product.precio * item.quantity
            })
            total += product.precio * item.quantity
    
    return render_template('carrito.html', cart_items=products_in_cart, total=total)

@cart_bp.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    try:
        print(f"Usuario autenticado: {current_user.is_authenticated}, Rol: {current_user.rol}")
        if current_user.rol not in ['cliente', 'vendedor']:
            print("Acceso denegado: rol no permitido")
            return jsonify({'success': False, 'message': 'Acceso denegado'}), 403
        
        product = Product.query.get_or_404(product_id)
        print(f"Producto encontrado: {product.nombre}")
        
        cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
        if cart_item:
            if cart_item.quantity + 1 > product.stock:
                print(f"No hay suficiente stock para el producto {product_id}")
                return jsonify({'success': False, 'message': 'No hay suficiente stock disponible'}), 400
            cart_item.quantity += 1
            print(f"Incrementando cantidad para el producto {product_id}: {cart_item.quantity}")
        else:
            if product.stock < 1:
                print(f"No hay suficiente stock para el producto {product_id}")
                return jsonify({'success': False, 'message': 'No hay suficiente stock disponible'}), 400
            cart_item = Cart(user_id=current_user.id, product_id=product_id, quantity=1)
            db.session.add(cart_item)
            print(f"Nuevo item en el carrito: producto {product_id}")
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Producto agregado al carrito'})
    except Exception as e:
        db.session.rollback()
        print(f"Error al agregar al carrito: {str(e)}")
        return jsonify({'success': False, 'message': f'Error al agregar al carrito: {str(e)}'}), 500

@cart_bp.route('/remove/<int:cart_item_id>', methods=['POST'])
@login_required
def remove_from_cart(cart_item_id):
    try:
        cart_item = Cart.query.filter_by(id=cart_item_id, user_id=current_user.id).first()
        if not cart_item:
            print(f"Ítem del carrito no encontrado: {cart_item_id}")
            return jsonify({'success': False, 'message': 'Ítem no encontrado en el carrito'}), 404
        
        db.session.delete(cart_item)
        db.session.commit()
        print(f"Ítem eliminado del carrito: {cart_item_id}")
        return jsonify({'success': True, 'message': 'Producto eliminado del carrito'})
    except Exception as e:
        db.session.rollback()
        print(f"Error al eliminar del carrito: {str(e)}")
        return jsonify({'success': False, 'message': f'Error al eliminar del carrito: {str(e)}'}), 500

@cart_bp.route('/increase/<int:cart_item_id>', methods=['POST'])
@login_required
def increase_quantity(cart_item_id):
    try:
        cart_item = Cart.query.filter_by(id=cart_item_id, user_id=current_user.id).first()
        if not cart_item:
            print(f"Ítem del carrito no encontrado: {cart_item_id}")
            return jsonify({'success': False, 'message': 'Ítem no encontrado en el carrito'}), 404
        
        product = Product.query.get(cart_item.product_id)
        if cart_item.quantity + 1 > product.stock:
            print(f"No hay suficiente stock para el producto {cart_item.product_id}")
            return jsonify({'success': False, 'message': 'No hay suficiente stock disponible'}), 400
        
        cart_item.quantity += 1
        db.session.commit()
        print(f"Cantidad incrementada para el ítem {cart_item_id}: {cart_item.quantity}")
        return jsonify({'success': True, 'message': 'Cantidad actualizada'})
    except Exception as e:
        db.session.rollback()
        print(f"Error al aumentar la cantidad: {str(e)}")
        return jsonify({'success': False, 'message': f'Error al actualizar la cantidad: {str(e)}'}), 500

@cart_bp.route('/decrease/<int:cart_item_id>', methods=['POST'])
@login_required
def decrease_quantity(cart_item_id):
    try:
        cart_item = Cart.query.filter_by(id=cart_item_id, user_id=current_user.id).first()
        if not cart_item:
            print(f"Ítem del carrito no encontrado: {cart_item_id}")
            return jsonify({'success': False, 'message': 'Ítem no encontrado en el carrito'}), 404
        
        if cart_item.quantity <= 1:
            db.session.delete(cart_item)
            print(f"Ítem eliminado del carrito (cantidad 0): {cart_item_id}")
        else:
            cart_item.quantity -= 1
            print(f"Cantidad disminuida para el ítem {cart_item_id}: {cart_item.quantity}")
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Cantidad actualizada'})
    except Exception as e:
        db.session.rollback()
        print(f"Error al disminuir la cantidad: {str(e)}")
        return jsonify({'success': False, 'message': f'Error al actualizar la cantidad: {str(e)}'}), 500