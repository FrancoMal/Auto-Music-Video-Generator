import os

# Path configurations / Configuraciones de paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MUSICA_DIR = os.path.join(BASE_DIR, "musica")
RECURSOS_DIR = os.path.join(BASE_DIR, "recursos")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Video configurations / Configuraciones de video
VIDEO_CONFIG = {
    "width": 1920,
    "height": 1080,
    "fps": 30,
    "output_format": "mp4",
    "video_codec": "libx264",
    "audio_codec": "aac",
    "bitrate": "5000k",
    "audio_bitrate": "320k"
}

# Visualizer configurations / Configuraciones del visualizador
VISUALIZER_CONFIG = {
    "num_bars": 64,
    "margin_x": 100,
    "background_color": (0, 255, 0),  # Green for chroma key / Verde para chroma key
    "bar_color": (255, 255, 255),     # White / Blanco
    "gap": 5,
    "vertical_offset": 140,
    "n_fft": 2048,
    "power": 1.0
}

# Configuraciones de audio
AUDIO_CONFIG = {
    "sample_rate": 44100,
    "channels": 2,
    "format": "mp3",
    "quality": "320k"
}

# Configuraciones de archivos
FILES_CONFIG = {
    "background_image": os.path.join(RECURSOS_DIR, "background.jpg"),
    "combined_audio": os.path.join(TEMP_DIR, "combined_audio.mp3"),
    "description_file": os.path.join(OUTPUT_DIR, "descripcion.txt"),
    "final_video": os.path.join(OUTPUT_DIR, "video_final.mp4"),
    "temp_video_prefix": os.path.join(TEMP_DIR, "temp_video_"),
    "temp_viz_prefix": os.path.join(TEMP_DIR, "viz_")
}

# Configuraciones del procesamiento
PROCESS_CONFIG = {
    "repeat_count": 1,  # Cuántas veces se repite la lista de canciones
    "supported_formats": ['.mp3', '.wav', '.flac', '.m4a', '.ogg'],
    "max_concurrent_processes": 4,
    "temp_cleanup": True
}

# Configuraciones de logging
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": os.path.join(OUTPUT_DIR, "app.log")
}

# Configuraciones de chroma key
CHROMA_CONFIG = {
    "lower_green": (40, 40, 40),
    "upper_green": (80, 255, 255),
    "blur_radius": 3,
    "dilate_kernel": 3
}

# Optimized visualizer configurations / Configuraciones del visualizador optimizado
VISUALIZER_OPTIMIZED_CONFIG = {
    "width": 1920,
    "height": 200,
    "position_from_bottom": 50,
    "color": "red",  # Available colors / Colores disponibles: red, cyan, white, yellow, green, blue, magenta, orange, pink
    "mode": "cline",  # Visualization modes / Modos de visualización: cline, line, point
    "mirror_effect": True,  # Horizontal mirror effect / Efecto espejo horizontal
    "opacity": 1.0,  # Visualizer opacity / Opacidad del visualizador (0.0 a 1.0)
    "scale": 1.0  # Visualizer scale / Escala del visualizador
}