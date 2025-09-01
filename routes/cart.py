from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request, make_response
from flask_login import login_required, current_user
from models.detalle_pedido import DetallePedido
from models.direccion import Direccion
from models.pedido import Pedido
from models.cart import Cart
from models.product import Product
from reportlab.lib.pagesizes import letter
from io import BytesIO
from extensions import db
from reportlab.pdfgen import canvas
import datetime

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
            cart_item = Cart(user_id=current_user.id, product_id=product_id)
            db.session.add(cart_item)
            print(f"Agregando nuevo ítem al carrito: {product_id}")
        
        db.session.commit()
        print(f"Ítem agregado al carrito: {product_id}")
        return jsonify({'success': True, 'message': 'Agregado al carrito'})
    except Exception as e:
        db.session.rollback()
        print(f"Error al agregar al carrito: {str(e)}")
        return jsonify({'success': False, 'message': f'Error al agregar al carrito: {str(e)}'}), 500

@cart_bp.route('/remove_from_cart/<int:cart_item_id>', methods=['POST'])
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
        return jsonify({'success': True, 'message': 'Eliminado del carrito'})
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

@cart_bp.route('/get_cart_count', methods=['GET'])
@login_required
def get_cart_count():
    cart_items = Cart.query.filter_by(user_id=current_user.id).count()
    return jsonify({'count': cart_items})

@cart_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if current_user.rol != 'cliente':
        flash('Acceso denegado', 'danger')
        return redirect(url_for('dashboard.client_dashboard'))
    
    # Obtener carrito
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash('Carrito vacío', 'warning')
        return redirect(url_for('cart.cart'))
    
    total = sum(Product.query.get(item.product_id).precio * item.quantity for item in cart_items)
    
    # Direcciones existentes del usuario
    direcciones = Direccion.query.filter_by(usuario_id=current_user.id).all()
    
    if request.method == 'POST':
        direccion_id = request.form.get('direccion_id')
        calle = request.form.get('calle')
        ciudad = request.form.get('ciudad')
        codigo_postal = request.form.get('codigo_postal')
        metodo_pago = request.form.get('metodo_pago')
        
        if not direccion_id and (not calle or not ciudad):
            flash('Debes proporcionar una dirección', 'danger')
            return render_template('checkout.html', total=total, direcciones=direcciones)
        
        # Crear nueva dirección si no se selecciona una existente
        if not direccion_id:
            nueva_direccion = Direccion(
                usuario_id=current_user.id,
                calle=calle,
                ciudad=ciudad,
                codigo_postal=codigo_postal
            )
            db.session.add(nueva_direccion)
            db.session.commit()
            direccion_id = nueva_direccion.id
        
        # Crear pedido
        pedido = Pedido(
            usuario_id=current_user.id,
            direccion_id=direccion_id,
            monto_total=total,
            metodo_pago=metodo_pago,
            estado='pendiente'  # Inicial
        )
        db.session.add(pedido)
        db.session.commit()
        
        # Guardar detalles del pedido
        for item in cart_items:
            detalle = DetallePedido(
                pedido_id=pedido.id,
                product_id=item.product_id,
                cantidad=item.quantity,
                precio_unitario=Product.query.get(item.product_id).precio
            )
            db.session.add(detalle)
        db.session.commit()
        
        # Simular pago (para Nequi real, ver abajo)
        if metodo_pago == 'nequi':
            # Simulación: Cambiar estado a 'pagado'
            pedido.estado = 'pagado'
            db.session.commit()
            flash('Pago simulado con Nequi exitoso', 'success')
        else:
            flash('Método de pago no implementado', 'warning')
        
        # Vaciar carrito
        for item in cart_items:
            db.session.delete(item)
        db.session.commit()
        
        return redirect(url_for('dashboard.mis_pedidos'))
    
    return render_template('checkout.html', total=total, direcciones=direcciones)

@cart_bp.route('/descargar_factura/<int:pedido_id>', methods=['GET'])
@login_required
def descargar_factura(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    if pedido.usuario_id != current_user.id:
        flash('Acceso denegado', 'danger')
        return redirect(url_for('dashboard.mis_pedidos'))
    
    # Generar PDF con reportlab
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Contenido de la factura (personaliza según necesites)
    p.drawString(100, height - 100, f"Factura #{pedido.id}")
    p.drawString(100, height - 120, f"Fecha: {pedido.fecha_creacion.strftime('%d/%m/%Y')}")
    p.drawString(100, height - 140, f"Cliente: {current_user.nombre_usuario}")
    p.drawString(100, height - 160, f"Método de Pago: {pedido.metodo_pago}")
    p.drawString(100, height - 180, f"Monto Total: ${pedido.monto_total}")
    
    # Agregar detalles de productos
    y = height - 220
    p.drawString(100, y, "Detalles:")
    y -= 20  # Mover a la siguiente línea para los items
    for detalle in pedido.detalles:
        p.drawString(100, y, f"{detalle.producto.nombre} x {detalle.cantidad} - ${detalle.precio_unitario * detalle.cantidad}")
        y -= 20
    
    p.save()
    buffer.seek(0)
    
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=factura_{pedido.id}.pdf'
    return response