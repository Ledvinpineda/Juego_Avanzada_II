import pygame          # Biblioteca principal para el desarrollo de juegos
import pygame.freetype # Módulo para renderizar fuentes con más control (ej. tamaño)
import random          # Para generar números aleatorios (letras, posición de estrellas)
import math            # Para funciones matemáticas (sin para la animación oscilante)
import time            # Para medir el tiempo (duración de la intro, animaciones)
import json            # Para guardar y cargar la configuración del juego en un archivo JSON
import os              # Para interactuar con el sistema operativo (rutas de archivos)
import sys             # Para controlar el sistema (salir del juego)
from datetime import datetime # Para gestionar las marcas de tiempo de las partidas guardadas

# ========================
# CONFIGURACIÓN INICIAL
# ========================
pygame.init()          # Inicializa todos los módulos de Pygame
pygame.freetype.init() # Inicializa el módulo de fuentes freetype
pygame.mixer.init()    # Asegura que el mezclador de sonido se inicialice temprano
clock = pygame.time.Clock() # Crea un objeto Clock para controlar la velocidad de fotogramas

info = pygame.display.Info() # Obtiene información de la pantalla actual
ANCHO, ALTO = info.current_w, info.current_h # Establece el ancho y alto de la pantalla a la resolución actual
pantalla = pygame.display.set_mode((ANCHO, ALTO)) # Crea la ventana del juego a pantalla completa
pygame.display.set_caption("SpeedType Animated") # Establece el título de la ventana

# ========================
# COLORES Y FUENTES DISPONIBLES
# ========================
NEGRO = (0, 0, 0)      # Definición del color negro (RGB)
BLANCO = (255, 255, 255) # Definición del color blanco (RGB)
ROJO = (255, 0, 0)     # Definición del color rojo (RGB)
VERDE = (0, 255, 0)    # Definición del color verde (RGB)
GRIS_OSCURO = (50, 50, 50) # Nuevo color para el botón
GRIS_CLARO = (100, 100, 100) # Nuevo color para el botón (hover)
AMARILLO = (255, 255, 0)

colores_disponibles = [ # Lista de colores predefinidos para la personalización
    (255, 255, 255),   # Blanco
    (255, 0, 0),       # Rojo
    (0, 255, 0),       # Verde
    (0, 0, 255),       # Azul
    (255, 255, 0),     # Amarillo
    (255, 165, 0),     # Naranja
    (128, 0, 128)      # Púrpura
]

fuentes_disponibles = ["arial", "comicsansms", "couriernew", "verdana"] # Nombres de fuentes del sistema disponibles

# Colores para el degradado del texto (Azul a Amarillo)
COLOR_GRADIENTE_TOP = (0, 100, 255)  # Azul brillante
COLOR_GRADIENTE_BOTTOM = (255, 255, 0) # Amarillo brillante
COLOR_CONTORNO = (0, 0, 0) # Negro para el contorno

# Fuente a usar para los textos con estilo de logo (puedes probar otras como "Impact", "Arial Black")
FUENTE_LOGO_STYLE = "arial" # Si tienes un archivo .ttf, cárgalo con pygame.freetype.Font("ruta/a/tu/fuente.ttf", tamaño)

# ========================
# CARGAR FONDO
# ========================
try:
    ruta_fondo = os.path.join(os.path.dirname(__file__), "Fondo2.png")
    fondo_img = pygame.image.load(ruta_fondo).convert()
    fondo_img = pygame.transform.scale(fondo_img, (ANCHO, ALTO))
except:
    fondo_img = pygame.Surface((ANCHO, ALTO))
    fondo_img.fill(NEGRO)

try:
    ruta_fondo_pausa = os.path.join(os.path.dirname(__file__), "fondo.jpg")
    fondo_pausa_img = pygame.image.load(ruta_fondo_pausa).convert()
    fondo_pausa_img = pygame.transform.scale(fondo_pausa_img, (ANCHO, ALTO))
except Exception as e:
    print(f"Error al cargar el fondo de pausa: {e}")
    fondo_pausa_img = None


# ========================
# ESTRELLAS ANIMADAS
# ========================
estrellas = [[random.randint(0, ANCHO), random.randint(0, ALTO), random.uniform(0.5, 1.5)] for _ in range(100)]

def dibujar_estrellas(velocidad=1):
    """
    Dibuja estrellas que se mueven hacia abajo y reaparecen en la parte superior.
    """
    for estrella in estrellas:
        estrella[1] += estrella[2] * velocidad
        if estrella[1] > ALTO:
            estrella[0] = random.randint(0, ANCHO)
            estrella[1] = 0
        pygame.draw.circle(pantalla, BLANCO, (int(estrella[0]), int(estrella[1])), 2)

# ========================
# PARTICULAS DE EFECTO
# ========================
particulas = [] # Lista para almacenar partículas

def crear_particulas(x, y, color):
    """Crea un rastro de partículas en la posición dada."""
    for _ in range(10): # Genera 10 partículas
        particulas.append({
            'x': x,
            'y': y,
            'vx': random.uniform(-2, 2), # Velocidad en X
            'vy': random.uniform(-2, 2), # Velocidad en Y
            'radius': random.randint(2, 5), # Tamaño
            'color': color,
            'life': 30 # Duración de vida en fotogramas
        })

def actualizar_y_dibujar_particulas():
    """Actualiza la posición y dibuja las partículas, eliminando las que 'mueren'."""
    global particulas
    particulas_vivas = []
    for p in particulas:
        p['x'] += p['vx']
        p['y'] += p['vy']
        p['radius'] -= 0.1 # Se encogen con el tiempo
        p['life'] -= 1 # Reduce la vida

        if p['life'] > 0 and p['radius'] > 0:
            pygame.draw.circle(pantalla, p['color'], (int(p['x']), int(p['y'])), int(p['radius']))
            particulas_vivas.append(p)
    particulas = particulas_vivas

# ========================
# SONIDOS
# ========================
music_loaded = False
acierto_sound = None
fallo_sound = None
game_over_sound = None

try:
    acierto_sound = pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), "acierto.wav"))
    fallo_sound = pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), "fallo.wav"))
    game_over_sound = pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), "game_over.wav"))
    pygame.mixer.music.load(os.path.join(os.path.dirname(__file__), "musica_fondo.mp3"))
    pygame.mixer.music.set_volume(0.5)
    music_loaded = True
except Exception as e:
    print(f"Error cargando música de fondo o sonidos: {e}")

# ========================
# GUARDAR Y CARGAR CONFIG
# ========================
def guardar_config(fuente, tam, color):
    config = {"fuente": fuente, "tam": tam, "color": color}
    with open("config.json", "w") as f:
        json.dump(config, f)

def cargar_config():
    if os.path.exists("config.json"):
        try:
            with open("config.json") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error al cargar configuración: {e}")
            os.remove("config.json")
            return None
    return None

# ========================
# FUNCIONES DE GUARDAR/CARGAR PARTIDA
# ========================
def guardar_partida(estado_juego, game_mode):
    """Guarda el estado actual del juego en un archivo JSON."""
    saved_games = [] 
    if os.path.exists("partida_guardada.json"):
        try:
            with open("partida_guardada.json", "r") as f:
                content = f.read()
                if content:
                    loaded_data = json.loads(content)
                    if isinstance(loaded_data, list):
                        saved_games = loaded_data
                    elif isinstance(loaded_data, dict):
                        saved_games = [loaded_data]
                    else:
                        print(f"Advertencia: Contenido inesperado en partida_guardada.json. Tipo: {type(loaded_data)}. Creando nuevo archivo.")
                        saved_games = []
                else:
                    saved_games = []
        except (json.JSONDecodeError, FileNotFoundError):
            print("Archivo de guardado corrupto o no encontrado, se creará uno nuevo.")
            saved_games = []
    
    new_save = {
        "timestamp": datetime.now().isoformat(),
        "mode": game_mode,
        "state": estado_juego
    }
    
    saved_games.append(new_save)
    
    saved_games = [s for s in saved_games if isinstance(s, dict) and 'timestamp' in s]

    saved_games.sort(key=lambda x: x['timestamp'], reverse=True)
    saved_games = saved_games[:5]

    try:
        with open("partida_guardada.json", "w") as f:
            json.dump(saved_games, f, indent=4)
        print("Partida guardada exitosamente.")
    except Exception as e:
        print(f"Error al guardar la partida: {e}")

def cargar_partida():
    """Carga el estado del juego desde un archivo JSON."""
    if os.path.exists("partida_guardada.json"):
        try:
            with open("partida_guardada.json", "r") as f:
                content = f.read()
                if content:
                    loaded_data = json.loads(content)
                    if isinstance(loaded_data, list):
                        return [s for s in loaded_data if isinstance(s, dict) and 'timestamp' in s]
                    elif isinstance(loaded_data, dict):
                        return [loaded_data] if 'timestamp' in loaded_data else []
                    else:
                        print(f"Advertencia: Contenido inesperado al cargar partida. Tipo: {type(loaded_data)}. Se devuelve lista vacía.")
                        return []
                else:
                    return []
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error al cargar las partidas: {e}")
            if os.path.exists("partida_guardada.json"):
                os.remove("partida_guardada.json")
            return []
    return []

def eliminar_partida_guardada(timestamp_a_eliminar):
    """Elimina una partida guardada específica del archivo JSON."""
    saved_games = cargar_partida()
    juegos_restantes = [game for game in saved_games if game.get("timestamp") != timestamp_a_eliminar]
    
    try:
        with open("partida_guardada.json", "w") as f:
            json.dump(juegos_restantes, f, indent=4)
        print(f"Partida con timestamp {timestamp_a_eliminar} eliminada.")
    except Exception as e:
        print(f"Error al eliminar la partida: {e}")

# --- INICIO: CÓDIGO AGREGADO PARA PUNTUACIONES ---
def cargar_highscores():
    """Carga las puntuaciones más altas desde un archivo JSON."""
    if not os.path.exists("highscores.json"):
        return []
    try:
        with open("highscores.json", "r") as f:
            scores = json.load(f)
            return sorted(scores, key=lambda x: x['score'], reverse=True)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def guardar_highscores(scores):
    """Guarda la lista de puntuaciones en el archivo JSON."""
    with open("highscores.json", "w") as f:
        json.dump(scores, f, indent=4)

def check_if_highscore(score):
    """Verifica si una puntuación es suficientemente alta para estar en el top 5."""
    highscores = cargar_highscores()
    if len(highscores) < 5 or score > highscores[-1]['score']:
        return True
    return False
# --- FIN: CÓDIGO AGREGADO ---

# ========================
# FUNCIÓN DE RENDERIZADO DE TEXTO CON DEGRADADO Y CONTORNO
# ========================
def render_text_gradient(font, text, target_rect, surface, gradient_colors, border_color, border_thickness):
    offsets = []
    for i in range(-border_thickness, border_thickness + 1):
        for j in range(-border_thickness, border_thickness + 1):
            if i != 0 or j != 0:
                offsets.append((i, j))
    
    for ox, oy in offsets:
        text_surf_border, text_rect_border = font.render(text, border_color)
        text_rect_border.center = (target_rect.centerx + ox, target_rect.centery + oy)
        surface.blit(text_surf_border, text_rect_border) 

    text_size_for_gradient = font.get_rect(text).size 
    temp_surf_gradient = pygame.Surface(text_size_for_gradient, pygame.SRCALPHA)
    temp_surf_gradient_rect = temp_surf_gradient.get_rect()

    num_gradient_colors = len(gradient_colors)
    if num_gradient_colors < 2:
        text_surf_main, text_rect_main = font.render(text, gradient_colors[0] if gradient_colors else BLANCO)
        text_rect_main.center = target_rect.center
        surface.blit(text_surf_main, text_rect_main)
        return

    for y_pixel in range(temp_surf_gradient_rect.height):
        t = y_pixel / temp_surf_gradient_rect.height
        r = int(gradient_colors[0][0] * (1 - t) + gradient_colors[1][0] * t)
        g = int(gradient_colors[0][1] * (1 - t) + gradient_colors[1][1] * t)
        b = int(gradient_colors[0][2] * (1 - t) + gradient_colors[1][2] * t)
        current_color = (r, g, b)
        pygame.draw.line(temp_surf_gradient, current_color, (0, y_pixel), (temp_surf_gradient_rect.width, y_pixel))

    text_surf_mask, _ = font.render(text, (255, 255, 255))
    temp_surf_gradient.blit(text_surf_mask, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
    final_text_rect = temp_surf_gradient.get_rect(center=target_rect.center)
    surface.blit(temp_surf_gradient, final_text_rect)


# ========================
# CLASES DE JUEGO
# ========================
class Button:
    def __init__(self, x, y, width, height, text, font, color, hover_color, text_color=BLANCO, border_color=BLANCO, border_thickness=3, border_radius=10):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.border_color = border_color
        self.border_thickness = border_thickness
        self.is_hovered = False
        self.border_radius = border_radius
        self.use_logo_style = False 
        self.logo_style_gradient_colors = [COLOR_GRADIENTE_TOP, COLOR_GRADIENTE_BOTTOM]
        self.logo_style_border_color = COLOR_CONTORNO
        self.logo_style_border_thickness = 2

    def set_logo_style(self, enable=True, gradient_colors=None, border_color=None, border_thickness=None):
        self.use_logo_style = enable
        if gradient_colors: self.logo_style_gradient_colors = gradient_colors
        if border_color: self.logo_style_border_color = border_color
        if border_thickness: self.logo_style_border_thickness = border_thickness

    def draw(self, surface):
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, current_color, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, self.border_color, self.rect, self.border_thickness, border_radius=self.border_radius)

        if self.use_logo_style:
            render_text_gradient(self.font, self.text, self.rect, surface, 
                                 self.logo_style_gradient_colors, 
                                 self.logo_style_border_color, 
                                 self.logo_style_border_thickness)
        else:
            text_surface, text_rect = self.font.render(self.text, BLANCO)
            text_rect.center = self.rect.center 
            surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False

# ========================
# PANTALLA INTRODUCCIÓN
# ========================
def pantalla_intro():
    alpha_logo = 0
    fade_in_duration = 1.5
    hold_duration = 1.5
    fade_out_duration = 1.5
    display_duration_total = fade_in_duration + hold_duration + fade_out_duration

    logo_img = None
    try:
        ruta_logo = os.path.join(os.path.dirname(__file__), "Logotipo.png")
        logo_img = pygame.image.load(ruta_logo).convert_alpha()
        logo_img = pygame.transform.scale(logo_img, (ANCHO, ALTO))
    except Exception as e:
        print(f"Error cargando el logo: {e}")
        return

    start_time = time.time()
    
    if music_loaded:
        pygame.mixer.music.play(-1, 0.0)

    while True:
        elapsed_time = time.time() - start_time
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_RETURN:
                return

        pantalla.blit(fondo_img, (0, 0))
        
        if elapsed_time < fade_in_duration:
            alpha_logo = int(255 * (elapsed_time / fade_in_duration))
        elif elapsed_time < fade_in_duration + hold_duration:
            alpha_logo = 255
        elif elapsed_time < display_duration_total:
            remaining_time = display_duration_total - elapsed_time
            alpha_logo = int(255 * (remaining_time / fade_out_duration))
        else:
            return

        alpha_logo = max(0, min(255, alpha_logo))

        if logo_img:
            logo_img.set_alpha(alpha_logo)
            pantalla.blit(logo_img, (0, 0))

        pygame.display.flip()
        clock.tick(60)

# ========================
# PANTALLA CONFIGURACIÓN
# ========================
def pantalla_configuracion(config):
    tam = config["tam"] if config else 60
    nombre_fuente = config["fuente"] if config else fuentes_disponibles[0]
    color = tuple(config["color"]) if config else colores_disponibles[0]

    idx_fuente = fuentes_disponibles.index(nombre_fuente) if nombre_fuente in fuentes_disponibles else 0
    idx_color = colores_disponibles.index(color) if color in colores_disponibles else 0

    texto_previo = "A"

    fuente_ui_btns_flecha = pygame.freetype.SysFont("arial", 25)
    fuente_ui_text = pygame.freetype.SysFont("arial", 40)
    fuente_instrucciones = pygame.freetype.SysFont("arial", 25)
    fuente_guardar_btn = pygame.freetype.SysFont(FUENTE_LOGO_STYLE, 22)

    start_time = time.time()

    btn_tam_left = Button(ANCHO//2 - 200, 150 + 50, 40, 40, "<", fuente_ui_btns_flecha, GRIS_OSCURO, GRIS_CLARO, border_radius=5)
    btn_tam_right = Button(ANCHO//2 + 160, 150 + 50, 40, 40, ">", fuente_ui_btns_flecha, GRIS_OSCURO, GRIS_CLARO, border_radius=5)
    btn_fuente_left = Button(ANCHO//2 - 200, 150 + 2*50, 40, 40, "<", fuente_ui_btns_flecha, GRIS_OSCURO, GRIS_CLARO, border_radius=5)
    btn_fuente_right = Button(ANCHO//2 + 160, 150 + 2*50, 40, 40, ">", fuente_ui_btns_flecha, GRIS_OSCURO, GRIS_CLARO, border_radius=5)
    btn_color_left = Button(ANCHO//2 - 200, 150 + 3*50, 40, 40, "<", fuente_ui_btns_flecha, GRIS_OSCURO, GRIS_CLARO, border_radius=5)
    btn_color_right = Button(ANCHO//2 + 160, 150 + 3*50, 40, 40, ">", fuente_ui_btns_flecha, GRIS_OSCURO, GRIS_CLARO, border_radius=5)
    btn_guardar = Button(ANCHO//2 - 130, ALTO - 100, 260, 60, "GUARDAR Y CONTINUAR", fuente_guardar_btn, GRIS_OSCURO, GRIS_CLARO) 
    btn_guardar.set_logo_style(True, [COLOR_GRADIENTE_TOP, COLOR_GRADIENTE_BOTTOM], COLOR_CONTORNO, 2)

    while True:
        pantalla.blit(fondo_img, (0, 0))
        dibujar_estrellas()

        fuente_letras = pygame.freetype.SysFont(nombre_fuente, tam)
        tiempo_actual = time.time() - start_time
        desplazamiento_y = int(10 * math.sin(tiempo_actual * 2))
        y_base = 100
        separacion = 50

        texto_opciones, _ = fuente_ui_text.render("CONFIGURACIÓN DE LETRAS", BLANCO)
        texto_tam, _ = fuente_ui_text.render(f"Tamaño: {tam}", BLANCO)
        texto_fuente, _ = fuente_ui_text.render(f"Fuente: {nombre_fuente}", BLANCO)
        texto_color, _ = fuente_ui_text.render(f"Color:", color)
        texto_prev, rect_prev = fuente_letras.render(texto_previo, color)
        pos_x = ANCHO // 2 - rect_prev.width // 2
        pos_y = y_base + 3*separacion + desplazamiento_y + 40

        pantalla.blit(texto_opciones, (ANCHO//2 - texto_opciones.get_width()//2, y_base))
        pantalla.blit(texto_tam, (ANCHO//2 - texto_tam.get_width()//2, y_base + separacion))
        pantalla.blit(texto_fuente, (ANCHO//2 - texto_fuente.get_width()//2, y_base + 2*separacion))
        pantalla.blit(texto_color, (ANCHO//2 - texto_color.get_width()//2, y_base + 3*separacion))
        pantalla.blit(texto_prev, (pos_x, pos_y))

        largo_linea = rect_prev.width
        line_y = pos_y + rect_prev.height + 5
        brillo = int(150 + 105 * (0.5 + 0.5 * math.sin(tiempo_actual * 4)))
        color_linea = (brillo, brillo, brillo)
        pygame.draw.line(pantalla, color_linea, (pos_x, line_y), (pos_x + largo_linea, line_y), 3)

        instrucciones, rect_instr = fuente_instrucciones.render("← → Tamaño | ↑ ↓ Fuente | C/V Color | ENTER para guardar y continuar", BLANCO)
        linea_instrucciones_y = pos_y + rect_prev.height + 60
        pantalla.blit(instrucciones, (ANCHO//2 - instrucciones.get_width()//2, linea_instrucciones_y))

        btn_tam_left.draw(pantalla)
        btn_tam_right.draw(pantalla)
        btn_fuente_left.draw(pantalla)
        btn_fuente_right.draw(pantalla)
        btn_color_left.draw(pantalla)
        btn_color_right.draw(pantalla)
        btn_guardar.draw(pantalla)

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if btn_tam_left.handle_event(evento):
                tam = max(30, tam - 5)
            elif btn_tam_right.handle_event(evento):
                tam = min(200, tam + 5)
            elif btn_fuente_left.handle_event(evento):
                idx_fuente = (idx_fuente - 1) % len(fuentes_disponibles)
                nombre_fuente = fuentes_disponibles[idx_fuente]
            elif btn_fuente_right.handle_event(evento):
                idx_fuente = (idx_fuente + 1) % len(fuentes_disponibles)
                nombre_fuente = fuentes_disponibles[idx_fuente]
            elif btn_color_left.handle_event(evento):
                idx_color = (idx_color + 1) % len(colores_disponibles)
                color = colores_disponibles[idx_color]
            elif btn_color_right.handle_event(evento):
                idx_color = (idx_color - 1) % len(colores_disponibles)
                color = colores_disponibles[idx_color]
            elif btn_guardar.handle_event(evento):
                guardar_config(nombre_fuente, tam, color)
                return nombre_fuente, tam, color

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_LEFT: tam = max(30, tam - 5)
                elif evento.key == pygame.K_RIGHT: tam = min(200, tam + 5)
                elif evento.key == pygame.K_DOWN:
                    idx_fuente = (idx_fuente + 1) % len(fuentes_disponibles)
                    nombre_fuente = fuentes_disponibles[idx_fuente]
                elif evento.key == pygame.K_UP:
                    idx_fuente = (idx_fuente - 1) % len(fuentes_disponibles)
                    nombre_fuente = fuentes_disponibles[idx_fuente]
                elif evento.key == pygame.K_c:
                    idx_color = (idx_color + 1) % len(colores_disponibles)
                    color = colores_disponibles[idx_color]
                elif evento.key == pygame.K_v:
                    idx_color = (idx_color - 1) % len(colores_disponibles)
                    color = colores_disponibles[idx_color]
                elif evento.key == pygame.K_RETURN:
                    guardar_config(nombre_fuente, tam, color)
                    return nombre_fuente, tam, color

# ========================
# PANTALLA MENÚ PRINCIPAL
# ========================
def pantalla_menu_principal():
    fuente_creditos = pygame.freetype.SysFont("arial", 25)
    fuente_opciones_estilo = pygame.freetype.SysFont(FUENTE_LOGO_STYLE, 30)

    try:
        logo_img = pygame.image.load(os.path.join(os.path.dirname(__file__), "logo.png")).convert_alpha()
    except Exception as e:
        print(f"Error al cargar logo.png: {e}")
        logo_img = None

    # --- INICIO: CÓDIGO MODIFICADO ---
    button_width = 280
    button_height = 60
    # Posición Y inicial de los botones, ajustada para estar debajo del logo
    button_y_start = ALTO // 2 - 50 
    button_spacing = 80
    # --- FIN: CÓDIGO MODIFICADO ---

    btn_modos_juego = Button(ANCHO // 2 - button_width//2, button_y_start, button_width, button_height, "MODOS DE JUEGO", fuente_opciones_estilo, GRIS_OSCURO, GRIS_CLARO)
    btn_modos_juego.set_logo_style(True, [COLOR_GRADIENTE_TOP, COLOR_GRADIENTE_BOTTOM], COLOR_CONTORNO, 2)

    btn_puntuaciones = Button(ANCHO // 2 - button_width//2, button_y_start + button_spacing, button_width, button_height, "PUNTUACIONES", fuente_opciones_estilo, GRIS_OSCURO, GRIS_CLARO)
    btn_puntuaciones.set_logo_style(True, [COLOR_GRADIENTE_TOP, COLOR_GRADIENTE_BOTTOM], COLOR_CONTORNO, 2)

    btn_cargar = Button(ANCHO // 2 - button_width//2, button_y_start + 2 * button_spacing, button_width, button_height, "CARGAR PARTIDA", fuente_opciones_estilo, GRIS_OSCURO, GRIS_CLARO)
    btn_cargar.set_logo_style(True, [COLOR_GRADIENTE_TOP, COLOR_GRADIENTE_BOTTOM], COLOR_CONTORNO, 2)

    btn_config = Button(ANCHO // 2 - button_width//2, button_y_start + 3 * button_spacing, button_width, button_height, "CONFIGURACIÓN", fuente_opciones_estilo, GRIS_OSCURO, GRIS_CLARO)
    btn_config.set_logo_style(True, [COLOR_GRADIENTE_TOP, COLOR_GRADIENTE_BOTTOM], COLOR_CONTORNO, 2)

    btn_salir = Button(ANCHO // 2 - button_width//2, button_y_start + 4 * button_spacing, button_width, button_height, "SALIR", fuente_opciones_estilo, GRIS_OSCURO, GRIS_CLARO)
    btn_salir.set_logo_style(True, [COLOR_GRADIENTE_TOP, COLOR_GRADIENTE_BOTTOM], COLOR_CONTORNO, 2)


    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if btn_modos_juego.handle_event(evento): return "seleccion_modo"
            if btn_puntuaciones.handle_event(evento): return "highscores"
            if btn_cargar.handle_event(evento): return "cargar_partida"
            if btn_config.handle_event(evento): return "configuracion"
            if btn_salir.handle_event(evento):
                if confirmar_salida(fuente_opciones_estilo):
                    pygame.quit()
                    sys.exit()

            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                if confirmar_salida(fuente_opciones_estilo):
                    pygame.quit()
                    sys.exit()

        pantalla.blit(fondo_img, (0, 0))
        dibujar_estrellas(0.5)

        # --- INICIO: CÓDIGO MODIFICADO ---
        # Dibujar el logo primero, en la parte superior de la pantalla
        if logo_img:
            logo_width = 500
            scale_factor = logo_width / logo_img.get_width()
            scaled_logo = pygame.transform.smoothscale(logo_img, (int(logo_img.get_width() * scale_factor), int(logo_img.get_height() * scale_factor)))
            logo_rect = scaled_logo.get_rect(center=(ANCHO // 2, ALTO // 4)) # Centrar el logo en el cuarto superior
            pantalla.blit(scaled_logo, logo_rect)
        else:
            # Fallback a texto si no se carga la imagen
            fuente_titulo_estilo = pygame.freetype.SysFont(FUENTE_LOGO_STYLE, 80)
            titulo_rect = pygame.Rect(0, 0, ANCHO, 100) 
            titulo_rect.center = (ANCHO // 2, ALTO // 4)
            render_text_gradient(fuente_titulo_estilo, "SPEEDTYPE", titulo_rect, pantalla, [COLOR_GRADIENTE_TOP, COLOR_GRADIENTE_BOTTOM], COLOR_CONTORNO, 4)
        
        # Dibujar los botones debajo del logo
        btn_modos_juego.draw(pantalla)
        btn_puntuaciones.draw(pantalla)
        btn_cargar.draw(pantalla)
        btn_config.draw(pantalla)
        btn_salir.draw(pantalla)
        # --- FIN: CÓDIGO MODIFICADO ---

        pygame.display.flip()
        clock.tick(60)

# ========================
# PANTALLA SELECCIÓN DE MODO DE JUEGO
# ========================
def pantalla_seleccion_modo_juego():
    fuente_titulo_estilo = pygame.freetype.SysFont(FUENTE_LOGO_STYLE, 60)
    fuente_opciones_estilo = pygame.freetype.SysFont(FUENTE_LOGO_STYLE, 40)

    btn_arcane = Button(ANCHO // 2 - 150, ALTO // 2 - 100, 300, 70, "MODO ARCANE (1P)", fuente_opciones_estilo, GRIS_OSCURO, GRIS_CLARO)
    btn_arcane.set_logo_style(True, [COLOR_GRADIENTE_TOP, COLOR_GRADIENTE_BOTTOM], COLOR_CONTORNO, 3)

    btn_versus = Button(ANCHO // 2 - 150, ALTO // 2 - 10, 300, 70, "MODO VERSUS (2P)", fuente_opciones_estilo, GRIS_OSCURO, GRIS_CLARO)
    btn_versus.set_logo_style(True, [COLOR_GRADIENTE_TOP, COLOR_GRADIENTE_BOTTOM], COLOR_CONTORNO, 3)

    btn_volver = Button(ANCHO // 2 - 150, ALTO // 2 + 150, 300, 70, "VOLVER", fuente_opciones_estilo, GRIS_OSCURO, GRIS_CLARO)
    btn_volver.set_logo_style(True, [COLOR_GRADIENTE_TOP, COLOR_GRADIENTE_BOTTOM], COLOR_CONTORNO, 3)

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if btn_arcane.handle_event(evento): return "arcane"
            if btn_versus.handle_event(evento): return "versus"
            if btn_volver.handle_event(evento): return "volver_menu"
            
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                return "volver_menu"

        pantalla.blit(fondo_img, (0, 0))
        dibujar_estrellas(0.5)

        titulo_rect = pygame.Rect(0, 0, ANCHO, 100)
        titulo_rect.center = (ANCHO // 2, ALTO // 4 - 50)
        render_text_gradient(fuente_titulo_estilo, "SELECCIONAR MODO", titulo_rect, pantalla, [COLOR_GRADIENTE_TOP, COLOR_GRADIENTE_BOTTOM], COLOR_CONTORNO, 4)

        btn_arcane.draw(pantalla)
        btn_versus.draw(pantalla)
        btn_volver.draw(pantalla)

        pygame.display.flip()
        clock.tick(60)

# ========================
# PANTALLA CONFIGURACIÓN VERSUS (Límite de Tiempo)
# ========================
def pantalla_configuracion_versus():
    fuente_titulo_estilo = pygame.freetype.SysFont(FUENTE_LOGO_STYLE, 50)
    fuente_opciones_estilo = pygame.freetype.SysFont(FUENTE_LOGO_STYLE, 30)
    fuente_tiempo_num = pygame.freetype.SysFont("arial", 60)

    tiempos_disponibles = [1, 2, 3, 5]
    tiempo_seleccionado_idx = 0

    btn_tiempo_left = Button(ANCHO // 2 - 200, ALTO // 2 - 30, 40, 40, "<", fuente_opciones_estilo, GRIS_OSCURO, GRIS_CLARO, border_radius=5)
    btn_tiempo_right = Button(ANCHO // 2 + 160, ALTO // 2 - 30, 40, 40, ">", fuente_opciones_estilo, GRIS_OSCURO, GRIS_CLARO, border_radius=5)
    btn_iniciar = Button(ANCHO // 2 - 150, ALTO // 2 + 100, 300, 70, "INICIAR VERSUS", fuente_opciones_estilo, GRIS_OSCURO, GRIS_CLARO)
    btn_iniciar.set_logo_style(True, [COLOR_GRADIENTE_TOP, COLOR_GRADIENTE_BOTTOM], COLOR_CONTORNO, 3)

    btn_volver = Button(ANCHO // 2 - 150, ALTO // 2 + 200, 300, 70, "VOLVER", fuente_opciones_estilo, GRIS_OSCURO, GRIS_CLARO)
    btn_volver.set_logo_style(True, [COLOR_GRADIENTE_TOP, COLOR_GRADIENTE_BOTTOM], COLOR_CONTORNO, 3)

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if btn_tiempo_left.handle_event(evento):
                tiempo_seleccionado_idx = (tiempo_seleccionado_idx - 1) % len(tiempos_disponibles)
            if btn_tiempo_right.handle_event(evento):
                tiempo_seleccionado_idx = (tiempo_seleccionado_idx + 1) % len(tiempos_disponibles)
            if btn_iniciar.handle_event(evento):
                return tiempos_disponibles[tiempo_seleccionado_idx]
            if btn_volver.handle_event(evento):
                return "volver_seleccion_modo"
            
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_LEFT:
                    tiempo_seleccionado_idx = (tiempo_seleccionado_idx - 1) % len(tiempos_disponibles)
                elif evento.key == pygame.K_RIGHT:
                    tiempo_seleccionado_idx = (tiempo_seleccionado_idx + 1) % len(tiempos_disponibles)
                elif evento.key == pygame.K_RETURN:
                    return tiempos_disponibles[tiempo_seleccionado_idx]
                elif evento.key == pygame.K_ESCAPE:
                    return "volver_seleccion_modo"

        pantalla.blit(fondo_img, (0, 0))
        dibujar_estrellas(0.5)

        titulo_rect = pygame.Rect(0, 0, ANCHO, 100)
        titulo_rect.center = (ANCHO // 2, ALTO // 4 - 50)
        render_text_gradient(fuente_titulo_estilo, "LÍMITE DE TIEMPO", titulo_rect, pantalla, [COLOR_GRADIENTE_TOP, COLOR_GRADIENTE_BOTTOM], COLOR_CONTORNO, 3)

        tiempo_texto, _ = fuente_tiempo_num.render(f"{tiempos_disponibles[tiempo_seleccionado_idx]} min", BLANCO)
        tiempo_texto_rect = tiempo_texto.get_rect(center=(ANCHO // 2, ALTO // 2 - 10))
        pantalla.blit(tiempo_texto, tiempo_texto_rect)

        btn_tiempo_left.draw(pantalla)
        btn_tiempo_right.draw(pantalla)
        btn_iniciar.draw(pantalla)
        btn_volver.draw(pantalla)

        pygame.display.flip()
        clock.tick(60)

# ========================
# PANTALLA CONFIGURACIÓN ARCANE (Límite de Fallos)
# ========================
def pantalla_configuracion_arcane():
    fuente_titulo_estilo = pygame.freetype.SysFont(FUENTE_LOGO_STYLE, 50)
    fuente_opciones_estilo = pygame.freetype.SysFont(FUENTE_LOGO_STYLE, 30)
    fuente_fallos_num = pygame.freetype.SysFont("arial", 60)

    fallos_disponibles = [5, 10, 15, 20]
    fallos_seleccionado_idx = 1

    btn_fallos_left = Button(ANCHO // 2 - 200, ALTO // 2 - 30, 40, 40, "<", fuente_opciones_estilo, GRIS_OSCURO, GRIS_CLARO, border_radius=5)
    btn_fallos_right = Button(ANCHO // 2 + 160, ALTO // 2 - 30, 40, 40, ">", fuente_opciones_estilo, GRIS_OSCURO, GRIS_CLARO, border_radius=5)
    btn_iniciar = Button(ANCHO // 2 - 150, ALTO // 2 + 100, 300, 70, "INICIAR ARCANE", fuente_opciones_estilo, GRIS_OSCURO, GRIS_CLARO)
    btn_iniciar.set_logo_style(True, [COLOR_GRADIENTE_TOP, COLOR_GRADIENTE_BOTTOM], COLOR_CONTORNO, 3)

    btn_volver = Button(ANCHO // 2 - 150, ALTO // 2 + 200, 300, 70, "VOLVER", fuente_opciones_estilo, GRIS_OSCURO, GRIS_CLARO)
    btn_volver.set_logo_style(True, [COLOR_GRADIENTE_TOP, COLOR_GRADIENTE_BOTTOM], COLOR_CONTORNO, 3)

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if btn_fallos_left.handle_event(evento):
                fallos_seleccionado_idx = (fallos_seleccionado_idx - 1) % len(fallos_disponibles)
            if btn_fallos_right.handle_event(evento):
                fallos_seleccionado_idx = (fallos_seleccionado_idx + 1) % len(fallos_disponibles)
            if btn_iniciar.handle_event(evento):
                return fallos_disponibles[fallos_seleccionado_idx]
            if btn_volver.handle_event(evento):
                return "volver_seleccion_modo"
            
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_LEFT:
                    fallos_seleccionado_idx = (fallos_seleccionado_idx - 1) % len(fallos_disponibles)
                elif evento.key == pygame.K_RIGHT:
                    fallos_seleccionado_idx = (fallos_seleccionado_idx + 1) % len(fallos_disponibles)
                elif evento.key == pygame.K_RETURN:
                    return fallos_disponibles[fallos_seleccionado_idx]
                elif evento.key == pygame.K_ESCAPE:
                    return "volver_seleccion_modo"

        pantalla.blit(fondo_img, (0, 0))
        dibujar_estrellas(0.5)

        titulo_rect = pygame.Rect(0, 0, ANCHO, 100)
        titulo_rect.center = (ANCHO // 2, ALTO // 4 - 50)
        render_text_gradient(fuente_titulo_estilo, "LÍMITE DE FALLOS", titulo_rect, pantalla, [COLOR_GRADIENTE_TOP, COLOR_GRADIENTE_BOTTOM], COLOR_CONTORNO, 3)

        fallos_texto, _ = fuente_fallos_num.render(f"{fallos_disponibles[fallos_seleccionado_idx]} fallos", BLANCO)
        fallos_texto_rect = fallos_texto.get_rect(center=(ANCHO // 2, ALTO // 2 - 10))
        pantalla.blit(fallos_texto, fallos_texto_rect)

        btn_fallos_left.draw(pantalla)
        btn_fallos_right.draw(pantalla)
        btn_iniciar.draw(pantalla)
        btn_volver.draw(pantalla)

        pygame.display.flip()
        clock.tick(60)

# ========================
# PANTALLA PAUSA
# ========================
def pantalla_de_pausa():
    fuente_pausa_titulo = pygame.freetype.SysFont(FUENTE_LOGO_STYLE, 60)
    fuente_pausa_opciones = pygame.freetype.SysFont(FUENTE_LOGO_STYLE, 30)

    superficie_oscura = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    superficie_oscura.fill((0, 0, 0, 180))

    btn_reanudar = Button(ANCHO // 2 - 150, ALTO // 2 - 100, 300, 70, "REANUDAR", fuente_pausa_opciones, GRIS_OSCURO, GRIS_CLARO)
    btn_reanudar.set_logo_style(True, [COLOR_GRADIENTE_TOP, COLOR_GRADIENTE_BOTTOM], COLOR_CONTORNO, 2)

    btn_guardar_salir = Button(ANCHO // 2 - 150, ALTO // 2, 300, 70, "GUARDAR Y SALIR", fuente_pausa_opciones, GRIS_OSCURO, GRIS_CLARO)
    btn_guardar_salir.set_logo_style(True, [COLOR_GRADIENTE_TOP, COLOR_GRADIENTE_BOTTOM], COLOR_CONTORNO, 2)

    btn_salir_sin_guardar = Button(ANCHO // 2 - 150, ALTO // 2 + 100, 300, 70, "SALIR SIN GUARDAR", fuente_pausa_opciones, GRIS_OSCURO, GRIS_CLARO)
    btn_salir_sin_guardar.set_logo_style(True, [COLOR_GRADIENTE_TOP, COLOR_GRADIENTE_BOTTOM], COLOR_CONTORNO, 2)

    if music_loaded:
        pygame.mixer.music.pause()

    while True:
        if fondo_pausa_img:
            pantalla.blit(fondo_pausa_img, (0,0))

        pantalla.blit(superficie_oscura, (0, 0))

        titulo_pausa_rect = pygame.Rect(0, 0, ANCHO, 70)
        titulo_pausa_rect.center = (ANCHO // 2, ALTO // 2 - 200)
        render_text_gradient(fuente_pausa_titulo, "PAUSA", titulo_pausa_rect, pantalla, [BLANCO, (200, 200, 200)], COLOR_CONTORNO, 3)

        btn_reanudar.draw(pantalla)
        btn_guardar_salir.draw(pantalla)
        btn_salir_sin_guardar.draw(pantalla)

        pygame.display.flip()
        clock.tick(60)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                if music_loaded: pygame.mixer.music.unpause()
                return "reanudar"

            if btn_reanudar.handle_event(evento):
                if music_loaded: pygame.mixer.music.unpause()
                return "reanudar"
            
            if btn_guardar_salir.handle_event(evento): return "guardar_y_salir"
            if btn_salir_sin_guardar.handle_event(evento): return "salir_sin_guardar"

# ========================
# GAME OVER
# ========================
def game_over(score, aciertos, fallos, fuente_ui_juego_normal):
    fuente_ui_go_text = pygame.freetype.SysFont(FUENTE_LOGO_STYLE, 40)
    fuente_ui_go_stats = pygame.freetype.SysFont("arial", 30)
    fuente_ui_go_btns = pygame.freetype.SysFont(FUENTE_LOGO_STYLE, 30)

    if game_over_sound:
        game_over_sound.play()

    if music_loaded and pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()

    while pygame.mixer.get_busy():
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.time.delay(100)

    if check_if_highscore(score):
        pantalla_ingresar_nombre(score)
        pantalla_highscores()
        return True

    btn_reiniciar = Button(ANCHO // 2 - 150, ALTO // 2 + 80, 140, 60, "REINICIAR", fuente_ui_go_btns, GRIS_OSCURO, GRIS_CLARO)
    btn_reiniciar.set_logo_style(True, [COLOR_GRADIENTE_TOP, COLOR_GRADIENTE_BOTTOM], COLOR_CONTORNO, 2)

    btn_salir_go = Button(ANCHO // 2 + 10, ALTO // 2 + 80, 140, 60, "SALIR", fuente_ui_go_btns, GRIS_OSCURO, GRIS_CLARO)
    btn_salir_go.set_logo_style(True, [COLOR_GRADIENTE_TOP, COLOR_GRADIENTE_BOTTOM], COLOR_CONTORNO, 2)

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if btn_reiniciar.handle_event(evento):
                return True
            if btn_salir_go.handle_event(evento):
                pygame.quit()
                sys.exit()

        pantalla.blit(fondo_img, (0, 0))
        dibujar_estrellas()

        total = aciertos + fallos
        prec = (aciertos / total) * 100 if total else 0

        t1_rect = pygame.Rect(0, 0, ANCHO, 50)
        t1_rect.center = (ANCHO // 2, 200)
        render_text_gradient(fuente_ui_go_text, "¡GAME OVER!", t1_rect, pantalla, [ROJO, (255, 100, 0)], COLOR_CONTORNO, 3)

        t2_surf, t2_rect = fuente_ui_go_stats.render(f"Puntaje: {score}", BLANCO)
        t3_surf, t3_rect = fuente_ui_go_stats.render(f"Aciertos: {aciertos} Fallos: {fallos} Precisión: {prec:.2f}%", BLANCO)

        pantalla.blit(t2_surf, (ANCHO//2 - t2_surf.get_width()//2, 250)) 
        pantalla.blit(t3_surf, (ANCHO//2 - t3_surf.get_width()//2, 300)) 
        
        btn_reiniciar.draw(pantalla)
        btn_salir_go.draw(pantalla)

        pygame.display.flip()
        clock.tick(60)

# ========================
# FUNCIONES DE UI DEL JUEGO
# ========================
def confirmar_salida(fuente_ui_para_confirmacion):
    if music_loaded and pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()

    caja_ancho, caja_alto = 400, 200
    caja_x = (ANCHO - caja_ancho) // 2
    caja_y = (ALTO - caja_alto) // 2
    caja_rect = pygame.Rect(caja_x, caja_y, caja_ancho, caja_alto)

    mensaje_font = pygame.freetype.SysFont("arial", 25)
    btn_font_confirm = pygame.freetype.SysFont(FUENTE_LOGO_STYLE, 20)

    btn_si = Button(caja_x + caja_ancho // 4 - 50, caja_y + caja_alto - 60, 100, 40, "SÍ", btn_font_confirm, GRIS_OSCURO, GRIS_CLARO)
    btn_si.set_logo_style(True, [COLOR_GRADIENTE_TOP, COLOR_GRADIENTE_BOTTOM], COLOR_CONTORNO, 1)

    btn_no = Button(caja_x + (3 * caja_ancho) // 4 - 50, caja_y + caja_alto - 60, 100, 40, "NO", btn_font_confirm, GRIS_OSCURO, GRIS_CLARO)
    btn_no.set_logo_style(True, [COLOR_GRADIENTE_TOP, COLOR_GRADIENTE_BOTTOM], COLOR_CONTORNO, 1)


    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if btn_si.handle_event(evento):
                return True 
            if btn_no.handle_event(evento):
                if music_loaded:
                    pygame.mixer.music.unpause()
                return False 

        pantalla.blit(fondo_img, (0, 0))
        dibujar_estrellas()
        
        pygame.draw.rect(pantalla, NEGRO, caja_rect, border_radius=15)
        pygame.draw.rect(pantalla, BLANCO, caja_rect, 3, border_radius=15)

        mensaje_texto, _ = mensaje_font.render("¿Estás seguro que quieres salir?", BLANCO)
        pantalla.blit(mensaje_texto, (caja_x + (caja_ancho - mensaje_texto.get_width()) // 2, caja_y + 40))

        btn_si.draw(pantalla)
        btn_no.draw(pantalla)

        pygame.display.flip()
        clock.tick(60)

# ========================
# FUNCIÓN DE CONTEO REGRESIVO
# ========================
def mostrar_conteo_regresivo(segundos, fuente, color):
    superficie_oscura = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    superficie_oscura.fill((0, 0, 0, 180))

    fuente_conteo = pygame.freetype.SysFont(FUENTE_LOGO_STYLE, 100)

    for i in range(segundos, 0, -1):
        pantalla.blit(fondo_img, (0, 0))
        dibujar_estrellas(0.5)
        pantalla.blit(superficie_oscura, (0, 0))

        conteo_texto = str(i)
        conteo_rect = pygame.Rect(0, 0, ANCHO, ALTO)
        render_text_gradient(fuente_conteo, conteo_texto, conteo_rect, pantalla, [COLOR_GRADIENTE_TOP, COLOR_GRADIENTE_BOTTOM], COLOR_CONTORNO, 5)

        pygame.display.flip()
        pygame.time.delay(1000)

# --- INICIO: CÓDIGO AGREGADO PARA PANTALLAS DE PUNTUACIÓN ---
def pantalla_ingresar_nombre(score):
    """Pantalla para que el jugador ingrese sus iniciales para el high score."""
    fuente_titulo = pygame.freetype.SysFont(FUENTE_LOGO_STYLE, 50)
    fuente_input = pygame.freetype.SysFont("arial", 60)
    fuente_instr = pygame.freetype.SysFont("arial", 25)
    
    nombre_jugador = ""
    input_activo = True

    while input_activo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN and len(nombre_jugador) > 0:
                    highscores = cargar_highscores()
                    highscores.append({"nombre": nombre_jugador.upper(), "score": score})
                    highscores.sort(key=lambda x: x['score'], reverse=True)
                    guardar_highscores(highscores[:5]) # Guardar solo el top 5
                    input_activo = False
                elif evento.key == pygame.K_BACKSPACE:
                    nombre_jugador = nombre_jugador[:-1]
                elif len(nombre_jugador) < 3 and evento.unicode.isalpha():
                    nombre_jugador += evento.unicode.upper()

        pantalla.blit(fondo_img, (0, 0))
        dibujar_estrellas()

        titulo_surf, titulo_rect = fuente_titulo.render("¡NUEVO RÉCORD!", AMARILLO)
        titulo_rect.center = (ANCHO // 2, ALTO // 2 - 150)
        pantalla.blit(titulo_surf, titulo_rect)

        instr_surf, instr_rect = fuente_instr.render("Ingresa tus iniciales (3 letras) y presiona ENTER", BLANCO)
        instr_rect.center = (ANCHO // 2, ALTO // 2 - 80)
        pantalla.blit(instr_surf, instr_rect)

        # Caja de texto
        caja_rect = pygame.Rect(ANCHO // 2 - 100, ALTO // 2 - 40, 200, 80)
        pygame.draw.rect(pantalla, GRIS_OSCURO, caja_rect, border_radius=10)
        pygame.draw.rect(pantalla, BLANCO, caja_rect, 3, border_radius=10)

        nombre_surf, nombre_rect = fuente_input.render(nombre_jugador, BLANCO)
        nombre_rect.center = caja_rect.center
        pantalla.blit(nombre_surf, nombre_rect)

        pygame.display.flip()
        clock.tick(60)

def pantalla_highscores():
    """Muestra la tabla de las 5 puntuaciones más altas."""
    fuente_titulo = pygame.freetype.SysFont(FUENTE_LOGO_STYLE, 60)
    fuente_score = pygame.freetype.SysFont("arial", 40)
    fuente_btn = pygame.freetype.SysFont(FUENTE_LOGO_STYLE, 30)

    highscores = cargar_highscores()

    btn_volver = Button(ANCHO // 2 - 150, ALTO - 100, 300, 70, "VOLVER", fuente_btn, GRIS_OSCURO, GRIS_CLARO)
    btn_volver.set_logo_style(True, [COLOR_GRADIENTE_TOP, COLOR_GRADIENTE_BOTTOM], COLOR_CONTORNO, 3)

    scores_run = True
    while scores_run:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if btn_volver.handle_event(evento):
                scores_run = False
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                scores_run = False

        pantalla.blit(fondo_img, (0, 0))
        dibujar_estrellas()

        titulo_rect = pygame.Rect(0, 0, ANCHO, 100)
        titulo_rect.center = (ANCHO // 2, 100)
        render_text_gradient(fuente_titulo, "PUNTUACIONES MÁS ALTAS", titulo_rect, pantalla, [AMARILLO, BLANCO], COLOR_CONTORNO, 4)

        if not highscores:
            no_scores_surf, no_scores_rect = fuente_score.render("Aún no hay récords. ¡Sé el primero!", BLANCO)
            no_scores_rect.center = (ANCHO // 2, ALTO // 2)
            pantalla.blit(no_scores_surf, no_scores_rect)
        else:
            y_pos = 200
            for i, entry in enumerate(highscores):
                texto = f"{i+1}. {entry['nombre']} - {entry['score']}"
                score_surf, score_rect = fuente_score.render(texto, BLANCO)
                score_rect.center = (ANCHO // 2, y_pos)
                pantalla.blit(score_surf, score_rect)
                y_pos += 60

        btn_volver.draw(pantalla)
        pygame.display.flip()
        clock.tick(60)
# --- FIN: CÓDIGO AGREGADO ---

# ========================
# JUEGO ESTÁNDAR
# ========================
def jugar(nombre_fuente, tam, color, num_jugadores=2, initial_speed=1.5, count_wrong_key_faults=False, time_limit_seconds=0, fallos_limit=10, initial_state=None):
    fuente_letras = pygame.freetype.SysFont(nombre_fuente, tam)
    fuente_ui = pygame.freetype.SysFont("arial", 30)
    
    fuente_btn_pausa = pygame.freetype.SysFont(FUENTE_LOGO_STYLE, 20)
    btn_pausa = Button(ANCHO - 120, 10, 110, 40, "PAUSA", fuente_btn_pausa, GRIS_OSCURO, GRIS_CLARO)
    btn_pausa.set_logo_style(True, [COLOR_GRADIENTE_TOP, COLOR_GRADIENTE_BOTTOM], COLOR_CONTORNO, 2)
    
    racha_actual = 0

    if music_loaded:
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1, 0.0)
        else:
            pygame.mixer.music.unpause()

    if num_jugadores == 1:
        game_mode = "arcane"
        if initial_state:
            jugadores = {"J1": initial_state["J1"]}
            velocidad = initial_state.get("velocidad", initial_speed)
            tiempo_transcurrido_cargado = initial_state.get("tiempo_transcurrido", 0)
            fallos_limit = initial_state.get("fallos_limit", fallos_limit)
        else:
            jugadores = {"J1": {"letra_actual": chr(random.randint(65, 90)), "x": random.randint(0, ANCHO - 50), "y": 0, "score": 0, "fallos": 0, "color": VERDE}}
            velocidad = initial_speed
            tiempo_transcurrido_cargado = 0
    else:
        game_mode = "versus"
        jugadores = {"J1": {"score": 0, "fallos": 0, "color": VERDE}, "J2": {"score": 0, "fallos": 0, "color": AMARILLO}}
        if initial_state:
            jugadores["J1"]["score"] = initial_state["J1"]["score"]
            jugadores["J1"]["fallos"] = initial_state["J1"]["fallos"]
            jugadores["J2"]["score"] = initial_state["J2"]["score"]
            jugadores["J2"]["fallos"] = initial_state["J2"]["fallos"]
            current_turn_player = initial_state.get("current_turn_player", "J1")
            active_letter = initial_state.get("active_letter", chr(random.randint(65, 90)))
            active_letter_x = initial_state.get("active_letter_x", (ANCHO // 4 if current_turn_player == "J1" else 3 * ANCHO // 4) - 25)
            active_letter_y = initial_state.get("active_letter_y", 0)
            velocidad = initial_state.get("velocidad", initial_speed)
            tiempo_transcurrido_cargado = initial_state.get("tiempo_transcurrido", 0)
            time_limit_seconds = initial_state.get("time_limit_seconds", time_limit_seconds)
            fallos_limit = initial_state.get("fallos_limit", fallos_limit)
        else:
            current_turn_player = "J1"
            active_letter = chr(random.randint(65, 90))
            active_letter_x = random.randint(0, ANCHO // 2 - 50)
            active_letter_y = 0
            velocidad = initial_speed
            tiempo_transcurrido_cargado = 0

    tiempo_inicio_juego = time.time()
    tiempo_pausado_total = 0
    score_para_velocidad_anterior = 0
    max_speed = 5.0
    
    if initial_state:
        mostrar_conteo_regresivo(3, fuente_ui, BLANCO)
        tiempo_inicio_juego = time.time()

    run = True
    while run:
        tiempo_actual = time.time()
        tiempo_transcurrido = (tiempo_actual - tiempo_inicio_juego - tiempo_pausado_total) + tiempo_transcurrido_cargado
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if btn_pausa.handle_event(evento):
                tiempo_inicio_pausa = time.time()
                accion_pausa = pantalla_de_pausa()
                tiempo_pausado_total += time.time() - tiempo_inicio_pausa

                if accion_pausa == "guardar_y_salir":
                    estado_actual = {"velocidad": velocidad, "tiempo_transcurrido": tiempo_transcurrido, "fallos_limit": fallos_limit, "J1": jugadores["J1"]}
                    if num_jugadores == 2:
                        estado_actual.update({"J2": jugadores["J2"], "time_limit_seconds": time_limit_seconds, "current_turn_player": current_turn_player, "active_letter": active_letter, "active_letter_x": active_letter_x, "active_letter_y": active_letter_y})
                    guardar_partida(estado_actual, game_mode)
                    return "menu_principal"
                elif accion_pausa == "salir_sin_guardar":
                    return "menu_principal"
                elif accion_pausa == "reanudar":
                    tiempo_inicio_juego = time.time() 
                    tiempo_transcurrido_cargado = tiempo_transcurrido

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    tiempo_inicio_pausa = time.time()
                    accion_pausa = pantalla_de_pausa()
                    tiempo_pausado_total += time.time() - tiempo_inicio_pausa

                    if accion_pausa == "guardar_y_salir":
                        estado_actual = {"velocidad": velocidad, "tiempo_transcurrido": tiempo_transcurrido, "fallos_limit": fallos_limit, "J1": jugadores["J1"]}
                        if num_jugadores == 2:
                            estado_actual.update({"J2": jugadores["J2"], "time_limit_seconds": time_limit_seconds, "current_turn_player": current_turn_player, "active_letter": active_letter, "active_letter_x": active_letter_x, "active_letter_y": active_letter_y})
                        guardar_partida(estado_actual, game_mode)
                        return "menu_principal"
                    elif accion_pausa == "salir_sin_guardar":
                        return "menu_principal"
                    elif accion_pausa == "reanudar":
                        tiempo_inicio_juego = time.time() 
                        tiempo_transcurrido_cargado = tiempo_transcurrido

                elif evento.key >= pygame.K_a and evento.key <= pygame.K_z:
                    typed_letter = pygame.key.name(evento.key).upper() 
                    
                    if num_jugadores == 1:
                        if typed_letter == jugadores["J1"]["letra_actual"]:
                            if acierto_sound: acierto_sound.play()
                            jugadores["J1"]["score"] += (1 + racha_actual)
                            racha_actual += 1
                            crear_particulas(jugadores["J1"]["x"] + 25, jugadores["J1"]["y"] + 25, jugadores["J1"]["color"])
                            jugadores["J1"]["letra_actual"] = chr(random.randint(65, 90))
                            jugadores["J1"]["x"] = random.randint(0, ANCHO - 50)
                            jugadores["J1"]["y"] = 0
                        elif count_wrong_key_faults:
                            if fallo_sound: fallo_sound.play()
                            racha_actual = 0
                            jugadores["J1"]["fallos"] += 1
                    else:
                        if typed_letter == active_letter:
                            if acierto_sound: acierto_sound.play()
                            jugadores[current_turn_player]["score"] += (1 + racha_actual)
                            racha_actual += 1
                            crear_particulas(active_letter_x + (fuente_letras.get_rect(active_letter).width // 2), active_letter_y + (fuente_letras.get_rect(active_letter).height // 2), jugadores[current_turn_player]["color"])
                        else:
                            if fallo_sound: fallo_sound.play()
                            racha_actual = 0
                            jugadores[current_turn_player]["fallos"] += 1
                        
                        active_letter = chr(random.randint(65, 90))
                        active_letter_y = 0
                        current_turn_player = "J2" if current_turn_player == "J1" else "J1"
                        active_letter_x = random.randint(0, ANCHO // 2 - 50) if current_turn_player == "J1" else random.randint(ANCHO // 2, ANCHO - 50)

        dt = clock.tick(60) / 1000.0
        pantalla.blit(fondo_img, (0, 0))
        dibujar_estrellas(1)

        if num_jugadores == 2:
            pygame.draw.line(pantalla, BLANCO, (ANCHO // 2, 0), (ANCHO // 2, ALTO), 2)

        if num_jugadores == 1:
            jugadores["J1"]["y"] += velocidad * 60 * dt
            fuente_letras.render_to(pantalla, (jugadores["J1"]["x"], jugadores["J1"]["y"]), jugadores["J1"]["letra_actual"], jugadores["J1"]["color"])
            if jugadores["J1"]["y"] > ALTO:
                if fallo_sound: fallo_sound.play()
                racha_actual = 0
                jugadores["J1"]["fallos"] += 1
                jugadores["J1"]["letra_actual"] = chr(random.randint(65, 90))
                jugadores["J1"]["x"] = random.randint(0, ANCHO - 50)
                jugadores["J1"]["y"] = 0
        else:
            active_letter_y += velocidad * 60 * dt
            fuente_letras.render_to(pantalla, (active_letter_x, active_letter_y), active_letter, jugadores[current_turn_player]["color"])
            if active_letter_y > ALTO:
                if fallo_sound: fallo_sound.play()
                racha_actual = 0
                jugadores[current_turn_player]["fallos"] += 1
                active_letter = chr(random.randint(65, 90))
                active_letter_y = 0
                current_turn_player = "J2" if current_turn_player == "J1" else "J1"
                active_letter_x = random.randint(0, ANCHO // 2 - 50) if current_turn_player == "J1" else random.randint(ANCHO // 2, ANCHO - 50)

        actualizar_y_dibujar_particulas()

        total_score_actual = sum(j["score"] for j in jugadores.values())
        if total_score_actual // 10 > score_para_velocidad_anterior // 10:
            if velocidad < max_speed:
                velocidad += 0.1
            score_para_velocidad_anterior = total_score_actual

        fuente_ui.render_to(pantalla, (10, 10), f"J1: {jugadores['J1']['score']} (Fallos: {jugadores['J1']['fallos']})", jugadores['J1']['color'])
        if num_jugadores == 2:
            fuente_ui.render_to(pantalla, (ANCHO // 2 + 10, 10), f"J2: {jugadores['J2']['score']} (Fallos: {jugadores['J2']['fallos']})", jugadores['J2']['color'])
            if current_turn_player == "J1":
                pygame.draw.circle(pantalla, jugadores["J1"]["color"], (ANCHO // 4, 50), 10)
            else:
                pygame.draw.circle(pantalla, jugadores["J2"]["color"], (3 * ANCHO // 4, 50), 10)

        if time_limit_seconds > 0:
            tiempo_restante = max(0, time_limit_seconds - int(tiempo_transcurrido))
            minutos, segundos = divmod(tiempo_restante, 60)
            fuente_ui.render_to(pantalla, (ANCHO // 2 - 70, 50), f"Tiempo: {minutos:02d}:{segundos:02d}", BLANCO)
            if tiempo_restante <= 0: run = False

        if any(j["fallos"] >= fallos_limit for j in jugadores.values()):
            run = False
        
        if racha_actual > 1:
            combo_text = f"COMBO x{racha_actual}"
            if racha_actual < 10: combo_color = BLANCO
            elif racha_actual < 20: combo_color = AMARILLO
            else: combo_color = ROJO
            
            fuente_combo = pygame.freetype.SysFont("arial", 40)
            texto_surf, texto_rect = fuente_combo.render(combo_text, combo_color)
            
            offset_x = 0
            offset_y = 0
            if racha_actual >= 15:
                offset_x = random.randint(-2, 2)
                offset_y = random.randint(-2, 2)

            pos_x = (ANCHO - texto_rect.width) // 2 + offset_x
            pos_y = 20 + offset_y
            pantalla.blit(texto_surf, (pos_x, pos_y))

        btn_pausa.draw(pantalla)
        pygame.display.flip()

    total_aciertos = sum(j["score"] for j in jugadores.values())
    total_fallos = sum(j["fallos"] for j in jugadores.values())

    if num_jugadores == 1:
        game_over(jugadores['J1']['score'], jugadores['J1']['score'], jugadores['J1']['fallos'], fuente_ui)
    else:
        ganador = "J1" if jugadores["J1"]["score"] >= jugadores["J2"]["score"] else "J2"
        game_over(jugadores[ganador]["score"], total_aciertos, total_fallos, fuente_ui)
    
    return "menu_principal"

# ========================
# MODO ARCANE (1 Jugador)
# ========================
def jugar_arcane(nombre_fuente, tam, color):
    print("Iniciando Modo ARCANE (1 Jugador)...")
    fallos_limit = pantalla_configuracion_arcane()
    if fallos_limit == "volver_seleccion_modo": return "volver_seleccion_modo"
    return jugar(nombre_fuente, tam, color, num_jugadores=1, initial_speed=1.5, count_wrong_key_faults=True, time_limit_seconds=0, fallos_limit=fallos_limit)

# ========================
# MODO VERSUS (2 Jugadores)
# ========================
def jugar_versus(nombre_fuente, tam, color):
    print("Iniciando Modo VERSUS (2 Jugadores)...")
    time_limit_minutes = pantalla_configuracion_versus()
    if time_limit_minutes == "volver_seleccion_modo": return "volver_seleccion_modo"
    time_limit_seconds = time_limit_minutes * 60
    return jugar(nombre_fuente, tam, color, num_jugadores=2, initial_speed=2.0, count_wrong_key_faults=True, time_limit_seconds=time_limit_seconds, fallos_limit=10)

# ========================
# PANTALLA SELECCIONAR PARTIDA GUARDADA
# ========================
def pantalla_seleccionar_partida(saved_games):
    fuente_titulo_estilo = pygame.freetype.SysFont(FUENTE_LOGO_STYLE, 50)
    fuente_opciones_estilo = pygame.freetype.SysFont(FUENTE_LOGO_STYLE, 30)
    fuente_partida_info = pygame.freetype.SysFont("arial", 25)
    fuente_eliminar_btn = pygame.freetype.SysFont("arial", 30)

    btns = []
    y_start = ALTO // 4
    spacing = 80

    for i, save in enumerate(saved_games):
        timestamp_dt = datetime.fromisoformat(save['timestamp'])
        display_time = timestamp_dt.strftime("%Y-%m-%d %H:%M")
        mode_display = "Arcane (1P)" if save['mode'] == "arcane" else "Versus (2P)"
        btn_text = f"{i+1}. {mode_display} - {display_time}"
        
        load_btn_y = y_start + i * spacing
        load_btn = Button(ANCHO // 2 - 250, load_btn_y, 500, 60, btn_text, fuente_partida_info, GRIS_OSCURO, GRIS_CLARO)
        load_btn.set_logo_style(False) 

        delete_btn_x = load_btn.rect.right + 10
        delete_btn = Button(delete_btn_x, load_btn_y, 60, 60, "X", fuente_eliminar_btn, (150,0,0), (255,0,0))
        delete_btn.set_logo_style(False)
        btns.append((load_btn, delete_btn, save))

    btn_volver = Button(ANCHO // 2 - 150, ALTO - 100, 300, 70, "VOLVER", fuente_opciones_estilo, GRIS_OSCURO, GRIS_CLARO)
    btn_volver.set_logo_style(True, [COLOR_GRADIENTE_TOP, COLOR_GRADIENTE_BOTTOM], COLOR_CONTORNO, 3)

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            for load_btn, delete_btn, save_data in btns:
                if load_btn.handle_event(evento): return save_data
                if delete_btn.handle_event(evento):
                    eliminar_partida_guardada(save_data['timestamp'])
                    return "refresh"
            
            if btn_volver.handle_event(evento): return "volver_menu"
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE: return "volver_menu"

        pantalla.blit(fondo_img, (0, 0))
        dibujar_estrellas(0.5)

        titulo_rect = pygame.Rect(0, 0, ANCHO, 100)
        titulo_rect.center = (ANCHO // 2, ALTO // 4 - 50)
        render_text_gradient(fuente_titulo_estilo, "CARGAR PARTIDA", titulo_rect, pantalla, [COLOR_GRADIENTE_TOP, COLOR_GRADIENTE_BOTTOM], COLOR_CONTORNO, 4)

        if not saved_games:
            no_saves_text, _ = fuente_partida_info.render("No hay partidas guardadas.", BLANCO)
            no_saves_text_rect = no_saves_text.get_rect(center=(ANCHO // 2, ALTO // 2))
            pantalla.blit(no_saves_text, no_saves_text_rect)
        
        for load_btn, delete_btn, _ in btns:
            load_btn.draw(pantalla)
            delete_btn.draw(pantalla)
        
        btn_volver.draw(pantalla)

        pygame.display.flip()
        clock.tick(60)

# ========================
# EJECUCIÓN PRINCIPAL
# ========================
if __name__ == '__main__':
    pantalla_intro()
    
    config = cargar_config()
    if not config:
        config = {"fuente": fuentes_disponibles[0], "tam": 60, "color": colores_disponibles[0]}

    nombre_fuente, tam, color = config["fuente"], config["tam"], tuple(config["color"])

    while True:
        accion = pantalla_menu_principal()
        
        if accion == "seleccion_modo":
            modo_seleccionado = pantalla_seleccion_modo_juego()
            if modo_seleccionado == "arcane":
                resultado_juego = jugar_arcane(nombre_fuente, tam, color)
                if resultado_juego == "volver_seleccion_modo": continue
            elif modo_seleccionado == "versus":
                resultado_juego = jugar_versus(nombre_fuente, tam, color)
                if resultado_juego == "volver_seleccion_modo": continue
            elif modo_seleccionado == "volver_menu": continue

        elif accion == "highscores":
            pantalla_highscores()
            continue

        elif accion == "cargar_partida":
            while True:
                saved_games_list = cargar_partida()
                selected_save_data = pantalla_seleccionar_partida(saved_games_list)

                if selected_save_data == "refresh": continue

                if selected_save_data and selected_save_data != "volver_menu":
                    loaded_state = selected_save_data["state"]
                    loaded_mode = selected_save_data["mode"]
                    loaded_fallos_limit = loaded_state.get("fallos_limit", 10)
                    loaded_time_limit_seconds = loaded_state.get("time_limit_seconds", 0)
                    
                    # ===== INICIO DE LA CORRECCIÓN =====
                    # Usar argumentos con nombre para evitar errores de posición
                    if loaded_mode == "arcane":
                        resultado_juego = jugar(nombre_fuente=nombre_fuente, tam=tam, color=color, 
                                                num_jugadores=1, 
                                                initial_speed=loaded_state.get("velocidad", 1.5), 
                                                count_wrong_key_faults=True, 
                                                fallos_limit=loaded_fallos_limit, 
                                                initial_state=loaded_state)
                    elif loaded_mode == "versus":
                        resultado_juego = jugar(nombre_fuente=nombre_fuente, tam=tam, color=color, 
                                                num_jugadores=2, 
                                                initial_speed=loaded_state.get("velocidad", 2.0), 
                                                count_wrong_key_faults=True, 
                                                time_limit_seconds=loaded_time_limit_seconds, 
                                                fallos_limit=loaded_fallos_limit, 
                                                initial_state=loaded_state)
                    # ===== FIN DE LA CORRECCIÓN =====
                else:
                    resultado_juego = None
                break
            
        elif accion == "configuracion":
            nombre_fuente, tam, color = pantalla_configuracion(config)
            config = {"fuente": nombre_fuente, "tam": tam, "color": color}
        
        if 'resultado_juego' in locals() and resultado_juego == "menu_principal":
            if music_loaded and pygame.mixer.music.get_busy() == 0: pygame.mixer.music.unpause() 
            del resultado_juego
            continue