"""
Main GUI for multiple videos generation
"""

import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QSpinBox, QPushButton, 
                             QScrollArea, QFrame, QMessageBox, QGroupBox)
from PySide6.QtCore import Qt, QThread, Signal

from config import MUSICA_DIR, RECURSOS_DIR, PROCESS_CONFIG
from gui_components.video_config_widget import VideoConfigWidget
from gui_components.progress_dialog import ProgressDialog
from multiple_videos_generator import MultipleVideosGenerator


class VideoGenerationThread(QThread):
    """Thread for generating videos without blocking the UI"""
    
    progress_updated = Signal(int, int, str)  # video_number, progress, message
    video_completed = Signal(int, bool, str)  # video_number, success, output_path
    generation_completed = Signal(bool)  # success
    
    def __init__(self, video_configs, parent=None):
        super().__init__(parent)
        self.video_configs = video_configs
        self.generator = None
        
    def run(self):
        """Run the video generation process"""
        try:
            # Create generator with progress callback
            self.generator = MultipleVideosGenerator(
                progress_callback=self._progress_callback
            )
            
            # Validate configurations
            is_valid, error_msg = self.generator.validate_configurations(self.video_configs)
            if not is_valid:
                raise Exception(error_msg)
                
            # Generate videos
            results = self.generator.generate_videos(self.video_configs)
            
            # Check if any videos failed
            success = all(result is not None for result in results)
            self.generation_completed.emit(success)
            
        except Exception as e:
            print(f"Generation error: {e}")
            self.generation_completed.emit(False)
            
    def _progress_callback(self, video_number, progress, message):
        """Handle progress updates from generator"""
        self.progress_updated.emit(video_number, progress, message)
        
    def cancel_generation(self):
        """Cancel the generation process"""
        if self.generator:
            self.generator.cancel_generation()


class SongAssignmentManager:
    """Manages automatic song assignment to videos"""
    
    def __init__(self, music_directory):
        self.music_directory = music_directory
        self.available_songs = self._load_songs()
        
    def _load_songs(self):
        """Load available songs from music directory"""
        if not os.path.exists(self.music_directory):
            return []
            
        supported_formats = PROCESS_CONFIG['supported_formats']
        songs = []
        
        for filename in os.listdir(self.music_directory):
            _, ext = os.path.splitext(filename.lower())
            if ext in supported_formats:
                full_path = os.path.join(self.music_directory, filename)
                songs.append(full_path)
                
        # Sort alphabetically
        songs.sort()
        return songs
        
    def assign_songs(self, video_configs, global_repetitions=0):
        """
        Assign songs to videos automatically based on configuration
        
        Args:
            video_configs: List of video configurations with songs_count and individual repetitions
            global_repetitions: Default repetitions (used if video doesn't have individual setting)
            
        Returns:
            List of video configs with assigned songs (with repetitions per video)
        """
        # Calculate total unique songs needed (without repetitions)
        total_unique_songs_needed = sum(config['songs_count'] for config in video_configs)
        
        if total_unique_songs_needed > len(self.available_songs):
            raise ValueError(f"No hay suficientes canciones. Necesarias: {total_unique_songs_needed}, Disponibles: {len(self.available_songs)}")
        
        song_index = 0
        result_configs = []
        
        for config in video_configs:
            new_config = config.copy()
            
            # Get repetitions for this specific video (individual or global)
            video_repetitions = config.get('repetitions', global_repetitions)
            
            # Get unique songs for this video
            unique_songs_for_video = []
            for _ in range(config['songs_count']):
                if song_index < len(self.available_songs):
                    unique_songs_for_video.append(self.available_songs[song_index])
                    song_index += 1
            
            # Apply repetitions to this specific video's songs
            # Example: 2 songs, 0 repetitions = [song1, song2] (play once)
            # Example: 2 songs, 1 repetition = [song1, song2, song1, song2] (play twice)
            repeated_songs_for_video = []
            if video_repetitions == 0:
                # No repetitions = play once
                repeated_songs_for_video.extend(unique_songs_for_video)
            else:
                # With repetitions = play original + repetitions times
                for _ in range(video_repetitions + 1):
                    repeated_songs_for_video.extend(unique_songs_for_video)
                    
            new_config['songs'] = repeated_songs_for_video
            new_config['unique_songs'] = unique_songs_for_video  # Store original for display
            new_config['effective_repetitions'] = video_repetitions  # Store effective repetitions used
            result_configs.append(new_config)
            
        return result_configs


class MultipleVideosMainWindow(QMainWindow):
    """Main window for multiple videos configuration"""
    
    def __init__(self):
        super().__init__()
        self.video_widgets = []
        self.song_manager = SongAssignmentManager(MUSICA_DIR)
        self.available_colors = ["red", "cyan", "white", "yellow", "green", "blue", "magenta", "orange", "pink"]
        self.setup_ui()
        self.update_video_widgets()
        
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("ACE Music Video Generator - Videos Múltiples")
        self.setMinimumSize(800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Global configuration
        global_group = QGroupBox("Configuración Global")
        global_layout = QHBoxLayout(global_group)
        
        # Number of videos
        global_layout.addWidget(QLabel("Número de videos:"))
        self.videos_spinbox = QSpinBox()
        self.videos_spinbox.setMinimum(1)
        self.videos_spinbox.setMaximum(10)
        self.videos_spinbox.setValue(2)
        self.videos_spinbox.valueChanged.connect(self.on_videos_count_changed)
        global_layout.addWidget(self.videos_spinbox)
        
        global_layout.addStretch()
        
        # Global songs per video
        global_layout.addWidget(QLabel("Canciones por video (por defecto):"))
        self.global_songs_spinbox = QSpinBox()
        self.global_songs_spinbox.setMinimum(1)
        self.global_songs_spinbox.setMaximum(20)
        self.global_songs_spinbox.setValue(2)
        self.global_songs_spinbox.valueChanged.connect(self.on_global_songs_changed)
        global_layout.addWidget(self.global_songs_spinbox)
        
        global_layout.addStretch()
        
        # Repetitions
        global_layout.addWidget(QLabel("Repeticiones (global):"))
        self.repetitions_spinbox = QSpinBox()
        self.repetitions_spinbox.setMinimum(0)
        self.repetitions_spinbox.setMaximum(5)
        self.repetitions_spinbox.setValue(0)
        self.repetitions_spinbox.valueChanged.connect(self.on_global_repetitions_changed)
        global_layout.addWidget(self.repetitions_spinbox)
        
        main_layout.addWidget(global_group)
        
        # Song information
        info_group = QGroupBox("Información de Canciones")
        info_layout = QVBoxLayout(info_group)
        
        self.songs_info_label = QLabel()
        self.update_songs_info()
        info_layout.addWidget(self.songs_info_label)
        
        main_layout.addWidget(info_group)
        
        # Scroll area for video configurations
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.videos_container = QWidget()
        self.videos_layout = QVBoxLayout(self.videos_container)
        scroll_area.setWidget(self.videos_container)
        
        main_layout.addWidget(scroll_area)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.generate_button = QPushButton("Generar Videos")
        self.generate_button.clicked.connect(self.on_generate_clicked)
        self.generate_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; }")
        button_layout.addWidget(self.generate_button)
        
        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)
        
        main_layout.addLayout(button_layout)
        
    def update_songs_info(self):
        """Update the songs information display"""
        total_songs = len(self.song_manager.available_songs)
        
        if total_songs > 0:
            songs_text = f"Canciones disponibles: {total_songs}\n"
            songs_text += "Archivos: " + ", ".join([os.path.basename(song) for song in self.song_manager.available_songs[:5]])
            if total_songs > 5:
                songs_text += f" ... (+{total_songs - 5} más)"
        else:
            songs_text = "No se encontraron canciones en la carpeta 'musica/'"
            
        self.songs_info_label.setText(songs_text)
        
    def on_videos_count_changed(self, count):
        """Handle change in number of videos"""
        self.update_video_widgets()
        
    def on_global_songs_changed(self, songs_count):
        """Handle change in global songs per video"""
        for widget in self.video_widgets:
            widget.set_songs_count(songs_count)
        self.update_song_assignments()
        
    def on_global_repetitions_changed(self, repetitions):
        """Handle change in global repetitions"""
        # Update all videos that don't have individual repetitions set
        for widget in self.video_widgets:
            if widget.get_repetitions() == 0:  # Assuming 0 means "use global"
                widget.set_repetitions(repetitions)
        self.update_song_assignments()
        
    def update_video_widgets(self):
        """Update the video configuration widgets"""
        # Clear existing widgets
        for widget in self.video_widgets:
            widget.setParent(None)
        self.video_widgets.clear()
        
        # Create new widgets
        videos_count = self.videos_spinbox.value()
        
        for i in range(videos_count):
            widget = VideoConfigWidget(
                video_number=i + 1,
                images_directory=RECURSOS_DIR,
                available_colors=self.available_colors
            )
            widget.configChanged.connect(self.update_song_assignments)
            
            # Set default color (cycle through available colors)
            default_color = self.available_colors[i % len(self.available_colors)]
            widget.set_color(default_color)
            
            self.video_widgets.append(widget)
            self.videos_layout.addWidget(widget)
            
        # Add stretch to push widgets to top
        self.videos_layout.addStretch()
        
        # Update song assignments
        self.update_song_assignments()
        
    def update_song_assignments(self):
        """Update automatic song assignments for all videos"""
        try:
            # Get current configurations including individual repetitions
            configs = []
            for widget in self.video_widgets:
                configs.append({
                    'video_number': widget.video_number,
                    'songs_count': widget.get_songs_count(),
                    'repetitions': widget.get_repetitions(),
                    'color': widget.get_color(),
                    'background_image': widget.get_background_image()
                })
            
            if not configs:
                return
                
            # Assign songs with global repetitions as fallback
            global_repetitions = self.repetitions_spinbox.value()
            assigned_configs = self.song_manager.assign_songs(configs, global_repetitions)
            
            # Update widgets with assigned songs
            for widget, config in zip(self.video_widgets, assigned_configs):
                # Show preview with repetition info
                unique_songs = config.get('unique_songs', config['songs'])
                effective_repetitions = config.get('effective_repetitions', 0)
                widget.update_songs_preview(config['songs'], unique_songs, effective_repetitions)
                
            # Update generate button state
            self.generate_button.setEnabled(True)
            self.generate_button.setText("Generar Videos")
            
        except ValueError as e:
            # Not enough songs
            for widget in self.video_widgets:
                widget.update_songs_preview([])
                
            self.generate_button.setEnabled(False)
            self.generate_button.setText(f"Error: {str(e)}")
            
        except Exception as e:
            print(f"Error updating song assignments: {e}")
            
    def get_video_configurations(self):
        """Get all video configurations with assigned songs"""
        try:
            configs = []
            for widget in self.video_widgets:
                configs.append({
                    'video_number': widget.video_number,
                    'songs_count': widget.get_songs_count(),
                    'color': widget.get_color(),
                    'background_image': widget.get_background_image()
                })
            
            repetitions = self.repetitions_spinbox.value()
            return self.song_manager.assign_songs(configs, repetitions)
            
        except Exception as e:
            raise Exception(f"Error getting configurations: {e}")
            
    def on_generate_clicked(self):
        """Handle generate videos button click"""
        try:
            # Get configurations
            video_configs = self.get_video_configurations()
            
            if not video_configs:
                QMessageBox.warning(self, "Error", "No hay configuraciones de video válidas")
                return
                
            # Show confirmation dialog
            config_summary = self._get_configuration_summary(video_configs)
            reply = QMessageBox.question(
                self, 
                "Confirmar Generación", 
                f"¿Generar los siguientes videos?\n\n{config_summary}",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
                
            # Disable generate button during generation
            self.generate_button.setEnabled(False)
            self.generate_button.setText("Generando...")
            
            # Show progress dialog
            self.progress_dialog = ProgressDialog(len(video_configs), self)
            self.progress_dialog.cancelRequested.connect(self.on_generation_cancelled)
            
            # Start generation thread
            self.generation_thread = VideoGenerationThread(video_configs, self)
            self.generation_thread.progress_updated.connect(self.on_progress_updated)
            self.generation_thread.video_completed.connect(self.on_video_completed)
            self.generation_thread.generation_completed.connect(self.on_generation_completed)
            
            self.progress_dialog.start_generation()
            self.progress_dialog.show()
            
            self.generation_thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al preparar la generación: {str(e)}")
            self.generate_button.setEnabled(True)
            self.generate_button.setText("Generar Videos")
            
    def _get_configuration_summary(self, configs):
        """Get a summary of the video configurations"""
        summary = []
        for config in configs:
            songs_count = len(config.get('songs', []))
            color = config.get('color', 'N/A')
            background = config.get('background_image', '')
            bg_name = os.path.basename(background) if background else 'Por defecto'
            
            summary.append(f"Video {config['video_number']}: {songs_count} canciones, color {color}, fondo {bg_name}")
            
        return "\n".join(summary)
        
    def on_progress_updated(self, video_number, progress, message):
        """Handle progress updates from generation thread"""
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            if progress <= 10:
                # Starting new video
                config = next((c for c in self.generation_thread.video_configs if c['video_number'] == video_number), {})
                self.progress_dialog.start_video(video_number, config)
            
            self.progress_dialog.update_video_progress(progress, message)
            
    def on_video_completed(self, video_number, success, output_path):
        """Handle video completion"""
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.complete_video(video_number, success, output_path)
            
    def on_generation_completed(self, success):
        """Handle generation completion"""
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.complete_generation(success)
            
        # Re-enable generate button
        self.generate_button.setEnabled(True)
        self.generate_button.setText("Generar Videos")
        
        if success:
            QMessageBox.information(
                self, 
                "Generación Completada", 
                "¡Todos los videos se han generado exitosamente!\n\nPuedes encontrarlos en la carpeta 'output/'."
            )
        else:
            QMessageBox.warning(
                self, 
                "Generación con Errores", 
                "La generación se completó pero algunos videos pueden haber fallado.\n\nRevisa los logs para más detalles."
            )
            
    def on_generation_cancelled(self):
        """Handle generation cancellation"""
        if hasattr(self, 'generation_thread') and self.generation_thread:
            self.generation_thread.cancel_generation()
            
        # Re-enable generate button
        self.generate_button.setEnabled(True)
        self.generate_button.setText("Generar Videos")


def main():
    """Main function"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = MultipleVideosMainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()