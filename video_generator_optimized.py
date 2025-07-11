import os
import logging
import subprocess
import json
import numpy as np
from config import VIDEO_CONFIG, FILES_CONFIG, CHROMA_CONFIG, VISUALIZER_OPTIMIZED_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizedVideoGenerator:
    def __init__(self):
        self.width = VIDEO_CONFIG['width']
        self.height = VIDEO_CONFIG['height']
        self.fps = VIDEO_CONFIG['fps']
        self.video_codec = 'h264_nvenc'  # GPU encoding / Codificación GPU
        self.audio_codec = VIDEO_CONFIG['audio_codec']
        self.bitrate = '15M'  # Higher bitrate for better quality / Mayor bitrate para mejor calidad
        self.audio_bitrate = VIDEO_CONFIG['audio_bitrate']
        
        # Optimized visualizer configurations / Configuraciones del visualizador optimizado
        self.viz_width = VISUALIZER_OPTIMIZED_CONFIG['width']
        self.viz_height = VISUALIZER_OPTIMIZED_CONFIG['height']
        self.viz_position_from_bottom = VISUALIZER_OPTIMIZED_CONFIG['position_from_bottom']
        self.viz_color = VISUALIZER_OPTIMIZED_CONFIG['color']
        self.viz_mode = VISUALIZER_OPTIMIZED_CONFIG['mode']
        self.viz_mirror_effect = VISUALIZER_OPTIMIZED_CONFIG['mirror_effect']
        self.viz_opacity = VISUALIZER_OPTIMIZED_CONFIG['opacity']
        self.viz_scale = VISUALIZER_OPTIMIZED_CONFIG['scale']
        
        # Check if GPU is available / Verificar si GPU está disponible
        self.gpu_available = self.check_gpu_support()
        if not self.gpu_available:
            logger.warning("GPU not available, using CPU / GPU no disponible, usando CPU")
            self.video_codec = 'libx264'
            self.bitrate = VIDEO_CONFIG['bitrate']
    
    def check_gpu_support(self):
        """Check if FFmpeg supports GPU acceleration / Verificar si FFmpeg soporta aceleración GPU"""
        try:
            result = subprocess.run(
                ['ffmpeg', '-encoders'], 
                capture_output=True, 
                text=True
            )
            return 'h264_nvenc' in result.stdout
        except:
            return False
    
    def create_audio_waveform_video(self, audio_path, output_path):
        """Crear video con forma de onda usando FFmpeg"""
        try:
            logger.info(f"Creando video con waveform: {output_path}")
            
            cmd = [
                'ffmpeg', '-y',
                '-i', audio_path,
                '-filter_complex', 
                f'[0:a]showwaves=s={self.width}x{self.height}:mode=cline:colors=white:rate={self.fps}[v]',
                '-map', '[v]',
                '-map', '0:a',
                '-c:v', self.video_codec,
                '-c:a', self.audio_codec,
                '-b:v', self.bitrate,
                '-b:a', self.audio_bitrate,
                '-r', str(self.fps),
                '-pix_fmt', 'yuv420p',
                output_path
            ]
            
            if self.gpu_available:
                cmd.extend(['-gpu', '0'])
            
            logger.info("Ejecutando FFmpeg con aceleración GPU...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Video con waveform creado: {output_path}")
                return True
            else:
                logger.error(f"Error en FFmpeg: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error al crear video con waveform: {e}")
            return False
    
    def create_spectrum_video(self, audio_path, output_path):
        """Crear video con espectro de frecuencias usando FFmpeg"""
        try:
            logger.info(f"Creando video con espectro: {output_path}")
            
            cmd = [
                'ffmpeg', '-y',
                '-i', audio_path,
                '-filter_complex', 
                f'[0:a]showfreqs=s={self.width}x{self.height}:mode=bar:colors=fire:rate={self.fps}[v]',
                '-map', '[v]',
                '-map', '0:a',
                '-c:v', self.video_codec,
                '-c:a', self.audio_codec,
                '-b:v', self.bitrate,
                '-b:a', self.audio_bitrate,
                '-r', str(self.fps),
                '-pix_fmt', 'yuv420p',
                output_path
            ]
            
            if self.gpu_available:
                cmd.extend(['-gpu', '0'])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Video con espectro creado: {output_path}")
                return True
            else:
                logger.error(f"Error en FFmpeg: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error al crear video con espectro: {e}")
            return False
    
    def create_background_video(self, background_image_path, audio_path, output_path):
        """Crear video de fondo con imagen y audio"""
        try:
            logger.info(f"Creando video de fondo: {output_path}")
            
            cmd = [
                'ffmpeg', '-y',
                '-loop', '1',
                '-i', background_image_path,
                '-i', audio_path,
                '-c:v', self.video_codec,
                '-c:a', self.audio_codec,
                '-b:v', self.bitrate,
                '-b:a', self.audio_bitrate,
                '-r', str(self.fps),
                '-shortest',
                '-vf', f'scale={self.width}:{self.height}',
                '-pix_fmt', 'yuv420p',
                output_path
            ]
            
            if self.gpu_available:
                cmd.extend(['-gpu', '0'])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Video de fondo creado: {output_path}")
                return True
            else:
                logger.error(f"Error en FFmpeg: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error al crear video de fondo: {e}")
            return False
    
    def overlay_videos(self, background_video, overlay_video, output_path, overlay_opacity=0.7):
        """Superponer videos usando FFmpeg"""
        try:
            logger.info(f"Superponiendo videos: {output_path}")
            
            cmd = [
                'ffmpeg', '-y',
                '-i', background_video,
                '-i', overlay_video,
                '-filter_complex', 
                f'[1:v]format=yuva420p,colorchannelmixer=aa={overlay_opacity}[overlay];[0:v][overlay]overlay[v]',
                '-map', '[v]',
                '-map', '0:a',
                '-c:v', self.video_codec,
                '-c:a', 'copy',
                '-shortest',
                output_path
            ]
            
            if self.gpu_available:
                cmd.extend(['-gpu', '0'])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Videos superpuestos: {output_path}")
                return True
            else:
                logger.error(f"Error en FFmpeg: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error al superponer videos: {e}")
            return False
    
    def generate_final_video_optimized(self, audio_path, background_image_path, output_path):
        """Generar video final optimizado usando solo FFmpeg"""
        try:
            logger.info("=== GENERANDO VIDEO FINAL OPTIMIZADO ===")
            
            # Crear directorio de salida
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Archivos temporales
            temp_dir = os.path.dirname(output_path)
            background_video = os.path.join(temp_dir, 'temp_background.mp4')
            spectrum_video = os.path.join(temp_dir, 'temp_spectrum.mp4')
            
            # 1. Crear video de fondo
            logger.info("Paso 1/3: Creando video de fondo...")
            if not self.create_background_video(background_image_path, audio_path, background_video):
                return False
            
            # 2. Crear video con espectro
            logger.info("Paso 2/3: Creando visualización de espectro...")
            if not self.create_spectrum_video(audio_path, spectrum_video):
                return False
            
            # 3. Superponer videos
            logger.info("Paso 3/3: Superponiendo videos...")
            if not self.overlay_videos(background_video, spectrum_video, output_path):
                return False
            
            # Limpiar archivos temporales
            for temp_file in [background_video, spectrum_video]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            
            logger.info(f"Video final generado exitosamente: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error al generar video final optimizado: {e}")
            return False
    
    def create_simple_music_video(self, audio_path, background_image_path, output_path):
        """Create simple and fast music video / Crear video musical simple y rápido"""
        try:
            logger.info("=== CREATING SIMPLE MUSIC VIDEO / CREANDO VIDEO MUSICAL SIMPLE ===")
            
            # Build complex filter using configuration / Construir el filtro complejo usando configuración
            if self.viz_mirror_effect:
                # With horizontal mirror effect / Con efecto espejo horizontal
                filter_complex = (
                    f'[0:v]scale={self.width}:{self.height}[bg];'
                    f'[1:a]showwaves=s={self.viz_width//2}x{self.viz_height}:mode={self.viz_mode}:colors={self.viz_color}:rate={self.fps}[wave_half];'
                    f'[wave_half]split[wave_orig][wave_copy];'
                    f'[wave_copy]hflip[wave_mirror];'
                    f'[wave_orig][wave_mirror]hstack[wave_symmetric];'
                    f'[bg][wave_symmetric]overlay=x=0:y=H-h-{self.viz_position_from_bottom}[v]'
                )
            else:
                # Without mirror effect / Sin efecto espejo
                filter_complex = (
                    f'[0:v]scale={self.width}:{self.height}[bg];'
                    f'[1:a]showwaves=s={self.viz_width}x{self.viz_height}:mode={self.viz_mode}:colors={self.viz_color}:rate={self.fps}[wave];'
                    f'[bg][wave]overlay=x=0:y=H-h-{self.viz_position_from_bottom}[v]'
                )
            
            cmd = [
                'ffmpeg', '-y',
                '-loop', '1',
                '-i', background_image_path,
                '-i', audio_path,
                '-filter_complex', filter_complex,
                '-map', '[v]',
                '-map', '1:a',
                '-c:v', self.video_codec,
                '-c:a', self.audio_codec,
                '-b:v', self.bitrate,
                '-b:a', self.audio_bitrate,
                '-r', str(self.fps),
                '-shortest',
                '-pix_fmt', 'yuv420p',
                output_path
            ]
            
            if self.gpu_available:
                cmd.extend(['-gpu', '0'])
            
            logger.info("Running FFmpeg / Ejecutando FFmpeg...")
            logger.debug(f"Command / Comando: {' '.join(cmd)}")
            logger.debug(f"Complex filter / Filtro complejo: {filter_complex}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Music video created / Video musical creado: {output_path}")
                return True
            else:
                logger.error(f"FFmpeg error / Error en FFmpeg: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error al crear video musical: {e}")
            return False

if __name__ == "__main__":
    generator = OptimizedVideoGenerator()
    
    # Configuración de prueba
    audio_path = FILES_CONFIG['combined_audio']
    background_path = FILES_CONFIG['background_image']
    output_path = FILES_CONFIG['final_video']
    
    # Generar video final optimizado
    success = generator.create_simple_music_video(
        audio_path, background_path, output_path
    )
    
    if success:
        print(f"Video final generado: {output_path}")
    else:
        print("Error al generar video final")