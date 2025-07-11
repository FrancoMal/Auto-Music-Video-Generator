#!/usr/bin/env python3
"""
Optimized main script for generating music videos
Leverages GPU acceleration and efficient RAM usage

Script principal optimizado para generar videos musicales
Aprovecha aceleración GPU y uso eficiente de RAM
"""

import os
import sys
import logging
import argparse
from datetime import datetime

# Import project modules / Importar módulos del proyecto
from audio_processor import AudioProcessor
from video_generator_optimized import OptimizedVideoGenerator
from config import (
    MUSICA_DIR, RECURSOS_DIR, TEMP_DIR, OUTPUT_DIR, 
    FILES_CONFIG, PROCESS_CONFIG, LOGGING_CONFIG
)

# Configure logging / Configurar logging
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG['level']),
    format=LOGGING_CONFIG['format'],
    handlers=[
        logging.FileHandler(LOGGING_CONFIG['file']),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OptimizedMusicVideoGenerator:
    def __init__(self):
        self.audio_processor = AudioProcessor()
        self.video_generator = OptimizedVideoGenerator()
        
    def setup_directories(self):
        """Create necessary directories / Crear directorios necesarios"""
        try:
            directories = [MUSICA_DIR, RECURSOS_DIR, TEMP_DIR, OUTPUT_DIR]
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
            logger.info("Directories configured correctly / Directorios configurados correctamente")
            return True
        except Exception as e:
            logger.error(f"Error setting up directories / Error al configurar directorios: {e}")
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
    
    def generate_final_video(self, audio_path, background_image_path, output_path):
        """Generar video final optimizado"""
        try:
            logger.info("=== GENERANDO VIDEO FINAL OPTIMIZADO ===")
            
            # Generar video usando FFmpeg optimizado
            success = self.video_generator.create_simple_music_video(
                audio_path,
                background_image_path,
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
                if os.path.exists(TEMP_DIR):
                    for file in os.listdir(TEMP_DIR):
                        file_path = os.path.join(TEMP_DIR, file)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
        except Exception as e:
            logger.error(f"Error al limpiar archivos temporales: {e}")
    
    def run(self):
        """Ejecutar el proceso completo optimizado"""
        try:
            start_time = datetime.now()
            logger.info("=== INICIANDO GENERACIÓN DE VIDEO MUSICAL OPTIMIZADO ===")
            logger.info(f"Usando GPU: {self.video_generator.gpu_available}")
            logger.info(f"Codec: {self.video_generator.video_codec}")
            
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
            
            # 4. Generar video final (sin visualizaciones separadas)
            background_image_path = FILES_CONFIG['background_image']
            output_path = FILES_CONFIG['final_video']
            
            final_video_path = self.generate_final_video(
                audio_path, 
                background_image_path, 
                output_path
            )
            
            if not final_video_path:
                logger.error("Error al generar video final")
                return False
            
            # 5. Limpiar archivos temporales
            self.cleanup()
            
            # Mostrar resumen
            end_time = datetime.now()
            duration = end_time - start_time
            
            logger.info("=== PROCESO COMPLETADO EXITOSAMENTE ===")
            logger.info(f"Tiempo total: {duration}")
            logger.info(f"Video final: {final_video_path}")
            logger.info(f"Descripción: {desc_path}")
            
            # Mostrar información del archivo
            if os.path.exists(final_video_path):
                file_size = os.path.getsize(final_video_path)
                logger.info(f"Tamaño del archivo: {file_size / (1024*1024):.2f} MB")
            
            return True
            
        except Exception as e:
            logger.error(f"Error en proceso principal: {e}")
            return False

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Generador de Videos Musicales Optimizado')
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
    parser.add_argument('--gpu', action='store_true',
                       help='Forzar uso de GPU')
    
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
    generator = OptimizedMusicVideoGenerator()
    success = generator.run()
    
    if success:
        print("\n🎉 ¡Video musical generado exitosamente!")
        print(f"🚀 Optimizado para RTX 4070Ti y 32GB RAM")
        print(f"📁 Encuentra tu video en: {FILES_CONFIG['final_video']}")
        print(f"📄 Descripción en: {FILES_CONFIG['description_file']}")
        sys.exit(0)
    else:
        print("\n❌ Error al generar video musical")
        print("📝 Revisa el archivo de log para más detalles")
        sys.exit(1)

if __name__ == "__main__":
    main()