from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.product import Product
from models.categoria import Categoria
from models.subcategoria import Subcategoria
from models.user import User
from models.pedido import Pedido
from models.cart import Cart
from extensions import db
from sqlalchemy.orm import joinedload
from sqlalchemy import or_

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/admin')
@login_required
def admin_panel():
    if current_user.rol != 'administrador':
        flash('Acceso denegado', 'danger')
        return redirect(url_for('auth.login'))
    productos = Product.query.all()
    categorias = Categoria.query.all()
    subcategorias = Subcategoria.query.all()
    usuarios = User.query.all()
    return render_template('admin_dashboard.html', productos=productos, categorias=categorias, 
                          subcategorias=subcategorias, usuarios=usuarios)

@dashboard_bp.route('/admin/productos')
@login_required
def productos():
    if current_user.rol != 'administrador':
        flash('Acceso denegado', 'danger')
        return redirect(url_for('auth.login'))
    productos = Product.query.all()
    return render_template('productos.html', productos=productos)

@dashboard_bp.route('/admin/usuarios')
@login_required
def usuarios():
    if current_user.rol != 'administrador':
        flash('Acceso denegado', 'danger')
        return redirect(url_for('auth.login'))
    usuarios = User.query.all()
    return render_template('usuarios.html', usuarios=usuarios)

@dashboard_bp.route('/admin/categorias', methods=['GET', 'POST'])
@login_required
def categorias():
    if current_user.rol != 'administrador':
        flash('Acceso denegado', 'danger')
        return redirect(url_for('auth.login'))
    db.session.remove()  # Forzar recarga de la sesión
    categorias = Categoria.query.all()
    subcategorias = Subcategoria.query.options(joinedload(Subcategoria.categoria)).all()
    print(f"Categorías cargadas: {[c.nombre for c in categorias]}")
    print(f"Subcategorías cargadas: {[s.nombre for s in subcategorias]}")
    if not subcategorias:
        print("Advertencia: No se encontraron subcategorías en la consulta.")

    if request.method == 'POST':
        if 'nombre_categoria' in request.form:
            nombre_categoria = request.form['nombre_categoria']
            nombre_subcategoria = request.form.get('nombre_subcategoria')
            nueva_categoria = Categoria(nombre=nombre_categoria, descripcion='')
            db.session.add(nueva_categoria)
            db.session.flush()
            if nombre_subcategoria:
                nueva_subcategoria = Subcategoria(nombre=nombre_subcategoria, categoria_id=nueva_categoria.id)
                db.session.add(nueva_subcategoria)
            db.session.commit()
            flash('Categoría y subcategoría agregadas exitosamente', 'success')
            return redirect(url_for('dashboard.categorias'))
        elif 'categoria_id' in request.form and 'nombre_subcategoria' in request.form:
            categoria_id = request.form['categoria_id']
            nombre_subcategoria = request.form['nombre_subcategoria']
            if not categoria_id or not nombre_subcategoria:
                flash('Por favor, completa todos los campos', 'danger')
            else:
                nueva_subcategoria = Subcategoria(nombre=nombre_subcategoria, categoria_id=categoria_id)
                db.session.add(nueva_subcategoria)
                db.session.commit()
                flash('Subcategoría agregada exitosamente', 'success')
            return redirect(url_for('dashboard.categorias'))

    return render_template('agregar_categoria.html', categorias=categorias, subcategorias=subcategorias)

@dashboard_bp.route('/admin/agregar_producto', methods=['GET', 'POST'])
@login_required
def agregar_producto():
    if current_user.rol != 'administrador':
        flash('Acceso denegado', 'danger')
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = float(request.form['precio'])
        stock = int(request.form['stock'])
        url_imagen = request.form['url_imagen']
        subcategoria_id = int(request.form['subcategoria_id'])
        
        nuevo_producto = Product(nombre=nombre, descripcion=descripcion, precio=precio, 
                               stock=stock, url_imagen=url_imagen, subcategoria_id=subcategoria_id)
        db.session.add(nuevo_producto)
        db.session.commit()
        flash('Producto agregado exitosamente', 'success')
        return redirect(url_for('dashboard.admin_panel'))
    categorias = Categoria.query.options(joinedload(Categoria.subcategorias)).all()
    return render_template('admin_productos.html', categorias=categorias)

@dashboard_bp.route('/admin/editar_producto/<int:product_id>', methods=['GET', 'POST'])
@login_required
def editar_producto(product_id):
    if current_user.rol != 'administrador':
        flash('Acceso denegado', 'danger')
        return redirect(url_for('auth.login'))
    
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        try:
            product.nombre = request.form['nombre']
            product.descripcion = request.form['descripcion']
            product.precio = float(request.form['precio'])
            product.stock = int(request.form['stock'])
            product.url_imagen = request.form['url_imagen']
            product.subcategoria_id = int(request.form['subcategoria_id'])
            
            db.session.commit()
            flash('Producto actualizado exitosamente', 'success')
            return redirect(url_for('dashboard.admin_panel'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el producto: {str(e)}', 'danger')
            return redirect(url_for('dashboard.editar_producto', product_id=product_id))
    
    categorias = Categoria.query.options(joinedload(Categoria.subcategorias)).all()
    return render_template('editar_producto.html', product=product, categorias=categorias)

@dashboard_bp.route('/admin/eliminar_producto/<int:product_id>', methods=['POST'])
@login_required
def eliminar_producto(product_id):
    try:
        print(f"Intentando eliminar producto ID: {product_id}")
        if current_user.rol != 'administrador':
            print("Acceso denegado: usuario no es administrador")
            return jsonify({'success': False, 'message': 'Acceso denegado'}), 403
        
        product = Product.query.get_or_404(product_id)
        print(f"Producto encontrado: {product.nombre}")
        # Eliminar ítems del carrito asociados al producto
        deleted_rows = Cart.query.filter_by(product_id=product_id).delete()
        print(f"Ítems del carrito eliminados: {deleted_rows}")
        db.session.delete(product)
        db.session.commit()
        print(f"Producto eliminado: {product_id}")
        return jsonify({'success': True, 'message': 'Producto eliminado'})
    except Exception as e:
        db.session.rollback()
        print(f"Error al eliminar el producto: {str(e)}")
        return jsonify({'success': False, 'message': f'Error al eliminar el producto: {str(e)}'}), 500

@dashboard_bp.route('/admin/eliminar_usuario/<int:user_id>', methods=['POST'])
@login_required
def eliminar_usuario(user_id):
    try:
        print(f"Intentando eliminar usuario ID: {user_id}")
        if current_user.rol != 'administrador':
            print("Acceso denegado: usuario no es administrador")
            return jsonify({'success': False, 'message': 'Acceso denegado'}), 403
        
        if user_id == current_user.id:
            print("Acceso denegado: no puedes eliminarte a ti mismo")
            return jsonify({'success': False, 'message': 'No puedes eliminar tu propia cuenta'}), 403
        
        user = User.query.get_or_404(user_id)
        print(f"Usuario encontrado: {user.nombre_usuario}")
        # Eliminar ítems del carrito asociados al usuario
        deleted_cart_rows = Cart.query.filter_by(user_id=user_id).delete()
        print(f"Ítems del carrito eliminados: {deleted_cart_rows}")
        # Eliminar pedidos asociados al usuario
        deleted_pedido_rows = Pedido.query.filter_by(usuario_id=user_id).delete()
        print(f"Pedidos eliminados: {deleted_pedido_rows}")
        db.session.delete(user)
        db.session.commit()
        print(f"Usuario eliminado: {user_id}")
        return jsonify({'success': True, 'message': 'Usuario eliminado'})
    except Exception as e:
        db.session.rollback()
        print(f"Error al eliminar el usuario: {str(e)}")
        return jsonify({'success': False, 'message': f'Error al eliminar el usuario: {str(e)}'}), 500

@dashboard_bp.route('/admin/eliminar_categoria/<int:categoria_id>', methods=['POST'])
@login_required
def eliminar_categoria(categoria_id):
    try:
        print(f"Intentando eliminar categoría ID: {categoria_id}")
        if current_user.rol != 'administrador':
            print("Acceso denegado: usuario no es administrador")
            return jsonify({'success': False, 'message': 'Acceso denegado'}), 403
        
        categoria = Categoria.query.get_or_404(categoria_id)
        print(f"Categoría encontrada: {categoria.nombre}")
        # Obtener subcategorías asociadas
        subcategorias = Subcategoria.query.filter_by(categoria_id=categoria_id).all()
        subcategoria_ids = [subcat.id for subcat in subcategorias]
        print(f"Subcategorías asociadas: {subcategoria_ids}")
        # Obtener productos asociados a las subcategorías
        productos = Product.query.filter(Product.subcategoria_id.in_(subcategoria_ids)).all()
        producto_ids = [prod.id for prod in productos]
        print(f"Productos asociados: {producto_ids}")
        # Eliminar ítems del carrito asociados a los productos
        deleted_cart_rows = Cart.query.filter(Cart.product_id.in_(producto_ids)).delete()
        print(f"Ítems del carrito eliminados: {deleted_cart_rows}")
        # Eliminar productos asociados
        deleted_product_rows = Product.query.filter(Product.subcategoria_id.in_(subcategoria_ids)).delete()
        print(f"Productos eliminados: {deleted_product_rows}")
        # Eliminar subcategorías asociadas
        deleted_subcat_rows = Subcategoria.query.filter_by(categoria_id=categoria_id).delete()
        print(f"Subcategorías eliminadas: {deleted_subcat_rows}")
        # Eliminar la categoría
        db.session.delete(categoria)
        db.session.commit()
        print(f"Categoría eliminada: {categoria_id}")
        return jsonify({'success': True, 'message': 'Categoría eliminada'})
    except Exception as e:
        db.session.rollback()
        print(f"Error al eliminar la categoría: {str(e)}")
        return jsonify({'success': False, 'message': f'Error al eliminar la categoría: {str(e)}'}), 500

@dashboard_bp.route('/admin/eliminar_subcategoria/<int:subcategoria_id>', methods=['POST'])
@login_required
def eliminar_subcategoria(subcategoria_id):
    try:
        print(f"Intentando eliminar subcategoría ID: {subcategoria_id}")
        if current_user.rol != 'administrador':
            print("Acceso denegado: usuario no es administrador")
            return jsonify({'success': False, 'message': 'Acceso denegado'}), 403
        
        subcategoria = Subcategoria.query.get_or_404(subcategoria_id)
        print(f"Subcategoría encontrada: {subcategoria.nombre}")
        # Obtener productos asociados
        productos = Product.query.filter_by(subcategoria_id=subcategoria_id).all()
        producto_ids = [prod.id for prod in productos]
        print(f"Productos asociados: {producto_ids}")
        # Eliminar ítems del carrito asociados a los productos
        deleted_cart_rows = Cart.query.filter(Cart.product_id.in_(producto_ids)).delete()
        print(f"Ítems del carrito eliminados: {deleted_cart_rows}")
        # Eliminar productos asociados
        deleted_product_rows = Product.query.filter_by(subcategoria_id=subcategoria_id).delete()
        print(f"Productos eliminados: {deleted_product_rows}")
        # Eliminar la subcategoría
        db.session.delete(subcategoria)
        db.session.commit()
        print(f"Subcategoría eliminada: {subcategoria_id}")
        return jsonify({'success': True, 'message': 'Subcategoría eliminada'})
    except Exception as e:
        db.session.rollback()
        print(f"Error al eliminar la subcategoría: {str(e)}")
        return jsonify({'success': False, 'message': f'Error al eliminar la subcategoría: {str(e)}'}), 500



@dashboard_bp.route('/admin/agregar_subcategoria', methods=['POST'])
@login_required
def agregar_subcategoria():
    if current_user.rol != 'administrador':
        flash('Acceso denegado', 'danger')
        return redirect(url_for('auth.login'))
    categoria_id = request.form['categoria_id']
    nombre_subcategoria = request.form['nombre_subcategoria']
    if not categoria_id or not nombre_subcategoria:
        flash('Por favor, completa todos los campos', 'danger')
        return redirect(url_for('dashboard.agregar_categoria'))
    nueva_subcategoria = Subcategoria(nombre=nombre_subcategoria, categoria_id=categoria_id)
    db.session.add(nueva_subcategoria)
    db.session.commit()
    flash('Subcategoría agregada exitosamente', 'success')
    return redirect(url_for('dashboard.categorias'))

@dashboard_bp.route('/client_dashboard', methods=['GET', 'POST'])
@login_required
def client_dashboard():
    if current_user.rol not in ['cliente', 'vendedor']:
        flash('Acceso denegado', 'danger')
        return redirect(url_for('auth.login'))
    print(f"Rendering usuarios_dashboard for user: {current_user.nombre_usuario}, rol: {current_user.rol}")
    
    pedidos = Pedido.query.filter_by(usuario_id=current_user.id).all() if current_user.rol == 'cliente' else Pedido.query.filter_by(estado='pendiente').all() if current_user.rol == 'vendedor' else []
    categories = Categoria.query.all()
    subcategories = Subcategoria.query.all()

    search_query = request.args.get('search', '').strip() if request.method == 'GET' else request.form.get('search', '').strip()
    selected_category_id = request.form.get('category_id') if request.method == 'POST' else request.args.get('category_id', '')
    selected_subcategory_id = request.form.get('subcategory_id') if request.method == 'POST' else request.args.get('subcategory_id', '')

    products = []
    if current_user.rol == 'cliente':
        query = Product.query

        # Aplicar filtro de búsqueda
        if search_query:
            query = query.filter(or_(
                Product.nombre.ilike(f'%{search_query}%'),
                Product.descripcion.ilike(f'%{search_query}%')
            ))

        # Aplicar filtro de categoría/subcategoría
        if selected_subcategory_id and selected_subcategory_id != "":
            query = query.filter_by(subcategoria_id=selected_subcategoria_id)
        elif selected_category_id and selected_category_id != "":
            query = query.join(Product.subcategoria).join(Subcategoria.categoria).filter(Categoria.id == selected_category_id)

        products = query.all()
    
    return render_template('usuarios_dashboard.html', pedidos=pedidos, products=products, rol=current_user.rol, categories=categories, subcategories=subcategories, selected_category_id=selected_category_id, selected_subcategory_id=selected_subcategory_id)

@dashboard_bp.route('/pedido_detalle/<int:pedido_id>')
@login_required
def pedido_detalle(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    if current_user.rol == 'cliente' and pedido.usuario_id != current_user.id:
        flash('Acceso denegado', 'danger')
        return redirect(url_for('dashboard.client_dashboard'))
    return render_template('pedido_detalle.html', pedido=pedido)

@dashboard_bp.route('/procesar_pedido/<int:pedido_id>', methods=['GET', 'POST'])
@login_required
def procesar_pedido(pedido_id):
    if current_user.rol != 'vendedor':
        flash('Acceso denegado', 'danger')
        return redirect(url_for('dashboard.client_dashboard'))
    pedido = Pedido.query.get_or_404(pedido_id)
    if request.method == 'POST':
        estado = request.form.get('estado')
        if estado:
            pedido.estado = estado
            db.session.commit()
            flash('Estado del pedido actualizado', 'success')
            return redirect(url_for('dashboard.client_dashboard'))
    return render_template('procesar_pedido.html', pedido=pedido)

@dashboard_bp.route('/mis_pedidos')
@login_required
def mis_pedidos():
    if current_user.rol != 'cliente':
        flash('Acceso denegado', 'danger')
        return redirect(url_for('dashboard.client_dashboard'))
    pedidos = Pedido.query.filter_by(usuario_id=current_user.id).all()
    return render_template('mis_pedidos.html', pedidos=pedidos)