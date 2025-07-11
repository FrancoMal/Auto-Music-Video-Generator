import numpy as np
import librosa
from PIL import Image, ImageDraw
import cv2
import os
import logging
from config import VIDEO_CONFIG, VISUALIZER_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioVisualizer:
    def __init__(self, config=None):
        """Inicializar el visualizador de audio con configuración"""
        if config is None:
            config = {}
        
        # Configuración de video
        self.width = config.get('width', VIDEO_CONFIG['width'])
        self.height = config.get('height', VIDEO_CONFIG['height'])
        self.fps = config.get('fps', VIDEO_CONFIG['fps'])
        
        # Configuración del visualizador
        self.num_bars = config.get('num_bars', VISUALIZER_CONFIG['num_bars'])
        self.margin_x = config.get('margin_x', VISUALIZER_CONFIG['margin_x'])
        self.background_color = config.get('background_color', VISUALIZER_CONFIG['background_color'])
        self.bar_color = config.get('bar_color', VISUALIZER_CONFIG['bar_color'])
        self.gap = config.get('gap', VISUALIZER_CONFIG['gap'])
        self.vertical_offset = config.get('vertical_offset', VISUALIZER_CONFIG['vertical_offset'])
        self.n_fft = config.get('n_fft', VISUALIZER_CONFIG['n_fft'])
        self.power = config.get('power', VISUALIZER_CONFIG['power'])
        
        # Calcular dimensiones
        self.max_bar_height = self.height // 3
        self.region_bottom = self.height - self.vertical_offset
        
        # Calcular ancho de cada barra
        total_gap = self.gap * (self.num_bars - 1)
        available_width = self.width - 2 * self.margin_x
        self.bar_width = (available_width - total_gap) // self.num_bars
        
    def load_audio(self, audio_path):
        """Cargar archivo de audio"""
        try:
            y, sr = librosa.load(audio_path, sr=None, mono=True)
            logger.info(f"Audio cargado: {audio_path} (sr={sr}, duration={len(y)/sr:.2f}s)")
            return y, sr
        except Exception as e:
            logger.error(f"Error al cargar audio {audio_path}: {e}")
            return None, None
    
    def calculate_mel_spectrogram(self, y, sr):
        """Calcular espectrograma de mel"""
        try:
            hop_length = int(sr / self.fps)
            
            mel_spec = librosa.feature.melspectrogram(
                y=y,
                sr=sr,
                n_fft=self.n_fft,
                hop_length=hop_length,
                n_mels=self.num_bars,
                power=self.power
            )
            
            # Normalizar cada banda al rango [0,1]
            band_max = np.max(mel_spec, axis=1, keepdims=True)
            band_max[band_max == 0] = 1e-6
            mel_spec_norm = mel_spec / band_max
            
            logger.info(f"Espectrograma calculado: {mel_spec_norm.shape[1]} frames")
            return mel_spec_norm
            
        except Exception as e:
            logger.error(f"Error al calcular espectrograma: {e}")
            return None
    
    def create_frame(self, magnitudes):
        """Crear un frame individual del visualizador"""
        try:
            # Crear lienzo
            img = Image.new("RGB", (self.width, self.height), self.background_color)
            draw = ImageDraw.Draw(img)
            
            # Dibujar barras verticales
            for i, mag in enumerate(magnitudes):
                bar_height = int(mag * self.max_bar_height)
                x0 = self.margin_x + i * (self.bar_width + self.gap)
                x1 = x0 + self.bar_width
                y1 = self.region_bottom
                y0 = self.region_bottom - bar_height
                draw.rectangle([(x0, y0), (x1, y1)], fill=self.bar_color)
            
            # Convertir PIL a BGR para OpenCV
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            return frame
            
        except Exception as e:
            logger.error(f"Error al crear frame: {e}")
            return None
    
    def generate_visualization(self, audio_path, output_path):
        """Generar visualización completa para un archivo de audio"""
        try:
            logger.info(f"Generando visualización: {audio_path} -> {output_path}")
            
            # Cargar audio
            y, sr = self.load_audio(audio_path)
            if y is None or sr is None:
                return False
            
            # Calcular espectrograma
            mel_spec_norm = self.calculate_mel_spectrogram(y, sr)
            if mel_spec_norm is None:
                return False
            
            # Crear directorio de salida si no existe
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Preparar escritor de video
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(output_path, fourcc, self.fps, (self.width, self.height))
            
            # Generar frames
            num_frames = mel_spec_norm.shape[1]
            for frame_idx in range(num_frames):
                if frame_idx % 100 == 0:
                    logger.info(f"Procesando frame {frame_idx}/{num_frames}")
                
                magnitudes = mel_spec_norm[:, frame_idx]
                frame = self.create_frame(magnitudes)
                
                if frame is not None:
                    video_writer.write(frame)
            
            # Finalizar y guardar video
            video_writer.release()
            logger.info(f"Visualización guardada: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error al generar visualización: {e}")
            return False
    
    def generate_batch_visualizations(self, audio_files, output_dir):
        """Generar visualizaciones para múltiples archivos de audio"""
        results = []
        
        for i, audio_file in enumerate(audio_files):
            try:
                # Crear nombre de archivo de salida
                base_name = os.path.splitext(os.path.basename(audio_file))[0]
                output_file = os.path.join(output_dir, f"viz_{i:03d}_{base_name}.mp4")
                
                # Generar visualización
                success = self.generate_visualization(audio_file, output_file)
                results.append((audio_file, output_file, success))
                
            except Exception as e:
                logger.error(f"Error en procesamiento por lotes para {audio_file}: {e}")
                results.append((audio_file, None, False))
        
        return results

# Mantener compatibilidad con el script original
if __name__ == "__main__":
    # Configuración por defecto para compatibilidad
    default_config = {
        'audio_path': "output_20250706195359_0.mp3",
        'output_path': "audio_visualization_vertical.mp4"
    }
    
    visualizer = AudioVisualizer()
    
    # Verificar si el archivo de audio existe
    if os.path.exists(default_config['audio_path']):
        success = visualizer.generate_visualization(
            default_config['audio_path'], 
            default_config['output_path']
        )
        if success:
            print(f"Video guardado en '{default_config['output_path']}'")
        else:
            print("Error al generar la visualización")
    else:
        print(f"Archivo de audio no encontrado: {default_config['audio_path']}")
        print("Usa: python visualizer_transparent.py <audio_file> <output_file>")
