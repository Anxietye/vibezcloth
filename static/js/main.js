document.addEventListener('DOMContentLoaded', () => {

    // --- 1. MODO OSCURO / CLARO ---
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

    // --- 2. LÓGICA GENERAL DEL CARRITO (ABRIR/CERRAR/ACTUALIZAR) ---
    const openCartBtn = document.getElementById('open-cart-btn');
    const closeCartBtn = document.getElementById('close-cart-btn');
    const cartSidebar = document.getElementById('cart-sidebar');
    const cartOverlay = document.getElementById('cart-overlay');
    const cartItemsContainer = document.getElementById('cart-items');
    const cartSubtotalEl = document.getElementById('cart-subtotal');
    const cartCounter = document.getElementById('cart-item-count');

    const openCart = () => { if (cartOverlay) cartOverlay.classList.remove('hidden'); if (cartSidebar) cartSidebar.classList.add('open'); };
    const closeCart = () => { if (cartOverlay) cartOverlay.classList.add('hidden'); if (cartSidebar) cartSidebar.classList.remove('open'); };

    const homeHero = document.querySelector('.home-hero-main');

    // Este código solo se ejecutará si estamos en la página de inicio y el elemento existe
    if (homeHero) {

        // Función que se ejecuta cada vez que el usuario hace scroll
        const handleScrollFade = () => {
            // Obtenemos la posición vertical del scroll
            const scrollPosition = window.scrollY;

            // Distancia en píxeles sobre la cual se completará el desvanecimiento.
            // Puedes aumentar o disminuir este número para que el efecto sea más rápido o más lento.
            const fadeOutDistance = 300;

            // Calculamos la nueva opacidad basándonos en la posición del scroll.
            // La fórmula asegura que la opacidad vaya de 1 (arriba) a 0 (al llegar a fadeOutDistance).
            const newOpacity = 1 - (scrollPosition / fadeOutDistance);

            // Nos aseguramos de que la opacidad se mantenga entre 0 y 1.
            const clampedOpacity = Math.max(0, Math.min(1, newOpacity));

            // Aplicamos el nuevo valor de opacidad al bloque "FEEL THE VIBE"
            homeHero.style.opacity = clampedOpacity;
        };

        // Le decimos al navegador que ejecute nuestra función cada vez que detecte un scroll.
        window.addEventListener('scroll', handleScrollFade);
    }
    async function updateCartView() {
        if (!cartItemsContainer || !cartSubtotalEl) return;
        try {
            const response = await fetch('/api/cart');
            const data = await response.json();
            const cartData = data.cart;
            cartItemsContainer.innerHTML = '';
            let subtotal = 0;
            if (Object.keys(cartData).length === 0) {
                cartItemsContainer.innerHTML = '<p class="empty-cart-msg">Your cart is empty.</p>';
            } else {
                for (const itemId in cartData) {
                    const item = cartData[itemId];
                    const itemEl = document.createElement('div');
                    itemEl.classList.add('cart-item-row');
                    itemEl.innerHTML = `
                        <img src="/static/${item.image}" alt="${item.name}">
                        <div class="item-details">
                            <span class="item-name">${item.name}</span>
                            <span class="item-price">${item.price} x ${item.quantity}</span>
                        </div>
                        <button class="remove-item-btn" data-product-id="${itemId}">×</button> 
                    `;
                    cartItemsContainer.appendChild(itemEl);
                    const price = parseFloat(item.price.replace('$', ''));
                    subtotal += price * item.quantity;
                }
            }
            cartSubtotalEl.textContent = `$${subtotal.toFixed(2)}`;
            const checkoutBtn = document.querySelector('.checkout-btn');
            if (checkoutBtn) {
                checkoutBtn.textContent = 'PROCEED TO CHECKOUT';
                checkoutBtn.onclick = () => { window.location.href = '/checkout'; };
                checkoutBtn.style.display = Object.keys(cartData).length > 0 ? 'block' : 'none';
            }
        } catch (error) {
            console.error("Error actualizando vista del carrito:", error);
        }
    }

    async function updateCartCounter() {
        if (!cartCounter) return;
        try {
            const response = await fetch('/api/cart');
            const data = await response.json();
            const cartData = data.cart;
            let totalQuantity = 0;
            for (const itemId in cartData) {
                totalQuantity += cartData[itemId].quantity;
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

    if (openCartBtn) {
        openCartBtn.addEventListener('click', (e) => {
            e.preventDefault();
            updateCartView();
            openCart();
        });
    }
    if (closeCartBtn) closeCartBtn.addEventListener('click', closeCart);
    if (cartOverlay) cartOverlay.addEventListener('click', closeCart);
    if (cartItemsContainer) {
        cartItemsContainer.addEventListener('click', (event) => {
            if (event.target.classList.contains('remove-item-btn')) {
                const itemId = event.target.dataset.productId;
                fetch(`/remove_from_cart/${itemId}`, { method: 'POST' })
                    .then(response => response.json())
                    .then(data => { if (data.success) { updateCartView(); updateCartCounter(); } });
            }
        });
    }

    // --- 3. LÓGICA DE LA PÁGINA DE PRODUCTO DETALLADO (CON AUTENTICACIÓN) ---
    const mainImage = document.getElementById('main-product-image');
    const thumbnails = document.querySelectorAll('.thumbnail-img');
    const colorSelector = document.getElementById('color-selector');
    const addToCartBtn = document.getElementById('add-to-cart-btn');
    const productDetailPage = document.querySelector('.product-detail-page'); // <-- Necesario

    // Obtenemos el estado de login desde el HTML
    const isAuthenticated = productDetailPage && productDetailPage.dataset.isAuthenticated === 'true';

    // Lógica de la Galería de Miniaturas
    if (mainImage && thumbnails.length > 0) {
        thumbnails.forEach(thumbnail => {
            thumbnail.addEventListener('click', () => {
                // 1. Cambiamos la imagen principal
                mainImage.src = thumbnail.dataset.imageSrc;

                // 2. Actualizamos la miniatura activa
                thumbnails.forEach(thumb => thumb.classList.remove('active'));
                thumbnail.classList.add('active');

                // 3. SINCRONIZACIÓN: Seleccionamos el botón de color correspondiente
                const colorOfThumbnail = thumbnail.dataset.color;
                if (colorSelector) { // Comprobamos si existe el selector de color
                    const colorOptions = colorSelector.querySelectorAll('.color-option');
                    colorOptions.forEach(btn => {
                        btn.classList.toggle('active', btn.dataset.color === colorOfThumbnail);
                    });
                }

                // 4. Actualizamos el estado del botón "Add to Cart"
                if (addToCartBtn && colorSelector) {
                    const selectedColors = colorSelector.querySelectorAll('.color-option.active');
                    addToCartBtn.disabled = selectedColors.length === 0;
                }
            });
        });
    }

    // Lógica de los Botones de Color y "Add to Cart"
    if (colorSelector && addToCartBtn) {
        const colorOptions = colorSelector.querySelectorAll('.color-option');

        function checkSelection() {
            const selectedColors = colorSelector.querySelectorAll('.color-option.active');
            addToCartBtn.disabled = selectedColors.length === 0;
        };

        colorOptions.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                button.classList.toggle('active');

                if (button.classList.contains('active')) {
                    if (mainImage) mainImage.src = button.dataset.imageSrc;
                    thumbnails.forEach(thumb => {
                        thumb.classList.toggle('active', thumb.dataset.imageSrc === button.dataset.imageSrc);
                    });
                }
                checkSelection();
            });
        });

        // --- LÓGICA CONDICIONAL PARA EL BOTÓN "ADD TO CART" ---
        if (isAuthenticated) {
            // --- Si el usuario ESTÁ logueado, funciona normal ---
            addToCartBtn.addEventListener('click', () => {
                const productId = addToCartBtn.dataset.productId;
                const selectedButtons = colorSelector.querySelectorAll('.color-option.active');
                const selectedColors = Array.from(selectedButtons).map(btn => btn.dataset.color);

                fetch(`/add_to_cart/${productId}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ colors: selectedColors })
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            updateCartView();
                            updateCartCounter();
                            openCart();
                            selectedButtons.forEach(btn => btn.classList.remove('active'));
                            checkSelection();
                        }
                    });
            });
        } else {
            // --- Si el usuario NO está logueado, redirige al login ---
            // Habilitamos el botón para que sea clicable
            addToCartBtn.disabled = false;
            addToCartBtn.textContent = 'Sign in to purchase';

            addToCartBtn.addEventListener('click', (e) => {
                e.preventDefault();
                window.location.href = '/login';
            });
        }

        checkSelection(); // Comprobación inicial
    }

    // --- 4. LÓGICA PARA LA VISTA DE CATEGORÍA (NUEVO BLOQUE) ---
    const featuredImage = document.getElementById('featured-image');
    const featuredName = document.getElementById('featured-name');
    const featuredPrice = document.getElementById('featured-price');
    const productListItems = document.querySelectorAll('.product-list-item');

    if (featuredImage && productListItems.length > 0) {
        productListItems.forEach(item => {
            // Evento para cambiar la vista destacada con un solo clic
            item.addEventListener('click', function () {
                featuredImage.src = this.dataset.image;
                featuredName.textContent = this.dataset.name;
                featuredPrice.textContent = this.dataset.price;

                productListItems.forEach(i => i.classList.remove('active'));
                this.classList.add('active');
            });

            // Evento para ir a la página del producto con doble clic
            item.addEventListener('dblclick', function () {
                window.location.href = this.dataset.url;
            });
        });
    }

    // =======================================================
    // === 5. LÓGICA DE LA WISHLIST (VERSIÓN FINAL) ========
    // =======================================================
    const wishlistTable = document.querySelector('.wishlist-table');
    const wishlistCounter = document.getElementById('wishlist-item-count');

    // Función para actualizar el contador (movida aquí para claridad)
    async function updateWishlistCounter() {
        if (!wishlistCounter) return;
        try {
            const response = await fetch('/api/wishlist');
            const wishlistData = await response.json();
            const totalItems = wishlistData.length;
            wishlistCounter.textContent = totalItems;
            wishlistCounter.classList.toggle('hidden', totalItems === 0);
        } catch (error) {
            console.error("Error al actualizar contador de wishlist:", error);
        }
    }

    // Lógica para el botón de AÑADIR/QUITAR en la página de producto
    // Se busca de nuevo para evitar conflictos con la lógica de la página de producto
    const pageProductAddToWishlistBtn = document.querySelector('.product-detail-page .add-to-wishlist-btn');
    if (pageProductAddToWishlistBtn) {
        pageProductAddToWishlistBtn.addEventListener('click', function (event) {
            event.preventDefault();

            const productId = this.dataset.productId;

            fetch(`/api/toggle_wishlist/${productId}`, { method: 'POST' })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        if (data.added) {
                            this.innerHTML = '<i class="fa-solid fa-heart"></i> <span>Added to Wishlist</span>';
                            this.classList.add('disabled');
                        } else {
                            this.innerHTML = '<i class="fa-regular fa-heart"></i> <span>Add to Wishlist</span>';
                            this.classList.remove('disabled');
                        }
                        updateWishlistCounter(); // ¡La llamada crucial!
                    }
                });
        });
    }

    // Lógica para ELIMINAR desde la tabla de la wishlist
    if (wishlistTable) {
        wishlistTable.addEventListener('click', function (e) {
            const removeBtn = e.target.closest('.remove-wishlist-btn');
            if (removeBtn) {
                const productId = removeBtn.dataset.productId;
                fetch(`/api/remove_from_wishlist/${productId}`, { method: 'POST' })
                    .then(res => res.json())
                    .then(data => {
                        if (data.success) {
                            document.getElementById(`wishlist-item-${productId}`).remove();
                            updateWishlistCounter();
                        }
                    });
            }
        });
    }
    // --- LÓGICA FINAL Y FUNCIONAL PARA EL CARRUSEL DE LA HOME ---
    const track = document.getElementById('carousel-track-final');
    const prevArrow = document.getElementById('prev-arrow-final');
    const nextArrow = document.getElementById('next-arrow-final');

    // Este código solo se ejecutará si los elementos del carrusel existen en la página
    if (track && prevArrow && nextArrow) {

        let currentIndex = 0;
        const items = track.querySelectorAll('.carousel-item-final');
        const totalItems = items.length;
        const itemsToShow = 4; // El número de items que muestras a la vez

        // Función para actualizar la visibilidad de las flechas
        function updateArrows() {
            // La flecha izquierda se deshabilita si estamos al principio
            prevArrow.disabled = currentIndex === 0;
            // La flecha derecha se deshabilita si ya no hay más items que mostrar
            nextArrow.disabled = currentIndex >= totalItems - itemsToShow;
        }

        // Función para mover la tira de productos
        function updateCarouselPosition() {
            const itemWidth = items[0].offsetWidth; // Calculamos el ancho de un item
            const newTransformValue = -currentIndex * itemWidth;
            track.style.transform = `translateX(${newTransformValue}px)`;
            updateArrows(); // Actualizamos las flechas después de cada movimiento
        }

        // Event listener para la flecha DERECHA
        nextArrow.addEventListener('click', () => {
            // Solo nos movemos si no hemos llegado al final
            if (currentIndex < totalItems - itemsToShow) {
                currentIndex++;
                updateCarouselPosition();
            }
        });

        // Event listener para la flecha IZQUIERDA
        prevArrow.addEventListener('click', () => {
            // Solo nos movemos si no estamos al principio
            if (currentIndex > 0) {
                currentIndex--;
                updateCarouselPosition();
            }
        });

        // Ocultamos las flechas si no hay suficientes productos para desplazar
        if (totalItems <= itemsToShow) {
            prevArrow.style.display = 'none';
            nextArrow.style.display = 'none';
        }

        // Establecemos el estado inicial de las flechas al cargar la página
        updateArrows();
    }
    // --- LÓGICA DE CUPONES EN LA PÁGINA DE CHECKOUT ---
    const checkoutPage = document.querySelector('.checkout-page');
    if (checkoutPage) {
        const applyBtn = document.getElementById('apply-coupon-btn');
        const removeBtn = document.getElementById('remove-coupon-btn');
        const couponInput = document.getElementById('coupon-code-input');
        const messageEl = document.getElementById('coupon-message');

        if (applyBtn) {
            applyBtn.addEventListener('click', () => {
                const code = couponInput.value.trim();
                if (!code) return;

                fetch('/api/apply_coupon', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ coupon_code: code })
                })
                    .then(res => res.json())
                    .then(data => {
                        if (data.success) {
                            window.location.reload(); // La forma más simple y robusta de actualizar
                        } else {
                            messageEl.textContent = data.message;
                            messageEl.className = 'error';
                        }
                    });
            });
        }

        if (removeBtn) {
            removeBtn.addEventListener('click', (e) => {
                e.preventDefault();
                fetch('/api/remove_coupon', { method: 'POST' })
                    .then(() => window.location.reload());
            });
        }
    }
    updateCartCounter();
    updateWishlistCounter();

});