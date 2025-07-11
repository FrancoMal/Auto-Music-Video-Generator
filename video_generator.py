import cv2
import numpy as np
import os
import logging
from PIL import Image, ImageDraw
import subprocess
import json
from config import VIDEO_CONFIG, FILES_CONFIG, CHROMA_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoGenerator:
    def __init__(self):
        self.width = VIDEO_CONFIG['width']
        self.height = VIDEO_CONFIG['height']
        self.fps = VIDEO_CONFIG['fps']
        self.video_codec = VIDEO_CONFIG['video_codec']
        self.audio_codec = VIDEO_CONFIG['audio_codec']
        self.bitrate = VIDEO_CONFIG['bitrate']
        self.audio_bitrate = VIDEO_CONFIG['audio_bitrate']
        
        # Configuraciones de chroma key
        self.lower_green = np.array(CHROMA_CONFIG['lower_green'])
        self.upper_green = np.array(CHROMA_CONFIG['upper_green'])
        self.blur_radius = CHROMA_CONFIG['blur_radius']
        self.dilate_kernel = CHROMA_CONFIG['dilate_kernel']
        
    def load_background_image(self, image_path):
        """Cargar y redimensionar imagen de fondo"""
        try:
            if not os.path.exists(image_path):
                logger.warning(f"Imagen de fondo no encontrada: {image_path}")
                return self.create_default_background()
            
            # Cargar imagen
            img = cv2.imread(image_path)
            if img is None:
                logger.error(f"No se pudo cargar la imagen: {image_path}")
                return self.create_default_background()
            
            # Redimensionar a las dimensiones del video
            img_resized = cv2.resize(img, (self.width, self.height))
            logger.info(f"Imagen de fondo cargada: {image_path}")
            return img_resized
            
        except Exception as e:
            logger.error(f"Error al cargar imagen de fondo: {e}")
            return self.create_default_background()
    
    def create_default_background(self):
        """Crear imagen de fondo por defecto"""
        try:
            # Crear imagen de fondo degradado
            img = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            
            # Crear degradado vertical
            for y in range(self.height):
                intensity = int(255 * (1 - y / self.height))
                img[y, :] = [intensity // 4, intensity // 2, intensity]
            
            logger.info("Imagen de fondo por defecto creada")
            return img
            
        except Exception as e:
            logger.error(f"Error al crear imagen de fondo por defecto: {e}")
            return np.zeros((self.height, self.width, 3), dtype=np.uint8)
    
    def get_video_duration(self, video_path):
        """Obtener duración de un video usando ffprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                duration = float(data['format']['duration'])
                return duration
            else:
                logger.error(f"Error al obtener duración de {video_path}")
                return 0.0
                
        except Exception as e:
            logger.error(f"Error al obtener duración de video: {e}")
            return 0.0
    
    def apply_chroma_key(self, foreground, background):
        """Aplicar chroma key (eliminar fondo verde)"""
        try:
            # Verificar y ajustar dimensiones
            if foreground.shape[:2] != background.shape[:2]:
                logger.debug(f"Redimensionando foreground de {foreground.shape[:2]} a {background.shape[:2]}")
                foreground = cv2.resize(foreground, (background.shape[1], background.shape[0]))
            
            # Convertir a HSV para mejor detección de verde
            hsv = cv2.cvtColor(foreground, cv2.COLOR_BGR2HSV)
            
            # Crear máscara para el fondo verde
            mask = cv2.inRange(hsv, self.lower_green, self.upper_green)
            
            # Aplicar morfología para limpiar la máscara
            kernel = np.ones((self.dilate_kernel, self.dilate_kernel), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            
            # Aplicar suavizado
            mask = cv2.GaussianBlur(mask, (self.blur_radius, self.blur_radius), 0)
            
            # Invertir máscara (queremos mantener lo que NO es verde)
            mask_inv = cv2.bitwise_not(mask)
            
            # Normalizar máscara
            mask_norm = mask_inv.astype(np.float32) / 255.0
            mask_norm = np.expand_dims(mask_norm, axis=2)
            
            # Aplicar chroma key
            result = foreground.astype(np.float32) * mask_norm + background.astype(np.float32) * (1 - mask_norm)
            
            return result.astype(np.uint8)
            
        except Exception as e:
            logger.error(f"Error al aplicar chroma key: {e}")
            return background
    
    def create_base_video(self, background_image_path, audio_path, output_path):
        """Crear video base con imagen de fondo y audio"""
        try:
            logger.info(f"Creando video base: {output_path}")
            
            # Verificar que existe el audio
            if not os.path.exists(audio_path):
                logger.error(f"Archivo de audio no encontrado: {audio_path}")
                return False
            
            # Cargar imagen de fondo
            background = self.load_background_image(background_image_path)
            
            # Crear directorio de salida si no existe
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Usar ffmpeg para crear video base
            cmd = [
                'ffmpeg', '-y',
                '-loop', '1',
                '-i', background_image_path if os.path.exists(background_image_path) else 'temp_bg.jpg',
                '-i', audio_path,
                '-c:v', self.video_codec,
                '-c:a', self.audio_codec,
                '-b:v', self.bitrate,
                '-b:a', self.audio_bitrate,
                '-r', str(self.fps),
                '-shortest',
                '-pix_fmt', 'yuv420p',
                output_path
            ]
            
            # Si no existe imagen de fondo, crear una temporalmente
            temp_bg_path = None
            if not os.path.exists(background_image_path):
                temp_bg_path = os.path.join(os.path.dirname(output_path), 'temp_bg.jpg')
                cv2.imwrite(temp_bg_path, background)
                cmd[3] = temp_bg_path
            
            logger.info("Ejecutando ffmpeg para crear video base...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Limpiar archivo temporal
            if temp_bg_path and os.path.exists(temp_bg_path):
                os.remove(temp_bg_path)
            
            if result.returncode == 0:
                logger.info(f"Video base creado exitosamente: {output_path}")
                return True
            else:
                logger.error(f"Error en ffmpeg: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error al crear video base: {e}")
            return False
    
    def overlay_visualizations(self, base_video_path, visualization_videos, output_path):
        """Superponer visualizaciones sobre el video base usando chroma key"""
        try:
            logger.info(f"Superponiendo visualizaciones en: {output_path}")
            
            if not visualization_videos:
                logger.warning("No hay visualizaciones para superponer")
                return False
            
            # Abrir video base
            cap_base = cv2.VideoCapture(base_video_path)
            if not cap_base.isOpened():
                logger.error(f"No se pudo abrir video base: {base_video_path}")
                return False
            
            # Configurar escritor de video
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, self.fps, (self.width, self.height))
            
            # Verificar que el escritor se abrió correctamente
            if not out.isOpened():
                logger.error(f"No se pudo abrir el escritor de video: {output_path}")
                return False
            
            # Abrir videos de visualización
            viz_caps = []
            for viz_video in visualization_videos:
                cap = cv2.VideoCapture(viz_video)
                if cap.isOpened():
                    viz_caps.append(cap)
                else:
                    logger.warning(f"No se pudo abrir visualización: {viz_video}")
            
            if not viz_caps:
                logger.error("No se pudieron abrir videos de visualización")
                cap_base.release()
                out.release()
                return False
            
            frame_count = 0
            while True:
                ret_base, frame_base = cap_base.read()
                if not ret_base:
                    break
                
                # Asegurar que el frame base tiene las dimensiones correctas
                if frame_base.shape[:2] != (self.height, self.width):
                    logger.debug(f"Redimensionando frame base de {frame_base.shape[:2]} a ({self.height}, {self.width})")
                    frame_base = cv2.resize(frame_base, (self.width, self.height))
                
                result_frame = frame_base.copy()
                
                # Superponer cada visualización
                for cap_viz in viz_caps:
                    ret_viz, frame_viz = cap_viz.read()
                    if ret_viz:
                        # Redimensionar frame de visualización si es necesario
                        if frame_viz.shape[:2] != (self.height, self.width):
                            logger.debug(f"Redimensionando frame de {frame_viz.shape[:2]} a ({self.height}, {self.width})")
                            frame_viz = cv2.resize(frame_viz, (self.width, self.height))
                        
                        # Aplicar chroma key
                        result_frame = self.apply_chroma_key(frame_viz, result_frame)
                
                # Verificar que el frame tiene las dimensiones correctas
                if result_frame.shape[:2] == (self.height, self.width):
                    out.write(result_frame)
                    frame_count += 1
                    
                    if frame_count % 100 == 0:
                        logger.info(f"Procesados {frame_count} frames")
                else:
                    current_h, current_w = result_frame.shape[:2]
                    logger.warning(f"Frame con dimensiones incorrectas: altura={current_h}, ancho={current_w}, esperado: altura={self.height}, ancho={self.width}")
            
            # Limpiar recursos
            cap_base.release()
            for cap in viz_caps:
                cap.release()
            out.release()
            
            logger.info(f"Video con visualizaciones creado: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error al superponer visualizaciones: {e}")
            return False
    
    def generate_final_video(self, audio_path, background_image_path, visualization_videos, output_path):
        """Generar video final completo"""
        try:
            logger.info("Iniciando generación de video final...")
            
            # Crear video base
            base_video_path = os.path.join(os.path.dirname(output_path), 'temp_base_video.mp4')
            
            if not self.create_base_video(background_image_path, audio_path, base_video_path):
                logger.error("Error al crear video base")
                return False
            
            # Superponer visualizaciones si existen
            if visualization_videos:
                if not self.overlay_visualizations(base_video_path, visualization_videos, output_path):
                    logger.error("Error al superponer visualizaciones")
                    return False
            else:
                # Si no hay visualizaciones, usar el video base como final
                import shutil
                shutil.copy2(base_video_path, output_path)
            
            # Limpiar archivo temporal
            if os.path.exists(base_video_path):
                os.remove(base_video_path)
            
            logger.info(f"Video final generado exitosamente: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error al generar video final: {e}")
            return False
    
    def cleanup_temp_files(self, temp_dir):
        """Limpiar archivos temporales"""
        try:
            if os.path.exists(temp_dir):
                for file in os.listdir(temp_dir):
                    file_path = os.path.join(temp_dir, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                logger.info("Archivos temporales limpiados")
        except Exception as e:
            logger.error(f"Error al limpiar archivos temporales: {e}")

if __name__ == "__main__":
    generator = VideoGenerator()
    
    # Configuración de prueba
    audio_path = FILES_CONFIG['combined_audio']
    background_path = FILES_CONFIG['background_image']
    output_path = FILES_CONFIG['final_video']
    
    # Generar video final
    success = generator.generate_final_video(
        audio_path, background_path, [], output_path
    )
    
    if success:
        print(f"Video final generado: {output_path}")
    else:
        print("Error al generar video final")