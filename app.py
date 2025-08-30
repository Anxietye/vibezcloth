from flask import (
    Flask,
    render_template,
    abort,
    url_for,
    redirect,
    session,
    request,
    jsonify,
    send_from_directory,
)
import requests
import urllib.parse
import random
import secrets
from datetime import datetime

app = Flask(__name__)

# ==============================================================================
# === CONFIGURACIÓN Y DATOS ====================================================
# ==============================================================================

# --- CONFIGURACIÓN DE LA APP Y OAUTH ---
app.secret_key = "y2PRyodNyyzu1mzZa2hTJy8tGP0MKDkJ8GQbuSbR"
CLIENT_ID = "76"
CLIENT_SECRET = "y2PRyodNyyzu1mzZa2hTJy8tGP0MKDkJ8GQbuSbR"

# ESTA ES LA LÍNEA MÁS IMPORTANTE - DEBE COINCIDIR CON TU PANEL
# Basado en tus datos, esta es la configuración correcta.
REDIRECT_URI = "https://vibezcloth.onrender.com/auth/callback"

AUTHORIZATION_URL = "https://ucp.gta.world/oauth/authorize"
TOKEN_URL = "https://ucp.gta.world/oauth/token"
USER_API_URL = "https://ucp.gta.world/api/user"

# --- API KEY DE BANKING ---
BANKING_GATEWAY_URL = "https://banking.gta.world/gateway/"
BANKING_AUTH_KEY = "xmD0M1OUh2n2scx1VJb8kU2yAwKyaqIVbTXXfwZL90FY51sijBwysY7sLZao3fQu"

# --- DATOS DE EJEMPLO DE PRODUCTOS ---
all_products = [
    {
        "id": 1,
        "category": "woman",
        "name": "Vibez Cozy Tracksuit",
        "price": "$8500",
        "slug": "vibez-tracksuit",
        "sku": "VF-001",
        # NUEVA ESTRUCTURA: Un diccionario de variantes de color
        "color_variants": {
            "Red": {  # Color 'Negro' usa la imagen woman1.png
                "image": "images/anaranjado.png",
                "download_file": "Vibez-Tracksuit-Red.zip",
            },
            "Blue": {  # Color 'Rojo' usa la imagen 1.png
                "image": "images/azul.png",
                "download_file": "Vibez-Tracksuit-Blue.zip",
            },
            "White": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/blanco.png",
                "download_file": "Vibez-Tracksuit-White.zip",
            },
            "Brown": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/marron.png",
                "download_file": "Vibez-Tracksuit-Brown.zip",
            },
            "Black": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/negro.png",
                "download_file": "Vibez-Tracksuit-Black.zip",
            },
            "Purple": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/purpura.png",
                "download_file": "Vibez-Tracksuit-Purple.zip",
            },
            "Pink": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/rosa.png",
                "download_file": "Vibez-Tracksuit-Pink.zip",
            },
            "Green": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/verde.png",
                "download_file": "Vibez-Tracksuit-Green.zip",
            },
        },
    },
    {
        "id": 2,
        "category": "woman",
        "name": "Grunge T-Shirt",
        "price": "$6000",
        "slug": "grunge-t-shirt",
        "sku": "TM-002",
        "color_variants": {
            "Torment": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/tblack9.png",
                "download_file": "Torment.zip",
            },
            "Heaven": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/tblack8.png",
                "download_file": "Heaven.zip",
            },
            "Distorted": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/tblack6.png",
                "download_file": "Distorted.zip",
            },
            "Red": {  # Color 'Negro' usa la imagen woman1.png
                "image": "images/Tred.png",
                "download_file": "Red.zip",
            },
            "Distorted Vibez": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/tblack7.png",
                "download_file": "Distorted-Vibez.zip",
            },
            "Dream Big": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/twhite2.png",
                "download_file": "Dream-Big.zip",
            },
            "Stuck-W": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/twhite3.png",
                "download_file": "Stuck-W.zip",
            },
            "Cry Baby": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/twhite4.png",
                "download_file": "Cry-Baby.zip",
            },
            "Western Shirt": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/twhite5.png",
                "download_file": "Western-Shirt.zip",
            },
            "Hell Full": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Tblack2.png",
                "download_file": "Hell-Full.zip",
            },
            "Hell Boring": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/tblack4.png",
                "download_file": "Hell-Boring.zip",
            },
            "Angel & Thoughts": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/tblack5.png",
                "download_file": "Angel-Thoughts.zip",
            },
        },
    },
    {
        "id": 3,
        "category": "woman",
        "name": "Cropped Tank Top",
        "price": "$4500",
        "slug": "cropped-tank-top",
        "sku": "CT-047",
        "color_variants": {
            "LS Vibez": {  # Color 'Negro' usa la imagen woman1.png
                "image": "images/Croptop3.png",
                "download_file": "LS-Vibez-Cropped-Tank-Top.zip",
            },
            "Hell Boring": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Croptop6.png",
                "download_file": "Hell-Boring-Cropped-Tank-Top.zip",
            },
            "Flames": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Croptop1.png",
                "download_file": "Flames-Cropped-Tank-Top.zip",
            },
            "Baked": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Croptop2.png",
                "download_file": "Baked-Cropped-Tank-Top.zip",
            },
            "Bad Things": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Croptop4.png",
                "download_file": "Bad-Things-Cropped-Tank-Top.zip",
            },
            "White": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Croptop5.png",
                "download_file": "White-Cropped-Tank-Top.zip",
            },
            "Black": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Croptop7.png",
                "download_file": "Black-Cropped-Tank-Top.zip",
            },
        },
    },
    {
        "id": 4,
        "category": "woman",
        "name": "Cropped Hoodie",
        "price": "$4700",
        "slug": "cropped-hoodie",
        "sku": "CH-008",
        "color_variants": {
            "D. Lettering": {  # Color 'Negro' usa la imagen woman1.png
                "image": "images/darklettering.png",
                "download_file": "Lettering.zip",
            },
            "Depravity": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/depravity.png",
                "download_file": "Depravity.zip",
            },
            "Dream Big": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/drambig.png",
                "download_file": "DreamBig.zip",
            },
            "Dystopia": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/dystopia.png",
                "download_file": "Dystopia.zip",
            },
            "Kuromi": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/kuromi.png",
                "download_file": "Kuromi.zip",
            },
            "Red L.": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/lettering.png",
                "download_file": "Red-L.zip",
            },
            "Run Away": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/runaway.png",
                "download_file": "Run-Away.zip",
            },
            "Stucked": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/stucked.png",
                "download_file": "Stuck.zip",
            },
            "Blue": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/azuls.png",
                "download_file": "Blue.zip",
            },
            "White": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/blancos.png",
                "download_file": "White.zip",
            },
            "Brown": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/marrons.png",
                "download_file": "Brown.zip",
            },
            "Black": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/negros.png",
                "download_file": "Black.zip",
            },
            "Pink": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/rosas.png",
                "download_file": "Pink.zip",
            },
        },
    },
    {
        "id": 5,
        "category": "woman",
        "name": "Vibez Jeans",
        "price": "$3500",
        "slug": "vibez-jeans",
        "sku": "VJ-004",
        "color_variants": {
            "Blue": {  # Color 'Negro' usa la imagen woman1.png
                "image": "images/pantazul.png",
                "download_file": "blue-jeans.zip",
            },
            "Black": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/pantnegro.png",
                "download_file": "black-jeans.zip",
            },
        },
    },
    {
        "id": 6,
        "category": "woman",
        "name": "Sports Pants",
        "price": "$3200",
        "slug": "sports-pants",
        "sku": "SP-040",
        "color_variants": {
            "Blue": {  # Color 'Negro' usa la imagen woman1.png
                "image": "images/bluepant.png",
                "download_file": "sp-blue.zip",
            },
            "Black": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/blackpant.png",
                "download_file": "sp-black.zip",
            },
            "Red": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/redpant.png",
                "download_file": "sp-red.zip",
            },
            "White": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/whitepant.png",
                "download_file": "sp-white.zip",
            },
        },
    },
    {
        "id": 7,
        "category": "woman",
        "name": "Oversized Band T-Shirts",
        "price": "$4000",
        "slug": "oversized-band-shirts",
        "sku": "OS-001",
        "color_variants": {
            "Metallica": {  # Color 'Negro' usa la imagen woman1.png
                "image": "images/metallica.png",
                "download_file": "Metallica.zip",
            },
            "Iron Maiden": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/ironmaiden.png",
                "download_file": "Iron-Maiden.zip",
            },
            "Black Sabbath": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/blacksabbath.png",
                "download_file": "Black-Sabbath.zip",
            },
            "Skulls": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/skulls.png",
                "download_file": "Skulls.zip",
            },
        },
    },
    {
        "id": 8,
        "category": "woman",
        "name": "Custom Sneaker",
        "price": "$15000",
        "slug": "custom-sneaker",
        "sku": "CS-101",
        "color_variants": {
            "Billie Eilish": {  # Color 'Negro' usa la imagen woman1.png
                "image": "images/Billie.png",
                "download_file": "Billie-Eilish.zip",
            },
            "Blue Flowers": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Blue-Flowers.png",
                "download_file": "Blue-Flowers.zip",
            },
            "Butterflies": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Butterflies.png",
                "download_file": "Butterflies.zip",
            },
            "BW Cartoon": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/BW-Cartoon.png",
                "download_file": "BW-Cartoon.zip",
            },
            "Cherry Flowers": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Cherry.png",
                "download_file": "Cherry-Flowers.zip",
            },
            "Classic": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Classic.png",
                "download_file": "Classic.zip",
            },
            "Melted": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Melted.png",
                "download_file": "Melted.zip",
            },
            "Pikachu": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Pikachu.png",
                "download_file": "Pikachu.zip",
            },
            "Pink": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Pinky.png",
                "download_file": "Pinky.zip",
            },
            "Stitch": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Stitch.png",
                "download_file": "Stitch.zip",
            },
            "Sunflower": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Sunflower.png",
                "download_file": "Sunflower.zip",
            },
            "White Cartoon": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/White-Cartoon.png",
                "download_file": "White-Cartoon.zip",
            },
            "All-White Cartoon": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/All-White.png",
                "download_file": "All-White.zip",
            },
        },
    },
]
# --- CUPONES
VALID_COUPONS = {
    "VIBE5": {"type": "percent", "value": 5},  # 5% de descuento
    "CLOTH1": {"type": "percent", "value": 10},  # 10% de descuento
    "VZ2604": {"type": "percent", "value": 15},  # $15 de descuento fijo
    "SAVEBIG": {"type": "percent", "value": 25},  # 25% de descuento
    "TAKE10": {"type": "percent", "value": 10},  # $10 de descuento fijo
    "LAUNCH40": {"type": "percent", "value": 40},  # $40 de descuento fijo
}
COUPONS_ENABLED = False


# --- FUNCIONES AUXILIARES ---
def find_product_by_id(product_id):
    try:
        pid = int(product_id)
        for product in all_products:
            if product.get("id") == pid:
                return product
    except (ValueError, TypeError):
        return None
    return None


def get_products_by_category(category_name):
    return [p for p in all_products if p["category"] == category_name]


# ==============================================================================
# === RUTAS DE LA TIENDA =======================================================
# ==============================================================================


@app.route("/my-account")
def my_account_page():
    """Muestra la página del dashboard del usuario."""
    # Protección de Ruta: Si no hay un usuario en la sesión, lo redirigimos al login.
    if "user" not in session or not session.get("user"):
        return redirect(url_for("login"))

    breadcrumbs = [
        {"text": "Home", "url": url_for("home")},
        {"text": "My Account", "url": None},
    ]

    # Pasamos active_page para que ningún otro enlace del header se resalte.
    return render_template(
        "my_account.html", active_page="my-account", breadcrumbs=breadcrumbs
    )


@app.route("/my-account/orders")
def my_account_orders():
    """Muestra el historial de pedidos del usuario."""
    if "user" not in session:
        return redirect(url_for("login"))

    # Obtenemos los pedidos de la sesión. Si no hay, es una lista vacía.
    orders = session.get("orders", [])

    return render_template("orders.html", orders=orders, active_page="my-account")


@app.route("/my-account/details")
def my_account_details():  # <-- El nombre de la función es 'my_account_details'
    """Muestra la página de detalles de la cuenta del usuario."""
    if "user" not in session:
        return redirect(url_for("login"))

    user_data = session.get("user")

    return render_template(
        "account_details.html", user=user_data, active_page="my-account"
    )


@app.route("/my-account/view-order/<int:order_number>")
def view_order_page(order_number):
    """Muestra los detalles de un pedido específico."""
    if "user" not in session:
        return redirect(url_for("login"))

    orders = session.get("orders", [])

    # Buscamos el pedido en la lista de la sesión por su número
    order_to_view = next(
        (order for order in orders if order.get("number") == order_number), None
    )

    # Si no se encuentra el pedido, redirigimos al historial
    if not order_to_view:
        return redirect(url_for("my_account_orders"))

    return render_template(
        "view_order.html", order=order_to_view, active_page="my-account"
    )


@app.route("/my-account/downloads")
def my_account_downloads():
    """Muestra la lista de productos descargables del usuario."""
    if "user" not in session:
        return redirect(url_for("login"))

    # Obtenemos las descargas de la sesión
    downloads = session.get("downloads", [])

    return render_template(
        "downloads.html", downloads=downloads, active_page="my-account"
    )


@app.route("/")
def home():
    # Mostraremos los últimos 8 productos, por ejemplo.
    latest_products = all_products[:8]

    return render_template(
        "index.html", active_page="home", body_class="page-home", products=all_products
    )


@app.route("/<category_name>")
def category_page(category_name):
    if category_name not in ["woman", "man", "accessories"]:
        abort(404)

    # Obtenemos la lista completa de productos para esta categoría
    products_list = get_products_by_category(category_name)

    breadcrumbs = [
        {"text": "Home", "url": url_for("home")},
        {"text": category_name.upper(), "url": None},
    ]

    # Pasamos la lista completa a la plantilla con el nombre 'products'
    return render_template(
        "category.html",
        title=category_name.capitalize(),
        products=products_list,  # Pasamos la lista completa
        active_page=category_name,
        breadcrumbs=breadcrumbs,
    )


@app.route("/terms-and-conditions")
def terms_page():
    """Muestra la página de Términos y Condiciones."""
    return render_template("terms.html", active_page="terms")


@app.route("/faq")
def faq_page():
    """Displays the Frequently Asked Questions page."""
    return render_template("faq.html", active_page="faq")


@app.route("/<category_name>/<product_slug>")
def product_detail(category_name, product_slug):
    product = next((p for p in all_products if p["slug"] == product_slug), None)
    if not product or product["category"] != category_name:
        abort(404)

    wishlist_ids = session.get("wishlist", [])
    is_in_wishlist = product["id"] in wishlist_ids

    breadcrumbs = [
        {"text": "Home", "url": url_for("home")},
        {
            "text": category_name.upper(),
            "url": url_for("category_page", category_name=category_name),
        },
        {"text": product["name"].upper(), "url": None},
    ]
    return render_template(
        "product_detail.html",
        product=product,
        active_page=category_name,
        breadcrumbs=breadcrumbs,
        is_in_wishlist=is_in_wishlist,
    )


# ARCHIVO: app.py


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    # --- Lógica que se ejecuta para AMBAS peticiones (GET y POST) ---
    cart = session.get("cart", {})
    if not cart:
        return redirect(url_for("home"))

    subtotal = sum(
        float(item["price"].replace("$", "")) * item["quantity"]
        for item in cart.values()
    )
    coupon = session.get("coupon")
    discount_amount = 0
    if coupon:
        if coupon["type"] == "percent":
            discount_amount = (subtotal * coupon["value"]) / 100
        else:
            discount_amount = coupon["value"]
    total = max(0, subtotal - discount_amount)

    # --- Lógica que se ejecuta SOLO al enviar el formulario (POST) ---
    if request.method == "POST":
        # 1. Recopilamos y guardamos la dirección
        billing_address = {
            "firstname": request.form.get("firstname"),
            "lastname": request.form.get("lastname"),
            "apartment": request.form.get("apartment"),
            "discord": request.form.get("discord"),
            "phone": request.form.get("phone"),
        }

        # 2. Generamos el token de seguridad y el pedido pendiente
        order_token = secrets.token_hex(16)
        session["pending_order"] = {
            "token": order_token,
            "cart": cart,
            "billing_address": billing_address,
            "coupon": coupon,
        }
        session.modified = True

        # 3. Construimos la URL del banco y redirigimos
        success_url = url_for("order_success", _external=True, order_token=order_token)
        cancel_url = url_for("order_cancel", _external=True)
        payment_path = f"{BANKING_GATEWAY_URL}{BANKING_AUTH_KEY}/0/{total:.2f}"
        return_params = {"successUrl": success_url, "cancelUrl": cancel_url}
        final_gateway_url = payment_path + "?" + urllib.parse.urlencode(return_params)

        print("Redirigiendo a:", final_gateway_url)
        return redirect(final_gateway_url)

    # --- Lógica que se ejecuta SOLO al visitar la página (GET) ---
    # Si la petición no fue un POST, simplemente mostramos la página del formulario.
    billing_address = session.get("billing_address", {})
    return render_template(
        "checkout.html",
        cart=cart,
        subtotal=subtotal,
        total=total,
        discount_amount=discount_amount,
        billing_address=billing_address,
        body_class="page-checkout",
        coupons_enabled=COUPONS_ENABLED,
    )


# ==============================================================================
# === RUTAS DE AUTENTICACIÓN (OAUTH) ===========================================
# ==============================================================================


@app.route("/login")
def login():
    auth_url = f"{AUTHORIZATION_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope="
    return redirect(auth_url)


@app.route("/auth/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Error: No se recibió el código de autorización.", 400

    token_payload = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": code,
    }
    token_response = requests.post(TOKEN_URL, data=token_payload)
    token_data = token_response.json()
    if "access_token" not in token_data:
        return "Error: No se pudo obtener el token de acceso.", 400

    access_token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    user_response = requests.get(USER_API_URL, headers=headers)
    user_data = user_response.json()

    session["user"] = user_data.get("user")
    session["access_token"] = access_token

    return redirect(url_for("home"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


# ==============================================================================
# === RUTAS DE LA API DEL CARRITO ==============================================
# ==============================================================================


@app.route("/add_to_cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    try:
        product = find_product_by_id(product_id)
        if not product:
            return jsonify({"success": False, "message": "Producto no encontrado"}), 404

        data = request.get_json()
        selected_colors = data.get("colors", [])
        if not selected_colors:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Se debe seleccionar al menos un color",
                    }
                ),
                400,
            )

        if "cart" not in session:
            session["cart"] = {}

        cart = session["cart"]

        for color in selected_colors:
            cart_item_id = f"{product_id}-{color}"

            # --- ESTA ES LA LÓGICA CORREGIDA ---
            # Comprobamos si el color seleccionado existe en las variantes del producto
            variant_data = product.get("color_variants", {}).get(color)

            if cart_item_id not in cart and variant_data:
                cart[cart_item_id] = {
                    "id": product["id"],
                    "name": f"{product['name']} ({color})",
                    "price": product["price"],
                    "image": variant_data[
                        "image"
                    ],  # Accedemos a la imagen de la variante
                    "quantity": 1,
                    "color": color,
                    "download_file": variant_data[
                        "download_file"
                    ],  # Guardamos también el archivo de descarga
                }

        session.modified = True
        return jsonify({"success": True, "message": "Productos añadidos"})

    except Exception as e:
        # Si algo falla, lo imprimimos en la terminal para verlo
        print(f"!!! ERROR EN add_to_cart: {e}")
        return jsonify({"success": False, "message": "Error interno del servidor"}), 500


@app.route("/remove_from_cart/<string:cart_item_id>", methods=["POST"])
def remove_from_cart(cart_item_id):
    cart = session.get("cart", {})
    # Usamos el cart_item_id directamente, que ya es único (ej. "1-Black")
    if cart_item_id in cart:
        del cart[cart_item_id]
        session.modified = True
        return jsonify({"success": True, "message": "Producto eliminado"})
    return jsonify({"success": False, "message": "Producto no encontrado"}), 404


@app.route("/api/cart")
def get_cart_data():
    is_authenticated = "user" in session and session.get("user") is not None
    cart_data = session.get("cart", {})
    if not isinstance(cart_data, dict):
        session["cart"] = {}
        cart_data = {}
    return jsonify({"cart": cart_data, "isAuthenticated": is_authenticated})


# ==============================================================================
# === CONFIRMACIÓN DE PAGO    ==================================================
# ==============================================================================
# ARCHIVO: app.py


@app.route("/order/success")
def order_success():
    # Obtenemos el token de esta variable temporal en lugar de la URL
    token_from_session = session.pop("last_order_token", None)
    pending_order = session.get("pending_order")

    # La comprobación de seguridad ahora usa el token de la sesión
    if (
        not token_from_session
        or not pending_order
        or token_from_session != pending_order.get("token")
    ):
        return redirect(url_for("home"))

    # --- SI LA VERIFICACIÓN ES EXITOSA, PROCEDEMOS A CREAR EL PEDIDO ---

    # 3. Recuperamos los datos del pedido pendiente (en lugar de la sesión principal)
    cart = pending_order.get("cart", {})
    billing_address = pending_order.get("billing_address", {})
    coupon = pending_order.get(
        "coupon"
    )  # Usamos el cupón guardado en el pedido pendiente

    # Esto ya no es necesario, lo reemplazamos con los datos del pending_order
    # discount_info = session.get('order_discount', None)

    # Verificamos de nuevo que el carrito no esté vacío por si acaso
    if not cart:
        return redirect(url_for("home"))

    # --- GUARDAR DESCARGAS (Tu lógica original, ahora usando los datos seguros) ---
    # 1. Inicializamos la lista de descargas si no existe
    if "downloads" not in session:
        session["downloads"] = []

    # 2. Creamos una lista de los nuevos items a descargar de esta compra
    new_downloads = []
    for item in cart.values():
        new_downloads.append(
            {"name": item["name"], "download_file": item["download_file"]}
        )

    # 3. Añadimos los nuevos items al PRINCIPIO de la lista de descargas existente
    current_downloads = session.get("downloads", [])
    unique_new_downloads = [d for d in new_downloads if d not in current_downloads]
    session["downloads"] = unique_new_downloads + current_downloads

    # --- LÓGICA PARA CREAR Y GUARDAR EL PEDIDO (Tu lógica original) ---
    subtotal = sum(
        float(item["price"].replace("$", "")) * item["quantity"]
        for item in cart.values()
    )

    discount_amount = 0
    if coupon:
        if coupon["type"] == "percent":
            discount_amount = (subtotal * coupon["value"]) / 100
        else:
            discount_amount = coupon["value"]

    total = subtotal - discount_amount

    # 1. Creamos el objeto del pedido
    new_order = {
        "number": random.randint(1000, 9999),
        "date": datetime.now().strftime("%B %d, %Y"),
        "status": "Completed",
        "total": total,
        "products": list(cart.values()),
        "billing_address": billing_address,
    }

    # 2. Inicializamos la lista de pedidos en la sesión si no existe
    if "orders" not in session:
        session["orders"] = []

    # 3. Añadimos el nuevo pedido al PRINCIPIO de la lista
    session["orders"].insert(0, new_order)

    # 4. Limpiamos la sesión de los datos de la compra actual
    session.pop("pending_order", None)
    session.pop("cart", None)
    session.pop(
        "coupon", None
    )  # Limpiamos el cupón general, ya que 'pending_order' se ha ido
    session.modified = True

    # 5. Pasamos el pedido recién creado a la página de confirmación
    return render_template(
        "order_success.html", order=new_order, body_class="order-success-page"
    )


@app.route("/order/cancel")
def order_cancel():
    """
    Página a la que el usuario es redirigido si cancela el pago.
    """
    # No limpiamos el carrito aquí, porque el usuario puede querer intentarlo de nuevo
    # En lugar de un string HTML, renderizamos una plantilla para consistencia (puedes crearla después)
    # Por ahora, un mensaje simple está bien.
    return """
        <body style="background-color: #121212; color: #fff; text-align: center; font-family: sans-serif; padding-top: 5rem;">
            <h1>Pago cancelado</h1>
            <p>Tu pedido ha sido cancelado. Puedes volver al carrito e intentarlo de nuevo.</p>
            <a href="/checkout" style="color: #AFFF00;">Volver al Checkout</a>
        </body>
    """


# ==============================================================================
# === BLOQUE DE WISHLIST ==================================================
# ==============================================================================
@app.route("/api/wishlist")
def get_wishlist_data():
    return jsonify(session.get("wishlist", []))


@app.route("/wishlist")
def wishlist_page():
    wishlist_ids = session.get("wishlist", [])
    wishlist_products = [
        p for p in [find_product_by_id(pid) for pid in wishlist_ids] if p is not None
    ]
    breadcrumbs = [
        {"text": "Home", "url": url_for("home")},
        {"text": "Wishlist", "url": None},
    ]
    return render_template(
        "wishlist.html",
        wishlist=wishlist_products,
        breadcrumbs=breadcrumbs,
        active_page="wishlist",
        body_class="page-full-width",
    )


@app.route("/api/toggle_wishlist/<int:product_id>", methods=["POST"])
def toggle_wishlist(product_id):
    """
    Añade un producto a la wishlist si no está, o lo elimina si ya está.
    Devuelve el estado final.
    """
    if "wishlist" not in session:
        session["wishlist"] = []

    # Comprobamos el estado actual
    if product_id in session["wishlist"]:
        # Si ya está, lo eliminamos
        session["wishlist"].remove(product_id)
        session.modified = True
        return jsonify(
            {
                "success": True,
                "added": False,  # Le decimos al frontend que se eliminó
                "message": "Product removed from wishlist.",
            }
        )
    else:
        # Si no está, lo añadimos
        session["wishlist"].append(product_id)
        session.modified = True
        return jsonify(
            {
                "success": True,
                "added": True,  # Le decimos al frontend que se añadió
                "message": "Product added to wishlist.",
            }
        )


@app.route("/api/remove_from_wishlist/<int:product_id>", methods=["POST"])
def remove_from_wishlist(product_id):
    if "wishlist" in session and product_id in session["wishlist"]:
        session["wishlist"].remove(product_id)
        session.modified = True
        return jsonify({"success": True, "message": "Product removed from wishlist."})
    return jsonify({"success": False, "message": "Product not found in wishlist."}), 404


# ==============================================================================
# === APLICAR CUPONES         ==================================================
# ==============================================================================


@app.route("/api/apply_coupon", methods=["POST"])
def apply_coupon():

    # 1. Comprobamos si el sistema de cupones está activado
    if not COUPONS_ENABLED:
        return (
            jsonify({"success": False, "message": "Coupons are currently disabled."}),
            403,
        )

    data = request.get_json()
    coupon_code = data.get("coupon_code", "").upper()  # Convertimos a mayúsculas

    if coupon_code in VALID_COUPONS:
        session["coupon"] = VALID_COUPONS[coupon_code]
        session["coupon"]["code"] = coupon_code  # Guardamos el código original
        session.modified = True
        return jsonify({"success": True, "message": "Coupon applied successfully!"})

    return jsonify({"success": False, "message": "Invalid coupon code."}), 400


@app.route("/api/remove_coupon", methods=["POST"])
def remove_coupon():
    if "coupon" in session:
        session.pop("coupon", None)
        session.modified = True
    return jsonify({"success": True})


@app.route("/download/<filename>")
def download_file(filename):
    """Ruta segura para servir archivos desde la carpeta 'downloads'."""
    # En una aplicación real, aquí comprobarías si el usuario tiene permiso
    # para descargar este archivo (ej. si lo ha comprado).

    # 'as_attachment=True' fuerza la descarga en lugar de abrir el archivo en el navegador.
    return send_from_directory("static/downloads", filename, as_attachment=True)


# ==============================================================================
# === INICIO DE LA APLICACIÓN ==================================================
# ==============================================================================

if __name__ == "__main__":
    # Usamos host='0.0.0.0' para que sea accesible desde fuera de tu PC (necesario para el despliegue)
    app.run(debug=True, host="0.0.0.0")
