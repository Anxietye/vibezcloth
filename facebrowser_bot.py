import requests
from bs4 import BeautifulSoup
import time
import os

FACEBROWSER_URL = "https://face.gta.world/pages/voidcraft"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1447961979347275897/MfYURuJLowly1ndXPiEVZ9WIwe3IXNAPXVFN7c4p-a_nwmCNSSx3OyBmOx-A26-UNw7F"
LAST_POST_FILE = "last_post.txt" # Archivo para guardar la última publicación
CHECK_INTERVAL_SECONDS = 300 # 300 segundos = 5 minutos

def get_last_seen_post():
    """Lee el contenido de la última publicación guardada."""
    if not os.path.exists(LAST_POST_FILE):
        return ""
    with open(LAST_POST_FILE, 'r', encoding='utf-8') as f:
        return f.read().strip()

def save_last_seen_post(content):
    """Guarda el contenido de la nueva publicación."""
    with open(LAST_POST_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

def send_discord_notification(post_url):
    """Envía la notificación a Discord con el enlace al post."""
    
    # Creamos un mensaje "embed" más atractivo
    payload = {
        "embeds": [
            {
                "title": "New Post on Facebrowser!",
                "description": f"A new post has been published on the Voidcraft page.\n\n[**Click here to view the post**]({post_url})",
                "color": 10813440, # Color rojo oscuro de Voidcraft
                "url": post_url,
                "footer": {
                    "text": "Voidcraft Social Bot"
                }
            }
        ]
    }
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print("Notificación de Discord enviada con éxito.")
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar la notificación a Discord: {e}")

def check_for_new_post():
    """La función principal que hace el scraping, busca el enlace y lo envía."""
    print("Buscando nuevas publicaciones...")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(FACEBROWSER_URL, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Encuentra el contenedor de la PRIMERA publicación en la página.
        #    Facebrowser parece envolver cada post en un div con la clase 'post'.
        latest_post_container = soup.find('div', class_='post')
        
        if not latest_post_container:
            print("No se pudo encontrar el contenedor principal de la publicación (selector 'div.post').")
            return

        # 2. Dentro de ese contenedor, busca el enlace del timestamp.
        #    Basado en tu imagen, está en 'a' dentro de 'div.post-time'.
        permalink_element = latest_post_container.find('div', class_='post-time').find('a')

        if not permalink_element or 'href' not in permalink_element.attrs:
            print("No se pudo encontrar el enlace permanente (permalink) de la publicación.")
            post_url = FACEBROWSER_URL # Usamos la URL general como fallback
        else:
            post_url = permalink_element['href']
            # El href ya es una URL completa, no necesitamos añadirle el dominio.
        
        last_seen_post_url = get_last_seen_post()

        # 3. Compara la URL y actúa
        if post_url and post_url != last_seen_post_url:
            print(f"¡Nueva publicación encontrada!: {post_url}")
            send_discord_notification(post_url)
            save_last_seen_post(post_url)
        else:
            print("No hay nuevas publicaciones.")

    except requests.exceptions.RequestException as e:
        print(f"Error al acceder a Facebrowser: {e}")

# --- Bucle Principal ---
if __name__ == "__main__":
    while True:
        check_for_new_post()
        print(f"Esperando {CHECK_INTERVAL_SECONDS} segundos para la próxima comprobación...")
        time.sleep(CHECK_INTERVAL_SECONDS)
        