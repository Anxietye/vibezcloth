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
DISCORD_WEBHOOK_URL = "https://discord.com/api/v10/webhooks/1418050508081594531/SaOV_sU29IyJdLHCVkYmNWe50CQKCgK04LcgMDN4gcHl5roTRTLo5uxLfKRzH_L3WmIb"
DISCORD_SALES_WEBHOOK_URL = "https://discord.com/api/webhooks/1418062058213085204/jdNjaIGtNyjFNwyyIFi9gkarJIy-Gy8RTJXDfEtoIF3JEYBFF20IBRgGR0ftuM6patGg"
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
        "category": "women",
        "name": "Vibez Cozy Tracksuit",
        "price": "$8500",
        "slug": "vibez-tracksuit",
        "sku": "VF-001",
        # NUEVA ESTRUCTURA: Un diccionario de variantes de color
        "color_variants": {
            "Red": {  
                "image": "images/anaranjado.png",
                "download_file": "Vibez-Tracksuit-Red.zip",
            },
            "Blue": {  
                "image": "images/azul.png",
                "download_file": "Vibez-Tracksuit-Blue.zip",
            },
            "White": { 
                "image": "images/blanco.png",
                "download_file": "Vibez-Tracksuit-White.zip",
            },
            "Brown": {  
                "image": "images/marron.png",
                "download_file": "Vibez-Tracksuit-Brown.zip",
            },
            "Black": {  
                "image": "images/negro.png",
                "download_file": "Vibez-Tracksuit-Black.zip",
            },
            "Purple": { 
                "image": "images/purpura.png",
                "download_file": "Vibez-Tracksuit-Purple.zip",
            },
            "Pink": {  
                "image": "images/rosa.png",
                "download_file": "Vibez-Tracksuit-Pink.zip",
            },
            "Green": { 
                "image": "images/verde.png",
                "download_file": "Vibez-Tracksuit-Green.zip",
            },
        },
    },
    {
        "id": 2,
        "category": "women",
        "name": "Grunge T-Shirt",
        "price": "$6000",
        "slug": "grunge-t-shirt",
        "sku": "TM-002",
        "color_variants": {
            "Torment": {  
                "image": "images/tblack9.png",
                "download_file": "Torment.zip",
            },
            "Heaven": { 
                "image": "images/tblack8.png",
                "download_file": "Heaven.zip",
            },
            "Distorted": { 
                "image": "images/tblack6.png",
                "download_file": "Distorted.zip",
            },
            "Red": {
                "image": "images/Tred.png",
                "download_file": "Red.zip",
            },
            "Distorted Vibez": {
                "image": "images/tblack7.png",
                "download_file": "Distorted-Vibez.zip",
            },
            "Dream Big": {
                "image": "images/twhite2.png",
                "download_file": "Dream-Big.zip",
            },
            "Stuck-W": { 
                "image": "images/twhite3.png",
                "download_file": "Stuck-W.zip",
            },
            "Cry Baby": {
                "image": "images/twhite4.png",
                "download_file": "Cry-Baby.zip",
            },
            "Western Shirt": { 
                "image": "images/twhite5.png",
                "download_file": "Western-Shirt.zip",
            },
            "Hell Full": {  
                "image": "images/Tblack2.png",
                "download_file": "Hell-Full.zip",
            },
            "Hell Boring": {  
                "image": "images/tblack4.png",
                "download_file": "Hell-Boring.zip",
            },
            "Angel & Thoughts": {  
                "image": "images/tblack5.png",
                "download_file": "Angel-Thoughts.zip",
            },
        },
    },
    {
        "id": 3,
        "category": "women",
        "name": "Cropped Tank Top",
        "price": "$4500",
        "slug": "cropped-tank-top",
        "sku": "CT-047",
        "color_variants": {
            "LS Vibez": {  
                "image": "images/Croptop3.png",
                "download_file": "LS-Vibez-Cropped-Tank-Top.zip",
            },
            "Hell Boring": {  
                "image": "images/Croptop6.png",
                "download_file": "Hell-Boring-Cropped-Tank-Top.zip",
            },
            "Flames": {  
                "image": "images/Croptop1.png",
                "download_file": "Flames-Cropped-Tank-Top.zip",
            },
            "Baked": {  
                "image": "images/Croptop2.png",
                "download_file": "Baked-Cropped-Tank-Top.zip",
            },
            "Bad Things": {  
                "image": "images/Croptop4.png",
                "download_file": "Bad-Things-Cropped-Tank-Top.zip",
            },
            "White": {  
                "image": "images/Croptop5.png",
                "download_file": "White-Cropped-Tank-Top.zip",
            },
            "Black": {  
                "image": "images/Croptop7.png",
                "download_file": "Black-Cropped-Tank-Top.zip",
            },
        },
    },
    {
        "id": 4,
        "category": "men",
        "name": "Vibez Jean",
        "price": "$4500",
        "slug": "vibez-jean-men",
        "sku": "VM-047",
        "color_variants": {
            "Black": {  
                "image": "images/jeannegro.png",
                "download_file": "Black-men.zip",
            },
            "Gray": {  
                "image": "images/jeangris.png",
                "download_file": "Gray-men.zip",
            },
            "Light Blue": {  
                "image": "images/azulclaro.png",
                "download_file": "Light-Blue-men.zip",
            },
            "Normal": {  
                "image": "images/jean.png",
                "download_file": "Normal-men.zip",
            },
            "Light Blue 2": {  
                "image": "images/lightblue2.png",
                "download_file": "Light-Blue2.zip",
            },
            "Light Black": {  
                "image": "images/lightblack.png",
                "download_file": "Light-Black.zip",
            },
            "Black 2": {  
                "image": "images/jeanblackblack.png",
                "download_file": "Jean-Black2.zip",
            },
            "Dark Blue": {  
                "image": "images/jeanblue.png",
                "download_file": "Jean-DarkBlue.zip",
            },
            "Gray 2": {  
                "image": "images/jeangray.png",
                "download_file": "Jean-Gray2.zip",
            },
            "White": {  
                "image": "images/jeanwhite.png",
                "download_file": "Jean-White.zip",
            },
        },
    },
    {
        "id": 5,
        "category": "women",
        "name": "Vibez Jeans",
        "price": "$4500",
        "slug": "vibez-jeans",
        "sku": "VJ-004",
        "color_variants": {
            "Blue": {  
                "image": "images/pantazul.png",
                "download_file": "blue-jeans.zip",
            },
            "Black": {  
                "image": "images/pantnegro.png",
                "download_file": "black-jeans.zip",
            },
        },
    },
    {
        "id": 6,
        "category": "women",
        "name": "Sports Pants",
        "price": "$4000",
        "slug": "sports-pants",
        "sku": "SP-040",
        "color_variants": {
            "Blue": {  
                "image": "images/bluepant.png",
                "download_file": "sp-blue.zip",
            },
            "Black": {  
                "image": "images/blackpant.png",
                "download_file": "sp-black.zip",
            },
            "Red": {  
                "image": "images/redpant.png",
                "download_file": "sp-red.zip",
            },
            "White": {  
                "image": "images/whitepant.png",
                "download_file": "sp-white.zip",
            },
        },
    },
    {
        "id": 7,
        "category": "women",
        "name": "Oversized Band T-Shirts",
        "price": "$7000",
        "slug": "oversized-band-shirts",
        "sku": "OS-001",
        "color_variants": {
            "Metallica": {  
                "image": "images/metallica.png",
                "download_file": "Metallica.zip",
            },
            "Iron Maiden": {  
                "image": "images/ironmaiden.png",
                "download_file": "Iron-Maiden.zip",
            },
            "Black Sabbath": {  
                "image": "images/blacksabbath.png",
                "download_file": "Black-Sabbath.zip",
            },
            "Skulls": {  
                "image": "images/skulls.png",
                "download_file": "Skulls.zip",
            },
        },
    },
    {
        "id": 8,
        "category": "women",
        "name": "Custom Sneaker",
        "price": "$15000",
        "slug": "custom-sneaker",
        "sku": "CS-101",
        "color_variants": {
            "Billie Eilish": {  
                "image": "images/Billie.png",
                "download_file": "Billie-Eilish.zip",
            },
            "Blue Flowers": {  
                "image": "images/Blue-Flowers.png",
                "download_file": "Blue-Flowers.zip",
            },
            "Butterflies": {  
                "image": "images/Butterflies.png",
                "download_file": "Butterflies.zip",
            },
            "BW Cartoon": {  
                "image": "images/BW-Cartoon.png",
                "download_file": "BW-Cartoon.zip",
            },
            "Cherry Flowers": {  
                "image": "images/Cherry.png",
                "download_file": "Cherry-Flowers.zip",
            },
            "Classic": {  
                "image": "images/Classic.png",
                "download_file": "Classic.zip",
            },
            "Melted": {  
                "image": "images/Melted.png",
                "download_file": "Melted.zip",
            },
            "Pikachu": {  
                "image": "images/Pikachu.png",
                "download_file": "Pikachu.zip",
            },
            "Pink": {  
                "image": "images/Pinky.png",
                "download_file": "Pinky.zip",
            },
            "Stitch": {  
                "image": "images/Stitch.png",
                "download_file": "Stitch.zip",
            },
            "Sunflower": {  
                "image": "images/Sunflower.png",
                "download_file": "Sunflower.zip",
            },
            "White Cartoon": {  
                "image": "images/White-Cartoon.png",
                "download_file": "White-Cartoon.zip",
            },
            "All-White Cartoon": {  
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
            "Dark Star": {  
                "image": "images/DarkStar.png",
                "download_file": "DarkStar.zip",
            },
            "Santa Cruz": {  
                "image": "images/SantaCruz.png",
                "download_file": "SantaCruz.zip",
            },
            "Seven Inch Girl": {  
                "image": "images/SevenInch.png",
                "download_file": "SevenInch-Girl.zip",
            },
            "Seven Inch Blue": {  
                "image": "images/SevenInch2.png",
                "download_file": "SevenInch-Blue.zip",
            },
            "American": {  
                "image": "images/USA.png",
                "download_file": "American.zip",
            },
        },
    },
    #{
     #   "id": 10,
     #   "category": "women",
      #  "name": "Cropped Hoodie",
       # "price": "$6600",
        #"slug": "cropped-hoodie",
        #"sku": "CH-008",
        #"color_variants": {
        #    "Depravity": {  # Color 'Azul' uses the image depravity.png
         #       "image": "images/depravity.png",
          #      "download_file": "Depravity.zip",
           # },
           # "Dream Big": {  # Color 'Azul' uses the image drambig.png
           #     "image": "images/drambig.png",
           #     "download_file": "DreamBig.zip",
           # },
           # "Dystopia": {  # Color 'Azul' uses the image dystopia.png
           #     "image": "images/dystopia.png",
           #     "download_file": "Dystopia.zip",
           # },
           # "Kuromi": {  # Color 'Azul' uses the image kuromi.png
            #    "image": "images/kuromi.png",
            #    "download_file": "Kuromi.zip",
            #},
            #"Red L.": {  # Color 'Azul' uses the image lettering.png
            #    "image": "images/lettering.png",
            #    "download_file": "Red-L.zip",
            #},
            #"Run Away": {  # Color 'Azul' uses the image runaway.png
            #    "image": "images/runaway.png",
            #    "download_file": "Run-Away.zip",
            #},
            #"Stucked": {  # Color 'Azul' uses the image stucked.png
            #    "image": "images/stucked.png",
            #    "download_file": "Stuck.zip",
            #},
            #"Blue": {  # Color 'Azul' uses the image azuls.png
            #    "image": "images/azuls.png",
            #    "download_file": "Blue.zip",
            #},
            #"White": {  # Color 'Azul' uses the image blancos.png
            #    "image": "images/blancos.png",
            #    "download_file": "White.zip",
            #},
            #"Brown": {  # Color 'Azul' uses the image marrons.png
            #    "image": "images/marrons.png",
            #    "download_file": "Brown.zip",
            #},
            #"Black": {  # Color 'Azul' uses the image negros.png
            #    "image": "images/negros.png",
            #    "download_file": "Black.zip",
            #},
            #"Pink": {  # Color 'Azul' uses the image rosas.png
            #    "image": "images/rosas.png",
            #    "download_file": "Pink.zip",
            #},
        #},
    #},
    {
        "id": 10,
        "category": "women",
        "name": "Preppy Set",
        "price": "$5500",
        "slug": "preppy-set",
        "sku": "PP-001",
        "color_variants": {
            "Blue A": {  
                "image": "images/Blue-PP.png",
                "download_file": "Blue-PP.zip",
            },
            "Blue B": {  
                "image": "images/Blue-PP-B.png",
                "download_file": "Blue-PP-B.zip",
            },
            "Blue C": {  
                "image": "images/Blue-PP-C.png",
                "download_file": "Blue-PP-C.zip",
            },
            "Gray": {  
                "image": "images/Gray-PP.png",
                "download_file": "Gray-PP.zip",
            },
            "Red A": {  
                "image": "images/Red-PP.png",
                "download_file": "Red-PP.zip",
            },
            "Red B": {  
                "image": "images/Red-PP-B.png",
                "download_file": "Red-PP-B.zip",
            },
            "White": {  
                "image": "images/White-PP.png",
                "download_file": "White-PP.zip",
            },
        },
    },
    {
        "id": 11,
        "category": "men",
        "name": "Simple Hoddie",
        "price": "$6600",
        "slug": "simple-hoddie",
        "sku": "SH-001",
        "color_variants": {
            "Angel": {  
                "image": "images/Angel.png",
                "download_file": "Angel.zip",
            },
            "Inferno": {  
                "image": "images/Inferno.png",
                "download_file": "Inferno.zip",
            },
            "Lil Vert": {  
                "image": "images/Lilvert.png",
                "download_file": "Lil-Vert.zip",
            },
            "Maquinary": {  
                "image": "images/maquinary.png",
                "download_file": "Maquinary.zip",
            },
            "Tyler": {  
                "image": "images/Tyler.png",
                "download_file": "Tyler.zip",
            },
            "Black": {  
                "image": "images/Blackhoddie.png",
                "download_file": "Blackhoddie.zip",
            },
        },
    },
    {
        "id": 12,
        "category": "men",
        "name": "Grunge T-Shirts",
        "price": "$6000",
        "slug": "grunge-tshirts-men",
        "sku": "GS-051",
        "color_variants": {
            "Darklight": {  
                "image": "images/Darklightman.png",
                "download_file": "Darklight.zip",
            },
            "21Savage": {  
                "image": "images/21Savage.png",
                "download_file": "21Savage.zip",
            },
            "Ghost": {  
                "image": "images/Ghost.png",
                "download_file": "Ghost.zip",
            },
            "Eazy-E": {  
                "image": "images/Eazye.png",
                "download_file": "Eazy-E.zip",
            },
            "Black Sabbath": {  
                "image": "images/blacksabbathman.png",
                "download_file": "BlackSabbath.zip",
            },
            "Hangxiety": {  
                "image": "images/Hangxiety.png",
                "download_file": "Hangxiety.zip",
            },
            "Marlboro": {  
                "image": "images/Marlboro.png",
                "download_file": "Marlboro.zip",
            },
            "Supra": {  
                "image": "images/Supra.png",
                "download_file": "Supra.zip",
            },
            "Split": {  
                "image": "images/Split.png",
                "download_file": "Split.zip",
            },
            "Zillakami": {  
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
            "VG Vibe": {  
                "image": "images/VG Vibe.png",
                "download_file": "VG Vibe.zip",
            },
            "Black Grunge": {  
                "image": "images/Black grunge.png",
                "download_file": "Black grunge.zip",
            },
            "Rose Grunge": {  
                "image": "images/Rose Grunge.png",
                "download_file": "Rose Grunge.zip",
            },
            "Noir Script": {  
                "image": "images/Noir Script.png",
                "download_file": "Noir Script-E.zip",
            },
            "Hype Collage": {  
                "image": "images/Hype Collage.png",
                "download_file": "Hype Collage.zip",
            },
            "Lost notes": {  
                "image": "images/Lost notes.png",
                "download_file": "Lost notes.zip",
            },
            "Stare drip": {  
                "image": "images/Stare drip.png",
                "download_file": "Stare drip.zip",
            },
            "Pink Chaos": {  
                "image": "images/Pink Chaos.png",
                "download_file": "Pink Chaos.zip",
            },
        },
    },
    {
        "id": 14,
        "category": "men",
        "name": "Oversized T-Shirts",
        "price": "$5000",
        "slug": "oversized-shirts",
        "sku": "OV-050",
        "color_variants": {
            "Download": {  
                "image": "images/Download.png",
                "download_file": "Download.zip",
            },
            "Metallica": {  
                "image": "images/Metallicaman.png",
                "download_file": "Metallica-men.zip",
            },
            "S.O.C": {  
                "image": "images/SOC.png",
                "download_file": "SOC.zip",
            },
            "Suffocation": {  
                "image": "images/Suffocationman.png",
                "download_file": "Suffocation-men.zip",
            },
            "Sinner": {  
                "image": "images/Sinner.png",
                "download_file": "Sinner.zip",
            },
        },
    },
    {
        "id": 15,
        "category": "women",
        "name": "Gothic Pearl Cross Choker",
        "price": "$3700",
        "slug": "cross-choker",
        "sku": "CS-050",
        "color_variants": {
            "Plate": {  
                "image": "images/Plate.png",
                "download_file": "Plate-Cross-Choker.zip",
            },
            "Bronze": {  
                "image": "images/Bronze.png",
                "download_file": "Bronze-Cross-Choker.zip",
            },
        },
    },
    {
        "id": 16,
        "category": "women",
        "name": "Gothic Cascade Ear Cuff",
        "price": "$3700",
        "slug": "ear-cuff",
        "sku": "CS-050",
        "color_variants": {
            "Gray & Black": {  
                "image": "images/GB-GCEC.png",
                "download_file": "GB-GCEC.zip",
            },
            "Black": {  
                "image": "images/Black-GCEC.png",
                "download_file": "Black-GCEC.zip",
            },
            "White": {  
                "image": "images/White-GCEC.png",
                "download_file": "White-GCEC.zip",
            },
            "Black & Gold": {  
                "image": "images/BG-GCEC.png",
                "download_file": "BG-GCEC.zip",
            },
            "White & Gold": {  
                "image": "images/WG-GCEC.png",
                "download_file": "WG-GCEC.zip",
            },
        },
    },
    {
        "id": 17,
        "category": "women",
        "name": "Midnight Cross Earrings",
        "price": "$3700",
        "slug": "cross-earrings",
        "sku": "CE-050",
        "color_variants": {
            "Black": {  
                "image": "images/Midnight-Cross-Earrings.png",
                "download_file": "Midnight-Cross-Earrings.zip",
            },
        },
    },
    {
        "id": 18,
        "category": "women",
        "name": "After Dark Vibez Jeans",
        "price": "$4500",
        "slug": "after-dark",
        "sku": "VJ-050",
        "color_variants": {
            "Black": {  
                "image": "images/Black-ADVJ.png",
                "download_file": "Black-ADVJ.zip",
            },
            "White": {  
                "image": "images/White-ADVJ.png",
                "download_file": "White-ADVJ.zip",
            },
            "Green": {  
                "image": "images/Green-ADVJ.png",
                "download_file": "Green-ADVJ.zip",
            },
            "Pink": {  
                "image": "images/Pink-ADVJ.png",
                "download_file": "Pink-ADVJ.zip",
            },
        },
    },
    {
        "id": 19,
        "category": "women",
        "name": "Vibez Riot Jeans",
        "price": "$4500",
        "slug": "riot-jeans",
        "sku": "VJ-051",
        "color_variants": {
            "Dark": {  
                "image": "images/Dark-VRJ.png",
                "download_file": "Dark-VRJ.zip",
            },
            "White": {  
                "image": "images/White-VRJ.png",
                "download_file": "White-VRJ.zip",
            },
            "Red": {  
                "image": "images/Red-VRJ.png",
                "download_file": "Red-VRJ.zip",
            },
            "Black": {  
                "image": "images/Black-VRJ.png",
                "download_file": "Black-VRJ.zip",
            },
            "Blue": {  
                "image": "images/Blue-VRJ.png",
                "download_file": "Blue-VRJ.zip",
            },
        },
    },
    {
        "id": 20,
        "category": "women",
        "name": "Vibez Summer Classic Shorts",
        "price": "$4500",
        "slug": "summer-shorts",
        "sku": "VJ-052",
        "color_variants": {
            "Black": {  
                "image": "images/Black-VSCS.png",
                "download_file": "Black-VSCS.zip",
            },
            "White": {  
                "image": "images/White-VSCS.png",
                "download_file": "White-VSCS.zip",
            },
            "Blue": {  
                "image": "images/Blue-VSCS.png",
                "download_file": "Blue-VSCS.zip",
            },
            "Gray": {  
                "image": "images/Gray-VSCS.png",
                "download_file": "Gray-VSCS.zip",
            },
        },
    },
    {
        "id": 21,
        "category": "women",
        "name": "Sunset Glow Top",
        "price": "$5000",
        "slug": "glow-top",
        "sku": "ST-052",
        "color_variants": {
            "Pink": {  
                "image": "images/Pink-SGT.png",
                "download_file": "Pink-SGT.zip",
            },
            "Black": {  
                "image": "images/Black-SGT.png",
                "download_file": "Black-SGT.zip",
            },
            "Blue": {  
                "image": "images/Blue-SGT.png",
                "download_file": "Blue-SGT.zip",
            },
            "Green": {  
                "image": "images/Green-SGT.png",
                "download_file": "Green-SGT.zip",
            },
            "Red": {  
                "image": "images/Red-SGT.png",
                "download_file": "Red-SGT.zip",
            },
            "Yellow": {  
                "image": "images/Yellow-SGT.png",
                "download_file": "Gray-SGT.zip",
            },
        },
    },
    {
        "id": 22,
        "category": "women",
        "name": "Sweet & Slouchy Set",
        "price": "$5000",
        "slug": "slouchy-set",
        "sku": "SS-052",
        "color_variants": {
            "Worn-out": {  
                "image": "images/Worn-out-SS.png",
                "download_file": "Worn-out-SS.zip",
            },
            "Black Rose": {  
                "image": "images/Rose-SS.png",
                "download_file": "Rose-SS.zip",
            },
            "Black": {  
                "image": "images/Black-SS.png",
                "download_file": "Black-SS.zip",
            },
            "Gray Cross": {  
                "image": "images/GrayCross-SS.png",
                "download_file": "GrayCross-SS.zip",
            },
            "Green": {  
                "image": "images/Green-SS.png",
                "download_file": "Green-SS.zip",
            },
            "Pink": {  
                "image": "images/Pink-SS.png",
                "download_file": "Pink-SS.zip",
            },
        },
    },
    {
        "id": 23,
        "category": "women",
        "name": "Striped Sleeve Grunge Top",
        "price": "$5500",
        "slug": "stripped-sleeve",
        "sku": "SS-053",
        "color_variants": {
            "Nirvana-Y": {  
                "image": "images/Nirvana-Yellow.png",
                "download_file": "Nirvana-Yellow.zip",
            },
            "Sinner-G": {  
                "image": "images/Sinner-Green.png",
                "download_file": "Sinner-Green.zip",
            },
            "Sinner-W": {  
                "image": "images/Sinner-Black.png",
                "download_file": "Sinner-Black.zip",
            },
            "Sweetheart-P": {  
                "image": "images/Sweetheart-Pink.png",
                "download_file": "Sweetheart-Pink.zip",
            },
            "Sweetheart-W": {  
                "image": "images/Sweetheart-White.png",
                "download_file": "Sweetheart-White.zip",
            },
            "Digital Monster-Y": {  
                "image": "images/Digital-Yellow.png",
                "download_file": "Digital-Yellow.zip",
            },
            "Sweetheart": {  
                "image": "images/Sweetheart.png",
                "download_file": "Sweetheart.zip",
            },
            "Smile": {  
                "image": "images/Smile.png",
                "download_file": "Smile.zip",
            },
            "Sinner-Y": {  
                "image": "images/Sinner-Yellow.png",
                "download_file": "Sinner-Yellow.zip",
            },
            "Nirvana-B": {  
                "image": "images/Nirvana-Black.png",
                "download_file": "Nirvana-Black.zip",
            },
            "Digital Monster-P": {  
                "image": "images/Digital-Pink.png",
                "download_file": "Digital-Pink.zip",
            },
            "Sinner-O": {  
                "image": "images/Sinner-Orange.png",
                "download_file": "Sinner-Orange.zip",
            },
            "Sinner-R": {  
                "image": "images/Sinner-Red.png",
                "download_file": "Sinner-Red.zip",
            },
            "Sinner-B": {  
                "image": "images/Sinner-White.png",
                "download_file": "Sinner-White.zip",
            },
        },
    },
    {
        "id": 24,
        "category": "women",
        "name": "Plaid Punk Mini Skirt",
        "price": "$4500",
        "slug": "skirt-punk",
        "sku": "SP-053",
        "color_variants": {
            "Black": {  
                "image": "images/Black-Skirt.png",
                "download_file": "Black-Skirt.zip",
            },
            "Green": {  
                "image": "images/Green-Skirt.png",
                "download_file": "Green-Skirt.zip",
            },
            "Pink": {  
                "image": "images/Pink-Skirt.png",
                "download_file": "Pink-Skirt.zip",
            },
            "Purple": {  
                "image": "images/Purple-Skirt.png",
                "download_file": "Purple-Skirt.zip",
            },
            "Red": {  
                "image": "images/Red-Skirt.png",
                "download_file": "Red-Skirt.zip",
            },
            "Yellow": {  
                "image": "images/Yellow-Skirt.png",
                "download_file": "Yellow-Skirt.zip",
            },
        },
    },
    {
        "id": 25,
        "category": "women",
        "name": "Cross Pocket Skirt",
        "price": "$4500",
        "slug": "pocket-skirt",
        "sku": "SP-053",
        "color_variants": {
            "Black": {  
                "image": "images/Black-PS.png",
                "download_file": "Black-PS.zip",
            },
            "Green": {  
                "image": "images/Green-PS.png",
                "download_file": "Green-PS.zip",
            },
            "Pink": {  
                "image": "images/Pink-PS.png",
                "download_file": "Pink-PS.zip",
            },
            "Blue": {  
                "image": "images/Blue-PS.png",
                "download_file": "Blue-PS.zip",
            },
            "White": {  
                "image": "images/White-PS.png",
                "download_file": "White-PS.zip",
            },
        },
    },
    {
        "id": 26,
        "category": "women",
        "name": "Cropped Denim Jacket",
        "price": "$4200",
        "slug": "denim-jacket",
        "sku": "DJ-053",
        "color_variants": {
            "Blue": {  
                "image": "images/Blue-DJ.png",
                "download_file": "Blue-DJ.zip",
            },
            "Gray": {  
                "image": "images/Gray-DJ.png",
                "download_file": "Gray-DJ.zip",
            },
            "Light Blue": {  
                "image": "images/LightBlue-DJ.png",
                "download_file": "LightBlue-DJ.zip",
            },
            "White": {  
                "image": "images/White-DJ.png",
                "download_file": "White-DJ.zip",
            },
        },
    },
    {
        "id": 27,
        "category": "women",
        "name": "Oversized Sweatshirt",
        "price": "$5000",
        "slug": "oversized-sweatshirt",
        "sku": "OS-050",
        "color_variants": {
            "Comic": {  
                "image": "images/Comic-OS.png",
                "download_file": "Comic-OS.zip",
            },
            "White": {  
                "image": "images/White-OS.png",
                "download_file": "White-OS.zip",
            },
            "Black": {  
                "image": "images/Black-OS.png",
                "download_file": "Black-OS.zip",
            },
            "Kenzo": {  
                "image": "images/Kenzo-OS.png",
                "download_file": "Kenzo-OS.zip",
            },
            "Pink": {  
                "image": "images/Pink-OS.png",
                "download_file": "Pink-OS.zip",
            },
        },
    },
    {
        "id": 28,
        "category": "women",
        "name": "Classic Zip-Up Hoodie",
        "price": "$4200",
        "slug": "classic-hoodie",
        "sku": "CH-053",
        "color_variants": {
            "Gray": {  
                "image": "images/Gray-CH.png",
                "download_file": "Gray-CH.zip",
            },
            "Gray Lettering": {  
                "image": "images/Lettering-CH.png",
                "download_file": "Lettering-CH.zip",
            },
            "Pink": {  
                "image": "images/Pink-CH.png",
                "download_file": "Pink-CH.zip",
            },
            "Brown": {  
                "image": "images/Brown-CH.png",
                "download_file": "Brown-CH.zip",
            },
            "Black": {  
                "image": "images/Black-CH.png",
                "download_file": "Black-CH.zip",
            },
        },
    },
    {
        "id": 29,
        "category": "women",
        "name": "Grunge Skirt & Hoodie Jacket Set",
        "price": "$6500",
        "slug": "grunge-hoodie",
        "sku": "GH-050",
        "color_variants": {
            "Pink": {  
                "image": "images/Pink-GH.png",
                "download_file": "Pink-GH.zip",
            },
            "Skeleton-B": {  
                "image": "images/Skeleton-GH.png",
                "download_file": "Skeleton-GH.zip",
            },
            "Clouds-B": {  
                "image": "images/Clouds-GH.png",
                "download_file": "Clouds-GH.zip",
            },
            "Hello Kitty": {  
                "image": "images/HelloKitty-GH.png",
                "download_file": "HelloKitty-GH.zip",
            },
            "Black": {  
                "image": "images/Black-GH.png",
                "download_file": "Black-GH.zip",
            },
            "Anime": {  
                "image": "images/Anime-GH.png",
                "download_file": "Anime-GH.zip",
            },
            "Himiko": {  
                "image": "images/Himiko-GH.png",
                "download_file": "Himiko-GH.zip",
            },
            "Green": {  
                "image": "images/Green-GH.png",
                "download_file": "Green-GH.zip",
            },
            "Skeleton-R": {  
                "image": "images/Red-GH.png",
                "download_file": "Red-GH.zip",
            },
            "Clouds-P": {  
                "image": "images/PinkClouds-GH.png",
                "download_file": "PinkClouds-GH.zip",
            },
            "Anime Eyes": {  
                "image": "images/AnimeEyes-GH.png",
                "download_file": "AnimeEyes-GH.zip",
            },
        },
    },
    {
        "id": 30,
        "category": "women",
        "name": "Heart & Star Earrings",
        "price": "$3700",
        "slug": "heart-earrings",
        "sku": "CH-053",
        "color_variants": {
            "Gold": {  
                "image": "images/Gold-HSE.png",
                "download_file": "Gold-HSE.zip",
            },
            "Black": {  
                "image": "images/Black-HSE.png",
                "download_file": "Black-HSE.zip",
            },
            "Bronze": {  
                "image": "images/Bronze-HSE.png",
                "download_file": "Bronze-HSE.zip",
            },
            "Plate": {  
                "image": "images/Plate-HSE.png",
                "download_file": "Plate-HSE.zip",
            },
        },
    },
    {
        "id": 31,
        "category": "women",
        "name": "Urban Cap",
        "price": "$3000",
        "slug": "urban-cap",
        "sku": "UC-100",
        "color_variants": {
            "Black": {  
                "image": "images/Black-Cap.png",
                "download_file": "Black-Cap.zip",
            },
            "Blue": {  
                "image": "images/Blue-Cap.png",
                "download_file": "Blue-Cap.zip",
            },
            "God's Favorite": {  
                "image": "images/Favorite-Cap.png",
                "download_file": "Favorite-Cap.zip",
            },
            "Military": {  
                "image": "images/Military-Cap.png",
                "download_file": "Military-Cap.zip",
            },
            "Stars": {  
                "image": "images/Stars-Cap.png",
                "download_file": "Stars-Cap.zip",
            },
            "Sunshine & Whiskey": {  
                "image": "images/Sunshine-Cap.png",
                "download_file": "Sunshine-Cap.zip",
            },
            "VonDutch": {  
                "image": "images/VonDutch-Cap.png",
                "download_file": "VonDutch-Cap.zip",
            },
        },
    },
    {
        "id": 32,
        "category": "women",
        "name": "Vintage Gothic Glam",
        "price": "$7000",
        "slug": "vintage-gothic",
        "sku": "VG-100",
        "color_variants": {
            "White": {  
                "image": "images/White-VG.png",
                "download_file": "White-VG.zip",
            },
            "Purple": {  
                "image": "images/Purple-VG.png",
                "download_file": "Purple-VG.zip",
            },
            "Gray": {  
                "image": "images/Gray-VG.png",
                "download_file": "Gray-VG.zip",
            },
            "Red": {  
                "image": "images/Red-VG.png",
                "download_file": "Red-VG.zip",
            },
        },
    },
    {
        "id": 33,
        "category": "women",
        "name": "Midnight Vibes Gothic Outfit",
        "price": "$7000",
        "slug": "midnight-gothic",
        "sku": "MG-100",
        "color_variants": {
            "Red": {  
                "image": "images/Red-MG.png",
                "download_file": "Red-MG.zip",
            },
            "Black": {  
                "image": "images/Black-MG.png",
                "download_file": "Black-MG.zip",
            },
            "Blue": {  
                "image": "images/Blue-MG.png",
                "download_file": "Blue-MG.zip",
            },
            "Purple": {  
                "image": "images/Purple-MG.png",
                "download_file": "Purple-MG.zip",
            },
            "Turquoise": {  
                "image": "images/Turquoise-MG.png",
                "download_file": "Turquoise-MG.zip",
            },
        },
    },
    {
        "id": 34,
        "category": "women",
        "name": "Cozy Grunge Sweater",
        "price": "$6000",
        "slug": "grunge-sweater",
        "sku": "GS-100",
        "color_variants": {
            "Fire-B": {  
                "image": "images/Fire-B-GS.png",
                "download_file": "Fire-B-GS.zip",
            },
            "Bats-B": {  
                "image": "images/Bats-B-GS.png",
                "download_file": "Bats-B-GS.zip",
            },
            "Black": {  
                "image": "images/Black-GS.png",
                "download_file": "Black-GS.zip",
            },
            "Red": {  
                "image": "images/Red-GS.png",
                "download_file": "Red-GS.zip",
            },
            "Bats-P": {  
                "image": "images/Bats-P-GS.png",
                "download_file": "Bats-P-GS.zip",
            },
            "White": {  
                "image": "images/White-GS.png",
                "download_file": "White-GS.zip",
            },
            "Fire": {  
                "image": "images/Fire-GS.png",
                "download_file": "Fire-GS.zip",
            },
            "Fire-P": {  
                "image": "images/Fire-P-GS.png",
                "download_file": "Fire-P-GS.zip",
            },
        },
    },
    {
        "id": 35,
        "category": "women",
        "name": "Edgy Punk Studded Corset",
        "price": "$6000",
        "slug": "studded-corset",
        "sku": "SC-100",
        "color_variants": {
            "Black": {  
                "image": "images/Black-SC.png",
                "download_file": "Black-SC.zip",
            },
            "Brown": {  
                "image": "images/Brown-SC.png",
                "download_file": "Brown-SC.zip",
            },
            "Purple": {  
                "image": "images/Purple-SC.png",
                "download_file": "Purple-SC.zip",
            },
            "Red": {  
                "image": "images/Red-SC.png",
                "download_file": "Red-SC.zip",
            },
            "White": {  
                "image": "images/White-SC.png",
                "download_file": "White-SC.zip",
            },
        },
    },
    {
        "id": 36,
        "category": "women",
        "name": "Sweet Cherry Heart Earrings",
        "price": "$4700",
        "slug": "cherry-earrings",
        "sku": "CE-100",
        "color_variants": {
            "Cherry": {  
                "image": "images/CE.png",
                "download_file": "Cherry-Earrings.zip",
            },
        },
    },
    {
        "id": 37,
        "category": "women",
        "name": "Delicate Triple Heart Earrings",
        "price": "$4700",
        "slug": "triple-heart",
        "sku": "TH-100",
        "color_variants": {
            "Gold": {  
                "image": "images/Gold-TH.png",
                "download_file": "Gold-TH.zip",
            },
            "Plate": {  
                "image": "images/Plate-TH.png",
                "download_file": "Plate-TH.zip",
            },
        },
    },
    {
        "id": 38,
        "category": "men",
        "name": "Urban Cargo Pants",
        "price": "$4500",
        "slug": "cargo-pants",
        "sku": "UP-100",
        "color_variants": {
            "Camo": {  
                "image": "images/Camo-UP.png",
                "download_file": "Camo-UP.zip",
            },
            "Black": {  
                "image": "images/Black-UP.png",
                "download_file": "Black-UP.zip",
            },
            "Gray": {  
                "image": "images/Gray-UP.png",
                "download_file": "Gray-UP.zip",
            },
            "Light Blue": {  
                "image": "images/LightBlue-UP.png",
                "download_file": "LightBlue-UP.zip",
            },
        },
    },
    {
        "id": 38,
        "category": "men",
        "name": "Cargo Pants with Chain",
        "price": "$4500",
        "slug": "cargo-chain",
        "sku": "PC-100",
        "color_variants": {
            "Black": {  
                "image": "images/Black-PC.png",
                "download_file": "Black-PC.zip",
            },
            "Gray": {  
                "image": "images/White-PC.png",
                "download_file": "Gray-PC.zip",
            },
            "Red": {  
                "image": "images/Red-PC.png",
                "download_file": "Red-PC.zip",
            },
        },
    },
    {
        "id": 39,
        "category": "men",
        "name": "Custom Sneaker",
        "price": "$15000",
        "slug": "custom-sneaker-men",
        "sku": "CS-102",
        "color_variants": {
            "Billie Eilish": {  
                "image": "images/Billie.png",
                "download_file": "Billie-men.zip",
            },
            "BW Cartoon": {  
                "image": "images/BW-Cartoon.png",
                "download_file": "BW-Cartoon-men.zip",
            },
            "Classic": {  
                "image": "images/Classic.png",
                "download_file": "Classic-men.zip",
            },
            "Melted": {  
                "image": "images/Melted.png",
                "download_file": "Melted-men.zip",
            },
            "Pikachu": {  
                "image": "images/Pikachu.png",
                "download_file": "Pikachu-men.zip",
            },
            "Stitch": {  
                "image": "images/Stitch.png",
                "download_file": "Stitch-men.zip",
            },
            "White Cartoon": {  
                "image": "images/White-Cartoon.png",
                "download_file": "White-Cartoon-men.zip",
            },
            "All-White Cartoon": {  
                "image": "images/All-White.png",
                "download_file": "All-White-men.zip",
            },
        },
    },
    {
        "id": 40,
        "category": "women",
        "name": "Cropped Jacket",
        "price": "$4500",
        "slug": "cropped-jacket",
        "sku": "CJ-100",
        "color_variants": {
            "Black": {  
                "image": "images/Black-CJ.png",
                "download_file": "Black-CJ.zip",
            },
            "Gray": {  
                "image": "images/Gray-CJ.png",
                "download_file": "Gray-CJ.zip",
            },
            "White": {  
                "image": "images/White-CJ.png",
                "download_file": "White-CJ.zip",
            },
            "Green": {  
                "image": "images/Green-CJ.png",
                "download_file": "Green-CJ.zip",
            },
        },
    },
    {
        "id": 44,
        "category": "men",
        "name": "Vibez Zip Hoodie",
        "price": "$4500",
        "slug": "zip-hoodie",
        "sku": "ZH-100",
        "color_variants": {
            "Black": {  
                "image": "images/Black-ZH.png",
                "download_file": "Black-ZH.zip",
            },
            "Blue": {  
                "image": "images/Blue-ZH.png",
                "download_file": "Blue-ZH.zip",
            },
            "Gray": {  
                "image": "images/Gray-ZH.png",
                "download_file": "Gray-ZH.zip",
            },
            "Red": {  
                "image": "images/Red-ZH.png",
                "download_file": "Red-ZH.zip",
            },
        },
    },
    {
        "id": 45,
        "category": "women",
        "name": "Off-Shoulder Top",
        "price": "$3700",
        "slug": "off-shoulder",
        "sku": "OS-100",
        "color_variants": {
            "Black S": {  
                "image": "images/BlackS-OS.png",
                "download_file": "BlackS-OS.zip",
            },
            "Ghost": {  
                "image": "images/Ghost-OS.png",
                "download_file": "Ghost-OS.zip",
            },
            "Black": {  
                "image": "images/BlackSS-OS.png",
                "download_file": "BlackSS-OS.zip",
            },
            "White": {  
                "image": "images/WhiteSS-OS.png",
                "download_file": "WhiteSS-OS.zip",
            },
            "White S": {  
                "image": "images/WhiteS-OS.png",
                "download_file": "WhiteS-OS.zip",
            },
        },
    },
    {
        "id": 46,
        "category": "women",
        "name": "Cargo Pants",
        "price": "$4500",
        "slug": "cargo-pants-female",
        "sku": "OS-100",
        "color_variants": {
            "White": {  
                "image": "images/White-FCP.png",
                "download_file": "White-FCP.zip",
            },
            "Green": {  
                "image": "images/Green-FCP.png",
                "download_file": "Green-FCP.zip",
            },
            "Black": {  
                "image": "images/Black-FCP.png",
                "download_file": "Black-FCP.zip",
            },
            "Gray": {  
                "image": "images/Gray-FCP.png",
                "download_file": "Gray-FCP.zip",
            },
            "Red": {  
                "image": "images/Red-FCP.png",
                "download_file": "Red-FCP.zip",
            },
            "Beige": {  
                "image": "images/Beige-FCP.png",
                "download_file": "Beige-FCP.zip",
            },
        },
    },
    {
        "id": 47,
        "category": "men",
        "name": "Baggy Pants",
        "price": "$4500",
        "slug": "baggy-pants",
        "sku": "BP-100",
        "color_variants": {
            "Blue": {  
                "image": "images/Blue-BP.png",
                "download_file": "Blue-BP.zip",
            },
            "Beige": {  
                "image": "images/Beige-BP.png",
                "download_file": "Beige-BP.zip",
            },
            "Gray": {  
                "image": "images/Gray-BP.png",
                "download_file": "Gray-BP.zip",
            },
            "Green": {  
                "image": "images/Green-BP.png",
                "download_file": "Green-BP.zip",
            },
            "White": {  
                "image": "images/White-BP.png",
                "download_file": "White-BP.zip",
            },
        },
    },
    {
        "id": 48,
        "category": "men",
        "name": "Jogger",
        "price": "$4500",
        "slug": "jogger",
        "sku": "JP-100",
        "color_variants": {
            "Black": {  
                "image": "images/Black-Jogger.png",
                "download_file": "Black-Jogger.zip",
            },
            "Blue": {  
                "image": "images/Blue-Jogger.png",
                "download_file": "Blue-Jogger.zip",
            },
            "Dark Gray": {  
                "image": "images/Dark-Gray-Jogger.png",
                "download_file": "Dark-Gray-Jogger.zip",
            },
            "Gray": {  
                "image": "images/Gray-Jogger.png",
                "download_file": "Gray-Jogger.zip",
            },
            "Green": {  
                "image": "images/Green-Jogger.png",
                "download_file": "Green-Jogger.zip",
            },
            "Light Blue": {  
                "image": "images/Light-Blue-Jogger.png",
                "download_file": "Light-Blue-Jogger.zip",
            },
            "Red": {  
                "image": "images/Red-Jogger.png",
                "download_file": "Red-Jogger.zip",
            },
        },
    },
    {
        "id": 49,
        "category": "men",
        "name": "Hoodie",
        "price": "$4000",
        "slug": "hoodie",
        "sku": "H-100",
        "color_variants": {
            "White": {  
                "image": "images/White-Hoodie.png",
                "download_file": "White-Hoodie.zip",
            },
            "Black": {  
                "image": "images/Black-Hoodie.png",
                "download_file": "Black-Hoodie.zip",
            },
            "Gray": {  
                "image": "images/Gray-Hoodie.png",
                "download_file": "Gray-Hoodie.zip",
            },
        },
    },
    {
        "id": 50,
        "category": "men",
        "name": "Tank Top",
        "price": "$6000",
        "slug": "tank-top",
        "sku": "TT-100",
        "color_variants": {
            "Gray A": {  
                "image": "images/Gray-A.png",
                "download_file": "Gray-A.zip",
            },
            "White": {  
                "image": "images/White-TT.png",
                "download_file": "White-TT.zip",
            },
            "Black A": {  
                "image": "images/Black-A.png",
                "download_file": "Black-A.zip",
            },
            "Black B": {  
                "image": "images/Black-B.png",
                "download_file": "Black-B.zip",
            },
            "Gray B": {  
                "image": "images/Gray-B.png",
                "download_file": "Gray-B.zip",
            },
            "Black C": {  
                "image": "images/Black-C.png",
                "download_file": "Black-C.zip",
            },
            "Black D": {  
                "image": "images/Black-D.png",
                "download_file": "Black-D.zip",
            },
            "Red": {  
                "image": "images/Red-TT.png",
                "download_file": "Red-TT.zip",
            },
            "Black": {  
                "image": "images/Black-TT.png",
                "download_file": "Black-TT.zip",
            },
        },
    },
    {
        "id": 51,
        "category": "women",
        "name": "Retro Runner 90s",
        "price": "$5500",
        "slug": "retro-runner",
        "sku": "RR-100",
        "color_variants": {
            "Green": {  
                "image": "images/Green-CS.png",
                "download_file": "Green-CS.zip",
            },
            "Pink": {  
                "image": "images/Pink-CS.png",
                "download_file": "Pink-CS.zip",
            },
            "Red": {  
                "image": "images/Red-CS.png",
                "download_file": "Red-CS.zip",
            },
            "White": {  
                "image": "images/White-CS.png",
                "download_file": "White-CS.zip",
            },
            "Yellow": {  
                "image": "images/Yellow-CS.png",
                "download_file": "Yellow-CS.zip",
            },
            "Black": {  
                "image": "images/Black-CS.png",
                "download_file": "Black-CS.zip",
            },
            "Blue": {  
                "image": "images/Blue-CS.png",
                "download_file": "Blue-CS.zip",
            },
        },
    },
    {
        "id": 52,
        "category": "men",
        "name": "Cross Necklace",
        "price": "$3000",
        "slug": "cross-necklace",
        "sku": "CN-100",
        "color_variants": {
            "Plate": {  
                "image": "images/Necklace-Cross-man.png",
                "download_file": "Necklace-Cross-men.zip",
            },
        },
    },
    {
        "id": 53,
        "category": "men",
        "name": "Retro Runner 90s",
        "price": "$5500",
        "slug": "retro-runner-men",
        "sku": "RR-101",
        "color_variants": {
            "Black": {  
                "image": "images/Black-RR-man.png",
                "download_file": "Black-RR-men.zip",
            },
            "Blue": {  
                "image": "images/Blue-RR-man.png",
                "download_file": "Blue-RR-men.zip",
            },
            "Green": {  
                "image": "images/Green-RR-man.png",
                "download_file": "Green-RR-men.zip",
            },
            "White": {  
                "image": "images/White-RR-man.png",
                "download_file": "White-RR-men.zip",
            },
            "Yellow": {  
                "image": "images/Yellow-RR-man.png",
                "download_file": "Yellow-RR-men.zip",
            },
            "Red": {  
                "image": "images/Red-RR-man.png",
                "download_file": "Red-RR-men.zip",
            },
        },
    },
    {
        "id": 54,
        "category": "men",
        "name": "Tank Top",
        "price": "$6000",
        "slug": "tank-top2",
        "sku": "TT-110",
        "color_variants": {
            "White": {  
                "image": "images/White-TTM.png",
                "download_file": "White-TTM.zip",
            },
            "Black": {  
                "image": "images/Black-TTM.png",
                "download_file": "Black-TTM.zip",
            },
            "Black 2": {  
                "image": "images/Black2-TTM.png",
                "download_file": "Black2-TTM.zip",
            },
            "Black 3": {  
                "image": "images/Black3-TTM.png",
                "download_file": "Black3-TTM.zip",
            },
            "Black 4": {  
                "image": "images/Black4-TTM.png",
                "download_file": "Black4-TTM.zip",
            },
            "Blue": {  
                "image": "images/Blue-TTM.png",
                "download_file": "Blue-TTM.zip",
            },
            "White 2": {  
                "image": "images/White2-TTM.png",
                "download_file": "White2-TTM.zip",
            },
            "White 3": {  
                "image": "images/White3-TTM.png",
                "download_file": "White3-TTM.zip",
            },
            "White 4": {  
                "image": "images/White4-TTM.png",
                "download_file": "White4-TTM.zip",
            },
        },
    },
    {
        "id": 55,
        "category": "women",
        "name": "Classic Sneakers",
        "price": "$5500",
        "slug": "classic-sneakers",
        "sku": "CS-110",
        "color_variants": {
            "Beige": {  
                "image": "images/Beige-SP.png",
                "download_file": "Beige-SP.zip",
            },
            "Black": {  
                "image": "images/Black-SP.png",
                "download_file": "Black-SP.zip",
            },
            "Blue": {  
                "image": "images/Blue-SP.png",
                "download_file": "Blue-SP.zip",
            },
            "Green": {  
                "image": "images/Green-SP.png",
                "download_file": "Green-SP.zip",
            },
            "Orange": {  
                "image": "images/Orange-SP.png",
                "download_file": "Orange-SP.zip",
            },
            "Pink": {  
                "image": "images/Pink-SP.png",
                "download_file": "Pink-SP.zip",
            },
            "Purple": {  
                "image": "images/Purple-SP.png",
                "download_file": "Purple-SP.zip",
            },
            "Red": {  
                "image": "images/Red-SP.png",
                "download_file": "Red-SP.zip",
            },
            "Salmon": {  
                "image": "images/Salmon-SP.png",
                "download_file": "Salmon-SP.zip",
            },
             "White": {  
                "image": "images/White-SP.png",
                "download_file": "White-SP.zip",
            },
              "Yellow": {  
                "image": "images/Yellow-SP.png",
                "download_file": "Yellow-SP.zip",
            },
        },
    },
    {
        "id": 56,
        "category": "men",
        "name": "Classic Sneakers",
        "price": "$5500",
        "slug": "classic-sneakers-men",
        "sku": "CS-111",
        "color_variants": {
            "Beige": {  
                "image": "images/Beige-SP.png",
                "download_file": "Beige-SPM.zip",
            },
            "Black": {  
                "image": "images/Black-SP.png",
                "download_file": "Black-SPM.zip",
            },
            "Blue": {  
                "image": "images/Blue-SP.png",
                "download_file": "Blue-SPM.zip",
            },
            "Green": {  
                "image": "images/Green-SP.png",
                "download_file": "Green-SPM.zip",
            },
            "Orange": {  
                "image": "images/Orange-SP.png",
                "download_file": "Orange-SPM.zip",
            },
            "Red": {  
                "image": "images/Red-SP.png",
                "download_file": "Red-SPM.zip",
            },
             "White": {  
                "image": "images/White-SP.png",
                "download_file": "White-SPM.zip",
            },
              "Yellow": {  
                "image": "images/Yellow-SP.png",
                "download_file": "Yellow-SPM.zip",
            },
        },
    },
    {
        "id": 57,
        "category": "women",
        "name": "Drawstring Neck Crop Top",
        "price": "$5000",
        "slug": "neck-crop",
        "sku": "NCT-100",
        "color_variants": {
            "Red": {  
                "image": "images/NCT-Red.png",
                "download_file": "NCT-Red.zip",
            },
            "Green": {  
                "image": "images/NCT-Green.png",
                "download_file": "NCT-Green.zip",
            },
            "Blue": {  
                "image": "images/NCT-Blue.png",
                "download_file": "NCT-Blue.zip",
            },
            "Purple": {  
                "image": "images/NCT-Purple.png",
                "download_file": "NCT-Purple.zip",
            },
            "Black": {  
                "image": "images/NCT-Black.png",
                "download_file": "NCT-Black.zip",
            },
            "Pink": {  
                "image": "images/NCT-Pink.png",
                "download_file": "NCT-Pink.zip",
            },
        },
    },
    {
        "id": 58,
        "category": "women",
        "name": "Ribbed Long Sleeve Sweater",
        "price": "$5000",
        "slug": "ribbed-sweater",
        "sku": "RS-100",
        "color_variants": {
            "Pink": {  
                "image": "images/RS-Pink.png",
                "download_file": "RS-Pink.zip",
            },
            "Black": {  
                "image": "images/RS-Black.png",
                "download_file": "RS-Black.zip",
            },
            "Red": {  
                "image": "images/RS-Red.png",
                "download_file": "RS-Red.zip",
            },
            "White": {  
                "image": "images/RS-White.png",
                "download_file": "RS-White.zip",
            },
            "Yellow": {  
                "image": "images/RS-Yellow.png",
                "download_file": "RS-Yellow.zip",
            },
        },
    },
    {
        "id": 59,
        "category": "women",
        "name": "Stretch Fit Active Shorts",
        "price": "$4000",
        "slug": "stretch-shorts",
        "sku": "SS-100",
        "color_variants": {
            "Gray": {  
                "image": "images/SS-Gray.png",
                "download_file": "SS-Gray.zip",
            },
            "White": {  
                "image": "images/SS-White.png",
                "download_file": "SS-White.zip",
            },
            "Purple": {  
                "image": "images/SS-Purple.png",
                "download_file": "SS-Purple.zip",
            },
            "Blue": {  
                "image": "images/SS-Blue.png",
                "download_file": "SS-Blue.zip",
            },
            "Orange": {  
                "image": "images/SS-Orange.png",
                "download_file": "SS-Orange.zip",
            },
            "Brown": {  
                "image": "images/SS-Brown.png",
                "download_file": "SS-Brown.zip",
            },
        },
    },
    {
        "id": 60,
        "category": "men",
        "name": "Retro Bomber Jacket",
        "price": "$7000",
        "slug": "retro-bomber",
        "sku": "BJ-100",
        "color_variants": {
            "Blue": {  
                "image": "images/BJ-Blue.png",
                "download_file": "BJ-Blue.zip",
            },
            "Black": {  
                "image": "images/BJ-Black.png",
                "download_file": "BJ-Black.zip",
            },
            "Red": {  
                "image": "images/BJ-Red.png",
                "download_file": "BJ-Red.zip",
            },
            "All Black": {  
                "image": "images/BJ-All-Black.png",
                "download_file": "BJ-All-Black.zip",
            },
            "Brown": {  
                "image": "images/BJ-Brown.png",
                "download_file": "BJ-Brown.zip",
            },
            "Gray": {  
                "image": "images/BJ-Gray.png",
                "download_file": "BJ-Gray.zip",
            },
        },
    },
    {
        "id": 61,
        "category": "men",
        "name": "Bart Collection",
        "price": "$6000",
        "slug": "bart-tee",
        "sku": "LPC-100",
        "color_variants": {
            "Hellboy White": {  
                "image": "images/LPC-HellboyW.png",
                "download_file": "LPC-HellboyW.zip",
            },
            "Hellboy Black": {  
                "image": "images/LPC-HellboyB.png",
                "download_file": "LPC-HellboyB.zip",
            },
            "Hellboy Pink": {  
                "image": "images/LPC-HellboyP.png",
                "download_file": "LPC-HellboyP.zip",
            },
            "Hellboy Gray": {  
                "image": "images/LPC-HellboyG.png",
                "download_file": "LPC-HellboyG.zip",
            },
            "Susboy": {  
                "image": "images/LPC-Susboy.png",
                "download_file": "LPC-Susboy.zip",
            },
        },
    },
    {
        "id": 62,
        "category": "men",
        "name": "Baseball Team Jerseys",
        "price": "$6300",
        "slug": "baseball-teams",
        "sku": "BT-100",
        "color_variants": {
            "Milwaukee": {  
                "image": "images/BT-Milwaukee.png",
                "download_file": "BT-Milwaukee.zip",
            },
            "Milwaukee Black": {  
                "image": "images/BT-MilwaukeeB.png",
                "download_file": "BT-MilwaukeeB.zip",
            },
            "Detroit": {  
                "image": "images/BT-Detroit.png",
                "download_file": "BT-Detroit.zip",
            },
            "Astros": {  
                "image": "images/BT-Astros.png",
                "download_file": "BT-Astros.zip",
            },
            "New York": {  
                "image": "images/BT-NewYork.png",
                "download_file": "BT-NewYork.zip",
            },
            "Pirates": {  
                "image": "images/BT-Pirates.png",
                "download_file": "BT-Pirates.zip",
            },
            "Dodgers": {  
                "image": "images/BT-Dodgers.png",
                "download_file": "BT-Dodgers.zip",
            },
            "Seattle": {  
                "image": "images/BT-Seattle.png",
                "download_file": "BT-Seattle.zip",
            },
            "RedSox": {  
                "image": "images/BT-RedSox.png",
                "download_file": "BT-RedSox.zip",
            },
            "Cardinals": {  
                "image": "images/BT-Cardinals.png",
                "download_file": "BT-Cardinals.zip",
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
    "TAKE50": {"type": "percent", "value": 50},  # $10 de descuento fijo
    #"LAUNCH40": {"type": "percent", "value": 40},  # $40 de descuento fijo
    "YANE90": {"type": "percent", "value": 90},  # 100 de descuento fijo
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


# ==============================================================================
# === RUTA PARA ENVIAR FEEDBACK A DISCORD ======================================
# ==============================================================================


@app.route("/api/submit_feedback", methods=["POST"])
def submit_feedback():
    """
    Recibe el feedback del formulario, lo formatea y lo envía a un webhook de Discord.
    """
    # Comprobamos si la URL del webhook está configurada
    if not DISCORD_WEBHOOK_URL:
        return jsonify({"success": False, "message": "Webhook not configured."}), 500

    try:
        # 1. Obtenemos los datos enviados desde JavaScript
        data = request.get_json()
        rating = data.get("recommend_rating")
        text = data.get("feedback_text", "No comment provided.")

        # Validación simple
        if rating is None:
            return jsonify({"success": False, "message": "Rating is required."}), 400

        # 2. Creamos un mensaje bonito para Discord usando "embeds"
        discord_payload = {
            "embeds": [
                {
                    "title": "New User Feedback! ✨",
                    "color": 3066993,  # Color verde
                    "fields": [
                        {
                            "name": "How likely to recommend?",
                            "value": f"**{rating} / 10**",
                            "inline": True,
                        },
                        {"name": "Comment", "value": text},
                    ],
                    "footer": {
                        "text": f"Received at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
                    },
                }
            ]
        }

        # 3. Enviamos la petición POST al webhook de Discord
        response = requests.post(DISCORD_WEBHOOK_URL, json=discord_payload)
        response.raise_for_status()  # Esto generará un error si la petición falla (ej. 404)

        # 4. Devolvemos una respuesta de éxito al navegador
        return jsonify({"success": True, "message": "Feedback sent successfully!"})

    except requests.exceptions.RequestException as e:
        print(f"!!! ERROR sending to Discord: {e}")
        return jsonify({"success": False, "message": "Failed to send feedback."}), 500
    except Exception as e:
        print(f"!!! UNEXPECTED ERROR in submit_feedback: {e}")
        return (
            jsonify({"success": False, "message": "An internal error occurred."}),
            500,
        )


@app.route("/")
def home():
    return render_template(
        "index.html", active_page="home", body_class="page-home", products=all_products
    )


@app.route("/<category_name>")
def category_page(category_name):
    if category_name not in ["women", "men", "accessories"]:
        abort(404)

    # --- LÓGICA DE PAGINACIÓN ---
    # 1. Obtenemos el número de página de la URL (ej. /women?page=2). Si no se especifica, es la página 1.
    page = request.args.get("page", 1, type=int)
    ITEMS_PER_PAGE = 12  # Definimos el máximo de artículos por página

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
        {"text": "Home", "url": url_for("home")},
        {"text": category_name.upper(), "url": None},
    ]

    # 5. Pasamos solo los productos de ESTA PÁGINA y la info de paginación a la plantilla
    return render_template(
        "category.html",
        title=category_name.capitalize(),
        products=paginated_products,  # Solo los 12 (o menos) productos de esta página
        active_page=category_name,
        breadcrumbs=breadcrumbs,
        # Nuevas variables para la paginación:
        current_page=page,
        total_pages=total_pages,
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
        # =======================================================
        # === ¡NUEVA LÓGICA DE NOTIFICACIÓN A DISCORD! ===
        # =======================================================
        if DISCORD_SALES_WEBHOOK_URL:
            try:
                # 1. Formateamos los detalles de la compra para que se vean bien
                character_name = f"{billing_address_data.get('firstname')} {billing_address_data.get('lastname')}"

                # Creamos una lista de los productos comprados
                items_purchased = "\n".join(
                    [f"- {item['name']} x{item['quantity']}" for item in cart.values()]
                )

                # 2. Creamos el mensaje "embed" para Discord
                discord_payload = {
                    "embeds": [
                        {
                            "title": "New Order Received! 💸",
                            "color": 3066993,  # Color verde
                            "fields": [
                                {
                                    "name": "Order Number",
                                    "value": f"`{new_order.order_number}`",
                                    "inline": True,
                                },
                                {
                                    "name": "Character Name",
                                    "value": character_name,
                                    "inline": True,
                                },
                                {
                                    "name": "Total Amount",
                                    "value": f"**${total:.2f}**",
                                    "inline": True,
                                },
                                {
                                    "name": "Items Purchased",
                                    "value": items_purchased,
                                    "inline": False,
                                },
                            ],
                            "footer": {
                                "text": f"Vibez Sales Bot | {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
                            },
                        }
                    ]
                }

                # 3. Enviamos la notificación al webhook
                requests.post(DISCORD_SALES_WEBHOOK_URL, json=discord_payload)

            except Exception as e:
                # Si falla el envío a Discord, solo lo imprimimos en la consola del servidor.
                # No detenemos la confirmación de la compra para el usuario.
                print(
                    f"!!! CRITICAL: Failed to send Discord sales notification. Error: {e}"
                )
        # === FIN DE LA LÓGICA DE NOTIFICACIÓN ===
        # =======================================================
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
