"""
Funciones utilitarias para el generador de videos musicales
"""

import os
import sys
import time
import logging
import shutil
import hashlib
import json
from pathlib import Path
from datetime import datetime, timedelta
import subprocess

logger = logging.getLogger(__name__)

def format_time(seconds):
    """Convertir segundos a formato HH:MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"

def format_file_size(size_bytes):
    """Convertir bytes a formato legible"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def get_file_info(file_path):
    """Obtener información detallada de un archivo"""
    try:
        if not os.path.exists(file_path):
            return None
        
        stat = os.stat(file_path)
        return {
            'path': file_path,
            'name': os.path.basename(file_path),
            'size': stat.st_size,
            'size_formatted': format_file_size(stat.st_size),
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'created': datetime.fromtimestamp(stat.st_ctime)
        }
    except Exception as e:
        logger.error(f"Error al obtener información de {file_path}: {e}")
        return None

def calculate_file_hash(file_path, algorithm='md5'):
    """Calcular hash de un archivo"""
    try:
        hash_algo = hashlib.new(algorithm)
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_algo.update(chunk)
        return hash_algo.hexdigest()
    except Exception as e:
        logger.error(f"Error al calcular hash de {file_path}: {e}")
        return None

def clean_directory(directory, pattern="*", keep_files=None):
    """Limpiar archivos de un directorio"""
    try:
        if not os.path.exists(directory):
            return 0
        
        if keep_files is None:
            keep_files = []
        
        files_removed = 0
        for file_path in Path(directory).glob(pattern):
            if file_path.is_file() and file_path.name not in keep_files:
                file_path.unlink()
                files_removed += 1
        
        logger.info(f"Limpiados {files_removed} archivos de {directory}")
        return files_removed
        
    except Exception as e:
        logger.error(f"Error al limpiar directorio {directory}: {e}")
        return 0

def ensure_directory(directory):
    """Asegurar que un directorio existe"""
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error al crear directorio {directory}: {e}")
        return False

def backup_file(file_path, backup_dir=None):
    """Crear copia de seguridad de un archivo"""
    try:
        if not os.path.exists(file_path):
            return None
        
        if backup_dir is None:
            backup_dir = os.path.dirname(file_path)
        
        ensure_directory(backup_dir)
        
        # Crear nombre de backup con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.basename(file_path)
        backup_name = f"{timestamp}_{base_name}"
        backup_path = os.path.join(backup_dir, backup_name)
        
        shutil.copy2(file_path, backup_path)
        logger.info(f"Backup creado: {backup_path}")
        return backup_path
        
    except Exception as e:
        logger.error(f"Error al crear backup de {file_path}: {e}")
        return None

def check_dependencies():
    """Verificar que las dependencias están instaladas"""
    dependencies = {
        'ffmpeg': ['ffmpeg', '-version'],
        'ffprobe': ['ffprobe', '-version']
    }
    
    missing = []
    for name, cmd in dependencies.items():
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                missing.append(name)
        except FileNotFoundError:
            missing.append(name)
    
    if missing:
        logger.error(f"Dependencias faltantes: {', '.join(missing)}")
        return False, missing
    
    logger.info("Todas las dependencias están disponibles")
    return True, []

def get_audio_info(audio_path):
    """Obtener información de un archivo de audio usando ffprobe"""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', audio_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            
            # Extraer información del formato
            format_info = data.get('format', {})
            duration = float(format_info.get('duration', 0))
            
            # Extraer información del stream de audio
            audio_stream = None
            for stream in data.get('streams', []):
                if stream.get('codec_type') == 'audio':
                    audio_stream = stream
                    break
            
            info = {
                'path': audio_path,
                'duration': duration,
                'duration_formatted': format_time(duration),
                'size': int(format_info.get('size', 0)),
                'size_formatted': format_file_size(int(format_info.get('size', 0))),
                'bitrate': int(format_info.get('bit_rate', 0)),
                'format': format_info.get('format_name', ''),
                'codec': audio_stream.get('codec_name', '') if audio_stream else '',
                'sample_rate': int(audio_stream.get('sample_rate', 0)) if audio_stream else 0,
                'channels': int(audio_stream.get('channels', 0)) if audio_stream else 0
            }
            
            return info
            
        else:
            logger.error(f"Error al obtener información de audio: {result.stderr}")
            return None
            
    except Exception as e:
        logger.error(f"Error al obtener información de audio de {audio_path}: {e}")
        return None

def progress_bar(current, total, width=50, prefix='Progress'):
    """Mostrar barra de progreso en la consola"""
    try:
        percent = (current / total) * 100
        filled_width = int(width * current // total)
        bar = '█' * filled_width + '░' * (width - filled_width)
        
        print(f'\r{prefix}: |{bar}| {percent:.1f}% ({current}/{total})', end='', flush=True)
        
        if current == total:
            print()  # Nueva línea al completar
            
    except Exception as e:
        logger.error(f"Error en barra de progreso: {e}")

def validate_audio_file(file_path):
    """Validar que un archivo de audio es válido"""
    try:
        # Verificar extensión
        valid_extensions = ['.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac']
        if not any(file_path.lower().endswith(ext) for ext in valid_extensions):
            return False, "Extensión no válida"
        
        # Verificar que existe
        if not os.path.exists(file_path):
            return False, "Archivo no encontrado"
        
        # Verificar que no está vacío
        if os.path.getsize(file_path) == 0:
            return False, "Archivo vacío"
        
        # Verificar con ffprobe
        audio_info = get_audio_info(file_path)
        if not audio_info:
            return False, "No se pudo leer el archivo de audio"
        
        if audio_info['duration'] <= 0:
            return False, "Duración inválida"
        
        return True, "Válido"
        
    except Exception as e:
        logger.error(f"Error al validar archivo de audio {file_path}: {e}")
        return False, str(e)

def create_project_summary(output_dir):
    """Crear resumen del proyecto generado"""
    try:
        summary_path = os.path.join(output_dir, "project_summary.txt")
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("=== RESUMEN DEL PROYECTO ===\n\n")
            f.write(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Información de archivos generados
            files_info = []
            for file_name in os.listdir(output_dir):
                if file_name == "project_summary.txt":
                    continue
                    
                file_path = os.path.join(output_dir, file_name)
                if os.path.isfile(file_path):
                    info = get_file_info(file_path)
                    if info:
                        files_info.append(info)
            
            if files_info:
                f.write("=== ARCHIVOS GENERADOS ===\n")
                for info in files_info:
                    f.write(f"- {info['name']}: {info['size_formatted']}\n")
                f.write("\n")
            
            # Información del sistema
            f.write("=== INFORMACIÓN DEL SISTEMA ===\n")
            f.write(f"Python: {sys.version}\n")
            f.write(f"Plataforma: {sys.platform}\n")
            f.write(f"Directorio de trabajo: {os.getcwd()}\n")
        
        logger.info(f"Resumen del proyecto creado: {summary_path}")
        return summary_path
        
    except Exception as e:
        logger.error(f"Error al crear resumen del proyecto: {e}")
        return None

class Timer:
    """Contexto para medir tiempo de ejecución"""
    
    def __init__(self, name="Operation"):
        self.name = name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        logger.info(f"Iniciando {self.name}...")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        logger.info(f"{self.name} completado en {duration:.2f} segundos")
        return False

def safe_remove(file_path):
    """Eliminar archivo de forma segura"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f"Archivo eliminado: {file_path}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error al eliminar {file_path}: {e}")
        return False

def get_available_space(directory):
    """Obtener espacio disponible en el directorio"""
    try:
        statvfs = os.statvfs(directory)
        available_bytes = statvfs.f_frsize * statvfs.f_bavail
        return available_bytes
    except Exception as e:
        logger.error(f"Error al obtener espacio disponible en {directory}: {e}")
        return 0

if __name__ == "__main__":
    # Pruebas de las funciones utilitarias
    print("Testing utility functions...")
    
    print(f"Time format: {format_time(3661)}")
    print(f"File size: {format_file_size(1048576)}")
    
    deps_ok, missing = check_dependencies()
    if deps_ok:
        print("✓ All dependencies available")
    else:
        print(f"✗ Missing dependencies: {missing}")
    
    print("Utils test completed.")