import requests
from bs4 import BeautifulSoup
import time
import os

# --- CONFIGURACIÓN ---
FACEBROWSER_URL = "https://face.gta.world/pages/voidcraft"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1447987628359291123/0aF3AmpaDkrLBjEWpdz2EOOFxrx35JAbX7-G08hjo62O2G1avn1ELu4qvK98aKHZ2QHX"
# El archivo ahora se guarda en el disco persistente de Render
LAST_POST_FILE = "/data/last_post.txt" 
CHECK_INTERVAL_SECONDS = 300 # 5 minutos

def get_last_seen_post():
    """Lee la URL de la última publicación guardada, con manejo de errores."""
    try:
        if not os.path.exists(LAST_POST_FILE):
            print("Archivo 'last_post.txt' no encontrado, se creará uno nuevo.")
            return ""
        with open(LAST_POST_FILE, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        print(f"!!! ERROR al leer el archivo '{LAST_POST_FILE}': {e}")
        return "" # Devuelve vacío si no se puede leer

def save_last_seen_post(url):
    """Guarda la URL de la nueva publicación, con manejo de errores."""
    try:
        # Aseguramos que el directorio /data exista
        os.makedirs(os.path.dirname(LAST_POST_FILE), exist_ok=True)
        with open(LAST_POST_FILE, 'w', encoding='utf-8') as f:
            f.write(url)
        print(f"URL guardada exitosamente en '{LAST_POST_FILE}'.")
    except Exception as e:
        print(f"!!! ERROR al guardar en el archivo '{LAST_POST_FILE}': {e}")


def send_discord_notification(post_url):
    """Envía la notificación a Discord solo con el enlace."""
    payload = {
        "content": f"@here {post_url}"
    }
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print(f"Enlace de la nueva publicación enviado a Discord: {post_url}")
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
        
        latest_post_container = soup.find('div', class_='post')
        
        if not latest_post_container:
            print("No se pudo encontrar el contenedor de la publicación.")
            return

        permalink_element = latest_post_container.find('div', class_='post-time').find('a')

        if not permalink_element or 'href' not in permalink_element.attrs:
            print("No se pudo encontrar el enlace permanente de la publicación.")
            post_url = FACEBROWSER_URL
        else:
            post_url = permalink_element['href']
        
        last_seen_post_url = get_last_seen_post()

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