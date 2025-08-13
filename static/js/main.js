document.addEventListener('DOMContentLoaded', () => {

    // --- 1. LÓGICA PARA EL MODO OSCURO / CLARO ---
    const themeToggleButton = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');

    if (themeToggleButton && themeIcon) {
        themeToggleButton.addEventListener('click', (event) => {
            event.preventDefault();
            document.body.classList.toggle('light-mode');

            if (document.body.classList.contains('light-mode')) {
                themeIcon.classList.remove('fa-sun');
                themeIcon.classList.add('fa-moon');
            } else {
                themeIcon.classList.remove('fa-moon');
                themeIcon.classList.add('fa-sun');
            }
        });
    }

    // --- 2. LÓGICA Y ELEMENTOS DEL CARRITO (SIDEBAR) ---
    const openCartBtn = document.getElementById('open-cart-btn');
    const closeCartBtn = document.getElementById('close-cart-btn');
    const cartSidebar = document.getElementById('cart-sidebar');
    const cartOverlay = document.getElementById('cart-overlay');
    const cartItemsContainer = document.getElementById('cart-items');
    const cartSubtotalEl = document.getElementById('cart-subtotal');
    const cartCounter = document.getElementById('cart-item-count');

    // Función para ABRIR el carrito
    const openCart = () => {
        if (cartOverlay) cartOverlay.classList.remove('hidden');
        if (cartSidebar) cartSidebar.classList.add('open');
    };

    // Función para CERRAR el carrito
    const closeCart = () => {
        if (cartOverlay) cartOverlay.classList.add('hidden');
        if (cartSidebar) cartSidebar.classList.remove('open');
    };

    // Función para ACTUALIZAR EL CONTADOR DEL ÍCONO
    async function updateCartCounter() {
        if (!cartCounter) return;
        try {
            const response = await fetch('/api/cart');
            const data = await response.json();
            const cartData = data.cart;
            let totalQuantity = 0;
            for (const productId in cartData) {
                totalQuantity += cartData[productId].quantity;
            }
            if (totalQuantity > 0) {
                cartCounter.textContent = totalQuantity;
                cartCounter.classList.remove('hidden');
            } else {
                cartCounter.classList.add('hidden');
            }
        } catch (error) {
            console.error("Error actualizando contador:", error);
        }
    }

    // Función para ACTUALIZAR LA VISTA del carrito con datos del servidor
    async function updateCartView() {
        if (!cartItemsContainer || !cartSubtotalEl) return;
        try {
            const response = await fetch('/api/cart');
            const data = await response.json();
            const cartData = data.cart;
            const isAuthenticated = data.isAuthenticated;

            cartItemsContainer.innerHTML = '';
            let subtotal = 0;

            if (Object.keys(cartData).length === 0) {
                cartItemsContainer.innerHTML = '<p class="empty-cart-msg">Your cart is empty.</p>';
            } else {
                for (const productId in cartData) {
                    const item = cartData[productId];
                    const itemEl = document.createElement('div');
                    itemEl.classList.add('cart-item-row');
                    itemEl.innerHTML = `
                        <img src="/static/${item.image}" alt="${item.name}">
                        <div class="item-details">
                            <span class="item-name">${item.name}</span>
                            <span class="item-price">${item.price} x ${item.quantity}</span>
                        </div>
                        <button class="remove-item-btn" data-product-id="${productId}">×</button>
                    `;
                    cartItemsContainer.appendChild(itemEl);
                    const price = parseFloat(item.price.replace('€', ''));
                    subtotal += price * item.quantity;
                }
            }
            cartSubtotalEl.textContent = `€${subtotal.toFixed(2)}`;

            // LÓGICA CORREGIDA PARA EL BOTÓN DE CHECKOUT
            const checkoutBtn = document.querySelector('.checkout-btn');
            if (checkoutBtn) {
                // El botón siempre dice lo mismo y hace lo mismo
                checkoutBtn.textContent = 'PROCEED TO CHECKOUT';
                checkoutBtn.onclick = () => {
                    window.location.href = '/checkout';
                };

                // Solo se muestra si hay productos en el carrito
                if (Object.keys(cartData).length > 0) {
                    checkoutBtn.style.display = 'block';
                } else {
                    checkoutBtn.style.display = 'none';
                }
            }
        } catch (error) {
            console.error("Error actualizando vista del carrito:", error);
            cartItemsContainer.innerHTML = '<p class="empty-cart-msg">Error loading cart.</p>';
        }
    }

    // --- 3. ASIGNACIÓN DE EVENTOS ---
    if (openCartBtn) {
        openCartBtn.addEventListener('click', (e) => {
            e.preventDefault();
            updateCartView();
            openCart();
        });
    }
    if (closeCartBtn) closeCartBtn.addEventListener('click', closeCart);
    if (cartOverlay) cartOverlay.addEventListener('click', closeCart);

    const addToCartBtn = document.getElementById('add-to-cart-btn');
    if (addToCartBtn) {
        addToCartBtn.addEventListener('click', () => {
            const productId = addToCartBtn.dataset.productId;
            fetch(`/add_to_cart/${productId}`, { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        updateCartView();
                        updateCartCounter();
                        openCart();
                    }
                });
        });
    }

    if (cartItemsContainer) {
        cartItemsContainer.addEventListener('click', (event) => {
            if (event.target.classList.contains('remove-item-btn')) {
                const productId = event.target.dataset.productId;
                fetch(`/remove_from_cart/${productId}`, { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            updateCartView();
                            updateCartCounter();
                        }
                    });
            }
        });
    }

    // --- 4. LLAMADA INICIAL ---
    // Actualiza el contador del ícono del carrito en cuanto carga la página
    updateCartCounter();

});