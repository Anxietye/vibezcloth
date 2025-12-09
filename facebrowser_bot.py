import requests
from bs4 import BeautifulSoup
import time
import os

# --- CONFIGURACIÓN ---
FACEBROWSER_URL = "https://face.gta.world/pages/voidcraft"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1447987628359291123/0aF3AmpaDkrLBjEWpdz2EOOFxrx35JAbX7-G08hjo62O2G1avn1ELu4qvK98aKHZ2QHX"
LAST_POST_FILE = "/data/last_post.txt"
CHECK_INTERVAL_SECONDS = 300

def get_last_seen_post():
    """Lee la URL de la última publicación guardada."""
    try:
        if not os.path.exists(LAST_POST_FILE):
            print("Archivo 'last_post.txt' no encontrado, se creará uno nuevo.")
            return ""
        with open(LAST_POST_FILE, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        print(f"!!! ERROR al leer el archivo '{LAST_POST_FILE}': {e}")
        return ""

def save_last_seen_post(url):
    """Guarda la URL de la nueva publicación."""
    try:
        os.makedirs(os.path.dirname(LAST_POST_FILE), exist_ok=True)
        with open(LAST_POST_FILE, 'w', encoding='utf-8') as f:
            f.write(url)
        print(f"URL guardada exitosamente en '{LAST_POST_FILE}'.")
    except Exception as e:
        print(f"!!! ERROR al guardar en el archivo '{LAST_POST_FILE}': {e}")

def send_discord_notification(post_url):
    """Envía la notificación a Discord."""
    payload = {"content": f"@here {post_url}"}
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print(f"Notificación enviada a Discord: {post_url}")
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar la notificación a Discord: {e}")

def check_for_new_post():
    """
    Función principal que hace el scraping. Ahora los errores son manejados
    internamente para no detener el bucle principal.
    """
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

        post_time_div = latest_post_container.find('div', class_='post-time')
        if not post_time_div:
            print("La publicación encontrada no tiene un div 'post-time'. Saltando esta comprobación.")
            return

        permalink_element = post_time_div.find('a')
        if not permalink_element or 'href' not in permalink_element.attrs:
            print("No se pudo encontrar el enlace permanente de la publicación.")
            return
        
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
    except AttributeError as e:
        print(f"!!! AttributeError: La estructura de Facebrowser pudo haber cambiado. Error: {e}")
    except Exception as e:
        print(f"!!! Ocurrió un error inesperado durante el scraping: {e}")

# --- Bucle Principal (Ahora a prueba de fallos) ---
if __name__ == "__main__":
    while True:
        # LA CLAVE: El try...except AHORA ESTÁ AQUÍ, envolviendo la llamada a la función
        try:
            check_for_new_post()
        except Exception as e:
            print(f"!!! ERROR CRÍTICO en el bucle principal, el bot se recuperará. Error: {e}")
        
        print(f"Esperando {CHECK_INTERVAL_SECONDS} segundos para la próxima comprobación...")
        time.sleep(CHECK_INTERVAL_SECONDS)