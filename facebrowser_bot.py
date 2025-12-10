import requests
from bs4 import BeautifulSoup
import time
import os
import sys # Importamos el módulo 'sys'

# --- CONFIGURACIÓN DE PRUEBA ---
FACEBROWSER_URL = "https://face.gta.world/pages/voidcraft"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1447987628359291123/0aF3AmpaDkrLBjEWpdz2EOOFxrx35JAbX7-G08hjo62O2G1avn1ELu4qvK98aKHZ2QHX"
LAST_POST_FILE = "/data/last_post.txt"
CHECK_INTERVAL_SECONDS = 60  # CAMBIO: Ahora es 1 minuto para pruebas

def get_last_seen_post():
    """Lee la URL de la última publicación guardada."""
    try:
        if not os.path.exists(LAST_POST_FILE):
            print("Archivo 'last_post.txt' no encontrado, se creará uno nuevo.", flush=True)
            return ""
        with open(LAST_POST_FILE, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        print(f"!!! ERROR al leer el archivo '{LAST_POST_FILE}': {e}", flush=True)
        return ""

def save_last_seen_post(url):
    """Guarda la URL de la nueva publicación."""
    try:
        os.makedirs(os.path.dirname(LAST_POST_FILE), exist_ok=True)
        with open(LAST_POST_FILE, 'w', encoding='utf-8') as f:
            f.write(url)
        print(f"URL guardada exitosamente en '{LAST_POST_FILE}'.", flush=True)
    except Exception as e:
        print(f"!!! ERROR al guardar en el archivo '{LAST_POST_FILE}': {e}", flush=True)

def send_discord_notification(post_url):
    """Envía la notificación a Discord."""
    payload = {"content": f"@here {post_url}"}
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print(f"Notificación enviada a Discord: {post_url}", flush=True)
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar la notificación a Discord: {e}", flush=True)

def check_for_new_post():
    """
    La función principal que ahora busca el <span> "Recent Updates"
    para encontrar la última publicación.
    """
    print("Buscando nuevas publicaciones...", flush=True)
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(FACEBROWSER_URL, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. LA CLAVE: Encontrar el <span> que contiene "Recent Updates"
        recent_updates_header = soup.find('span', string='Recent Updates')
        
        latest_post_container = None
        if recent_updates_header:
            # 2. A partir del <span>, buscamos su contenedor padre 'posts-filter'
            #    y luego el primer 'div.post' que le sigue.
            posts_filter_div = recent_updates_header.find_parent('div', class_='posts-filter')
            if posts_filter_div:
                latest_post_container = posts_filter_div.find_next_sibling('div', class_='post')
            print("Sección 'Recent Updates' encontrada. Analizando la primera publicación.", flush=True)
        
        # Fallback si la lógica anterior falla
        if not latest_post_container:
            print("No se encontró la publicación a través de 'Recent Updates', usando método de fallback.", flush=True)
            # Como fallback, cogemos el segundo div.post de la página
            all_posts = soup.find_all('div', class_='post')
            if len(all_posts) > 1:
                latest_post_container = all_posts[1]

        if not latest_post_container:
            print("No se pudo encontrar un contenedor de publicación válido.", flush=True)
            return

        # 4. El resto de la lógica para encontrar el enlace es la misma
        post_time_div = latest_post_container.find('div', class_='post-time')
        if not post_time_div:
            print("La publicación más reciente no tiene un 'post-time'. Saltando.", flush=True)
            return

        permalink_element = post_time_div.find('a')
        if not permalink_element or 'href' not in permalink_element.attrs:
            print("No se pudo encontrar el enlace permanente de la publicación.", flush=True)
            return
        
        post_url = permalink_element['href']
        last_seen_post_url = get_last_seen_post()

        if post_url and post_url != last_seen_post_url:
            print(f"¡Nueva publicación encontrada!: {post_url}", flush=True)
            send_discord_notification(post_url)
            save_last_seen_post(post_url)
        else:
            print("No hay nuevas publicaciones.", flush=True)

    except Exception as e:
        print(f"!!! Ocurrió un error inesperado durante el scraping: {e}", flush=True)

# --- Bucle Principal (Ahora a prueba de fallos) ---
if __name__ == "__main__":
    print("Iniciando el bot de Facebrowser...", flush=True)
    while True:
        try:
            check_for_new_post()
        except Exception as e:
            print(f"!!! ERROR CRÍTICO en el bucle principal. Error: {e}", flush=True)
        
        print(f"Esperando {CHECK_INTERVAL_SECONDS} segundos para la próxima comprobación...", flush=True)
        time.sleep(CHECK_INTERVAL_SECONDS)
