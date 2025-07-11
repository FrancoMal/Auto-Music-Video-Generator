# 🎵 Optimized Music Video Generator

A complete and optimized application for creating spectacular music videos with audio visualizations, leveraging modern hardware with GPU acceleration.

## 🌟 Key Features

### 🚀 **Performance Optimized**
- **GPU Acceleration**: NVIDIA GPU support with hardware H.264 encoding (NVENC)
- **Lightning Fast**: 1-2 minutes processing vs. hours with traditional methods
- **Memory Optimized**: Efficient RAM usage for parallel processing
- **Pure FFmpeg**: Eliminates frame-by-frame processing bottlenecks

### 🎨 **Advanced Visualizer**
- **Horizontal Mirror Effect**: Symmetric visualizer from center outward
- **Precise Positioning**: Pixel-perfect configuration from any edge
- **Customizable Colors**: 9 available colors with simple configuration
- **Full Width**: Spans entire screen width (1920px)

### 🎵 **Professional Audio**
- **Multiple Formats**: MP3, WAV, FLAC, M4A, OGG
- **High Quality**: 320kbps AAC output
- **Smart Combination**: Configurable repeat sequences
- **Automatic Analysis**: Description with timing for each song

### 🎬 **Quality Video**
- **Full HD Resolution**: 1920x1080 @ 30fps
- **High Bitrate**: 15M for maximum quality
- **Modern Codec**: H.264 with GPU acceleration
- **Optimized Size**: Perfect quality/size balance

## 📁 Project Structure

```
ACE-Proyect/
├── 🚀 MAIN SCRIPTS
│   ├── main_optimized.py              # 🎯 Optimized main script (USE THIS)
│   ├── main.py                        # Original script (slower)
│   └── video_generator_optimized.py   # GPU-accelerated generator
├── 📚 CORE MODULES
│   ├── audio_processor.py             # Audio processing and combination
│   ├── video_generator.py             # Original generator (OpenCV)
│   ├── visualizer_transparent.py      # Chroma key visualizer
│   ├── config.py                      # ⚙️ Centralized configuration
│   └── utils.py                       # Utility functions
├── 📂 WORKING DIRECTORIES
│   ├── musica/                        # 🎵 Place your songs here
│   │   ├── song1.mp3
│   │   ├── song2.mp3
│   │   └── ...
│   ├── recursos/                      # 🖼️ Background image
│   │   └── background.jpg             # Custom background image
│   ├── temp/                          # 📁 Temporary files (auto-cleanup)
│   └── output/                        # 📹 Final videos
│       ├── video_final.mp4            # Generated video
│       ├── descripcion.txt            # Timing for each song
│       └── app.log                    # Detailed log
├── 📖 DOCUMENTATION
│   ├── README.md                      # Spanish documentation
│   ├── README_EN.md                   # This English documentation
│   └── VISUALIZER_CONFIG_GUIDE.md     # Visualizer configuration guide
└── 🛠️ ENVIRONMENT
    └── .venv/                         # Python virtual environment
```

## 🚀 Installation and Setup

### System Requirements

**Recommended Hardware:**
- **GPU**: NVIDIA GPU with NVENC support (GTX 1660 or higher)
- **RAM**: 16GB or more (32GB recommended for large projects)
- **CPU**: Modern multi-core processor (Intel i5/AMD Ryzen 5 or higher)
- **Storage**: 10GB free space for temporary files

### 1. System Dependencies

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg python3-pip python3-venv

# macOS
brew install ffmpeg python3

# Windows
# Download ffmpeg from https://ffmpeg.org/download.html
# Install Python 3.8+ from python.org
```

### 2. Environment Setup

```bash
# Clone or download the project
cd ACE-Proyect

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# or on Windows: .venv\Scripts\activate

# Install dependencies
pip install librosa opencv-python pillow numpy pydub
```

### 3. GPU Verification

```bash
# Check GPU support in FFmpeg
ffmpeg -encoders | grep nvenc

# Should show:
# V..... h264_nvenc         NVIDIA NVENC H.264 encoder
```

## 📖 Usage Guide

### 🎯 Quick Start (Recommended)

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Place songs in the musica/ folder
cp your_songs/*.mp3 musica/

# 3. Run optimized version
python main_optimized.py

# 4. Find your video in output/video_final.mp4!
```

### 📝 Detailed Preparation

#### 1. **Audio Files**
```bash
# Place your songs in musica/
musica/
├── 01-song1.mp3
├── 02-song2.mp3
├── 03-song3.mp3
└── ...
```
- **Formats**: MP3, WAV, FLAC, M4A, OGG
- **Order**: Alphabetical by filename
- **Quantity**: 5-20 songs recommended

#### 2. **Background Image** (optional)
```bash
# Place your image in recursos/
cp my_image.jpg recursos/background.jpg
```
- **Formats**: JPG, PNG
- **Resolution**: Any (automatically resized)
- **If missing**: Default gradient background is generated

### 🚀 Execution

#### **Optimized Version** (Recommended)
```bash
# Basic - Uses all default settings
python main_optimized.py

# With options
python main_optimized.py --verbose                    # More details
python main_optimized.py --background my_image.jpg    # Custom image
python main_optimized.py --no-cleanup                 # Don't delete temp files
```

#### **Original Version** (Slower)
```bash
# Only if you need to use the original method
python main.py
```

### 📊 Results

Upon completion you'll get:
- **📹 Final video**: `output/video_final.mp4` (1-2GB approximately)
- **📄 Description**: `output/descripcion.txt` with timing for each song
- **📋 Log**: `output/app.log` with processing details
- **⏱️ Time**: 1-2 minutes with GPU, 10-30 minutes without GPU

## ⚙️ Advanced Configuration

### 🎨 Visualizer Configuration

Edit `config.py` to customize the visualizer:

```python
# Optimized visualizer configuration
VISUALIZER_OPTIMIZED_CONFIG = {
    "width": 1920,                    # Visualizer width
    "height": 200,                    # Visualizer height
    "position_from_bottom": 50,       # Position from bottom (pixels)
    "color": "red",                   # Visualizer color
    "mode": "cline",                  # Visualization mode
    "mirror_effect": True,            # Horizontal mirror effect
    "opacity": 1.0,                   # Opacity (0.0 to 1.0)
    "scale": 1.0                      # Visualizer scale
}
```

**Available Colors:**
`red`, `cyan`, `white`, `yellow`, `green`, `blue`, `magenta`, `orange`, `pink`

### 🎬 Video Configuration

```python
# Video quality and resolution
VIDEO_CONFIG = {
    "width": 1920,              # Video width
    "height": 1080,             # Video height
    "fps": 30,                  # Frames per second
    "bitrate": "5000k",         # Bitrate (original version)
    "audio_bitrate": "320k"     # Audio bitrate
}
```

### 🔄 Processing Configuration

```python
# Processing control
PROCESS_CONFIG = {
    "repeat_count": 1,                    # List repetitions
    "max_concurrent_processes": 4,        # Parallel processes
    "temp_cleanup": True,                 # Clean temporary files
    "supported_formats": ['.mp3', '.wav', '.flac', '.m4a', '.ogg']
}
```

## 🎮 Practical Examples

### 🎵 Example 1: Electronic Music Playlist

```bash
# 1. Organize songs
musica/
├── 01-intro.mp3
├── 02-drop.mp3
├── 03-buildup.mp3
└── 04-outro.mp3

# 2. Configure visualizer for electronic music
# In config.py:
VISUALIZER_OPTIMIZED_CONFIG = {
    "color": "cyan",
    "height": 250,
    "position_from_bottom": 100
}

# 3. Execute
python main_optimized.py --verbose
```

### 🎸 Example 2: Rock Mixtape

```bash
# 1. Configure visualizer for rock
# In config.py:
VISUALIZER_OPTIMIZED_CONFIG = {
    "color": "red",
    "height": 300,
    "mirror_effect": True
}

# 2. Use custom background image
cp album_cover.jpg recursos/background.jpg

# 3. Execute without cleaning temp files
python main_optimized.py --no-cleanup
```

### 🎻 Example 3: Classical Music

```bash
# 1. Configure elegant colors
# In config.py:
VISUALIZER_OPTIMIZED_CONFIG = {
    "color": "white",
    "height": 150,
    "position_from_bottom": 400,
    "mirror_effect": False
}

# 2. Execute
python main_optimized.py
```

## 🔧 Troubleshooting

### ❌ Common Errors

#### **Error: "ffmpeg not found"**
```bash
# Verify installation
ffmpeg -version

# If not installed:
sudo apt install ffmpeg  # Ubuntu/Debian
brew install ffmpeg       # macOS
```

#### **Error: "No audio files found"**
- ✅ Verify files are in `musica/`
- ✅ Check valid extensions: `.mp3`, `.wav`, `.flac`, `.m4a`, `.ogg`
- ✅ Check file read permissions

#### **Error: "GPU not available"**
- ✅ Verify updated NVIDIA drivers
- ✅ Check NVENC support: `ffmpeg -encoders | grep nvenc`
- ✅ System will continue on CPU (slower)

#### **Error: "Insufficient memory"**
```python
# Reduce parallel processes in config.py
PROCESS_CONFIG = {
    "max_concurrent_processes": 2  # Reduce from 4 to 2
}
```

### 🐛 Performance Issues

#### **Very slow processing**
- ✅ Use `main_optimized.py` instead of `main.py`
- ✅ Verify GPU is available
- ✅ Reduce resolution if necessary

#### **Final video too large**
```python
# Reduce bitrate in config.py
VIDEO_CONFIG = {
    "bitrate": "8000k"  # Reduce from 15M
}
```

### 📋 Diagnostics

#### **Check system configuration**
```bash
# System information
python main_optimized.py --verbose

# Check GPU
nvidia-smi  # NVIDIA systems only

# Check disk space
df -h
```

#### **Review logs**
```bash
# View complete log
cat output/app.log

# View errors only
grep ERROR output/app.log
```

## 📊 Technical Information

### 🔄 Optimized Process Flow

1. **🔍 Validation**: Verify files, dependencies, and hardware
2. **🎵 Audio Processing**: Combine songs using PyDub + FFmpeg
3. **🎨 Video Generation**: Create final video with integrated visualizer using FFmpeg + GPU
4. **🧹 Cleanup**: Remove temporary files automatically

### 🎬 Output Specifications

| Aspect | Optimized Version | Original Version |
|--------|-------------------|------------------|
| **Video Codec** | H.264 (GPU) | H.264 (CPU) |
| **Audio Codec** | AAC 320kbps | AAC 320kbps |
| **Resolution** | 1920x1080 @ 30fps | 1920x1080 @ 30fps |
| **Bitrate** | 15M (high quality) | 5M (standard) |
| **Time** | 1-2 minutes | 10-60 minutes |

### ⚡ Performance Comparison

| Metric | GPU (NVIDIA NVENC) | CPU Only |
|--------|-------------------|----------|
| **Time (10 songs)** | 1-2 minutes | 15-30 minutes |
| **Quality** | Maximum (15M) | Standard (5M) |
| **RAM Usage** | 4-8GB | 2-4GB |
| **Temperature** | GPU: 60-70°C | CPU: 70-80°C |

### 🏗️ System Architecture

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

### 🔧 Critical Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| **FFmpeg** | 6.1+ | Video/audio processing |
| **Python** | 3.8+ | Main runtime |
| **librosa** | 0.10+ | Audio analysis |
| **OpenCV** | 4.8+ | Image processing |
| **PyDub** | 0.25+ | Audio manipulation |
| **NumPy** | 1.20+ | Mathematical operations |

### 🎯 Implemented Optimizations

1. **🔥 GPU Acceleration**: NVENC for H.264 encoding
2. **⚡ Direct FFmpeg**: Eliminates frame-by-frame processing
3. **🔄 Complex Filters**: Integrated visualizer in single pass
4. **📊 Parallelism**: Multiple processes for audio
5. **🧠 Smart Caching**: Resource reuse

## 🎉 Expected Results

With GPU acceleration (NVIDIA NVENC supported GPU):
- **⏱️ Time**: 1-2 minutes for 10 songs
- **📈 Quality**: Maximum (15M bitrate, 1080p30)
- **🎨 Visualizer**: Horizontal mirror with configurable color
- **💾 Size**: 1-2GB per hour of final audio

Enjoy professional speed and quality! 🚀

## 📄 License

This project is provided as-is for educational and personal use.

## 🤝 Contributing

If you encounter issues or have suggestions:
1. **Review** `output/app.log` for details
2. **Verify** all dependencies are installed
3. **Check** input files are valid
4. **Use** `--verbose` for more information

---

*Made with ❤️ for the global music community*