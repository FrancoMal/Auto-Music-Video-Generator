"""
Progress dialog with real-time logs and time estimation
"""

import time
from datetime import datetime, timedelta
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QProgressBar, QPushButton, QTextEdit, QGroupBox)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont


class ProgressDialog(QDialog):
    """Dialog showing progress, logs, and time estimation for video generation"""
    
    cancelRequested = Signal()
    
    def __init__(self, total_videos, parent=None, youtube_mode=False):
        super().__init__(parent)
        self.total_videos = total_videos
        self.youtube_mode = youtube_mode
        self.current_video = 0
        self.start_time = None
        self.video_start_times = []
        self.video_durations = []
        self.quota_countdown_timer = None
        self.quota_end_time = None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        title = "Generando y Subiendo Videos a YouTube" if self.youtube_mode else "Generando Videos Múltiples"
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(700, 600 if self.youtube_mode else 500)
        
        layout = QVBoxLayout(self)
        
        # Progress section
        progress_group = QGroupBox("Progreso")
        progress_layout = QVBoxLayout(progress_group)
        
        # Overall progress
        self.overall_label = QLabel("Progreso general:")
        progress_layout.addWidget(self.overall_label)
        
        self.overall_progress = QProgressBar()
        self.overall_progress.setMaximum(self.total_videos)
        self.overall_progress.setValue(0)
        progress_layout.addWidget(self.overall_progress)
        
        # Current video progress
        self.current_label = QLabel("Video actual:")
        progress_layout.addWidget(self.current_label)
        
        self.current_progress = QProgressBar()
        self.current_progress.setMaximum(100)
        self.current_progress.setValue(0)
        progress_layout.addWidget(self.current_progress)
        
        # Time information
        time_layout = QHBoxLayout()
        
        self.elapsed_label = QLabel("Tiempo transcurrido: 00:00:00")
        time_layout.addWidget(self.elapsed_label)
        
        self.remaining_label = QLabel("Tiempo estimado restante: --:--:--")
        time_layout.addWidget(self.remaining_label)
        
        progress_layout.addLayout(time_layout)
        layout.addWidget(progress_group)
        
        # YouTube quota section (only in YouTube mode)
        if self.youtube_mode:
            quota_group = QGroupBox("Estado de Cuota de YouTube")
            quota_layout = QVBoxLayout(quota_group)
            
            self.quota_status_label = QLabel("Videos subidos hoy: 0/6")
            quota_layout.addWidget(self.quota_status_label)
            
            self.quota_countdown_label = QLabel("Estado: Listo para subir")
            quota_layout.addWidget(self.quota_countdown_label)
            
            layout.addWidget(quota_group)
        
        # Logs section
        logs_group = QGroupBox("Logs en tiempo real")
        logs_layout = QVBoxLayout(logs_group)
        
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        
        # Set monospace font for logs
        font = QFont("Consolas", 9)
        font.setStyleHint(QFont.Monospace)
        self.logs_text.setFont(font)
        
        logs_layout.addWidget(self.logs_text)
        layout.addWidget(logs_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        button_layout.addWidget(self.cancel_button)
        
        self.close_button = QPushButton("Cerrar")
        self.close_button.clicked.connect(self.accept)
        self.close_button.setEnabled(False)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        # Timer for updating elapsed time
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_time_display)
        self.update_timer.start(1000)  # Update every second
        
    def start_generation(self):
        """Start the generation process"""
        self.start_time = time.time()
        if self.youtube_mode:
            self.add_log("=== INICIANDO GENERACIÓN Y SUBIDA A YOUTUBE ===")
            self.add_log(f"Total de videos a procesar: {self.total_videos}")
            self.add_log("Proceso: Generar → Subir → Eliminar archivo local")
        else:
            self.add_log("=== INICIANDO GENERACIÓN DE VIDEOS MÚLTIPLES ===")
            self.add_log(f"Total de videos a generar: {self.total_videos}")
        self.add_log(f"Hora de inicio: {datetime.now().strftime('%H:%M:%S')}")
        self.add_log("")
        
    def start_video(self, video_number, config):
        """Start generation of a specific video"""
        self.current_video = video_number
        video_start_time = time.time()
        self.video_start_times.append(video_start_time)
        
        self.current_label.setText(f"Video actual: {video_number}/{self.total_videos}")
        self.current_progress.setValue(0)
        
        self.add_log(f"--- INICIANDO VIDEO {video_number} ---")
        self.add_log(f"Canciones: {config.get('songs_count', 0)}")
        self.add_log(f"Color: {config.get('color', 'N/A')}")
        background = config.get('background_image', '')
        if background:
            self.add_log(f"Imagen: {background.split('/')[-1]}")
        self.add_log("")
        
    def update_video_progress(self, progress, message=""):
        """Update current video progress"""
        self.current_progress.setValue(int(progress))
        if message:
            self.add_log(f"[Video {self.current_video}] {message}")
            
    def complete_video(self, video_number, success=True, output_path=""):
        """Complete generation of a specific video"""
        if len(self.video_start_times) > 0:
            video_duration = time.time() - self.video_start_times[-1]
            self.video_durations.append(video_duration)
        
        self.overall_progress.setValue(video_number)
        
        if success:
            self.add_log(f"✅ VIDEO {video_number} COMPLETADO EXITOSAMENTE")
            if output_path:
                self.add_log(f"Archivo: {output_path}")
            self.add_log(f"Duración: {self.format_duration(video_duration)}")
        else:
            self.add_log(f"❌ ERROR EN VIDEO {video_number}")
            
        self.add_log("")
        
    def complete_generation(self, success=True):
        """Complete the entire generation process"""
        total_duration = time.time() - self.start_time if self.start_time else 0
        
        if success:
            self.add_log("🎉 GENERACIÓN COMPLETADA EXITOSAMENTE")
            self.add_log(f"Videos generados: {self.total_videos}")
        else:
            self.add_log("❌ GENERACIÓN FINALIZADA CON ERRORES")
            
        self.add_log(f"Tiempo total: {self.format_duration(total_duration)}")
        self.add_log(f"Hora de finalización: {datetime.now().strftime('%H:%M:%S')}")
        
        self.cancel_button.setEnabled(False)
        self.close_button.setEnabled(True)
        self.update_timer.stop()
        
    def add_log(self, message):
        """Add a log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        self.logs_text.append(formatted_message)
        
        # Auto-scroll to bottom
        scrollbar = self.logs_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def update_time_display(self):
        """Update elapsed and remaining time display"""
        if not self.start_time:
            return
            
        elapsed = time.time() - self.start_time
        self.elapsed_label.setText(f"Tiempo transcurrido: {self.format_duration(elapsed)}")
        
        # Estimate remaining time based on completed videos
        if self.current_video > 0 and self.video_durations:
            avg_duration = sum(self.video_durations) / len(self.video_durations)
            remaining_videos = self.total_videos - self.current_video
            estimated_remaining = avg_duration * remaining_videos
            
            self.remaining_label.setText(f"Tiempo estimado restante: {self.format_duration(estimated_remaining)}")
        else:
            self.remaining_label.setText("Tiempo estimado restante: Calculando...")
            
    def format_duration(self, seconds):
        """Format duration in seconds to HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
    def on_cancel_clicked(self):
        """Handle cancel button click"""
        self.add_log("🛑 CANCELACIÓN SOLICITADA POR EL USUARIO")
        self.cancel_button.setEnabled(False)
        self.cancelRequested.emit()
        
    def closeEvent(self, event):
        """Handle dialog close event"""
        if self.cancel_button.isEnabled():
            self.on_cancel_clicked()
        event.accept()
        
    # YouTube-specific methods
    def update_upload_progress(self, video_number, stage, message=""):
        """Update progress for YouTube upload stages"""
        if not self.youtube_mode:
            return
            
        stage_messages = {
            'generating': f"🎬 Generando video {video_number}...",
            'uploading': f"☁️ Subiendo video {video_number} a YouTube...",
            'uploaded': f"✅ Video {video_number} subido exitosamente",
            'deleting': f"🗑️ Eliminando archivo local del video {video_number}...",
            'completed': f"✨ Video {video_number} procesado completamente"
        }
        
        if stage in stage_messages:
            self.add_log(stage_messages[stage])
        if message:
            self.add_log(f"   {message}")
            
    def update_quota_status(self, videos_uploaded, daily_limit=6):
        """Update YouTube quota status display"""
        if not self.youtube_mode:
            return
            
        self.quota_status_label.setText(f"Videos subidos hoy: {videos_uploaded}/{daily_limit}")
        
        if videos_uploaded >= daily_limit:
            self.quota_countdown_label.setText("Estado: Límite diario alcanzado")
            self.quota_countdown_label.setStyleSheet("color: orange; font-weight: bold;")
        else:
            remaining = daily_limit - videos_uploaded
            self.quota_countdown_label.setText(f"Estado: Pueden subirse {remaining} videos más")
            self.quota_countdown_label.setStyleSheet("color: green;")
            
    def start_quota_countdown(self, end_time):
        """Start quota cooldown countdown"""
        if not self.youtube_mode:
            return
            
        self.quota_end_time = end_time
        self.add_log("⏰ INICIANDO PERÍODO DE ESPERA DE CUOTA")
        self.add_log(f"Reanudación programada: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Start countdown timer
        if self.quota_countdown_timer:
            self.quota_countdown_timer.stop()
            
        self.quota_countdown_timer = QTimer()
        self.quota_countdown_timer.timeout.connect(self.update_quota_countdown)
        self.quota_countdown_timer.start(1000)  # Update every second
        
    def update_quota_countdown(self):
        """Update quota countdown display"""
        if not self.quota_end_time:
            return
            
        now = datetime.now()
        if now >= self.quota_end_time:
            # Countdown finished
            self.quota_countdown_timer.stop()
            self.quota_countdown_label.setText("Estado: Listo para continuar")
            self.quota_countdown_label.setStyleSheet("color: green; font-weight: bold;")
            self.add_log("✅ PERÍODO DE ESPERA COMPLETADO - Continuando con subidas")
            return
            
        # Calculate remaining time
        remaining = self.quota_end_time - now
        hours, remainder = divmod(int(remaining.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        countdown_text = f"Reanudando en: {hours:02d}:{minutes:02d}:{seconds:02d}"
        self.quota_countdown_label.setText(countdown_text)
        self.quota_countdown_label.setStyleSheet("color: orange; font-weight: bold;")
        
    def log_upload_error(self, video_number, error_message):
        """Log upload error"""
        if self.youtube_mode:
            self.add_log(f"❌ ERROR AL SUBIR VIDEO {video_number}")
            self.add_log(f"   Error: {error_message}")
        
    def log_video_deleted(self, video_number, file_path):
        """Log video file deletion"""
        if self.youtube_mode:
            self.add_log(f"🗑️ Archivo local eliminado: {file_path}")