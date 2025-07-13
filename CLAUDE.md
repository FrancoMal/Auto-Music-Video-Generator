# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Start Commands

### Run the Application
```bash
# Single video (optimized version) - GPU accelerated
python main_optimized.py

# Single video (original version) - slower, CPU only
python main.py

# Multiple videos with GUI interface
python multiple_videos_gui.py

# With options
python main_optimized.py --verbose --no-cleanup
```

### Dependencies
```bash
# Install required Python packages for video generation
pip install librosa opencv-python pillow numpy pydub PySide6

# Install YouTube API dependencies (for upload functionality)
pip install pytz google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

# System dependency - FFmpeg is required
# Ubuntu/Debian: sudo apt install ffmpeg
# macOS: brew install ffmpeg
# Windows: Download from https://ffmpeg.org/
```

### Testing
```bash
# Test YouTube integration (mock mode - no API calls)
python test_youtube_integration.py

# Test YouTube scheduling functionality
python test_scheduling.py

# Test improved YouTube upload workflow
python test_upload_workflow.py

# Test multiple videos system components
python test_corrections.py

# Test quick single video generation
python test_quick_video.py

# Test complete multiple videos workflow
python test_complete_fix.py
```

## Architecture Overview

This is a Python-based music video generator that creates visualized videos from audio files with GPU acceleration support.

### Core Components

1. **Main Entry Points**:
   - `main_optimized.py` - GPU-accelerated single video using FFmpeg directly (recommended)
   - `main.py` - Original single video using OpenCV frame-by-frame processing (slower)
   - `multiple_videos_gui.py` - GUI for generating multiple videos with different configurations

2. **Audio Processing** (`audio_processor.py`):
   - Combines multiple audio files from `musica/` directory 
   - Supports MP3, WAV, FLAC, M4A, OGG formats
   - Generates timing descriptions for each track

3. **Video Generation**:
   - `video_generator_optimized.py` - GPU-accelerated using FFmpeg with NVENC
   - `video_generator.py` - Original OpenCV-based implementation
   - Creates 1920x1080 @ 30fps videos with integrated audio visualizer

4. **Visualizer** (`visualizer_transparent.py`):
   - Creates audio-reactive visualizations using chroma key
   - Supports horizontal mirror effects
   - Configurable colors and positioning

5. **Configuration** (`config.py`):
   - Centralized configuration for all components
   - Video settings, visualizer options, file paths, processing options

6. **Multiple Videos System**:
   - `multiple_videos_generator.py` - Logic for generating multiple videos with individual configurations
   - `gui_components/` - Reusable GUI components (video config widgets, progress dialogs, image previews)
   - Supports individual repetitions, colors, and background images per video

7. **YouTube Upload Integration**:
   - `youtube_uploader.py` - YouTube API wrapper with quota management and mock mode for testing
   - `auth.py` - OAuth2 authentication for YouTube API
   - `gui_components/youtube_config_dialog.py` - Configuration dialog with scheduling support
   - `youtube_scheduled_uploader.py` - Script for executing scheduled uploads
   - Two upload modes: Immediate (Generate→Upload→Delete) and Scheduled (Generate→Schedule→Upload later)
   - Calendar-based scheduling with custom times and preview functionality
   - Automatic quota management (6 videos/day limit for unverified apps)

### Data Flow

**Single Video Mode:**
1. Audio files from `musica/` → Combined into single track → Audio analysis
2. Background image from `recursos/` → Processed for video background
3. Audio data → Visualizer → Final MP4 video in `output/`

**Multiple Videos Mode:**
1. Audio files assigned per video with individual repetitions
2. Each video gets unique songs, colors, and background images
3. Each video processed independently with OptimizedVideoGenerator.create_simple_music_video()
4. Multiple MP4 files generated in `output/` (video_1.mp4, video_2.mp4, etc.)

**Multiple Videos + YouTube Mode:**

*Immediate Upload:*
1. Same as Multiple Videos Mode for generation
2. Each video immediately uploaded to YouTube after generation
3. Local video file deleted after successful upload (keeps logs)
4. Automatic quota management with 24.5h cooldown when limit reached
5. Process stops on upload failure

*Scheduled Upload:*
1. Generate video → Upload with `publish_at` (YouTube handles scheduling) → Delete local file
2. Repeat for each video with individual scheduled times
3. Videos upload immediately but publish at scheduled time
4. Detailed logging to `output/youtube_uploads.log` and `output/youtube_uploads_detailed.json`
5. Process stops on upload failure

### Key Configuration Areas

- **VISUALIZER_OPTIMIZED_CONFIG**: Colors, positioning, effects for audio visualizer
- **VIDEO_CONFIG**: Resolution, codecs, bitrates
- **PROCESS_CONFIG**: Parallel processing, cleanup options
- **FILES_CONFIG**: Input/output paths

### Performance Characteristics

- **Optimized version**: 1-2 minutes processing time with NVIDIA GPU (NVENC)
- **Original version**: 10-60 minutes processing time (CPU only)
- **Memory usage**: 4-8GB RAM during processing
- **Output**: 1-2GB per hour of final audio

### Directory Structure

```
musica/          # Input audio files (MP3, WAV, FLAC, M4A, OGG)
recursos/        # Background images (PNG, JPG, JPEG)
temp/            # Temporary processing files (auto-cleaned)
output/          # Final videos and logs
  ├── video_final.mp4        # Single video mode output
  ├── video_1.mp4           # Multiple videos mode outputs
  ├── video_2.mp4
  ├── video_N.mp4
  ├── video_N_descripcion.txt  # Individual video descriptions
  ├── descripcion.txt       # Single video description
  ├── app.log              # Single video processing logs
  ├── multiple_videos.log  # Multiple videos processing logs
  ├── youtube_uploads.log  # YouTube upload logs (text format)
  └── youtube_uploads_detailed.json  # Detailed upload logs (JSON format)
gui_components/  # GUI components for multiple videos interface
  ├── video_config_widget.py     # Individual video configuration widget
  ├── progress_dialog.py         # Progress tracking with logs and time estimation
  ├── image_preview_widget.py    # Background image selection with preview
  └── youtube_config_dialog.py   # YouTube upload configuration dialog
client_secret.json  # YouTube API credentials (user must provide)
token.pickle        # YouTube authentication token (auto-generated)
auth.py            # YouTube OAuth2 authentication
upload_video.py    # Legacy upload functions
youtube_uploader.py # Modern YouTube API wrapper
```

### GPU Acceleration

The optimized version requires:
- NVIDIA GPU with NVENC support (GTX 1660 or higher recommended)
- FFmpeg compiled with NVENC support
- Check with: `ffmpeg -encoders | grep nvenc`

### YouTube Integration Setup

For YouTube upload functionality:

1. **Create Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable YouTube Data API v3

2. **Create OAuth2 Credentials**:
   - Go to APIs & Credentials → Credentials
   - Create OAuth 2.0 Client ID (Desktop Application)
   - Download the JSON file as `client_secret.json`

3. **Important Notes**:
   - Unverified apps have a 6 videos/day quota limit
   - First authentication opens browser for OAuth consent
   - `token.pickle` stores auth tokens (don't commit to git)
   - Upload failure stops the entire process to prevent data loss

### YouTube Upload Modes

**Immediate Upload Mode:**
- Videos upload immediately after generation
- Files deleted after successful upload
- Real-time quota management

**Scheduled Upload Mode:**
- Videos upload immediately but publish at scheduled time
- Uses YouTube API's `publish_at` parameter
- Calendar-based scheduling with custom times per day
- Videos remain private until scheduled publish time
- Comprehensive logging with duration and timing details

### Upload Logs

The system creates detailed logs of all uploads:

- `output/youtube_uploads.log` - Human-readable text log
- `output/youtube_uploads_detailed.json` - Structured JSON log with:
  - Video title and YouTube ID
  - File size and estimated duration
  - Upload time and scheduled publish time
  - Upload status and any errors

### Common Patterns

- All processing uses centralized logging to `output/app.log` (single video) or `output/multiple_videos.log` (multiple videos)
- Parallel processing configurable via `PROCESS_CONFIG['max_concurrent_processes']`
- Temporary files auto-cleaned unless `--no-cleanup` specified
- Background image auto-detected from `recursos/` with PNG/JPG/JPEG extensions

## Multiple Videos Feature

### Key Features

- **GUI Interface**: Intuitive PySide6-based interface for configuring multiple videos
- **Individual Configuration**: Each video can have different songs, repetitions, colors, and background images
- **Flexible Repetitions**: 0 repetitions (play once) to N repetitions per video
- **Auto Song Assignment**: Automatic distribution of songs from `musica/` directory in alphabetical order
- **Real-time Progress**: Live progress tracking with time estimation and detailed logs
- **GPU Accelerated**: Uses the same optimized `create_simple_music_video()` method as `main_optimized.py`

### Multiple Videos Workflow

1. **Launch GUI**: `python multiple_videos_gui.py`
2. **Configure Videos**: Set number of videos, songs per video, repetitions
3. **Individual Settings**: For each video, configure:
   - Number of songs (can be different per video)
   - Individual repetitions (overrides global setting)
   - Visualizer color (red, cyan, white, yellow, green, blue, magenta, orange, pink)
   - Background image (with preview)
4. **Preview Assignment**: Interface shows which songs are assigned to each video
5. **Generate**: Click "Generar Videos" to start batch processing
6. **Monitor Progress**: Real-time progress dialog with logs and time estimation

### Critical Implementation Details

**Important**: Multiple videos system uses `OptimizedVideoGenerator.create_simple_music_video()` method, NOT `generate_final_video_optimized()`. This ensures the visualizer appears correctly with waves and horizontal mirror effect, exactly like the single video mode.

**Repetitions Logic**: 
- `0 repetitions` = Play songs once (no repeating)
- `1 repetition` = Play songs twice total (original + 1 repeat)
- `N repetitions` = Play songs N+1 times total

**Song Assignment**: Songs are assigned sequentially from `musica/` directory in alphabetical order, then each video applies its own repetition pattern to its assigned songs.

### Testing

```bash
# Test multiple videos system components
python test_corrections.py

# Test quick single video generation
python test_quick_video.py

# Test complete multiple videos workflow
python test_complete_fix.py
```