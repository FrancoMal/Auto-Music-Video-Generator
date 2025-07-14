"""
Video Metadata Preview Dialog for editing individual video metadata before upload
"""

import logging
import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QTextEdit, QPushButton, QComboBox,
                              QGroupBox, QFormLayout, QMessageBox, QScrollArea,
                              QFrame, QWidget, QSplitter)
from PySide6.QtCore import Qt
from config import OUTPUT_DIR


class VideoMetadataWidget(QFrame):
    """Widget for editing individual video metadata"""
    
    def __init__(self, video_number, title, description, category, tags, parent=None):
        super().__init__(parent)
        self.video_number = video_number
        self.setup_ui(title, description, category, tags)
    
    def setup_ui(self, title, description, category, tags):
        """Setup the UI for this video metadata"""
        self.setFrameStyle(QFrame.StyledPanel)
        self.setLineWidth(2)
        
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel(f"Video {self.video_number}")
        header_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2196F3;")
        layout.addWidget(header_label)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Title
        self.title_edit = QLineEdit(title)
        self.title_edit.setPlaceholderText(f"Título del video {self.video_number}")
        form_layout.addRow("Título:", self.title_edit)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setPlainText(description)
        self.description_edit.setMaximumHeight(150)
        self.description_edit.setPlaceholderText("Descripción del video...")
        form_layout.addRow("Descripción:", self.description_edit)
        
        # Category
        self.category_combo = QComboBox()
        categories = ["Música", "Entretenimiento", "Videojuegos", "Educación"]
        self.category_combo.addItems(categories)
        self.category_combo.setCurrentText(category)
        form_layout.addRow("Categoría:", self.category_combo)
        
        # Tags
        self.tags_edit = QLineEdit(tags)
        self.tags_edit.setPlaceholderText("tag1, tag2, tag3...")
        form_layout.addRow("Tags:", self.tags_edit)
        
        layout.addLayout(form_layout)
        
        # Preview button for timestamps
        preview_btn = QPushButton("Vista Previa de Timestamps")
        preview_btn.clicked.connect(self.preview_timestamps)
        layout.addWidget(preview_btn)
        
    def preview_timestamps(self):
        """Show timestamps preview"""
        timestamps_file = os.path.join(OUTPUT_DIR, f"video_{self.video_number}_timestamps.txt")
        
        if not os.path.exists(timestamps_file):
            QMessageBox.information(self, "Info", 
                                  f"Archivo de timestamps no encontrado: {timestamps_file}\n"
                                  "Los timestamps se generarán después de crear el video.")
            return
        
        try:
            with open(timestamps_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract just the timestamps
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
                timestamp_text = "\n".join(timestamps)
                QMessageBox.information(self, f"Timestamps - Video {self.video_number}", 
                                      f"Timestamps que se añadirán a la descripción:\n\n{timestamp_text}")
            else:
                QMessageBox.information(self, "Info", "No se encontraron timestamps en el archivo.")
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al leer timestamps: {str(e)}")
    
    def get_metadata(self):
        """Get the current metadata from the form"""
        category_map = {
            "Música": "10",
            "Entretenimiento": "24", 
            "Videojuegos": "20",
            "Educación": "27"
        }
        
        return {
            'title': self.title_edit.text().strip(),
            'description': self.description_edit.toPlainText().strip(),
            'category_id': category_map.get(self.category_combo.currentText(), "10"),
            'tags': self.tags_edit.text().strip()
        }


class VideoMetadataPreviewDialog(QDialog):
    """Dialog for previewing and editing metadata for all videos"""
    
    def __init__(self, video_count, youtube_config, parent=None):
        super().__init__(parent)
        self.video_count = video_count
        self.youtube_config = youtube_config
        self.video_widgets = []
        self.logger = logging.getLogger(__name__)
        
        self.setup_ui()
        self.generate_video_metadata()
    
    def setup_ui(self):
        """Setup the main UI"""
        self.setWindowTitle("Vista Previa de Videos - Editar Metadata")
        self.setModal(True)
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel(f"Vista Previa de {self.video_count} Videos")
        header_label.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        info_label = QLabel("Edita la metadata individual de cada video antes de subirlos a YouTube:")
        info_label.setStyleSheet("margin-bottom: 10px;")
        layout.addWidget(info_label)
        
        # Scroll area for video widgets
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # This will be populated by generate_video_metadata
        self.videos_layout = scroll_layout
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        back_button = QPushButton("← Atrás")
        back_button.clicked.connect(self.reject)
        button_layout.addWidget(back_button)
        
        cancel_button = QPushButton("Cancelar")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        accept_button = QPushButton("Subir Videos")
        accept_button.clicked.connect(self.accept_videos)
        accept_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        button_layout.addWidget(accept_button)
        
        layout.addLayout(button_layout)
    
    def generate_video_metadata(self):
        """Generate metadata widgets for each video"""
        for video_num in range(1, self.video_count + 1):
            # Generate title with video number
            title = self.youtube_config['title_base'].replace('{}', str(video_num))
            
            # Start with base description
            description = self.youtube_config['description']
            
            # Add timestamps section
            description += "\n\n[timestamps]"
            
            # Try to read and add actual timestamps
            timestamps_file = os.path.join(OUTPUT_DIR, f"video_{video_num}_timestamps.txt")
            if os.path.exists(timestamps_file):
                try:
                    with open(timestamps_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract timestamps
                    lines = content.split('\n')
                    in_timestamps_section = False
                    
                    for line in lines:
                        if "=== TIEMPOS DE REPRODUCCIÓN ===" in line:
                            in_timestamps_section = True
                            continue
                        elif "=== DURACIÓN TOTAL ===" in line:
                            break
                        elif in_timestamps_section and line.strip() and not line.startswith("==="):
                            description += f"\n{line.strip()}"
                    
                except Exception as e:
                    self.logger.warning(f"Could not read timestamps for video {video_num}: {e}")
                    description += f"\n(Los timestamps se añadirán automáticamente)"
            else:
                description += f"\n(Los timestamps se añadirán automáticamente)"
            
            # Get category name from ID
            category_id = self.youtube_config.get('category_id', '10')
            category_name = {
                '10': 'Música',
                '24': 'Entretenimiento', 
                '20': 'Videojuegos',
                '27': 'Educación'
            }.get(category_id, 'Música')
            
            # Create widget
            widget = VideoMetadataWidget(
                video_number=video_num,
                title=title,
                description=description,
                category=category_name,
                tags=self.youtube_config['tags']
            )
            
            self.video_widgets.append(widget)
            self.videos_layout.addWidget(widget)
        
        # Add stretch at the end
        self.videos_layout.addStretch()
    
    def accept_videos(self):
        """Accept the metadata and proceed with upload"""
        # Validate all forms
        for widget in self.video_widgets:
            metadata = widget.get_metadata()
            if not metadata['title'].strip():
                QMessageBox.warning(self, "Error", 
                                  f"El título del Video {widget.video_number} no puede estar vacío.")
                return
        
        # Store the metadata for later use
        self.video_metadata = []
        for widget in self.video_widgets:
            self.video_metadata.append(widget.get_metadata())
        
        self.accept()
    
    def get_video_metadata(self):
        """Get all video metadata"""
        return getattr(self, 'video_metadata', [])