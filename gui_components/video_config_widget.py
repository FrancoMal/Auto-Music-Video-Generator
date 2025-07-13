"""
Video configuration widget for individual video settings
"""

import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QSpinBox, QGroupBox, QListWidget, 
                             QPushButton)
from PySide6.QtCore import Qt, Signal

from .image_preview_widget import ImagePreviewWidget
from .greenscreen_effects_dialog import GreenschreenEffectsDialog


class VideoConfigWidget(QWidget):
    """Widget for configuring individual video settings"""
    
    configChanged = Signal()  # Emits when any configuration changes
    
    def __init__(self, video_number, images_directory, available_colors, parent=None):
        super().__init__(parent)
        self.video_number = video_number
        self.images_directory = images_directory
        self.available_colors = available_colors
        self.songs_list = []
        self.greenscreen_effects = []  # List of selected greenscreen effects
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Group box for this video
        self.group_box = QGroupBox(f"Video {self.video_number}")
        group_layout = QVBoxLayout(self.group_box)
        
        # Top row: songs per video and color
        top_layout = QHBoxLayout()
        
        # Songs per video
        top_layout.addWidget(QLabel("Canciones:"))
        self.songs_spinbox = QSpinBox()
        self.songs_spinbox.setMinimum(1)
        self.songs_spinbox.setMaximum(20)
        self.songs_spinbox.setValue(2)  # Default value
        self.songs_spinbox.valueChanged.connect(self.on_config_changed)
        top_layout.addWidget(self.songs_spinbox)
        
        top_layout.addStretch()
        
        # Individual repetitions
        top_layout.addWidget(QLabel("Repeticiones:"))
        self.repetitions_spinbox = QSpinBox()
        self.repetitions_spinbox.setMinimum(0)
        self.repetitions_spinbox.setMaximum(5)
        self.repetitions_spinbox.setValue(0)  # Default: no repetitions
        self.repetitions_spinbox.valueChanged.connect(self.on_config_changed)
        top_layout.addWidget(self.repetitions_spinbox)
        
        top_layout.addStretch()
        
        # Color selection
        top_layout.addWidget(QLabel("Color:"))
        self.color_combo = QComboBox()
        self.color_combo.addItems(self.available_colors)
        self.color_combo.currentTextChanged.connect(self.on_config_changed)
        top_layout.addWidget(self.color_combo)
        
        group_layout.addLayout(top_layout)
        
        # Middle row: Image preview and Greenscreen Effects button
        middle_layout = QHBoxLayout()
        
        # Image preview (takes most space)
        self.image_preview = ImagePreviewWidget(self.images_directory)
        self.image_preview.imageChanged.connect(self.on_config_changed)
        middle_layout.addWidget(self.image_preview, stretch=3)
        
        # Greenscreen effects section
        effects_layout = QVBoxLayout()
        effects_layout.addWidget(QLabel("Efectos:"))
        
        self.greenscreen_button = QPushButton("Green Effects")
        self.greenscreen_button.clicked.connect(self.open_greenscreen_dialog)
        self.greenscreen_button.setMaximumWidth(120)
        effects_layout.addWidget(self.greenscreen_button)
        
        self.effects_count_label = QLabel("0 efectos")
        self.effects_count_label.setStyleSheet("color: #666; font-size: 11px;")
        effects_layout.addWidget(self.effects_count_label)
        
        effects_layout.addStretch()
        middle_layout.addLayout(effects_layout, stretch=1)
        
        group_layout.addLayout(middle_layout)
        
        # Bottom: Songs preview
        songs_label = QLabel("Canciones asignadas:")
        group_layout.addWidget(songs_label)
        
        self.songs_list_widget = QListWidget()
        self.songs_list_widget.setMaximumHeight(60)
        group_layout.addWidget(self.songs_list_widget)
        
        # Repetitions info
        self.repetitions_label = QLabel("Reproducciones: 0")
        group_layout.addWidget(self.repetitions_label)
        
        layout.addWidget(self.group_box)
        
    def get_songs_count(self):
        """Get the number of songs for this video"""
        return self.songs_spinbox.value()
    
    def set_songs_count(self, count):
        """Set the number of songs for this video"""
        self.songs_spinbox.setValue(count)
    
    def get_color(self):
        """Get the selected visualizer color"""
        return self.color_combo.currentText()
    
    def set_color(self, color):
        """Set the visualizer color"""
        index = self.color_combo.findText(color)
        if index >= 0:
            self.color_combo.setCurrentIndex(index)
    
    def get_repetitions(self):
        """Get the number of repetitions for this video"""
        return self.repetitions_spinbox.value()
    
    def set_repetitions(self, repetitions):
        """Set the number of repetitions for this video"""
        self.repetitions_spinbox.setValue(repetitions)
    
    def get_background_image(self):
        """Get the selected background image path"""
        return self.image_preview.get_selected_image()
    
    def set_background_image(self, filename):
        """Set the background image by filename"""
        self.image_preview.set_selected_image(filename)
    
    def update_songs_preview(self, songs, unique_songs=None, repetitions=0):
        """Update the preview of assigned songs with repetition info"""
        self.songs_list = songs
        self.songs_list_widget.clear()
        
        if songs:
            if unique_songs:
                # Show only unique songs in the list
                for song in unique_songs:
                    song_name = os.path.basename(song)
                    self.songs_list_widget.addItem(f"• {song_name}")
                
                # Update repetitions label
                if repetitions == 0:
                    self.repetitions_label.setText(f"Reproducciones: {len(songs)} (sin repetir)")
                else:
                    total_reproductions = len(songs)
                    self.repetitions_label.setText(f"Reproducciones: {total_reproductions} ({repetitions} repeticiones)")
            else:
                # Fallback: show all songs
                for song in songs:
                    song_name = os.path.basename(song)
                    self.songs_list_widget.addItem(f"• {song_name}")
                self.repetitions_label.setText(f"Reproducciones: {len(songs)}")
        else:
            self.songs_list_widget.addItem("Sin canciones asignadas")
            self.repetitions_label.setText("Reproducciones: 0")
    
    def get_songs_list(self):
        """Get the list of assigned songs"""
        return self.songs_list
    
    def open_greenscreen_dialog(self):
        """Open the greenscreen effects selection dialog"""
        dialog = GreenschreenEffectsDialog(self, self.greenscreen_effects)
        dialog.effects_changed.connect(self.on_effects_changed)
        dialog.exec()
    
    def on_effects_changed(self, effects):
        """Handle changes in greenscreen effects"""
        self.greenscreen_effects = effects
        self.update_effects_display()
        self.on_config_changed()
    
    def update_effects_display(self):
        """Update the display of selected effects"""
        count = len(self.greenscreen_effects)
        if count == 0:
            self.effects_count_label.setText("0 efectos")
            self.greenscreen_button.setStyleSheet("")
            self.greenscreen_button.setText("Green Effects")
            # Reset group box style
            self.group_box.setTitle(f"Video {self.video_number}")
            self.group_box.setStyleSheet("")
        else:
            effect_names = [effect.get('name', 'unnamed') for effect in self.greenscreen_effects]
            self.effects_count_label.setText(f"🎬 {count} efecto{'s' if count > 1 else ''}")
            self.effects_count_label.setToolTip(f"Efectos: {', '.join(effect_names)}")
            self.greenscreen_button.setStyleSheet("background-color: #e6ffe6; border: 2px solid #4CAF50; font-weight: bold;")
            self.greenscreen_button.setText("✅ Effects ON")
            # Highlight group box when effects are active
            self.group_box.setTitle(f"🎬 Video {self.video_number} (con efectos)")
            self.group_box.setStyleSheet("QGroupBox::title { color: #4CAF50; font-weight: bold; }")
    
    def get_greenscreen_effects(self):
        """Get the list of selected greenscreen effects"""
        return self.greenscreen_effects
    
    def set_greenscreen_effects(self, effects):
        """Set the greenscreen effects"""
        self.greenscreen_effects = effects
        self.update_effects_display()
    
    def on_config_changed(self):
        """Handle configuration changes"""
        self.configChanged.emit()
    
    def get_config(self):
        """Get the complete configuration for this video"""
        return {
            'video_number': self.video_number,
            'songs_count': self.get_songs_count(),
            'repetitions': self.get_repetitions(),
            'color': self.get_color(),
            'background_image': self.get_background_image(),
            'songs': self.get_songs_list(),
            'greenscreen_effects': self.get_greenscreen_effects()
        }