"""
Image preview widget for background image selection
"""

import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap


class ImagePreviewWidget(QWidget):
    """Widget that shows a dropdown of available images with preview"""
    
    imageChanged = Signal(str)  # Emits the selected image path
    
    def __init__(self, images_directory, parent=None):
        super().__init__(parent)
        self.images_directory = images_directory
        self.setup_ui()
        self.load_images()
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Image selection dropdown
        selection_layout = QHBoxLayout()
        selection_layout.addWidget(QLabel("Imagen de fondo:"))
        
        self.image_combo = QComboBox()
        self.image_combo.currentTextChanged.connect(self.on_image_changed)
        selection_layout.addWidget(self.image_combo)
        
        layout.addLayout(selection_layout)
        
        # Image preview
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(200, 112)  # 16:9 aspect ratio preview
        self.preview_label.setStyleSheet("border: 1px solid gray;")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setScaledContents(True)
        layout.addWidget(self.preview_label)
        
    def load_images(self):
        """Load available images from the resources directory"""
        if not os.path.exists(self.images_directory):
            return
            
        # Supported image formats
        supported_formats = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff'}
        
        images = []
        for filename in os.listdir(self.images_directory):
            _, ext = os.path.splitext(filename.lower())
            if ext in supported_formats:
                images.append(filename)
        
        # Sort alphabetically
        images.sort()
        
        # Add to combo box
        self.image_combo.clear()
        if images:
            self.image_combo.addItems(images)
        else:
            self.image_combo.addItem("No hay imágenes disponibles")
            
    def on_image_changed(self, filename):
        """Handle image selection change"""
        if filename == "No hay imágenes disponibles":
            self.preview_label.setText("Sin imagen")
            self.imageChanged.emit("")
            return
            
        image_path = os.path.join(self.images_directory, filename)
        
        # Update preview
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                self.preview_label.setPixmap(pixmap)
            else:
                self.preview_label.setText("Error cargando imagen")
        else:
            self.preview_label.setText("Imagen no encontrada")
        
        # Emit signal
        self.imageChanged.emit(image_path)
    
    def get_selected_image(self):
        """Get the currently selected image path"""
        current_text = self.image_combo.currentText()
        if current_text and current_text != "No hay imágenes disponibles":
            return os.path.join(self.images_directory, current_text)
        return ""
    
    def set_selected_image(self, filename):
        """Set the selected image by filename"""
        index = self.image_combo.findText(filename)
        if index >= 0:
            self.image_combo.setCurrentIndex(index)