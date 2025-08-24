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
from datetime import datetime

app = Flask(__name__)

# ==============================================================================
# === CONFIGURACIÓN Y DATOS ====================================================
# ==============================================================================

# --- CONFIGURACIÓN DE LA APP Y OAUTH ---
# Tu Client Secret debe ser privado. Idealmente, se carga desde variables de entorno.
app.secret_key = "KnChzlbMneQFKL1yMbeUji0juPLQCMKT1h0C4eXE"
CLIENT_ID = "62"
CLIENT_SECRET = "KnChzlbMneQFKL1yMbeUji0juPLQCMKT1h0C4eXE"

# Asegúrate de que esta URL está registrada en el panel de GTA.world
# Para desarrollo local, debería ser: 'http://127.0.0.1:5000/auth/callback'
REDIRECT_URI = "https://vibezp.onrender.com/auth/callback"

AUTHORIZATION_URL = "https://ucp.gta.world/oauth/authorize"
TOKEN_URL = "https://ucp.gta.world/oauth/token"
USER_API_URL = "https://ucp.gta.world/api/user"

#### API KEY DE BANKING
BANKING_GATEWAY_URL = "https://banking.gta.world/gateway/"
BANKING_AUTH_KEY = "0EkAqPyV7mx2NVvoni2TV1O3KXIiOVTWZ3dFtR6d5BRSlNbIWZgBSxAzr3Q4ExPQ"

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
]
# --- CUPONES
VALID_COUPONS = {
    "VIBE5": {"type": "percent", "value": 5},  # 5% de descuento
    "CLOTH1": {"type": "percent", "value": 10},  # 10% de descuento
    "VZ2604": {"type": "fixed", "value": 15},  # $15 de descuento fijo
    "SAVEBIG": {"type": "percent", "value": 25},  # 25% de descuento
    "TAKE10": {"type": "fixed", "value": 10},  # $10 de descuento fijo
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


@app.route("/")
def home():
    # Mostraremos los últimos 8 productos, por ejemplo.
    latest_products = all_products[:8]

    return render_template(
        "index.html",
        active_page="home",
        body_class="page-home",
        products=latest_products,
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
    cart = session.get("cart", {})
    if not cart:
        return redirect(url_for("home"))

    # Recuperamos la dirección de facturación guardada, si existe
    billing_address = session.get("billing_address", {})

    subtotal = sum(
        float(item["price"].replace("$", "")) * item["quantity"]
        for item in cart.values()
    )

    # --- LÓGICA DE CUPÓN ---
    coupon = session.get("coupon")
    discount_amount = 0
    if coupon:
        if coupon["type"] == "percent":
            discount_amount = (subtotal * coupon["value"]) / 100
        elif coupon["type"] == "fixed":
            discount_amount = coupon["value"]

    total = max(
        0, subtotal - discount_amount
    )  # Aseguramos que el total no sea negativo

    if request.method == "POST":

        # 1. Recopilamos los datos del cliente del formulario
        billing_address = {
            "firstname": request.form.get("firstname"),
            "lastname": request.form.get("lastname"),
            "apartment": request.form.get("apartment"),
            "discord": request.form.get("discord"),
            "phone": request.form.get("phone"),
        }
        # 2. Guardamos la dirección de facturación en la sesión
        session["billing_address"] = billing_address

        if coupon:
            session["order_discount"] = {
                "code": coupon["code"],
                "amount": discount_amount,
            }

        session.modified = True

        payment_path = f"{BANKING_GATEWAY_URL}{BANKING_AUTH_KEY}/0/{total:.2f}"

        # (El resto de la lógica para los parámetros de retorno es opcional pero recomendado)
        return_params = {
            "successUrl": url_for("order_success", _external=True),
            "cancelUrl": url_for("order_cancel", _external=True),
        }
        final_gateway_url = f"{BANKING_GATEWAY_URL}{BANKING_AUTH_KEY}/0/{total:.2f}"

        print("Redirigiendo a:", final_gateway_url)

        return redirect(final_gateway_url)

    # La parte del GET no cambia
    return render_template(
        "checkout.html",
        cart=cart,
        subtotal=subtotal,
        total=total,
        active_page="checkout",
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
@app.route("/order/success")
def order_success():
    cart = session.get("cart", {})
    # LEEMOS los datos de la sesión. Si no existen, usamos un dict vacío para evitar errores.
    billing_address = session.get("billing_address", {})
    # Leemos los datos del descuento de la sesión
    discount_info = session.get("order_discount", None)

    if (
        not cart and not billing_address
    ):  # Si no hay ni carrito ni dirección, es un acceso inválido
        return redirect(url_for("home"))

    # Calculamos subtotal y total de nuevo para la confirmación
    subtotal = sum(
        float(item["price"].replace("$", "")) * item["quantity"]
        for item in cart.values()
    )
    discount_amount = discount_info["amount"] if discount_info else 0
    total = subtotal - discount_amount

    order_details = {
        "number": random.randint(1000, 9999),
        "date": datetime.now().strftime("%B %d, %Y"),
        "subtotal": "%.2f" % subtotal,
        "total": "%.2f" % total,
        "discount_info": discount_info,  # Pasamos la info del descuento
        "payment_method": "Fleeca Bank",
        "products": list(cart.values()),
        "billing_address": billing_address,
    }

    session.pop("cart", None)
    session.pop("billing_address", None)
    session.pop("order_discount", None)

    return render_template(
        "order_success.html", order=order_details, body_class="order-success-page"
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
