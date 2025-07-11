import os
import librosa
import numpy as np
from pydub import AudioSegment
from pydub.utils import make_chunks
import logging
from config import MUSICA_DIR, FILES_CONFIG, AUDIO_CONFIG, PROCESS_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioProcessor:
    def __init__(self):
        self.supported_formats = PROCESS_CONFIG['supported_formats']
        self.repeat_count = PROCESS_CONFIG['repeat_count']
        self.sample_rate = AUDIO_CONFIG['sample_rate']
        
    def get_audio_files(self, music_dir=MUSICA_DIR):
        """Obtiene lista de archivos de audio de la carpeta música"""
        audio_files = []
        
        if not os.path.exists(music_dir):
            logger.error(f"La carpeta {music_dir} no existe")
            return audio_files
            
        for file in os.listdir(music_dir):
            if any(file.lower().endswith(ext) for ext in self.supported_formats):
                file_path = os.path.join(music_dir, file)
                audio_files.append(file_path)
        
        # Ordenar alfabéticamente para consistencia
        audio_files.sort()
        logger.info(f"Encontrados {len(audio_files)} archivos de audio")
        
        return audio_files
    
    def get_audio_duration(self, audio_path):
        """Obtiene la duración de un archivo de audio en segundos"""
        try:
            audio = AudioSegment.from_file(audio_path)
            return len(audio) / 1000.0  # Convertir de ms a segundos
        except Exception as e:
            logger.error(f"Error al obtener duración de {audio_path}: {e}")
            return 0.0
    
    def combine_audio_files(self, audio_files, output_path=None):
        """Combina archivos de audio en el orden especificado (repetido 2 veces)"""
        if not audio_files:
            logger.error("No hay archivos de audio para combinar")
            return None
            
        if output_path is None:
            output_path = FILES_CONFIG['combined_audio']
            
        try:
            # Crear lista de archivos repetida según configuración
            playlist = audio_files * self.repeat_count
            logger.info(f"Combinando {len(playlist)} archivos (lista repetida {self.repeat_count} veces)")
            
            # Inicializar con silencio
            combined_audio = AudioSegment.silent(duration=0)
            
            # Combinar archivos secuencialmente
            for i, audio_file in enumerate(playlist):
                logger.info(f"Procesando archivo {i+1}/{len(playlist)}: {os.path.basename(audio_file)}")
                
                # Cargar archivo de audio
                audio_segment = AudioSegment.from_file(audio_file)
                
                # Normalizar el volumen si es necesario
                audio_segment = audio_segment.normalize()
                
                # Añadir al audio combinado
                combined_audio += audio_segment
                
            # Exportar el archivo combinado
            combined_audio.export(output_path, format="mp3", bitrate=AUDIO_CONFIG['quality'])
            logger.info(f"Audio combinado guardado en: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error al combinar archivos de audio: {e}")
            return None
    
    def generate_description_file(self, audio_files, output_path=None):
        """Genera archivo de descripción con los tiempos de cada canción"""
        if not audio_files:
            logger.error("No hay archivos de audio para generar descripción")
            return None
            
        if output_path is None:
            output_path = FILES_CONFIG['description_file']
            
        try:
            # Crear lista de archivos repetida según configuración
            playlist = audio_files * self.repeat_count
            
            description_lines = []
            current_time = 0.0
            
            description_lines.append("=== DESCRIPCIÓN DEL VIDEO MUSICAL ===\n")
            description_lines.append(f"Total de canciones: {len(playlist)}")
            description_lines.append(f"Repeticiones: {self.repeat_count}")
            description_lines.append("\n=== TIEMPOS DE REPRODUCCIÓN ===\n")
            
            for i, audio_file in enumerate(playlist):
                song_name = os.path.splitext(os.path.basename(audio_file))[0]
                duration = self.get_audio_duration(audio_file)
                
                # Convertir tiempo actual a formato mm:ss
                minutes = int(current_time // 60)
                seconds = int(current_time % 60)
                time_str = f"{minutes:02d}:{seconds:02d}"
                
                # Determinar si es primera vez o repetición
                cycle = (i // len(audio_files)) + 1
                position = (i % len(audio_files)) + 1
                
                description_lines.append(f"{time_str} - {song_name} [Ciclo {cycle}, Posición {position}]")
                
                current_time += duration
            
            # Añadir tiempo total
            total_minutes = int(current_time // 60)
            total_seconds = int(current_time % 60)
            description_lines.append(f"\n=== DURACIÓN TOTAL ===")
            description_lines.append(f"Tiempo total: {total_minutes:02d}:{total_seconds:02d}")
            
            # Escribir archivo
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(description_lines))
                
            logger.info(f"Archivo de descripción generado: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error al generar archivo de descripción: {e}")
            return None
    
    def process_audio(self, music_dir=None):
        """Procesa todo el audio: combina archivos y genera descripción"""
        if music_dir is None:
            music_dir = MUSICA_DIR
            
        logger.info("Iniciando procesamiento de audio...")
        
        # Obtener archivos de audio
        audio_files = self.get_audio_files(music_dir)
        if not audio_files:
            logger.error("No se encontraron archivos de audio")
            return None, None
            
        # Combinar archivos de audio
        combined_audio_path = self.combine_audio_files(audio_files)
        if not combined_audio_path:
            logger.error("Error al combinar archivos de audio")
            return None, None
            
        # Generar archivo de descripción
        description_path = self.generate_description_file(audio_files)
        if not description_path:
            logger.error("Error al generar archivo de descripción")
            return combined_audio_path, None
            
        logger.info("Procesamiento de audio completado exitosamente")
        return combined_audio_path, description_path

if __name__ == "__main__":
    processor = AudioProcessor()
    audio_path, desc_path = processor.process_audio()
    
    if audio_path and desc_path:
        print(f"Audio combinado: {audio_path}")
        print(f"Descripción: {desc_path}")
    else:
        print("Error en el procesamiento")