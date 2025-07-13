"""
Chroma Key Preview Dialog for adjusting MP4 greenscreen parameters
"""

import os
import subprocess
import tempfile
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QSlider, QSpinBox, QGroupBox,
                               QComboBox, QTextEdit, QProgressBar, QFrame)
from PySide6.QtCore import Qt, Signal, QThread, QTimer
from PySide6.QtGui import QPixmap

from config import GREENSCREEN_CONFIG


class PreviewGeneratorThread(QThread):
    """Thread for generating preview frames without blocking UI"""
    
    preview_ready = Signal(str)  # Emits path to generated preview image
    error_occurred = Signal(str)  # Emits error message
    
    def __init__(self, video_path, similarity, tolerance, output_path):
        super().__init__()
        self.video_path = video_path
        self.similarity = similarity
        self.tolerance = tolerance
        self.output_path = output_path
    
    def run(self):
        """Generate preview frame with current chroma settings"""
        try:
            # Generate a single frame preview with colorkey applied
            cmd = [
                'ffmpeg', '-y',
                '-i', self.video_path,
                '-vf', f'colorkey=green:{self.similarity}:{self.tolerance},scale=400:300',
                '-frames:v', '1',
                '-f', 'image2',
                self.output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and os.path.exists(self.output_path):
                self.preview_ready.emit(self.output_path)
            else:
                self.error_occurred.emit(f"FFmpeg error: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            self.error_occurred.emit("Preview generation timed out")
        except Exception as e:
            self.error_occurred.emit(f"Error generating preview: {e}")


class ChromaPreviewDialog(QDialog):
    """Dialog for previewing and adjusting chroma key parameters for MP4 videos"""
    
    parameters_changed = Signal(float, float)  # Emits (similarity, tolerance)
    
    def __init__(self, video_path, parent=None):
        super().__init__(parent)
        self.video_path = video_path
        self.preview_thread = None
        self.temp_preview_path = None
        self.setup_ui()
        self.setup_temp_file()
        
        # Generate initial preview
        QTimer.singleShot(500, self.generate_preview)
    
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("Chroma Key Preview")
        self.setModal(True)
        self.resize(600, 700)
        
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Chroma Key Parameter Adjustment")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(header_label)
        
        # Video info
        video_name = os.path.basename(self.video_path)
        info_label = QLabel(f"Video: {video_name}")
        info_label.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(info_label)
        
        # Instructions
        instructions = QLabel(
            "Adjust the parameters below to fine-tune green screen removal. "
            "Higher similarity removes more green variations, higher tolerance "
            "removes more similar colors."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; font-style: italic; padding: 10px; border: 1px solid #ddd; background: #f9f9f9;")
        layout.addWidget(instructions)
        
        # Parameters section
        params_group = QGroupBox("Chroma Key Parameters")
        params_layout = QVBoxLayout(params_group)
        
        # Similarity parameter
        similarity_layout = QHBoxLayout()
        similarity_layout.addWidget(QLabel("Similarity:"))
        
        self.similarity_slider = QSlider(Qt.Horizontal)
        self.similarity_slider.setMinimum(1)
        self.similarity_slider.setMaximum(100)
        self.similarity_slider.setValue(int(GREENSCREEN_CONFIG['similarity'] * 100))
        self.similarity_slider.valueChanged.connect(self.on_parameter_changed)
        similarity_layout.addWidget(self.similarity_slider)
        
        self.similarity_value = QLabel(f"{GREENSCREEN_CONFIG['similarity']:.2f}")
        self.similarity_value.setMinimumWidth(40)
        similarity_layout.addWidget(self.similarity_value)
        
        params_layout.addLayout(similarity_layout)
        
        # Tolerance parameter
        tolerance_layout = QHBoxLayout()
        tolerance_layout.addWidget(QLabel("Tolerance:"))
        
        self.tolerance_slider = QSlider(Qt.Horizontal)
        self.tolerance_slider.setMinimum(1)
        self.tolerance_slider.setMaximum(100)
        self.tolerance_slider.setValue(int(GREENSCREEN_CONFIG['tolerance'] * 100))
        self.tolerance_slider.valueChanged.connect(self.on_parameter_changed)
        tolerance_layout.addWidget(self.tolerance_slider)
        
        self.tolerance_value = QLabel(f"{GREENSCREEN_CONFIG['tolerance']:.2f}")
        self.tolerance_value.setMinimumWidth(40)
        tolerance_layout.addWidget(self.tolerance_value)
        
        params_layout.addLayout(tolerance_layout)
        
        # Preset buttons
        presets_layout = QHBoxLayout()
        presets_layout.addWidget(QLabel("Presets:"))
        
        strict_btn = QPushButton("Strict")
        strict_btn.clicked.connect(lambda: self.apply_preset(0.2, 0.05))
        presets_layout.addWidget(strict_btn)
        
        normal_btn = QPushButton("Normal")
        normal_btn.clicked.connect(lambda: self.apply_preset(0.3, 0.1))
        presets_layout.addWidget(normal_btn)
        
        loose_btn = QPushButton("Loose")
        loose_btn.clicked.connect(lambda: self.apply_preset(0.4, 0.2))
        presets_layout.addWidget(loose_btn)
        
        optimal_btn = QPushButton("Optimal")
        optimal_btn.clicked.connect(lambda: self.apply_preset(0.5, 0.25))
        optimal_btn.setStyleSheet("background-color: #e6ffe6; font-weight: bold;")
        presets_layout.addWidget(optimal_btn)
        
        presets_layout.addStretch()
        params_layout.addLayout(presets_layout)
        
        layout.addWidget(params_group)
        
        # Preview section
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        # Progress bar for preview generation
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.hide()
        preview_layout.addWidget(self.progress_bar)
        
        # Preview image
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(400, 300)
        self.preview_label.setStyleSheet("border: 1px solid gray; background-color: #f0f0f0;")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setText("Generating preview...")
        preview_layout.addWidget(self.preview_label)
        
        # Preview info
        self.preview_info = QLabel("Adjust parameters to see changes")
        self.preview_info.setStyleSheet("color: #666; font-size: 11px;")
        preview_layout.addWidget(self.preview_info)
        
        layout.addWidget(preview_group)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.generate_btn = QPushButton("Refresh Preview")
        self.generate_btn.clicked.connect(self.generate_preview)
        buttons_layout.addWidget(self.generate_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        apply_btn = QPushButton("Apply Settings")
        apply_btn.clicked.connect(self.accept_settings)
        apply_btn.setDefault(True)
        buttons_layout.addWidget(apply_btn)
        
        layout.addLayout(buttons_layout)
        
        # Timer for delayed preview generation
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self.generate_preview)
    
    def setup_temp_file(self):
        """Setup temporary file for preview generation"""
        temp_dir = tempfile.gettempdir()
        self.temp_preview_path = os.path.join(temp_dir, 'chroma_preview.png')
    
    def apply_preset(self, similarity, tolerance):
        """Apply preset parameter values"""
        self.similarity_slider.setValue(int(similarity * 100))
        self.tolerance_slider.setValue(int(tolerance * 100))
        self.on_parameter_changed()
    
    def on_parameter_changed(self):
        """Handle parameter changes"""
        similarity = self.similarity_slider.value() / 100.0
        tolerance = self.tolerance_slider.value() / 100.0
        
        self.similarity_value.setText(f"{similarity:.2f}")
        self.tolerance_value.setText(f"{tolerance:.2f}")
        
        # Delayed preview generation to avoid too many calls
        self.preview_timer.stop()
        self.preview_timer.start(1000)  # 1 second delay
    
    def generate_preview(self):
        """Generate preview with current parameters"""
        if self.preview_thread and self.preview_thread.isRunning():
            return
        
        similarity = self.similarity_slider.value() / 100.0
        tolerance = self.tolerance_slider.value() / 100.0
        
        self.progress_bar.show()
        self.generate_btn.setEnabled(False)
        self.preview_label.setText("Generating preview...")
        
        self.preview_thread = PreviewGeneratorThread(
            self.video_path, similarity, tolerance, self.temp_preview_path
        )
        self.preview_thread.preview_ready.connect(self.on_preview_ready)
        self.preview_thread.error_occurred.connect(self.on_preview_error)
        self.preview_thread.start()
    
    def on_preview_ready(self, preview_path):
        """Handle preview generation completion"""
        self.progress_bar.hide()
        self.generate_btn.setEnabled(True)
        
        try:
            pixmap = QPixmap(preview_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.preview_label.setPixmap(scaled_pixmap)
                self.preview_info.setText("Preview generated successfully")
            else:
                self.preview_label.setText("Failed to load preview")
                self.preview_info.setText("Error loading preview image")
        except Exception as e:
            self.preview_label.setText("Preview error")
            self.preview_info.setText(f"Error: {e}")
    
    def on_preview_error(self, error_message):
        """Handle preview generation error"""
        self.progress_bar.hide()
        self.generate_btn.setEnabled(True)
        self.preview_label.setText("Preview failed")
        self.preview_info.setText(f"Error: {error_message}")
    
    def accept_settings(self):
        """Accept the current settings"""
        similarity = self.similarity_slider.value() / 100.0
        tolerance = self.tolerance_slider.value() / 100.0
        
        self.parameters_changed.emit(similarity, tolerance)
        self.accept()
    
    def get_parameters(self):
        """Get the current parameter values"""
        return (
            self.similarity_slider.value() / 100.0,
            self.tolerance_slider.value() / 100.0
        )
    
    def closeEvent(self, event):
        """Clean up when dialog is closed"""
        if self.preview_thread and self.preview_thread.isRunning():
            self.preview_thread.terminate()
            self.preview_thread.wait()
        
        if self.temp_preview_path and os.path.exists(self.temp_preview_path):
            try:
                os.remove(self.temp_preview_path)
            except:
                pass
        
        event.accept()