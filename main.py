#!/usr/bin/env python3
"""
Script principal para generar videos musicales con visualizaciones
"""

import os
import sys
import logging
import argparse
from datetime import datetime
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, as_completed

# Importar módulos del proyecto
from audio_processor import AudioProcessor
from visualizer_transparent import AudioVisualizer
from video_generator import VideoGenerator
from config import (
    MUSICA_DIR, RECURSOS_DIR, TEMP_DIR, OUTPUT_DIR, 
    FILES_CONFIG, PROCESS_CONFIG, LOGGING_CONFIG
)

# Configurar logging
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG['level']),
    format=LOGGING_CONFIG['format'],
    handlers=[
        logging.FileHandler(LOGGING_CONFIG['file']),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MusicVideoGenerator:
    def __init__(self):
        self.audio_processor = AudioProcessor()
        self.visualizer = AudioVisualizer()
        self.video_generator = VideoGenerator()
        self.visualization_videos = []
        
    def setup_directories(self):
        """Crear directorios necesarios"""
        try:
            directories = [MUSICA_DIR, RECURSOS_DIR, TEMP_DIR, OUTPUT_DIR]
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
            logger.info("Directorios configurados correctamente")
            return True
        except Exception as e:
            logger.error(f"Error al configurar directorios: {e}")
            return False
    
    def validate_inputs(self):
        """Validar que existan los archivos necesarios"""
        try:
            # Verificar carpeta de música
            if not os.path.exists(MUSICA_DIR):
                logger.error(f"Carpeta de música no encontrada: {MUSICA_DIR}")
                return False
            
            # Verificar archivos de audio
            audio_files = self.audio_processor.get_audio_files()
            if not audio_files:
                logger.error("No se encontraron archivos de audio en la carpeta música")
                return False
            
            logger.info(f"Validación exitosa: {len(audio_files)} archivos de audio encontrados")
            return True
            
        except Exception as e:
            logger.error(f"Error en validación: {e}")
            return False
    
    def process_audio(self):
        """Procesar audio y generar descripción"""
        try:
            logger.info("=== PROCESANDO AUDIO ===")
            
            # Procesar audio
            audio_path, desc_path = self.audio_processor.process_audio()
            
            if not audio_path:
                logger.error("Error al procesar audio")
                return None, None
            
            logger.info(f"Audio procesado: {audio_path}")
            logger.info(f"Descripción generada: {desc_path}")
            
            return audio_path, desc_path
            
        except Exception as e:
            logger.error(f"Error al procesar audio: {e}")
            return None, None
    
    def generate_visualizations(self, audio_files):
        """Generar visualizaciones para cada archivo de audio"""
        try:
            logger.info("=== GENERANDO VISUALIZACIONES ===")
            
            if not audio_files:
                logger.warning("No hay archivos de audio para visualizar")
                return []
            
            # Crear lista de archivos repetida según configuración
            playlist = audio_files * PROCESS_CONFIG['repeat_count']
            
            visualization_results = []
            
            # Configurar procesamiento paralelo
            max_workers = min(PROCESS_CONFIG['max_concurrent_processes'], len(playlist))
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Enviar tareas
                future_to_audio = {}
                
                for i, audio_file in enumerate(playlist):
                    # Crear nombre de archivo de salida
                    base_name = os.path.splitext(os.path.basename(audio_file))[0]
                    output_file = os.path.join(TEMP_DIR, f"viz_{i:03d}_{base_name}.mp4")
                    
                    # Enviar tarea
                    future = executor.submit(
                        self.visualizer.generate_visualization,
                        audio_file,
                        output_file
                    )
                    future_to_audio[future] = (audio_file, output_file)
                
                # Recopilar resultados
                for future in as_completed(future_to_audio):
                    audio_file, output_file = future_to_audio[future]
                    try:
                        success = future.result()
                        visualization_results.append((audio_file, output_file, success))
                        
                        if success:
                            logger.info(f"Visualización completada: {os.path.basename(output_file)}")
                        else:
                            logger.error(f"Error en visualización: {os.path.basename(audio_file)}")
                            
                    except Exception as e:
                        logger.error(f"Error al generar visualización para {audio_file}: {e}")
                        visualization_results.append((audio_file, output_file, False))
            
            # Filtrar visualizaciones exitosas
            successful_visualizations = [
                result[1] for result in visualization_results if result[2]
            ]
            
            logger.info(f"Visualizaciones generadas exitosamente: {len(successful_visualizations)}")
            return successful_visualizations
            
        except Exception as e:
            logger.error(f"Error al generar visualizaciones: {e}")
            return []
    
    def generate_final_video(self, audio_path, visualization_videos):
        """Generar video final"""
        try:
            logger.info("=== GENERANDO VIDEO FINAL ===")
            
            # Configurar paths
            background_image_path = FILES_CONFIG['background_image']
            output_path = FILES_CONFIG['final_video']
            
            # Generar video final
            success = self.video_generator.generate_final_video(
                audio_path,
                background_image_path,
                visualization_videos,
                output_path
            )
            
            if success:
                logger.info(f"Video final generado exitosamente: {output_path}")
                return output_path
            else:
                logger.error("Error al generar video final")
                return None
                
        except Exception as e:
            logger.error(f"Error al generar video final: {e}")
            return None
    
    def cleanup(self):
        """Limpiar archivos temporales"""
        try:
            if PROCESS_CONFIG['temp_cleanup']:
                logger.info("Limpiando archivos temporales...")
                self.video_generator.cleanup_temp_files(TEMP_DIR)
        except Exception as e:
            logger.error(f"Error al limpiar archivos temporales: {e}")
    
    def run(self):
        """Ejecutar el proceso completo"""
        try:
            start_time = datetime.now()
            logger.info("=== INICIANDO GENERACIÓN DE VIDEO MUSICAL ===")
            
            # 1. Configurar directorios
            if not self.setup_directories():
                logger.error("Error al configurar directorios")
                return False
            
            # 2. Validar inputs
            if not self.validate_inputs():
                logger.error("Error en validación de inputs")
                return False
            
            # 3. Procesar audio
            audio_path, desc_path = self.process_audio()
            if not audio_path:
                logger.error("Error al procesar audio")
                return False
            
            # 4. Generar visualizaciones
            audio_files = self.audio_processor.get_audio_files()
            visualization_videos = self.generate_visualizations(audio_files)
            
            # 5. Generar video final
            final_video_path = self.generate_final_video(audio_path, visualization_videos)
            if not final_video_path:
                logger.error("Error al generar video final")
                return False
            
            # 6. Limpiar archivos temporales
            self.cleanup()
            
            # Mostrar resumen
            end_time = datetime.now()
            duration = end_time - start_time
            
            logger.info("=== PROCESO COMPLETADO EXITOSAMENTE ===")
            logger.info(f"Tiempo total: {duration}")
            logger.info(f"Video final: {final_video_path}")
            logger.info(f"Descripción: {desc_path}")
            logger.info(f"Canciones procesadas: {len(audio_files)}")
            logger.info(f"Visualizaciones generadas: {len(visualization_videos)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error en proceso principal: {e}")
            return False

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Generador de Videos Musicales')
    parser.add_argument('--music-dir', default=MUSICA_DIR, 
                       help='Directorio con archivos de música')
    parser.add_argument('--output-dir', default=OUTPUT_DIR,
                       help='Directorio de salida')
    parser.add_argument('--background', default=FILES_CONFIG['background_image'],
                       help='Imagen de fondo')
    parser.add_argument('--no-cleanup', action='store_true',
                       help='No limpiar archivos temporales')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Modo verbose')
    
    args = parser.parse_args()
    
    # Configurar logging según argumentos
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Actualizar configuraciones si se especificaron
    if args.music_dir != MUSICA_DIR:
        import config
        config.MUSICA_DIR = args.music_dir
    
    if args.output_dir != OUTPUT_DIR:
        import config
        config.OUTPUT_DIR = args.output_dir
    
    if args.background != FILES_CONFIG['background_image']:
        import config
        config.FILES_CONFIG['background_image'] = args.background
    
    if args.no_cleanup:
        import config
        config.PROCESS_CONFIG['temp_cleanup'] = False
    
    # Crear y ejecutar generador
    generator = MusicVideoGenerator()
    success = generator.run()
    
    if success:
        print("\n🎉 ¡Video musical generado exitosamente!")
        print(f"📁 Encuentra tu video en: {FILES_CONFIG['final_video']}")
        print(f"📄 Descripción en: {FILES_CONFIG['description_file']}")
        sys.exit(0)
    else:
        print("\n❌ Error al generar video musical")
        print("📝 Revisa el archivo de log para más detalles")
        sys.exit(1)

if __name__ == "__main__":
    main()