document.addEventListener('DOMContentLoaded', function() {
    // Wishlist (agregar / quitar)
    const wishlistBtns = document.querySelectorAll('.wishlist-btn');
    wishlistBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (this.tagName === 'A') return; // Ignorar enlaces (usuarios no logueados)
            e.preventDefault();
            const productId = this.dataset.productId;
            const isFavorited = this.classList.contains('favorited');
            const url = isFavorited ? `/wishlist/remove_from_wishlist/${productId}` : `/wishlist/add_to_wishlist/${productId}`;
            
            fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }})
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    this.classList.toggle('favorited');
                    alert(data.message);
                    if (document.querySelector('#wishlistModal')?.classList.contains('show')) {
                        location.reload();
                    }
                } else {
                    alert(data.message);
                }
            })
            .catch(err => console.error('Error:', err));
        });
    });

    // Eliminar de wishlist
    const removeBtns = document.querySelectorAll('.remove-wishlist-btn');
    removeBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const productId = this.dataset.productId;
            fetch(`/wishlist/remove_from_wishlist/${productId}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }})
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    this.parentElement.remove();
                    if (document.querySelectorAll('.wishlist-item').length === 0) {
                        location.reload();
                    }
                } else {
                    alert(data.message);
                }
            })
            .catch(err => console.error('Error:', err));
        });
    });

    // Agregar al carrito
    const addToCartBtns = document.querySelectorAll('.add-to-cart-btn');
    addToCartBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (this.tagName === 'A') return;
            e.preventDefault();
            const productId = this.dataset.productId;
            fetch(`/cart/add_to_cart/${productId}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }})
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    const cartCount = document.querySelector('.cart-count');
                    if (cartCount) {
                        cartCount.textContent = parseInt(cartCount.textContent) + 1;
                    }
                } else {
                    alert(data.message);
                }
            })
            .catch(err => console.error('Error al agregar al carrito:', err));
        });
    });

    // Actualizar contador carrito inicial
    function updateCartCount() {
        fetch('/cart/get_cart_count', { method: 'GET' })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const cartCount = document.querySelector('.cart-count');
                if (cartCount) {
                    cartCount.textContent = data.count;
                }
            }
        })
        .catch(err => console.error('Error al actualizar contador de carrito:', err));
    }
    updateCartCount();

    // Modales
    const modalCloses = document.querySelectorAll('.modal-close');
    modalCloses.forEach(close => {
        close.addEventListener('click', function() {
            this.closest('.modal').classList.remove('show');
        });
    });

    document.querySelectorAll('.nav-link[data-toggle="modal"]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = this.getAttribute('data-target');
            document.querySelector(target).classList.add('show');
        });
    });
});
