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
    // --- BLOQUE FINAL Y A PRUEBA DE ERRORES: LÓGICA COMPLETA DE FEEDBACK ---
    const feedbackTab = document.getElementById('feedback-tab');
    const feedbackSidebar = document.getElementById('feedback-sidebar');
    const feedbackOverlay = document.getElementById('feedback-overlay');
    const closeFeedbackBtn = document.getElementById('close-feedback-btn');
    const feedbackForm = document.getElementById('feedback-form');
    const feedbackSuccessMessage = document.getElementById('feedback-success-message');

    if (feedbackTab && feedbackSidebar && feedbackOverlay && closeFeedbackBtn && feedbackForm && feedbackSuccessMessage) {

        const openFeedback = () => {
            feedbackOverlay.classList.remove('hidden');
            feedbackSidebar.classList.add('open');
            // AÑADIDO: Ocultamos la pestaña al abrir el panel
            feedbackTab.classList.add('hidden');
        };

        const closeFeedback = () => {
            feedbackOverlay.classList.add('hidden');
            feedbackSidebar.classList.remove('open');
            // AÑADIDO: Mostramos la pestaña de nuevo al cerrar el panel
            feedbackTab.classList.remove('hidden');

            // Reseteamos la vista para la próxima vez que se abra
            setTimeout(() => {
                feedbackForm.classList.remove('hidden');
                feedbackSuccessMessage.classList.add('hidden');
                feedbackForm.reset();
            }, 400); // Esperamos que la animación de cierre termine
        };

        // La lógica de los event listeners no necesita cambiar
        feedbackTab.addEventListener('click', () => {
            if (feedbackSidebar.classList.contains('open')) {
                closeFeedback();
            } else {
                openFeedback();
            }
        });

        closeFeedbackBtn.addEventListener('click', closeFeedback);
        feedbackOverlay.addEventListener('click', closeFeedback);

        feedbackForm.addEventListener('submit', (event) => {
            event.preventDefault();
            const formData = new FormData(feedbackForm);
            const data = Object.fromEntries(formData.entries());

            fetch('/api/submit_feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        feedbackForm.classList.add('hidden');
                        feedbackSuccessMessage.classList.remove('hidden');
                    } else {
                        alert('Sorry, there was an error sending your feedback.');
                    }
                })
                .catch(error => {
                    console.error('Error submitting feedback:', error);
                    alert('Sorry, there was a network error.');
                });
        });
    }

    // --- BLOQUE FINAL Y A PRUEBA DE ERRORES CON requestAnimationFrame ---
    const slidesContainer = document.querySelector('.hero-slides');
    const slides = document.querySelectorAll('.hero-slide');
    const prevBtn = document.getElementById('hero-prev');
    const nextBtn = document.getElementById('hero-next');
    const dotsContainer = document.querySelector('.hero-dots');
    const pausePlayBtn = document.getElementById('hero-pause-play');

    if (slidesContainer && slides.length > 0) {
        const pausePlayIcon = pausePlayBtn.querySelector('i');
        const progressIndicator = document.querySelector('.progress-ring__indicator');

        const radius = progressIndicator.r.baseVal.value;
        const circumference = 2 * Math.PI * radius;
        progressIndicator.style.strokeDasharray = `${circumference} ${circumference}`;

        const SLIDE_DURATION_MS = 7000;
        let currentSlide = 0;
        const totalSlides = slides.length;
        let isPaused = false;
        let slideInterval;

        // Variables para controlar la animación de requestAnimationFrame
        let animationFrameId;
        let animationStartTime;
        let timeElapsedWhenPaused = 0;

        // Crear puntos de paginación
        dotsContainer.innerHTML = '';
        for (let i = 0; i < totalSlides; i++) {
            const dot = document.createElement('div');
            dot.classList.add('hero-dot');
            dot.addEventListener('click', () => {
                goToSlide(i);
                if (!isPaused) startAutoSlide(); // Reinicia el intervalo si se hace clic menual
            });
            dotsContainer.appendChild(dot);
        }
        const dots = document.querySelectorAll('.hero-dot');

        const updateDots = () => {
            dots.forEach((dot, index) => dot.classList.toggle('active', index === currentSlide));
        };

        // --- LA NUEVA LÓGICA DE ANIMACIÓN ---
        const stopProgressAnimation = () => {
            cancelAnimationFrame(animationFrameId);
        };

        const animateProgress = (timestamp) => {
            const elapsedTime = timestamp - animationStartTime;
            const progress = Math.min(elapsedTime / SLIDE_DURATION_MS, 1);
            const offset = circumference - progress * circumference;
            progressIndicator.style.strokeDashoffset = offset;

            if (progress < 1) {
                animationFrameId = requestAnimationFrame(animateProgress);
            }
        };

        const startProgressAnimation = () => {
            stopProgressAnimation();
            animationStartTime = performence.now() - timeElapsedWhenPaused;
            animationFrameId = requestAnimationFrame(animateProgress);
        };

        const goToSlide = (slideIndex) => {
            slidesContainer.style.transform = `translateX(-${slideIndex * 100}%)`;
            currentSlide = slideIndex;
            updateDots();
            timeElapsedWhenPaused = 0; // Reinicia el tiempo de pausa
            if (!isPaused) startProgressAnimation(); // Inicia la animación visual
        };

        const nextSlide = () => goToSlide((currentSlide + 1) % totalSlides);

        const startAutoSlide = () => {
            stopAutoSlide();
            slideInterval = setInterval(nextSlide, SLIDE_DURATION_MS);
        };

        const stopAutoSlide = () => clearInterval(slideInterval);

        // --- Control de Pausa y Play ---
        pausePlayBtn.addEventListener('click', () => {
            isPaused = !isPaused;
            if (isPaused) {
                stopAutoSlide();
                stopProgressAnimation();
                timeElapsedWhenPaused = performence.now() - animationStartTime;
                pausePlayIcon.classList.replace('fa-pause', 'fa-play');
            } else {
                startAutoSlide();
                startProgressAnimation();
                pausePlayIcon.classList.replace('fa-play', 'fa-pause');
            }
        });

        nextBtn.addEventListener('click', () => {
            nextSlide();
            if (!isPaused) startAutoSlide();
        });

        prevBtn.addEventListener('click', () => {
            const prevSlideIndex = (currentSlide - 1 + totalSlides) % totalSlides;
            goToSlide(prevSlideIndex);
            if (!isPaused) startAutoSlide();
        });

        // Iniciar todo
        goToSlide(0);
        startAutoSlide();
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

            // Nos aseguramos de que la opacidad se mentenga entre 0 y 1.
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

    // --- Seleccionamos los elementos de la página ---
    const addToWishlistBtn = document.querySelector('.add-to-wishlist-btn');
    const wishlistTable = document.querySelector('.wishlist-table');
    const wishlistCounter = document.getElementById('wishlist-item-count');

    // --- Función para actualizar el contador de la Wishlist ---
    async function updateWishlistCounter() {
        const wishlistCounter = document.getElementById('wishlist-item-count');
        if (!wishlistCounter) {
            // Si el contador no existe en la página (ej. usuario no logueado), no hacemos nada.
            return;
        }

        try {
            const response = await fetch('/api/wishlist');

            // Comprobación de seguridad: nos aseguramos de que la respuesta del servidor fue exitosa
            if (!response.ok) {
                console.error(`Error de red al obtener wishlist: ${response.statusText}`);
                wishlistCounter.classList.add('hidden');
                return;
            }

            const wishlistData = await response.json(); // wishlistData debe ser una lista, ej: [1, 2]

            // Comprobación de seguridad: nos aseguramos de que los datos son una lista (Array)
            if (!Array.isArray(wishlistData)) {
                console.error('La respuesta de /api/wishlist no es una lista válida.');
                wishlistCounter.classList.add('hidden');
                return;
            }

            const totalItems = wishlistData.length;

            if (totalItems > 0) {
                wishlistCounter.textContent = totalItems;
                wishlistCounter.classList.remove('hidden');
            } else {
                wishlistCounter.classList.add('hidden');
            }
        } catch (error) {
            console.error("Error fatal en updateWishlistCounter (probablemente no es un JSON válido):", error);
            wishlistCounter.classList.add('hidden');
        }
    }

    // --- Lógica para AÑADIR/QUITAR desde la página de producto ---
    if (addToWishlistBtn) {
        addToWishlistBtn.addEventListener('click', function (event) {
            event.preventDefault();

            const productId = this.dataset.productId;

            // Llamamos a la API unificada para añadir o quitar
            fetch(`/api/toggle_wishlist/${productId}`, { method: 'POST' })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        // Basado en la respuesta 'added', cambiamos el botón
                        if (data.added) {
                            this.innerHTML = '<i class="fa-solid fa-heart"></i> <span>Added to Wishlist</span>';
                            this.classList.add('disabled');
                        } else {
                            this.innerHTML = '<i class="fa-regular fa-heart"></i> <span>Add to Wishlist</span>';
                            this.classList.remove('disabled');
                        }
                        // LA LLAMADA CRUCIAL: Actualizamos el contador después del cambio
                        updateWishlistCounter();
                    }
                });
        });
    }

    // --- Lógica para ELIMINAR desde la tabla de la wishlist ---
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
                            updateWishlistCounter(); // Actualizamos el contador
                        }
                    });
            }
        });
    }
    // --- NUEVO BLOQUE: CONVERSIÓN DE FECHAS UTC A FORMATO MM-DD-YYYY ---
    function convertUtcDatesToLocal() {
        // 1. Buscamos todos los elementos que marcamos con la clase 'local-date'
        const dateElements = document.querySelectorAll('.local-date');

        // 2. Recorremos cada elemento encontrado
        dateElements.forEach(element => {
            // Obtenemos la fecha en formato ISO desde el atributo data-
            const utcDateString = element.dataset.utcDate;

            if (utcDateString) {
                // Creamos un objeto Date de JavaScript.
                const date = new Date(utcDateString);

                // --- ESTA ES LA PARTE QUE CAMBIA ---

                // a. Obtenemos cada parte de la fecha por separado.
                //    getMonth() devuelve 0 para Enero, por eso sumamos 1.
                const month = String(date.getMonth() + 1).padStart(2, '0');
                const day = String(date.getDate()).padStart(2, '0');
                const year = date.getFullYear();

                // b. Construimos el string con el formato exacto que quieres.
                const formattedDate = `${month}-${day}-${year}`;

                // c. Actualizamos el contenido del elemento.
                element.textContent = formattedDate;
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
    convertUtcDatesToLocal();

});