"""
Multiple videos generator - extends the optimized generator for batch processing
"""

import os
import sys
import logging
import shutil
from datetime import datetime
from pathlib import Path

from audio_processor import AudioProcessor
from video_generator_optimized import OptimizedVideoGenerator
from config import (
    MUSICA_DIR, RECURSOS_DIR, TEMP_DIR, OUTPUT_DIR, 
    FILES_CONFIG, PROCESS_CONFIG, LOGGING_CONFIG, VISUALIZER_OPTIMIZED_CONFIG
)


class MultipleVideosGenerator:
    """Generator for creating multiple videos with different configurations"""
    
    def __init__(self, progress_callback=None):
        """
        Initialize the multiple videos generator
        
        Args:
            progress_callback: Function to call with progress updates
                              Should accept (video_number, progress_percent, message)
        """
        self.progress_callback = progress_callback
        self.audio_processor = AudioProcessor()
        self.video_generator = OptimizedVideoGenerator()
        self.cancelled = False
        
        # Setup logging
        self.logger = self._setup_logging()
        
    def _setup_logging(self):
        """Setup logging for multiple videos generation"""
        logger = logging.getLogger("MultipleVideosGenerator")
        
        # Create a specific log file for multiple videos
        log_file = os.path.join(OUTPUT_DIR, "multiple_videos.log")
        
        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(file_handler)
        logger.setLevel(logging.DEBUG)
        
        return logger
        
    def _report_progress(self, video_number, progress, message=""):
        """Report progress to callback and logger"""
        if self.progress_callback:
            self.progress_callback(video_number, progress, message)
        
        if message:
            self.logger.info(f"Video {video_number}: {message}")
            
    def cancel_generation(self):
        """Cancel the generation process"""
        self.cancelled = True
        self.logger.info("Generation cancelled by user")
        
    def generate_videos(self, video_configs):
        """
        Generate multiple videos based on configurations
        
        Args:
            video_configs: List of dictionaries with video configurations
                          Each dict should contain:
                          - video_number: int
                          - songs: list of song paths
                          - color: str (visualizer color)
                          - background_image: str (path to background image)
                          
        Returns:
            List of generated video paths (or None for failed videos)
        """
        try:
            self.logger.info("=== STARTING MULTIPLE VIDEOS GENERATION ===")
            self.logger.info(f"Total videos to generate: {len(video_configs)}")
            
            # Ensure output directory exists
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            
            generated_videos = []
            
            for i, config in enumerate(video_configs):
                if self.cancelled:
                    self.logger.info("Generation cancelled")
                    break
                    
                try:
                    video_path = self._generate_single_video(config)
                    generated_videos.append(video_path)
                    
                except Exception as e:
                    self.logger.error(f"Error generating video {config['video_number']}: {e}")
                    generated_videos.append(None)
                    
            self.logger.info("=== MULTIPLE VIDEOS GENERATION COMPLETED ===")
            return generated_videos
            
        except Exception as e:
            self.logger.error(f"Critical error in multiple videos generation: {e}")
            raise
            
    def _generate_single_video(self, config):
        """
        Generate a single video with the given configuration
        
        Args:
            config: Dictionary with video configuration
            
        Returns:
            Path to generated video file
        """
        video_number = config['video_number']
        songs = config['songs']
        color = config['color']
        background_image = config.get('background_image', '')
        
        self.logger.info(f"--- STARTING VIDEO {video_number} ---")
        self.logger.info(f"Songs: {[os.path.basename(s) for s in songs]}")
        self.logger.info(f"Color: {color}")
        self.logger.info(f"Background: {os.path.basename(background_image) if background_image else 'Default'}")
        
        # Create temp directory for this video
        video_temp_dir = os.path.join(TEMP_DIR, f"video_{video_number}")
        os.makedirs(video_temp_dir, exist_ok=True)
        
        try:
            # Step 1: Process audio (combine songs)
            self._report_progress(video_number, 10, "Procesando audio...")
            combined_audio_path = self._process_audio(songs, video_temp_dir, video_number)
            
            if self.cancelled:
                return None
                
            # Step 2: Prepare visualizer configuration
            self._report_progress(video_number, 30, "Configurando visualizador...")
            original_config = self._backup_visualizer_config()
            self._update_visualizer_config(color)
            
            # Step 3: Prepare background image
            self._report_progress(video_number, 50, "Preparando imagen de fondo...")
            background_path = self._prepare_background_image(background_image, video_temp_dir)
            
            # Step 4: Generate final video using the SAME method as main_optimized.py
            self._report_progress(video_number, 70, "Generando video con visualizador optimizado...")
            output_path = os.path.join(OUTPUT_DIR, f"video_{video_number}.mp4")
            
            # Use the exact same method that works in main_optimized.py
            success = self.video_generator.create_simple_music_video(
                combined_audio_path,
                background_path,
                output_path
            )
            
            if not success:
                raise Exception("Video generation failed")
                
            self._report_progress(video_number, 95, "Finalizando...")
            
            # Step 5: Generate description file
            self._generate_description_file(songs, video_number)
            
            # Restore original configuration
            self._restore_visualizer_config(original_config)
            
            # Cleanup temp directory for this video
            if PROCESS_CONFIG.get('temp_cleanup', True):
                shutil.rmtree(video_temp_dir, ignore_errors=True)
                
            self._report_progress(video_number, 100, "Completado")
            self.logger.info(f"✅ Video {video_number} generated successfully: {output_path}")
            
            return output_path
            
        except Exception as e:
            # Restore configuration in case of error
            if 'original_config' in locals():
                self._restore_visualizer_config(original_config)
                
            # Cleanup temp directory
            if os.path.exists(video_temp_dir):
                shutil.rmtree(video_temp_dir, ignore_errors=True)
                
            raise e
            
    def _process_audio(self, songs, temp_dir, video_number):
        """Process and combine audio files for a single video"""
        if not songs:
            raise Exception("No songs provided for video")
            
        # Set temporary output path for combined audio
        combined_audio_path = os.path.join(temp_dir, f"combined_audio_{video_number}.mp3")
        
        # Use the existing audio processor but override the output path
        original_output = FILES_CONFIG['combined_audio']
        FILES_CONFIG['combined_audio'] = combined_audio_path
        
        try:
            # Create a temporary list of songs for this video
            temp_music_dir = os.path.join(temp_dir, "temp_music")
            os.makedirs(temp_music_dir, exist_ok=True)
            
            # Copy songs to temp directory (for AudioProcessor to find them)
            for i, song_path in enumerate(songs):
                song_name = f"{i:03d}_{os.path.basename(song_path)}"
                temp_song_path = os.path.join(temp_music_dir, song_name)
                shutil.copy2(song_path, temp_song_path)
            
            # Temporarily override music directory
            original_music_dir = self.audio_processor.music_dir if hasattr(self.audio_processor, 'music_dir') else MUSICA_DIR
            
            # Create a custom audio processor for this video
            from audio_processor import AudioProcessor
            custom_processor = AudioProcessor()
            
            # Override the get_audio_files method to return our specific songs
            def get_custom_audio_files(self=None):
                return songs
                
            custom_processor.get_audio_files = get_custom_audio_files
            
            # Process audio
            result_path, desc_path = custom_processor.process_audio()
            
            if not result_path or not os.path.exists(result_path):
                raise Exception("Audio processing failed")
                
            return result_path
            
        finally:
            # Restore original configuration
            FILES_CONFIG['combined_audio'] = original_output
            
            # Cleanup temp music directory
            if os.path.exists(temp_music_dir):
                shutil.rmtree(temp_music_dir, ignore_errors=True)
                
    def _backup_visualizer_config(self):
        """Backup current visualizer configuration"""
        return VISUALIZER_OPTIMIZED_CONFIG.copy()
        
    def _update_visualizer_config(self, color):
        """Update visualizer configuration with new color for optimized visualizer"""
        # The optimized visualizer uses color names directly
        VISUALIZER_OPTIMIZED_CONFIG['color'] = color
        
    def _restore_visualizer_config(self, original_config):
        """Restore original visualizer configuration"""
        VISUALIZER_OPTIMIZED_CONFIG.update(original_config)
        
    def _prepare_background_image(self, background_image, temp_dir):
        """Prepare background image for video generation"""
        if not background_image or not os.path.exists(background_image):
            # Use default background from recursos
            from config import get_background_image_path
            return get_background_image_path()
            
        return background_image
        
    def _generate_description_file(self, songs, video_number):
        """Generate description file for the video"""
        desc_path = os.path.join(OUTPUT_DIR, f"video_{video_number}_descripcion.txt")
        
        try:
            # Get unique songs and detect repetitions
            unique_songs = []
            song_counts = {}
            
            for song_path in songs:
                song_name = os.path.basename(song_path)
                if song_name not in song_counts:
                    song_counts[song_name] = 0
                    unique_songs.append(song_path)
                song_counts[song_name] += 1
            
            # Calculate repetitions (assuming all songs have same count)
            repetitions_count = max(song_counts.values()) if song_counts else 1
            
            with open(desc_path, 'w', encoding='utf-8') as f:
                f.write(f"Descripción del Video {video_number}\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Canciones únicas: {len(unique_songs)}\n")
                f.write(f"Repeticiones: {repetitions_count - 1} (se reproduce {repetitions_count} veces cada canción)\n")
                f.write(f"Total de reproducciones: {len(songs)}\n\n")
                
                f.write("Canciones únicas:\n")
                for i, song_path in enumerate(unique_songs, 1):
                    song_name = os.path.basename(song_path)
                    f.write(f"{i:2d}. {song_name} (se reproduce {song_counts[song_name]} veces)\n")
                    
                f.write(f"\nSecuencia completa:\n")
                for i, song_path in enumerate(songs, 1):
                    song_name = os.path.basename(song_path)
                    f.write(f"{i:2d}. {song_name}\n")
                    
        except Exception as e:
            self.logger.warning(f"Could not generate description file: {e}")
            
    def validate_configurations(self, video_configs):
        """
        Validate video configurations before generation
        
        Args:
            video_configs: List of video configurations
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not video_configs:
            return False, "No video configurations provided"
            
        for config in video_configs:
            # Check required fields
            required_fields = ['video_number', 'songs', 'color']
            for field in required_fields:
                if field not in config:
                    return False, f"Missing required field '{field}' in video {config.get('video_number', '?')}"
                    
            # Check songs exist
            if not config['songs']:
                return False, f"No songs provided for video {config['video_number']}"
                
            for song_path in config['songs']:
                if not os.path.exists(song_path):
                    return False, f"Song file not found: {song_path}"
                    
            # Check background image if provided
            background = config.get('background_image')
            if background and not os.path.exists(background):
                return False, f"Background image not found: {background}"
                
        return True, "Configuration is valid"