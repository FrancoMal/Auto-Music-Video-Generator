"""
Multiple videos generator - extends the optimized generator for batch processing
"""

import os
import sys
import json
import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from audio_processor import AudioProcessor
from video_generator_optimized import OptimizedVideoGenerator
from youtube_uploader import YouTubeUploader, format_time_remaining
from config import (
    MUSICA_DIR, RECURSOS_DIR, TEMP_DIR, OUTPUT_DIR, 
    FILES_CONFIG, PROCESS_CONFIG, LOGGING_CONFIG, VISUALIZER_OPTIMIZED_CONFIG
)


class MultipleVideosGenerator:
    """Generator for creating multiple videos with different configurations"""
    
    def __init__(self, progress_callback=None, youtube_config=None, individual_metadata=None):
        """
        Initialize the multiple videos generator
        
        Args:
            progress_callback: Function to call with progress updates
                              Should accept (video_number, progress_percent, message)
            youtube_config: Optional YouTube configuration for upload
            individual_metadata: Optional list of individual metadata for each video
        """
        self.progress_callback = progress_callback
        self.youtube_config = youtube_config
        self.individual_metadata = individual_metadata or []
        self.audio_processor = AudioProcessor()
        self.video_generator = OptimizedVideoGenerator()
        self.cancelled = False
        
        # YouTube uploader (if needed)
        self.youtube_uploader = youtube_config.get('uploader') if youtube_config else None
        
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
            if self.youtube_config:
                self.logger.info("=== STARTING MULTIPLE VIDEOS GENERATION WITH YOUTUBE UPLOAD ===")
                self.logger.info(f"Total videos to process: {len(video_configs)}")
                self.logger.info("Workflow: Generate → Upload → Delete local file")
            else:
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
                    if self.youtube_config:
                        if self.youtube_config.get('immediate_mode', True):
                            # Immediate upload mode
                            video_path = self._generate_and_upload_video(config)
                        else:
                            # Scheduled upload mode - upload with publish_at
                            video_path = self._generate_and_upload_scheduled_video(config)
                    else:
                        video_path = self._generate_single_video(config)
                    generated_videos.append(video_path)
                    
                except Exception as e:
                    self.logger.error(f"Error processing video {config['video_number']}: {e}")
                    generated_videos.append(None)
                    
                    # If YouTube upload fails, stop the entire process
                    if self.youtube_config:
                        self.logger.error("Stopping process due to YouTube upload failure")
                        break
                    
            if self.youtube_config:
                self.logger.info("=== MULTIPLE VIDEOS GENERATION AND UPLOAD COMPLETED ===")
            else:
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
            
            # Get greenscreen effects from config
            greenscreen_effects = config.get('greenscreen_effects', [])
            
            # Use the exact same method that works in main_optimized.py
            success = self.video_generator.create_simple_music_video(
                combined_audio_path,
                background_path,
                output_path,
                greenscreen_effects
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
            
    def _generate_and_upload_video(self, config):
        """
        Generate a video and upload it to YouTube, then delete local file
        
        Args:
            config: Dictionary with video configuration
            
        Returns:
            YouTube video ID if successful, None if failed
        """
        video_number = config['video_number']
        
        try:
            # First, check if we can upload (quota management)
            if not self.youtube_uploader.quota_manager.can_upload():
                if self.youtube_uploader.quota_manager.is_in_cooldown():
                    # Wait for quota reset
                    self._wait_for_quota_reset()
                else:
                    raise Exception("Daily upload limit reached")
            
            # Step 1: Generate video
            self._report_progress(video_number, 5, "Iniciando generación...")
            video_path = self._generate_single_video(config)
            
            if not video_path or not os.path.exists(video_path):
                raise Exception("Video generation failed")
                
            # Step 2: Upload to YouTube
            self._report_progress(video_number, 85, "Subiendo a YouTube...")
            self._update_upload_progress(video_number, 'uploading')
            
            # Get metadata for this video (individual or global)
            metadata = self._get_video_metadata(video_number)
            
            success, video_id, error_msg = self.youtube_uploader.upload_video(
                video_path=video_path,
                title=metadata['title'],
                description=metadata['description'],
                tags=metadata['tags'],
                category_id=metadata['category_id'],
                privacy_status=self.youtube_config['privacy_status']
            )
            
            if not success:
                raise Exception(f"YouTube upload failed: {error_msg}")
                
            self._update_upload_progress(video_number, 'uploaded', f"Video ID: {video_id}")
            
            # Step 3: Delete local file
            self._report_progress(video_number, 95, "Eliminando archivo local...")
            self._update_upload_progress(video_number, 'deleting')
            
            try:
                os.remove(video_path)
                self.logger.info(f"Deleted local file: {video_path}")
                self._update_upload_progress(video_number, 'completed')
            except Exception as e:
                self.logger.warning(f"Could not delete local file {video_path}: {e}")
                
            self._report_progress(video_number, 100, "Completado")
            
            # Update quota status in UI
            quota_status = self.youtube_uploader.get_quota_status()
            self._update_quota_status(quota_status['videos_uploaded_today'])
            
            return video_id
            
        except Exception as e:
            self.logger.error(f"Error in generate and upload workflow for video {video_number}: {e}")
            # Clean up local file if it exists
            if 'video_path' in locals() and video_path and os.path.exists(video_path):
                try:
                    os.remove(video_path)
                    self.logger.info(f"Cleaned up failed video file: {video_path}")
                except:
                    pass
            raise e
    
    def _generate_and_upload_scheduled_video(self, config):
        """
        Generate a video and upload it with scheduled publish time
        
        Args:
            config: Dictionary with video configuration
            
        Returns:
            YouTube video ID if successful, None if failed
        """
        video_number = config['video_number']
        
        try:
            # First, check if we can upload (quota management)
            if not self.youtube_uploader.quota_manager.can_upload():
                if self.youtube_uploader.quota_manager.is_in_cooldown():
                    # Wait for quota reset
                    self._wait_for_quota_reset()
                else:
                    raise Exception("Daily upload limit reached")
            
            # Step 1: Generate video
            self._report_progress(video_number, 5, "Iniciando generación...")
            video_path = self._generate_single_video(config)
            
            if not video_path or not os.path.exists(video_path):
                raise Exception("Video generation failed")
                
            # Step 2: Get scheduled upload info for this video
            schedule_item = self._get_schedule_for_video(video_number)
            if not schedule_item:
                raise Exception(f"No schedule found for video {video_number}")
                
            # Step 3: Upload to YouTube with scheduled publish time
            self._report_progress(video_number, 85, f"Subiendo a YouTube (programado para {schedule_item['date']} {schedule_item['time']})...")
            self._update_upload_progress(video_number, 'uploading')
            
            # Get metadata for this video (individual or global)
            metadata = self._get_video_metadata(video_number)
            
            success, video_id, error_msg = self.youtube_uploader.upload_video(
                video_path=video_path,
                title=metadata['title'],
                description=metadata['description'],
                tags=metadata['tags'],
                category_id=metadata['category_id'],
                privacy_status="private",  # Must be private for scheduled publishing
                publish_at=schedule_item['publish_at']
            )
            
            if not success:
                raise Exception(f"YouTube upload failed: {error_msg}")
                
            self._update_upload_progress(video_number, 'uploaded', f"Video ID: {video_id}, se publicará {schedule_item['date']} {schedule_item['time']}")
            
            # Step 4: Create upload log entry
            self._log_upload_details(video_number, video_path, video_id, schedule_item)
            
            # Step 5: Delete local file
            self._report_progress(video_number, 95, "Eliminando archivo local...")
            self._update_upload_progress(video_number, 'deleting')
            
            try:
                os.remove(video_path)
                self.logger.info(f"Deleted local file: {video_path}")
                self._update_upload_progress(video_number, 'completed')
            except Exception as e:
                self.logger.warning(f"Could not delete local file {video_path}: {e}")
                
            self._report_progress(video_number, 100, "Completado")
            
            # Update quota status in UI
            quota_status = self.youtube_uploader.get_quota_status()
            self._update_quota_status(quota_status['videos_uploaded_today'])
            
            return video_id
            
        except Exception as e:
            self.logger.error(f"Error in scheduled upload workflow for video {video_number}: {e}")
            # Clean up local file if it exists
            if 'video_path' in locals() and video_path and os.path.exists(video_path):
                try:
                    os.remove(video_path)
                    self.logger.info(f"Cleaned up failed video file: {video_path}")
                except:
                    pass
            raise e
    
    def _get_schedule_for_video(self, video_number):
        """Get schedule item for specific video number"""
        if not self.youtube_config or not self.youtube_config.get('scheduling'):
            return None
            
        schedule = self.youtube_config['scheduling']['schedule']
        for item in schedule:
            if item['video_number'] == video_number:
                return item
        return None
    
    def _log_upload_details(self, video_number, video_path, video_id, schedule_item):
        """Log detailed upload information"""
        try:
            # Calculate video duration (from audio files)
            duration = self._calculate_video_duration(video_number)
            
            # Get file size
            file_size = os.path.getsize(video_path) if os.path.exists(video_path) else 0
            file_size_mb = file_size / (1024 * 1024)
            
            # Create log entry
            log_entry = {
                'video_number': video_number,
                'title': metadata['title'],
                'youtube_id': video_id,
                'duration_minutes': duration,
                'file_size_mb': round(file_size_mb, 2),
                'scheduled_publish': f"{schedule_item['date']} {schedule_item['time']}",
                'upload_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'uploaded_scheduled'
            }
            
            # Write to upload log
            log_file = os.path.join(OUTPUT_DIR, "youtube_uploads.log")
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - "
                       f"Video {video_number}: {metadata['title']} - "
                       f"ID: {video_id} - Duration: {duration}min - "
                       f"Size: {file_size_mb:.1f}MB - "
                       f"Scheduled: {schedule_item['date']} {schedule_item['time']}\n")
                       
            # Also create detailed JSON log
            json_log_file = os.path.join(OUTPUT_DIR, "youtube_uploads_detailed.json")
            
            # Load existing logs or create new list
            upload_logs = []
            if os.path.exists(json_log_file):
                try:
                    with open(json_log_file, 'r', encoding='utf-8') as f:
                        upload_logs = json.load(f)
                except:
                    upload_logs = []
                    
            upload_logs.append(log_entry)
            
            # Save updated logs
            with open(json_log_file, 'w', encoding='utf-8') as f:
                json.dump(upload_logs, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Upload details logged for video {video_number}")
            
        except Exception as e:
            self.logger.warning(f"Could not log upload details for video {video_number}: {e}")
            
    def _calculate_video_duration(self, video_number):
        """Calculate video duration from audio files (approximate)"""
        try:
            # This is an approximation - in a real scenario you'd use librosa or similar
            # For now, estimate based on number of songs and average duration
            # You could enhance this to actually analyze the combined audio file
            return 3.5  # Default estimate in minutes
        except:
            return 0
            
    def _wait_for_quota_reset(self):
        """Wait for YouTube quota reset with progress updates"""
        remaining = self.youtube_uploader.quota_manager.get_cooldown_remaining()
        if not remaining:
            return
            
        end_time = datetime.now() + remaining
        self.logger.info(f"Waiting for quota reset. End time: {end_time}")
        
        # Notify UI about quota countdown start
        self._start_quota_countdown(end_time)
        
        # Wait with progress callback
        def quota_progress_callback(remaining_seconds, total_seconds):
            if self.cancelled:
                return
            # Update is handled by the progress dialog's timer
            
        self.youtube_uploader.wait_for_quota_reset(quota_progress_callback)
        
    def _update_upload_progress(self, video_number, stage, message=""):
        """Update upload progress in UI"""
        if hasattr(self, 'progress_callback') and self.progress_callback:
            # This will be handled by the progress dialog
            pass
            
    def _update_quota_status(self, videos_uploaded):
        """Update quota status in UI"""
        if hasattr(self, 'progress_callback') and self.progress_callback:
            # This will be handled by the progress dialog
            pass
            
    def _start_quota_countdown(self, end_time):
        """Start quota countdown in UI"""
        if hasattr(self, 'progress_callback') and self.progress_callback:
            # This will be handled by the progress dialog
            pass
    
    def _schedule_uploads(self, generated_videos):
        """Schedule uploads for generated videos"""
        if not self.youtube_config or not self.youtube_config.get('scheduling'):
            self.logger.warning("No scheduling configuration available")
            return
            
        scheduling_config = self.youtube_config['scheduling']
        schedule = scheduling_config['schedule']
        
        # Filter out failed video generations
        valid_videos = [v for v in generated_videos if v is not None]
        
        if len(valid_videos) == 0:
            self.logger.error("No valid videos to schedule")
            return
            
        # Create scheduling data file
        schedule_data = []
        for i, video_path in enumerate(valid_videos):
            if i < len(schedule):
                schedule_item = schedule[i]
                schedule_data.append({
                    'video_path': video_path,
                    'video_number': schedule_item['video_number'],
                    'title': schedule_item['title'],
                    'publish_at': schedule_item['publish_at'],
                    'date': schedule_item['date'],
                    'time': schedule_item['time'],
                    'description': self.youtube_config['description'],
                    'tags': self.youtube_config['tags'],
                    'category_id': self.youtube_config['category_id'],
                    'privacy_status': self.youtube_config['privacy_status']
                })
                
        # Save schedule to file
        import json
        schedule_file = os.path.join(OUTPUT_DIR, "youtube_upload_schedule.json")
        try:
            with open(schedule_file, 'w', encoding='utf-8') as f:
                json.dump(schedule_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Schedule saved to {schedule_file}")
            self.logger.info(f"Scheduled {len(schedule_data)} videos for upload")
            
            # Log schedule summary
            for item in schedule_data:
                self.logger.info(f"  {item['date']} {item['time']} - {item['title']}")
                
        except Exception as e:
            self.logger.error(f"Error saving schedule: {e}")
            
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
            
            # Disable AudioProcessor's own repetitions since GUI already applied them
            custom_processor.repeat_count = 1  # 1 means "no additional repetitions"
            
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
        """Generate timestamps file for the video using AudioProcessor"""
        timestamps_path = os.path.join(OUTPUT_DIR, f"video_{video_number}_timestamps.txt")
        
        try:
            # Use AudioProcessor to generate proper timestamps
            audio_processor = AudioProcessor()
            
            # Generate timestamps using the same method as single video
            generated_path = audio_processor.generate_description_file(songs, timestamps_path)
            
            if generated_path:
                self.logger.info(f"✅ Timestamps file generated: {timestamps_path}")
            else:
                self.logger.warning(f"Failed to generate timestamps file for video {video_number}")
            
        except Exception as e:
            self.logger.warning(f"Could not generate timestamps file: {e}")
            
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
    
    def _get_video_metadata(self, video_number):
        """Get metadata for a specific video (individual or global)"""
        # Check if we have individual metadata for this video
        video_index = video_number - 1
        if (self.individual_metadata and 
            video_index < len(self.individual_metadata) and 
            self.individual_metadata[video_index]):
            
            # Use individual metadata
            metadata = self.individual_metadata[video_index].copy()
            
            # Ensure all required fields are present
            if 'title' not in metadata or not metadata['title']:
                metadata['title'] = self.youtube_config['title_base'].replace('{}', str(video_number))
            if 'tags' not in metadata:
                metadata['tags'] = self.youtube_config['tags']
            if 'category_id' not in metadata:
                metadata['category_id'] = self.youtube_config['category_id']
            
            # Add real timestamps to description if [timestamps] placeholder exists
            if 'description' in metadata and '[timestamps]' in metadata['description']:
                metadata['description'] = self._add_timestamps_to_description(metadata['description'], video_number)
                
            return metadata
        else:
            # Use global configuration
            if self.youtube_config:
                description = self.youtube_config['description']
                # Add timestamps if placeholder exists
                if '[timestamps]' in description:
                    description = self._add_timestamps_to_description(description, video_number)
                
                return {
                    'title': self.youtube_config['title_base'].replace('{}', str(video_number)),
                    'description': description,
                    'tags': self.youtube_config['tags'],
                    'category_id': self.youtube_config['category_id']
                }
            else:
                # Fallback when no YouTube config
                return {
                    'title': f'Video {video_number}',
                    'description': 'Default description',
                    'tags': 'default, tags',
                    'category_id': '10'
                }
    
    def _add_timestamps_to_description(self, description, video_number):
        """Add real timestamps to description by reading timestamps file"""
        timestamps_file = os.path.join(OUTPUT_DIR, f"video_{video_number}_timestamps.txt")
        
        if not os.path.exists(timestamps_file):
            # If timestamps file doesn't exist, just remove the placeholder
            return description.replace('[timestamps]', '(Los timestamps se añadirán automáticamente)')
        
        try:
            with open(timestamps_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract just the timestamps lines
            lines = content.split('\n')
            timestamps = []
            in_timestamps_section = False
            
            for line in lines:
                if "=== TIEMPOS DE REPRODUCCIÓN ===" in line:
                    in_timestamps_section = True
                    continue
                elif "=== DURACIÓN TOTAL ===" in line:
                    break
                elif in_timestamps_section and line.strip() and not line.startswith("==="):
                    timestamps.append(line.strip())
            
            if timestamps:
                timestamps_text = '\n'.join(timestamps)
                return description.replace('[timestamps]', timestamps_text)
            else:
                return description.replace('[timestamps]', '(No se encontraron timestamps)')
                
        except Exception as e:
            self.logger.warning(f"Could not read timestamps for video {video_number}: {e}")
            return description.replace('[timestamps]', '(Error al leer timestamps)')