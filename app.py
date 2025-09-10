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
from datetime import datetime
import pytz
import requests, urllib.parse, random, secrets
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

app = Flask(__name__)
# --- CONFIGURACIÓN ---
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///vibez.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ==============================================================================
# === CONFIGURACIÓN Y DATOS ====================================================
# ==============================================================================

app.secret_key = "y2PRyodNyyzu1mzZa2hTJy8tGP0MKDkJ8GQbuSbR"
CLIENT_ID = "76"
CLIENT_SECRET = "y2PRyodNyyzu1mzZa2hTJy8tGP0MKDkJ8GQbuSbR"
REDIRECT_URI = "https://vibezcloth.onrender.com/auth/callback"
AUTHORIZATION_URL = "https://ucp.gta.world/oauth/authorize"
TOKEN_URL = "https://ucp.gta.world/oauth/token"
USER_API_URL = "https://ucp.gta.world/api/user"
BANKING_GATEWAY_URL = "https://banking.gta.world/gateway/"
BANKING_AUTH_KEY = "xmD0M1OUh2n2scx1VJb8kU2yAwKyaqIVbTXXfwZL90FY51sijBwysY7sLZao3fQu"
COUPONS_ENABLED = True


# --- MODELOS DE DATOS ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    orders = db.relationship("Order", backref="user", lazy=True)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Completed")
    payment_method = db.Column(
        db.String(50), nullable=False, default="Fleeca Bank"
    )  # <-- CAMPO AÑADIDO
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    items = db.relationship(
        "OrderItem", backref="order", lazy=True, cascade="all, delete-orphan"
    )
    billing_address = db.relationship(
        "BillingAddress", backref="order", uselist=False, cascade="all, delete-orphan"
    )


# NUEVA TABLA para guardar la dirección
class BillingAddress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    apartment = db.Column(db.String(200))
    discord = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    # CORRECCIÓN: Le decimos que el order_id debe ser único, ya que cada pedido solo tiene una dirección
    order_id = db.Column(
        db.Integer, db.ForeignKey("order.id"), unique=True, nullable=False
    )


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    download_file = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)  # <-- AÑADE ESTA LÍNEA
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)


# (Aquí podrías añadir un modelo 'Product' en el futuro si quieres gestionar los productos desde una DB)

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
        "category": "man",
        "name": "Vibez Jean",
        "price": "$4500",
        "slug": "vibez-jean-man",
        "sku": "VM-047",
        "color_variants": {
            "Black": {  # Color 'Negro' usa la imagen woman1.png
                "image": "images/jeannegro.png",
                "download_file": "Black-Man.zip",
            },
            "Gray": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/jeangris.png",
                "download_file": "Gray-Man.zip",
            },
            "Light Blue": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/azulclaro.png",
                "download_file": "Light-Blue-Man.zip",
            },
            "Normal": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/jean.png",
                "download_file": "Normal-Man.zip",
            },
            "Light Blue 2": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/lightblue2.png",
                "download_file": "Light-Blue2.zip",
            },
            "Light Black": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/lightblack.png",
                "download_file": "Light-Black.zip",
            },
            "Black 2": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/jeanblackblack.png",
                "download_file": "Jean-Black2.zip",
            },
            "Dark Blue": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/jeanblue.png",
                "download_file": "Jean-DarkBlue.zip",
            },
            "Gray 2": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/jeangray.png",
                "download_file": "Jean-Gray2.zip",
            },
            "White": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/jeanwhite.png",
                "download_file": "Jean-White.zip",
            },
        },
    },
    {
        "id": 5,
        "category": "woman",
        "name": "Vibez Jeans",
        "price": "$4500",
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
        "price": "$4000",
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
        "price": "$7000",
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
    {
        "id": 9,
        "category": "accessories",
        "name": "Skateboards",
        "price": "$2000",
        "slug": "skateboards",
        "sku": "SB-001",
        "color_variants": {
            "Dark Star": {  # Color 'Negro' usa la imagen woman1.png
                "image": "images/DarkStar.png",
                "download_file": "DarkStar.zip",
            },
            "Santa Cruz": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/SantaCruz.png",
                "download_file": "SantaCruz.zip",
            },
            "Seven Inch Girl": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/SevenInch.png",
                "download_file": "SevenInch-Girl.zip",
            },
            "Seven Inch Blue": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/SevenInch2.png",
                "download_file": "SevenInch-Blue.zip",
            },
            "American": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/USA.png",
                "download_file": "American.zip",
            },
        },
    },
    {
        "id": 10,
        "category": "woman",
        "name": "Cropped Hoodie",
        "price": "$6600",
        "slug": "cropped-hoodie",
        "sku": "CH-008",
        "color_variants": {
            "Depravity": {  # Color 'Azul' uses the image depravity.png
                "image": "images/depravity.png",
                "download_file": "Depravity.zip",
            },
            "Dream Big": {  # Color 'Azul' uses the image drambig.png
                "image": "images/drambig.png",
                "download_file": "DreamBig.zip",
            },
            "Dystopia": {  # Color 'Azul' uses the image dystopia.png
                "image": "images/dystopia.png",
                "download_file": "Dystopia.zip",
            },
            "Kuromi": {  # Color 'Azul' uses the image kuromi.png
                "image": "images/kuromi.png",
                "download_file": "Kuromi.zip",
            },
            "Red L.": {  # Color 'Azul' uses the image lettering.png
                "image": "images/lettering.png",
                "download_file": "Red-L.zip",
            },
            "Run Away": {  # Color 'Azul' uses the image runaway.png
                "image": "images/runaway.png",
                "download_file": "Run-Away.zip",
            },
            "Stucked": {  # Color 'Azul' uses the image stucked.png
                "image": "images/stucked.png",
                "download_file": "Stuck.zip",
            },
            "Blue": {  # Color 'Azul' uses the image azuls.png
                "image": "images/azuls.png",
                "download_file": "Blue.zip",
            },
            "White": {  # Color 'Azul' uses the image blancos.png
                "image": "images/blancos.png",
                "download_file": "White.zip",
            },
            "Brown": {  # Color 'Azul' uses the image marrons.png
                "image": "images/marrons.png",
                "download_file": "Brown.zip",
            },
            "Black": {  # Color 'Azul' uses the image negros.png
                "image": "images/negros.png",
                "download_file": "Black.zip",
            },
            "Pink": {  # Color 'Azul' uses the image rosas.png
                "image": "images/rosas.png",
                "download_file": "Pink.zip",
            },
        },
    },
    {
        "id": 11,
        "category": "man",
        "name": "Simple Hoddie",
        "price": "$6600",
        "slug": "hoddie",
        "sku": "SH-001",
        "color_variants": {
            "Angel": {  # Color 'Negro' usa la imagen woman1.png
                "image": "images/Angel.png",
                "download_file": "Angel.zip",
            },
            "Inferno": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Inferno.png",
                "download_file": "Inferno.zip",
            },
            "Lil Vert": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Lilvert.png",
                "download_file": "Lil-Vert.zip",
            },
            "Maquinary": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/maquinary.png",
                "download_file": "Maquinary.zip",
            },
            "Tyler": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Tyler.png",
                "download_file": "Tyler.zip",
            },
            "Black": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Blackhoddie.png",
                "download_file": "Blackhoddie.zip",
            },
        },
    },
    {
        "id": 12,
        "category": "man",
        "name": "Grunge T-Shirts",
        "price": "$6000",
        "slug": "grunge-tshirts-man",
        "sku": "GS-051",
        "color_variants": {
            "Darklight": {  # Color 'Negro' usa la imagen woman1.png
                "image": "images/Darklightman.png",
                "download_file": "Darklight.zip",
            },
            "21Savage": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/21Savage.png",
                "download_file": "21Savage.zip",
            },
            "Ghost": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Ghost.png",
                "download_file": "Ghost.zip",
            },
            "Eazy-E": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Eazye.png",
                "download_file": "Eazy-E.zip",
            },
            "Black Sabbath": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/blacksabbathman.png",
                "download_file": "BlackSabbath.zip",
            },
            "Hangxiety": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Hangxiety.png",
                "download_file": "Hangxiety.zip",
            },
            "Marlboro": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Marlboro.png",
                "download_file": "Marlboro.zip",
            },
            "Supra": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Supra.png",
                "download_file": "Supra.zip",
            },
            "Split": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Split.png",
                "download_file": "Split.zip",
            },
            "Zillakami": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Zillakami.png",
                "download_file": "Zillakami.zip",
            },
        },
    },
    {
        "id": 13,
        "category": "accessories",
        "name": "Phone Cases",
        "price": "$5000",
        "slug": "phone-cases",
        "sku": "PC-050",
        "color_variants": {
            "VG Vibe": {  # Color 'Negro' usa la imagen woman1.png
                "image": "images/VG Vibe.png",
                "download_file": "VG Vibe.zip",
            },
            "Black Grunge": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Black grunge.png",
                "download_file": "Black grunge.zip",
            },
            "Rose Grunge": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Rose Grunge.png",
                "download_file": "Rose Grunge.zip",
            },
            "Noir Script": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Noir Script.png",
                "download_file": "Noir Script-E.zip",
            },
            "Hype Collage": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Hype Collage.png",
                "download_file": "Hype Collage.zip",
            },
            "Lost notes": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Lost notes.png",
                "download_file": "Lost notes.zip",
            },
            "Stare drip": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Stare drip.png",
                "download_file": "Stare drip.zip",
            },
            "Pink Chaos": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Pink Chaos.png",
                "download_file": "Pink Chaos.zip",
            },
        },
    },
    {
        "id": 14,
        "category": "man",
        "name": "Oversized T-Shirts",
        "price": "$5000",
        "slug": "phone-cases",
        "sku": "OV-050",
        "color_variants": {
            "Download": {  # Color 'Negro' usa la imagen woman1.png
                "image": "images/Download.png",
                "download_file": "Download.zip",
            },
            "Metallica": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Metallicaman.png",
                "download_file": "Metallica-man.zip",
            },
            "S.O.C": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/SOC.png",
                "download_file": "SOC.zip",
            },
            "Suffocation": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Suffocationman.png",
                "download_file": "Suffocation-man.zip",
            },
            "Sinner": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Sinner.png",
                "download_file": "Sinner.zip",
            },
        },
    },
    {
        "id": 15,
        "category": "woman",
        "name": "Gothic Pearl Cross Choker",
        "price": "$3700",
        "slug": "cross-choker",
        "sku": "CS-050",
        "color_variants": {
            "Plate": {  # Color 'Negro' usa la imagen woman1.png
                "image": "images/Plate.png",
                "download_file": "Plate-Cross-Choker.zip",
            },
            "Bronze": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Bronze.png",
                "download_file": "Bronze-Cross-Choker.zip",
            },
        },
    },
    {
        "id": 16,
        "category": "woman",
        "name": "Gothic Cascade Ear Cuff",
        "price": "$3700",
        "slug": "ear-cuff",
        "sku": "CS-050",
        "color_variants": {
            "Gray & Black": {  # Color 'Negro' usa la imagen woman1.png
                "image": "images/GB-GCEC.png",
                "download_file": "GB-GCEC.zip",
            },
            "Black": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Black-GCEC.png",
                "download_file": "Black-GCEC.zip",
            },
            "White": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/White-GCEC.png",
                "download_file": "White-GCEC.zip",
            },
            "Black & Gold": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/BG-GCEC.png",
                "download_file": "BG-GCEC.zip",
            },
            "White & Gold": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/WG-GCEC.png",
                "download_file": "WG-GCEC4.zip",
            },
        },
    },
    {
        "id": 17,
        "category": "woman",
        "name": "Midnight Cross Earrings",
        "price": "$3700",
        "slug": "cross-earrings",
        "sku": "CE-050",
        "color_variants": {
            "Black": {  # Color 'Negro' usa la imagen woman1.png
                "image": "images/Midnight-Cross-Earrings.png",
                "download_file": "Midnight-Cross-Earrings.zip",
            },
        },
    },
    {
        "id": 18,
        "category": "woman",
        "name": "After Dark Vibez Jeans",
        "price": "$4500",
        "slug": "after-dark",
        "sku": "VJ-050",
        "color_variants": {
            "Black": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Black-ADVJ.png",
                "download_file": "Black-ADVJ.zip",
            },
            "White": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/White-ADVJ.png",
                "download_file": "White-ADVJ.zip",
            },
            "Green": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Green-ADVJ.png",
                "download_file": "Green-ADVJ.zip",
            },
            "Pink": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Pink-ADVJ.png",
                "download_file": "Pink-ADVJ.zip",
            },
        },
    },
    {
        "id": 19,
        "category": "woman",
        "name": "Vibez Riot Jeans",
        "price": "$4500",
        "slug": "riot-jeans",
        "sku": "VJ-051",
        "color_variants": {
            "Dark": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Dark-VRJ.png",
                "download_file": "Dark-VRJ.zip",
            },
            "White": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/White-VRJ.png",
                "download_file": "White-VRJ.zip",
            },
            "Red": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Red-VRJ.png",
                "download_file": "Red-VRJ.zip",
            },
            "Black": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Black-VRJ.png",
                "download_file": "Black-VRJ.zip",
            },
            "Blue": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Blue-VRJ.png",
                "download_file": "Blue-VRJ.zip",
            },
        },
    },
    {
        "id": 20,
        "category": "woman",
        "name": "Vibez Summer Classic Shorts",
        "price": "$4500",
        "slug": "summer-shorts",
        "sku": "VJ-052",
        "color_variants": {
            "Black": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Black-VSCS.png",
                "download_file": "Black-VSCS.zip",
            },
            "White": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/White-VSCS.png",
                "download_file": "White-VSCS.zip",
            },
            "Blue": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Blue-VSCS.png",
                "download_file": "Blue-VSCS.zip",
            },
            "Gray": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Gray-VSCS.png",
                "download_file": "Gray-VSCS.zip",
            },
        },
    },
    {
        "id": 21,
        "category": "woman",
        "name": "Sunset Glow Top",
        "price": "$5000",
        "slug": "glow-top",
        "sku": "ST-052",
        "color_variants": {
            "Pink": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Pink-SGT.png",
                "download_file": "Pink-SGT.zip",
            },
            "Black": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Black-SGT.png",
                "download_file": "Black-SGT.zip",
            },
            "Blue": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Blue-SGT.png",
                "download_file": "Blue-SGT.zip",
            },
            "Green": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Green-SGT.png",
                "download_file": "Green-SGT.zip",
            },
            "Red": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Red-SGT.png",
                "download_file": "Red-SGT.zip",
            },
            "Yellow": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Yellow-SGT.png",
                "download_file": "Gray-SGT.zip",
            },
        },
    },
    {
        "id": 22,
        "category": "woman",
        "name": "Sweet & Slouchy Set",
        "price": "$5000",
        "slug": "slouchy-set",
        "sku": "SS-052",
        "color_variants": {
            "Worn-out": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Worn-out-SS.png",
                "download_file": "Worn-out-SS.zip",
            },
            "Black Rose": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Rose-SS.png",
                "download_file": "Rose-SS.zip",
            },
            "Black": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Black-SS.png",
                "download_file": "Black-SS.zip",
            },
            "Gray Cross": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/GrayCross-SS.png",
                "download_file": "GrayCross-SS.zip",
            },
            "Green": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Green-SS.png",
                "download_file": "Green-SS.zip",
            },
            "Pink": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Pink-SS.png",
                "download_file": "Pink-SS.zip",
            },
        },
    },
    {
        "id": 23,
        "category": "woman",
        "name": "Striped Sleeve Grunge Top",
        "price": "$5500",
        "slug": "stripped-sleeve",
        "sku": "SS-053",
        "color_variants": {
            "Nirvana-Y": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Nirvana-Yellow.png",
                "download_file": "Nirvana-Yellow.zip",
            },
            "Sinner-G": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Sinner-Green.png",
                "download_file": "Sinner-Green.zip",
            },
            "Sinner-W": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Sinner-Black.png",
                "download_file": "Sinner-Black.zip",
            },
            "Sweetheart-P": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Sweetheart-Pink.png",
                "download_file": "Sweetheart-Pink.zip",
            },
            "Sweetheart-W": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Sweetheart-White.png",
                "download_file": "Sweetheart-White.zip",
            },
            "Digital Monster-Y": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Digital-Yellow.png",
                "download_file": "Digital-Yellow.zip",
            },
            "Sweetheart": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Sweetheart.png",
                "download_file": "Sweetheart.zip",
            },
            "Smile": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Smile.png",
                "download_file": "Smile.zip",
            },
            "Sinner-Y": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Sinner-Yellow.png",
                "download_file": "Sinner-Yellow.zip",
            },
            "Nirvana-B": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Nirvana-Black.png",
                "download_file": "Nirvana-Black.zip",
            },
            "Digital Monster-P": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Digital-Pink.png",
                "download_file": "Digital-Pink.zip",
            },
            "Sinner-O": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Sinner-Orange.png",
                "download_file": "Sinner-Orange.zip",
            },
            "Sinner-R": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Sinner-Red.png",
                "download_file": "Sinner-Red.zip",
            },
            "Sinner-B": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Sinner-White.png",
                "download_file": "Sinner-White.zip",
            },
        },
    },
    {
        "id": 24,
        "category": "woman",
        "name": "Plaid Punk Mini Skirt",
        "price": "$4500",
        "slug": "skirt-punk",
        "sku": "SP-053",
        "color_variants": {
            "Black": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Black-Skirt.png",
                "download_file": "Black-Skirt.zip",
            },
            "Green": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Green-Skirt.png",
                "download_file": "Green-Skirt.zip",
            },
            "Pink": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Pink-Skirt.png",
                "download_file": "Pink-Skirt.zip",
            },
            "Purple": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Purple-Skirt.png",
                "download_file": "Purple-Skirt.zip",
            },
            "Red": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Red-Skirt.png",
                "download_file": "Red-Skirt.zip",
            },
            "Yellow": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Yellow-Skirt.png",
                "download_file": "Yellow-Skirt.zip",
            },
        },
    },
    {
        "id": 25,
        "category": "woman",
        "name": "Cross Pocket Skirt",
        "price": "$4500",
        "slug": "pocket-skirt",
        "sku": "SP-053",
        "color_variants": {
            "Black": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Black-PS.png",
                "download_file": "Black-PS.zip",
            },
            "Green": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Green-PS.png",
                "download_file": "Green-PS.zip",
            },
            "Pink": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Pink-PS.png",
                "download_file": "Pink-PS.zip",
            },
            "Blue": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Blue-PS.png",
                "download_file": "Blue-PS.zip",
            },
            "White": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/White-PS.png",
                "download_file": "White-PS.zip",
            },
        },
    },
    {
        "id": 26,
        "category": "woman",
        "name": "Cropped Denim Jacket",
        "price": "$4200",
        "slug": "denim-jacket",
        "sku": "DJ-053",
        "color_variants": {
            "Blue": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Blue-DJ.png",
                "download_file": "Blue-DJ.zip",
            },
            "Gray": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Gray-DJ.png",
                "download_file": "Gray-DJ.zip",
            },
            "Light Blue": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/LightBlue-DJ.png",
                "download_file": "LightBlue-DJ.zip",
            },
            "White": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/White-DJ.png",
                "download_file": "White-DJ.zip",
            },
        },
    },
    {
        "id": 27,
        "category": "woman",
        "name": "Oversized Sweatshirt",
        "price": "$5000",
        "slug": "oversized-sweatshirt",
        "sku": "OS-050",
        "color_variants": {
            "Comic": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Comic-OS.png",
                "download_file": "Comic-OS.zip",
            },
            "White": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/White-OS.png",
                "download_file": "White-OS.zip",
            },
            "Black": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Black-OS.png",
                "download_file": "Black-OS.zip",
            },
            "Kenzo": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Kenzo-OS.png",
                "download_file": "Kenzo-OS.zip",
            },
            "Pink": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Pink-OS.png",
                "download_file": "Pink-OS.zip",
            },
        },
    },
    {
        "id": 28,
        "category": "woman",
        "name": "Classic Zip-Up Hoodie",
        "price": "$4200",
        "slug": "classic-hoodie",
        "sku": "CH-053",
        "color_variants": {
            "Gray": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Gray-CH.png",
                "download_file": "Gray-CH.zip",
            },
            "Gray Lettering": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Lettering-CH.png",
                "download_file": "Lettering-CH.zip",
            },
            "Pink": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Pink-CH.png",
                "download_file": "Pink-CH.zip",
            },
            "Brown": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Brown-CH.png",
                "download_file": "Brown-CH.zip",
            },
            "Black": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Black-CH.png",
                "download_file": "Black-CH.zip",
            },
        },
    },
    {
        "id": 29,
        "category": "woman",
        "name": "Grunge Skirt & Hoodie Jacket Set",
        "price": "$6500",
        "slug": "grunge-hoodie",
        "sku": "GH-050",
        "color_variants": {
            "Pink": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Pink-GH.png",
                "download_file": "Pink-GH.zip",
            },
            "Skeleton-B": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Skeleton-GH.png",
                "download_file": "Skeleton-GH.zip",
            },
            "Clouds-B": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Clouds-B.png",
                "download_file": "Clouds-B.zip",
            },
            "Hello Kitty": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/HelloKitty-GH.png",
                "download_file": "HelloKitty-GH.zip",
            },
            "Black": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Black-GH.png",
                "download_file": "Black-GH.zip",
            },
            "Anime": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Anime-GH.png",
                "download_file": "Anime-GH.zip",
            },
            "Himiko": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Himiko-GH.png",
                "download_file": "Himiko-GH.zip",
            },
            "Green": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Green-GH.png",
                "download_file": "Green-GH.zip",
            },
            "Skeleton-R": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Red-GH.png",
                "download_file": "Red-GH.zip",
            },
            "Clouds-P": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/PinkClouds-GH.png",
                "download_file": "PinkClouds-GH.zip",
            },
            "Anime Eyes": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/AnimeEyes-GH.png",
                "download_file": "AnimeEyes-GH.zip",
            },
        },
    },
    {
        "id": 30,
        "category": "woman",
        "name": "Heart & Star Earrings",
        "price": "$3700",
        "slug": "heart-earrings",
        "sku": "CH-053",
        "color_variants": {
            "Gold": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Gold-HSE.png",
                "download_file": "Gold-HSE.zip",
            },
            "Black": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Black-HSE.png",
                "download_file": "Black-HSE.zip",
            },
            "Bronze": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Bronze-HSE.png",
                "download_file": "Bronze-HSE.zip",
            },
            "Plate": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Plate-HSE.png",
                "download_file": "Plate-HSE.zip",
            },
        },
    },
    {
        "id": 31,
        "category": "woman",
        "name": "Urban Cap",
        "price": "$3000",
        "slug": "urban-cap",
        "sku": "UC-100",
        "color_variants": {
            "Black": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Black-Cap.png",
                "download_file": "Black-Cap.zip",
            },
            "Blue": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Blue-Cap.png",
                "download_file": "Blue-Cap.zip",
            },
            "God's Favorite": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Favorite-Cap.png",
                "download_file": "Favorite-Cap.zip",
            },
            "Military": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Military-Cap.png",
                "download_file": "Military-Cap.zip",
            },
             "Stars": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Stars-Cap.png",
                "download_file": "Stars-Cap.zip",
            },
            "Sunshine & Whiskey": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/Sunshine-Cap.png",
                "download_file": "Sunshine-Cap.zip",
            },
            "VonDutch": {  # Color 'Azul' usa la imagen woman3.jpg
                "image": "images/VonDutch-Cap.png",
                "download_file": "VonDutch-Cap.zip",
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
COUPONS_ENABLED = True


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
    # CORRECCIÓN: Comprobamos 'user_id', la clave correcta de la sesión.
    if "user_id" not in session:
        return redirect(url_for("login"))

    breadcrumbs = [
        {"text": "Home", "url": url_for("home")},
        {"text": "My Account", "url": None},
    ]
    return render_template(
        "my_account.html", active_page="my-account", breadcrumbs=breadcrumbs
    )


@app.route("/my-account/orders")
def my_account_orders():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])

    # --- NUEVA COMPROBACIÓN DE SEGURIDAD ---
    if user is None:
        # Si el usuario de la sesión no se encuentra en la DB, la sesión es inválida.
        session.clear()  # Limpiamos la sesión corrupta
        return redirect(url_for("login"))  # Forzamos a que inicie sesión de nuevo

    orders = sorted(user.orders, key=lambda x: x.date, reverse=True)
    return render_template("orders.html", orders=orders, active_page="my-account")


@app.route("/my-account/downloads")
def my_account_downloads():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])

    if user is None:
        session.clear()
        return redirect(url_for("login"))

    # --- LÓGICA CORREGIDA ---
    # 1. Obtenemos todos los items de todos los pedidos del usuario
    downloads = [item for order in user.orders for item in order.items]

    # 2. Ordenamos la lista de items basándonos en la fecha del pedido al que pertenecen
    downloads.sort(key=lambda x: x.order.date, reverse=True)

    return render_template(
        "downloads.html", downloads=downloads, active_page="my-account"
    )


# @app.route("/my-account/details")
# def my_account_details():
#    """Muestra la página de detalles de la cuenta del usuario."""
#    # CORRECCIÓN: Comprobamos 'user_id'.
#    if "user_id" not in session:
#        return redirect(url_for("login"))
#
#    # Usamos 'user_info' para mostrar el nombre, que es correcto.
#    user_data = session.get("user_info")
#    return render_template(
#        "account_details.html", user=user_data, active_page="my-account"
#    )


@app.route("/my-account/view-order/<string:order_number>")
def view_order_page(order_number):
    """Muestra los detalles de un pedido específico desde la base de datos."""
    if "user_id" not in session:
        return redirect(url_for("login"))

    # --- BÚSQUEDA EN LA BASE DE DATOS ---
    # Buscamos el pedido por su número de orden Y nos aseguramos de que pertenezca al usuario actual
    order_to_view = Order.query.filter_by(
        order_number=order_number, user_id=session["user_id"]
    ).first()

    if not order_to_view:
        # Si no se encuentra el pedido o no pertenece a este usuario, redirigimos
        return redirect(url_for("my_account_orders"))

    # --- CÁLCULO DE SUBTOTAL ---
    # En un sistema real, el subtotal y descuento se guardarían en la DB.
    # Por ahora, como no lo hacemos, el subtotal es el total.
    # En el futuro, podrías recalcular el descuento aquí si fuera necesario.
    subtotal = order_to_view.total

    return render_template(
        "view_order.html",
        order=order_to_view,
        subtotal=subtotal,
        active_page="my-account",
    )


@app.route("/")
def home():
    return render_template(
        "index.html", active_page="home", body_class="page-home", products=all_products
    )


@app.route('/<category_name>')
def category_page(category_name):
    if category_name not in ['woman', 'man', 'accessories']:
        abort(404)
    
    # --- LÓGICA DE PAGINACIÓN ---
    # 1. Obtenemos el número de página de la URL (ej. /woman?page=2). Si no se especifica, es la página 1.
    page = request.args.get('page', 1, type=int)
    ITEMS_PER_PAGE = 12 # Definimos el máximo de artículos por página

    # 2. Obtenemos la lista COMPLETA de productos para esta categoría
    all_products_in_category = get_products_by_category(category_name)
    
    # 3. Calculamos el "trozo" de la lista que corresponde a la página actual
    start_index = (page - 1) * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE
    paginated_products = all_products_in_category[start_index:end_index]

    # 4. Calculamos el número total de páginas necesarias
    total_products = len(all_products_in_category)
    # Usamos una división entera para redondear hacia arriba
    total_pages = (total_products + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    
    breadcrumbs = [
        {'text': 'Home', 'url': url_for('home')},
        {'text': category_name.upper(), 'url': None}
    ]
    
    # 5. Pasamos solo los productos de ESTA PÁGINA y la info de paginación a la plantilla
    return render_template('category.html', 
                           title=category_name.capitalize(), 
                           products=paginated_products, # Solo los 12 (o menos) productos de esta página
                           active_page=category_name,
                           breadcrumbs=breadcrumbs,
                           # Nuevas variables para la paginación:
                           current_page=page, 
                           total_pages=total_pages)


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
    # --- Lógica GET (se ejecuta al visitar la página) ---
    if request.method == "GET":
        cart = session.get("cart", {})
        if not cart:
            return redirect(url_for("home"))

        billing_address = session.get("billing_address", {})
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

    # --- Lógica POST (se ejecuta al hacer clic en "Place Order") ---
    if request.method == "POST":
        cart = session.get("cart", {})
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

        billing_address = {
            "firstname": request.form.get("firstname"),
            "lastname": request.form.get("lastname"),
            "apartment": request.form.get("apartment"),
            "discord": request.form.get("discord"),
            "phone": request.form.get("phone"),
        }

        session["pending_order"] = {
            "cart": cart,
            "billing_address": billing_address,
            "coupon": coupon,
        }
        session.modified = True

        # Construimos la URL LIMPIA, sin parámetros de consulta.
        final_gateway_url = f"{BANKING_GATEWAY_URL}{BANKING_AUTH_KEY}/0/{total:.2f}"

        print("Redirigiendo a:", final_gateway_url)
        return redirect(final_gateway_url)


# ==============================================================================
# === RUTAS DE AUTENTICACIÓN (OAUTH) ===========================================
# ==============================================================================


@app.route("/login")
def login():
    # Eliminamos la lógica de 'next_url' para simplificar
    auth_url = f"{AUTHORIZATION_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope="
    print(f"--- Redirigiendo a la autorización de OAuth: {auth_url}")
    return redirect(auth_url)


@app.route("/auth/callback")
def callback():
    print("--- Entrando en la ruta /auth/callback ---")
    code = request.args.get("code")
    if not code:
        print("   -> ERROR: No se recibió el código de autorización.")
        return "Error: No se recibió el código de autorización.", 400
    print(f"   -> Código de autorización recibido: {code[:10]}...")

    token_payload = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": code,
    }
    token_response = requests.post(TOKEN_URL, data=token_payload)

    if token_response.status_code != 200:
        print(
            f"   -> ERROR: Fallo al obtener el token. Status: {token_response.status_code}, Respuesta: {token_response.text}"
        )
        return "Error: No se pudo obtener el token de acceso.", 400

    token_data = token_response.json()
    access_token = token_data.get("access_token")
    if not access_token:
        print("   -> ERROR: La respuesta del token no contenía 'access_token'.")
        return "Error: La respuesta del token no contenía 'access_token'.", 400

    headers = {"Authorization": f"Bearer {access_token}"}
    user_response = requests.get(USER_API_URL, headers=headers)

    if user_response.status_code != 200:
        print(
            f"   -> ERROR: Fallo al obtener los datos del usuario. Status: {user_response.status_code}, Respuesta: {user_response.text}"
        )
        return "Error: No se pudieron obtener los datos del usuario.", 400

    user_info = user_response.json().get("user")
    if not user_info:
        print("   -> ERROR: La respuesta de la API no contenía la clave 'user'.")
        return "Error: La respuesta de la API no contenía la clave 'user'.", 400

    # Guardado en Base de Datos
    user = User.query.get(user_info["id"])
    if not user:
        user = User(id=user_info["id"], username=user_info["username"])
        db.session.add(user)
    else:
        user.username = user_info["username"]
    db.session.commit()
    print(
        f"   -> Usuario '{user.username}' (ID: {user.id}) guardado/actualizado en la DB."
    )

    # Guardado en Sesión
    session.clear()  # Limpiamos la sesión antigua por si acaso
    session["user_id"] = user.id
    session["user_info"] = user_info
    session.modified = True

    print(f"--- Sesión creada exitosamente para el usuario {user.id} ---")
    print("   -> Contenido de la sesión:", session)

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


@app.route("/order/success/<path:receipt_token>", methods=["GET", "POST"])
@app.route("/order/success/", methods=["GET", "POST"])
def order_success(receipt_token=None):
    # --- VERIFICACIÓN DE SEGURIDAD ---
    pending_order = session.get("pending_order")
    user_id = session.get("user_id")
    if not pending_order or not user_id:
        return redirect(url_for("home"))

    # --- PROCESAMIENTO DE DATOS ---
    cart = pending_order.get("cart", {})
    billing_address_data = pending_order.get("billing_address", {})
    coupon = pending_order.get("coupon")
    if not cart:
        return redirect(url_for("home"))

    subtotal = sum(
        float(item["price"].replace("$", "")) * item["quantity"]
        for item in cart.values()
    )
    discount_amount = 0
    if coupon:
        if coupon.get("type") == "percent":
            discount_amount = (subtotal * coupon.get("value", 0)) / 100
        else:
            discount_amount = coupon.get("value", 0)
    total = subtotal - discount_amount

    # --- GUARDADO EN BASE DE DATOS ---
    try:
        new_order = Order(
            order_number=str(random.randint(10000, 99999)),
            total=total,
            status="Completed",
            payment_method="Fleeca Bank",
            user_id=user_id,
        )

        new_address = BillingAddress(
            firstname=billing_address_data.get("firstname"),
            lastname=billing_address_data.get("lastname"),
            apartment=billing_address_data.get("apartment"),
            discord=billing_address_data.get("discord"),
            phone=billing_address_data.get("phone"),
            order=new_order,
        )

        for item_data in cart.values():
            order_item = OrderItem(
                product_name=item_data["name"],
                download_file=item_data["download_file"],
                quantity=item_data["quantity"],
                order=new_order,
            )
            db.session.add(order_item)

        db.session.add(new_order)
        db.session.add(new_address)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print(f"!!! ERROR AL GUARDAR EL PEDIDO EN LA BASE DE DATOS: {e}")
        return "An error occurred while saving your order. Please contact support.", 500

    # --- PREPARAMOS DATOS EXTRA PARA LA PLANTILLA ---
    # Creamos un diccionario con el subtotal y la info del descuento para pasarlo a la plantilla
    order_extra_details = {
        "subtotal": "%.2f" % subtotal,
        "discount_info": (
            {"code": coupon["code"], "amount": discount_amount} if coupon else None
        ),
    }

    # --- LIMPIEZA DE SESIÓN ---
    session.pop("pending_order", None)
    session.pop("cart", None)
    session.pop("coupon", None)
    session.modified = True

    # Pasamos el objeto 'new_order' y los datos extra a la plantilla
    return render_template(
        "order_success.html",
        order=new_order,
        order_extra=order_extra_details,
        body_class="order-success-page",
    )


@app.route("/api/wishlist")
def get_wishlist_data():
    """
    Devuelve la lista de IDs de productos en la wishlist del usuario.
    """
    wishlist_ids = session.get("wishlist", [])
    return jsonify(wishlist_ids)


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


@app.route("/wishlist")
def wishlist_page():  # <-- El nombre de la función es 'wishlist_page'
    wishlist_ids = session.get("wishlist", [])
    # Usamos nuestra lógica de base de datos para obtener los productos
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
