# 🎵 Generador de Videos Musicales Optimizado

Una aplicación completa y optimizada para crear videos musicales con visualizaciones de audio espectaculares, aprovechando al máximo hardware moderno con aceleración GPU.

## 🌟 Características Principales

### 🚀 **Rendimiento Optimizado**
- **Aceleración GPU**: Soporte para GPUs NVIDIA con codificación H.264 por hardware (NVENC)
- **Procesamiento rápido**: 1-2 minutos de procesamiento vs. horas del método tradicional
- **Memoria optimizada**: Uso eficiente de RAM para procesamiento paralelo
- **FFmpeg puro**: Elimina bottlenecks de procesamiento frame-by-frame

### 🎨 **Visualizador Avanzado**
- **Efecto espejo horizontal**: Visualizador simétrico desde el centro hacia afuera
- **Posicionamiento preciso**: Configurable a pixels exactos desde cualquier borde
- **Colores personalizables**: 9 colores disponibles con configuración simple
- **Ancho completo**: Se extiende por toda la pantalla (1920px)

### 🎵 **Audio Profesional**
- **Múltiples formatos**: MP3, WAV, FLAC, M4A, OGG
- **Calidad alta**: 320kbps AAC de salida
- **Combinación inteligente**: Secuencias repetidas configurables
- **Análisis automático**: Descripción con tiempos de cada canción

### 🎬 **Video de Calidad**
- **Resolución Full HD**: 1920x1080 @ 30fps
- **Bitrate alto**: 15M para máxima calidad
- **Codec moderno**: H.264 con aceleración GPU
- **Tamaño optimizado**: Balance perfecto calidad/tamaño

## 📁 Estructura del Proyecto

```
ACE-Proyect/
├── 🚀 SCRIPTS PRINCIPALES
│   ├── main_optimized.py              # 🎯 Script principal optimizado (USAR ESTE)
│   ├── main.py                        # Script original (más lento)
│   └── video_generator_optimized.py   # Generador con aceleración GPU
├── 📚 MÓDULOS CORE
│   ├── audio_processor.py             # Procesamiento y combinación de audio
│   ├── video_generator.py             # Generador original (OpenCV)
│   ├── visualizer_transparent.py      # Visualizador con chroma key
│   ├── config.py                      # ⚙️ Configuraciones centralizadas
│   └── utils.py                       # Funciones auxiliares
├── 📂 DIRECTORIOS DE TRABAJO
│   ├── musica/                        # 🎵 Coloca aquí tus canciones
│   │   ├── cancion1.mp3
│   │   ├── cancion2.mp3
│   │   └── ...
│   ├── recursos/                      # 🖼️ Imagen de fondo
│   │   └── background.jpg             # Imagen de fondo personalizada
│   ├── temp/                          # 📁 Archivos temporales (auto-limpieza)
│   └── output/                        # 📹 Videos finales
│       ├── video_final.mp4            # Video generado
│       ├── descripcion.txt            # Tiempos de cada canción
│       └── app.log                    # Log detallado
├── 📖 DOCUMENTACIÓN
│   ├── README.md                      # Esta documentación
│   └── VISUALIZER_CONFIG_GUIDE.md     # Guía de configuración del visualizador
└── 🛠️ AMBIENTE
    └── .venv/                         # Entorno virtual Python
```

## 🚀 Instalación y Configuración

### Requisitos del Sistema

**Hardware Recomendado:**
- **GPU**: GPU NVIDIA con soporte NVENC (recomendada para máximo rendimiento)
- **RAM**: 16GB o más (32GB recomendado para proyectos grandes)
- **CPU**: Procesador multi-core moderno (Intel i5/AMD Ryzen 5 o superior)
- **Almacenamiento**: 10GB libres para archivos temporales

### 1. Dependencias del Sistema

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg python3-pip python3-venv

# macOS
brew install ffmpeg python3

# Windows
# Descargar ffmpeg desde https://ffmpeg.org/download.html
# Instalar Python 3.8+ desde python.org
```

### 2. Configuración del Entorno

```bash
# Clonar o descargar el proyecto
cd ACE-Proyect

# Crear entorno virtual
python3 -m venv .venv

# Activar entorno virtual
source .venv/bin/activate  # Linux/macOS
# o en Windows: .venv\Scripts\activate

# Instalar dependencias
pip install librosa opencv-python pillow numpy pydub
```

### 3. Verificación de GPU

```bash
# Verificar soporte GPU en FFmpeg
ffmpeg -encoders | grep nvenc

# Debería mostrar:
# V..... h264_nvenc         NVIDIA NVENC H.264 encoder
```

## 📖 Guía de Uso

### 🎯 Inicio Rápido (Recomendado)

```bash
# 1. Activar entorno virtual
source .venv/bin/activate

# 2. Colocar canciones en la carpeta musica/
cp tus_canciones/*.mp3 musica/

# 3. Ejecutar versión optimizada
python main_optimized.py

# 4. ¡Encuentra tu video en output/video_final.mp4!
```

### 📝 Preparación Detallada

#### 1. **Archivos de Audio**
```bash
# Coloca tus canciones en musica/
musica/
├── 01-cancion1.mp3
├── 02-cancion2.mp3
├── 03-cancion3.mp3
└── ...
```
- **Formatos**: MP3, WAV, FLAC, M4A, OGG
- **Orden**: Alfabético por nombre de archivo
- **Cantidad**: 5-20 canciones recomendadas

#### 2. **Imagen de Fondo** (opcional)
```bash
# Coloca tu imagen en recursos/
cp mi_imagen.jpg recursos/background.jpg
```
- **Formatos**: JPG, PNG
- **Resolución**: Cualquiera (se redimensiona automáticamente)
- **Si no existe**: Se genera un fondo degradado por defecto

### 🚀 Ejecución

#### **Versión Optimizada** (Recomendada)
```bash
# Básico - Usa todas las configuraciones por defecto
python main_optimized.py

# Con opciones
python main_optimized.py --verbose                    # Más detalles
python main_optimized.py --background mi_imagen.jpg   # Imagen personalizada
python main_optimized.py --no-cleanup                 # No borrar archivos temporales
```

#### **Versión Original** (Más lenta)
```bash
# Solo si necesitas usar el método original
python main.py
```

### 📊 Resultados

Al finalizar obtendrás:
- **📹 Video final**: `output/video_final.mp4` (1-2GB aproximadamente)
- **📄 Descripción**: `output/descripcion.txt` con tiempos de cada canción
- **📋 Log**: `output/app.log` con detalles del procesamiento
- **⏱️ Tiempo**: 1-2 minutos con GPU, 10-30 minutos sin GPU

## ⚙️ Configuración Avanzada

### 🎨 Configuración del Visualizador

Edita `config.py` para personalizar el visualizador:

```python
# Configuración del visualizador optimizado
VISUALIZER_OPTIMIZED_CONFIG = {
    "width": 1920,                    # Ancho del visualizador
    "height": 200,                    # Alto del visualizador
    "position_from_bottom": 300,      # Posición desde abajo (pixels)
    "color": "red",                   # Color del visualizador
    "mode": "cline",                  # Modo de visualización
    "mirror_effect": True,            # Efecto espejo horizontal
    "opacity": 1.0,                   # Opacidad (0.0 a 1.0)
    "scale": 1.0                      # Escala del visualizador
}
```

**Colores Disponibles:**
`red`, `cyan`, `white`, `yellow`, `green`, `blue`, `magenta`, `orange`, `pink`

### 🎬 Configuración de Video

```python
# Calidad y resolución del video
VIDEO_CONFIG = {
    "width": 1920,              # Ancho del video
    "height": 1080,             # Alto del video
    "fps": 30,                  # Frames por segundo
    "bitrate": "5000k",         # Bitrate (versión original)
    "audio_bitrate": "320k"     # Bitrate de audio
}
```

### 🔄 Configuración de Procesamiento

```python
# Control del procesamiento
PROCESS_CONFIG = {
    "repeat_count": 1,                    # Repeticiones de la lista
    "max_concurrent_processes": 4,        # Procesos paralelos
    "temp_cleanup": True,                 # Limpiar archivos temporales
    "supported_formats": ['.mp3', '.wav', '.flac', '.m4a', '.ogg']
}
```

### 📁 Configuración de Archivos

```python
# Ubicaciones de archivos
FILES_CONFIG = {
    "background_image": "recursos/background.jpg",
    "final_video": "output/video_final.mp4",
    "description_file": "output/descripcion.txt"
}
```

Para más detalles, consulta: **[VISUALIZER_CONFIG_GUIDE.md](VISUALIZER_CONFIG_GUIDE.md)**

## 🎮 Ejemplos Prácticos

### 🎵 Ejemplo 1: Playlist de Música Electrónica

```bash
# 1. Organizar canciones
musica/
├── 01-intro.mp3
├── 02-drop.mp3
├── 03-buildup.mp3
└── 04-outro.mp3

# 2. Configurar visualizador para música electrónica
# En config.py:
VISUALIZER_OPTIMIZED_CONFIG = {
    "color": "cyan",
    "height": 250,
    "position_from_bottom": 200
}

# 3. Ejecutar
python main_optimized.py --verbose
```

### 🎸 Ejemplo 2: Mixtape de Rock

```bash
# 1. Configurar visualizador para rock
# En config.py:
VISUALIZER_OPTIMIZED_CONFIG = {
    "color": "red",
    "height": 300,
    "mirror_effect": True
}

# 2. Usar imagen de fondo personalizada
cp portada_album.jpg recursos/background.jpg

# 3. Ejecutar sin limpiar archivos temporales
python main_optimized.py --no-cleanup
```

### 🎻 Ejemplo 3: Música Clásica

```bash
# 1. Configurar colores elegantes
# En config.py:
VISUALIZER_OPTIMIZED_CONFIG = {
    "color": "white",
    "height": 150,
    "position_from_bottom": 400,
    "mirror_effect": False
}

# 2. Ejecutar
python main_optimized.py
```

### 🎤 Ejemplo 4: Personalización Avanzada

```bash
# 1. Configurar múltiples aspectos
# En config.py:
VISUALIZER_OPTIMIZED_CONFIG = {
    "width": 1920,
    "height": 180,
    "position_from_bottom": 320,
    "color": "magenta",
    "mode": "cline",
    "opacity": 0.9,
    "scale": 1.2
}

# 2. Configurar menos repeticiones
PROCESS_CONFIG = {
    "repeat_count": 1
}

# 3. Ejecutar
python main_optimized.py --verbose
```

## 🔧 Solución de Problemas

### ❌ Errores Comunes

#### **Error: "ffmpeg not found"**
```bash
# Verificar instalación
ffmpeg -version

# Si no está instalado:
sudo apt install ffmpeg  # Ubuntu/Debian
brew install ffmpeg       # macOS
```

#### **Error: "No se encontraron archivos de audio"**
- ✅ Verificar que los archivos estén en `musica/`
- ✅ Confirmar extensiones válidas: `.mp3`, `.wav`, `.flac`, `.m4a`, `.ogg`
- ✅ Revisar permisos de lectura en los archivos

#### **Error: "GPU no disponible"**
- ✅ Verificar drivers NVIDIA actualizados
- ✅ Comprobar soporte NVENC: `ffmpeg -encoders | grep nvenc`
- ✅ El sistema seguirá funcionando en CPU (más lento)

#### **Error: "Memoria insuficiente"**
```python
# Reducir procesos paralelos en config.py
PROCESS_CONFIG = {
    "max_concurrent_processes": 2  # Reducir de 4 a 2
}
```

### 🐛 Problemas de Rendimiento

#### **Procesamiento muy lento**
- ✅ Usar `main_optimized.py` en lugar de `main.py`
- ✅ Verificar que GPU esté disponible
- ✅ Reducir resolución si es necesario

#### **Video final con tamaño muy grande**
```python
# Reducir bitrate en config.py
VIDEO_CONFIG = {
    "bitrate": "8000k"  # Reducir de 15M
}
```

### 📋 Diagnóstico

#### **Verificar configuración del sistema**
```bash
# Información del sistema
python main_optimized.py --verbose

# Verificar GPU
nvidia-smi  # Solo en sistemas con NVIDIA

# Verificar espacio en disco
df -h
```

#### **Revisar logs**
```bash
# Ver log completo
cat output/app.log

# Ver solo errores
grep ERROR output/app.log
```

### 🆘 Soporte

Si persisten los problemas:
1. **Revisar** `output/app.log` para detalles
2. **Verificar** que todas las dependencias estén instaladas
3. **Comprobar** que los archivos de entrada sean válidos
4. **Usar** `--verbose` para más información

## 📊 Información Técnica

### 🔄 Flujo del Proceso Optimizado

1. **🔍 Validación**: Verifica archivos, dependencias y hardware
2. **🎵 Procesamiento Audio**: Combina canciones usando PyDub + FFmpeg
3. **🎨 Generación Video**: Crea video final con visualizador integrado usando FFmpeg + GPU
4. **🧹 Limpieza**: Elimina archivos temporales automáticamente

### 🎬 Especificaciones de Salida

| Aspecto | Versión Optimizada | Versión Original |
|---------|-------------------|------------------|
| **Codec Video** | H.264 (GPU) | H.264 (CPU) |
| **Codec Audio** | AAC 320kbps | AAC 320kbps |
| **Resolución** | 1920x1080 @ 30fps | 1920x1080 @ 30fps |
| **Bitrate** | 15M (alta calidad) | 5M (estándar) |
| **Tiempo** | 1-2 minutos | 10-60 minutos |

### ⚡ Rendimiento Comparativo

| Métrica | GPU (NVIDIA con NVENC) | CPU (moderno) |
|---------|-------------------|-------------------|
| **Tiempo (10 canciones)** | 1-2 minutos | 15-30 minutos |
| **Calidad** | Máxima (15M) | Estándar (5M) |
| **Uso RAM** | 4-8GB | 2-4GB |
| **Temperatura** | GPU: 60-70°C | CPU: 70-80°C |

### 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Audio Input   │    │   Background    │    │   Final Video   │
│   (MP3, WAV)    │    │   (JPG, PNG)    │    │   (MP4, H.264)  │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  PyDub + FFmpeg │    │  Image Scaling  │    │  GPU Encoding   │
│  (Combination)  │    │   (FFmpeg)      │    │   (NVENC)       │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────┬───────────┘                      │
                     ▼                                  │
            ┌─────────────────┐                         │
            │ Visualizer Gen  │                         │
            │ (FFmpeg Filter) │                         │
            └─────────┬───────┘                         │
                      │                                 │
                      └─────────────────────────────────┘
```

### 🔧 Dependencias Críticas

| Dependencia | Versión | Propósito |
|-------------|---------|-----------|
| **FFmpeg** | 6.1+ | Procesamiento de video/audio |
| **Python** | 3.8+ | Runtime principal |
| **librosa** | 0.10+ | Análisis de audio |
| **OpenCV** | 4.8+ | Procesamiento de imágenes |
| **PyDub** | 0.25+ | Manipulación de audio |
| **NumPy** | 1.20+ | Operaciones matemáticas |

### 💾 Gestión de Memoria

- **RAM Uso**: 4-8GB durante procesamiento
- **Almacenamiento Temporal**: 2-5GB
- **Salida Final**: 500MB-2GB por hora de audio
- **Limpieza**: Automática al completar

### 🎯 Optimizaciones Implementadas

1. **🔥 Aceleración GPU**: NVENC para codificación H.264
2. **⚡ FFmpeg Directo**: Elimina procesamiento frame-by-frame
3. **🔄 Filtros Complejos**: Visualizador integrado en una sola pasada
4. **📊 Paralelismo**: Múltiples procesos para audio
5. **🧠 Caché Inteligente**: Reutilización de recursos

## 🎉 Resultados Esperados

Con el setup recomendado (GPU NVIDIA + 32GB RAM + CPU moderno):
- **⏱️ Tiempo**: 1-2 minutos para 10 canciones
- **📈 Calidad**: Máxima (15M bitrate, 1080p30)
- **🎨 Visualizador**: Espejo horizontal con color configurable
- **💾 Tamaño**: 1-2GB por hora de audio final

¡Disfruta de la velocidad y calidad profesional! 🚀