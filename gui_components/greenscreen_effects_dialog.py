"""
Greenscreen Effects Dialog for selecting and ordering effects with priority
"""

import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QListWidget, QListWidgetItem, 
                               QWidget, QFrame, QMessageBox, QScrollArea)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QIcon

from config import GREENSCREEN_CONFIG
from .chroma_preview_dialog import ChromaPreviewDialog


class EffectItem(QWidget):
    """Widget for individual effect item with preview and controls"""
    
    def __init__(self, effect_data, parent=None):
        super().__init__(parent)
        self.effect_data = effect_data
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Preview thumbnail (if image) or icon
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(60, 60)
        self.preview_label.setStyleSheet("border: 1px solid gray; background-color: #f0f0f0;")
        self.preview_label.setAlignment(Qt.AlignCenter)
        
        if self.effect_data['type'] == 'image' and self.effect_data['path'].lower().endswith('.png'):
            try:
                pixmap = QPixmap(self.effect_data['path'])
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(58, 58, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.preview_label.setPixmap(scaled_pixmap)
                else:
                    self.preview_label.setText("PNG")
            except:
                self.preview_label.setText("PNG")
        else:
            self.preview_label.setText("MP4" if self.effect_data['type'] == 'video' else "IMG")
        
        layout.addWidget(self.preview_label)
        
        # Effect info
        info_layout = QVBoxLayout()
        
        name_label = QLabel(self.effect_data['name'])
        name_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(name_label)
        
        type_label = QLabel(f"Type: {self.effect_data['type'].title()}")
        type_label.setStyleSheet("color: #666; font-size: 11px;")
        info_layout.addWidget(type_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # Preview chroma button for videos
        if self.effect_data['type'] == 'video':
            self.chroma_btn = QPushButton("Preview\nChroma")
            self.chroma_btn.setMaximumWidth(60)
            self.chroma_btn.setStyleSheet("font-size: 10px;")
            self.chroma_btn.clicked.connect(self.preview_chroma)
            layout.addWidget(self.chroma_btn)
    
    def preview_chroma(self):
        """Open chroma preview dialog for video effects"""
        if self.effect_data['type'] == 'video':
            dialog = ChromaPreviewDialog(self.effect_data['path'], self)
            dialog.parameters_changed.connect(self.on_chroma_parameters_changed)
            dialog.exec()
    
    def on_chroma_parameters_changed(self, similarity, tolerance):
        """Handle chroma parameter changes"""
        # Store the custom parameters in the effect data
        self.effect_data['custom_similarity'] = similarity
        self.effect_data['custom_tolerance'] = tolerance
        
        # Visual feedback that parameters were customized
        self.chroma_btn.setStyleSheet("font-size: 10px; background-color: #e6ffe6; border: 1px solid #4CAF50;")


class GreenschreenEffectsDialog(QDialog):
    """Dialog for selecting and ordering greenscreen effects"""
    
    effects_changed = Signal(list)  # Emits list of selected effects with priorities
    
    def __init__(self, parent=None, selected_effects=None):
        super().__init__(parent)
        self.available_effects = []
        self.selected_effects = selected_effects or []
        self.setup_ui()
        self.load_available_effects()
        self.populate_lists()
    
    def setup_ui(self):
        self.setWindowTitle("Greenscreen Effects")
        self.setModal(True)
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Select and Order Greenscreen Effects")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(header_label)
        
        # Info label
        info_label = QLabel("Effects will be applied in order from bottom to top (1 = bottom layer, higher numbers = top layers)")
        info_label.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Main content
        content_layout = QHBoxLayout()
        
        # Available effects section
        available_section = QVBoxLayout()
        available_label = QLabel("Available Effects")
        available_label.setStyleSheet("font-weight: bold;")
        available_section.addWidget(available_label)
        
        self.available_list = QListWidget()
        self.available_list.setDragDropMode(QListWidget.DragOnly)
        available_section.addWidget(self.available_list)
        
        content_layout.addLayout(available_section)
        
        # Control buttons
        controls_layout = QVBoxLayout()
        controls_layout.addStretch()
        
        self.add_button = QPushButton("Add →")
        self.add_button.clicked.connect(self.add_effect)
        controls_layout.addWidget(self.add_button)
        
        self.remove_button = QPushButton("← Remove")
        self.remove_button.clicked.connect(self.remove_effect)
        controls_layout.addWidget(self.remove_button)
        
        controls_layout.addStretch()
        
        self.move_up_button = QPushButton("Move Up ↑")
        self.move_up_button.clicked.connect(self.move_up)
        controls_layout.addWidget(self.move_up_button)
        
        self.move_down_button = QPushButton("Move Down ↓")
        self.move_down_button.clicked.connect(self.move_down)
        controls_layout.addWidget(self.move_down_button)
        
        controls_layout.addStretch()
        
        content_layout.addLayout(controls_layout)
        
        # Selected effects section
        selected_section = QVBoxLayout()
        selected_label = QLabel("Selected Effects (Bottom to Top)")
        selected_label.setStyleSheet("font-weight: bold;")
        selected_section.addWidget(selected_label)
        
        self.selected_list = QListWidget()
        self.selected_list.setDragDropMode(QListWidget.InternalMove)
        selected_section.addWidget(self.selected_list)
        
        priority_info = QLabel("Priority: 1 (bottom) → N (top)")
        priority_info.setStyleSheet("color: #666; font-size: 11px;")
        selected_section.addWidget(priority_info)
        
        content_layout.addLayout(selected_section)
        
        layout.addLayout(content_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.preview_button = QPushButton("Preview Order")
        self.preview_button.clicked.connect(self.preview_order)
        buttons_layout.addWidget(self.preview_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept_changes)
        ok_button.setDefault(True)
        buttons_layout.addWidget(ok_button)
        
        layout.addLayout(buttons_layout)
        
        # Connect list selection changes
        self.available_list.itemSelectionChanged.connect(self.update_button_states)
        self.selected_list.itemSelectionChanged.connect(self.update_button_states)
        
        self.update_button_states()
    
    def load_available_effects(self):
        """Load available effects from greenscreen directory"""
        self.available_effects = []
        
        if not os.path.exists(GREENSCREEN_CONFIG['directory']):
            return
        
        try:
            for file in os.listdir(GREENSCREEN_CONFIG['directory']):
                file_ext = os.path.splitext(file.lower())[1]
                if file_ext in GREENSCREEN_CONFIG['supported_formats']:
                    effect_path = os.path.join(GREENSCREEN_CONFIG['directory'], file)
                    effect_data = {
                        'name': os.path.splitext(file)[0],
                        'path': effect_path,
                        'type': 'video' if file_ext == '.mp4' else 'image'
                    }
                    self.available_effects.append(effect_data)
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Error loading effects: {e}")
    
    def populate_lists(self):
        """Populate available and selected lists"""
        # Populate available effects
        self.available_list.clear()
        selected_names = [effect['name'] for effect in self.selected_effects]
        
        for effect in self.available_effects:
            if effect['name'] not in selected_names:
                item = QListWidgetItem()
                widget = EffectItem(effect)
                item.setSizeHint(widget.sizeHint())
                item.setData(Qt.UserRole, effect)
                self.available_list.addItem(item)
                self.available_list.setItemWidget(item, widget)
        
        # Populate selected effects
        self.selected_list.clear()
        for i, effect in enumerate(self.selected_effects):
            item = QListWidgetItem()
            widget = EffectItem(effect)
            item.setSizeHint(widget.sizeHint())
            item.setData(Qt.UserRole, effect)
            item.setText(f"Priority {i+1}: {effect['name']}")
            self.selected_list.addItem(item)
            self.selected_list.setItemWidget(item, widget)
    
    def add_effect(self):
        """Add selected effect from available to selected list"""
        current_item = self.available_list.currentItem()
        if not current_item:
            return
        
        effect_data = current_item.data(Qt.UserRole)
        effect_data['priority'] = len(self.selected_effects) + 1
        self.selected_effects.append(effect_data)
        
        self.populate_lists()
        self.update_button_states()
    
    def remove_effect(self):
        """Remove selected effect from selected list"""
        current_row = self.selected_list.currentRow()
        if current_row < 0:
            return
        
        self.selected_effects.pop(current_row)
        
        # Update priorities
        for i, effect in enumerate(self.selected_effects):
            effect['priority'] = i + 1
        
        self.populate_lists()
        self.update_button_states()
    
    def move_up(self):
        """Move selected effect up in priority"""
        current_row = self.selected_list.currentRow()
        if current_row <= 0:
            return
        
        # Swap effects
        self.selected_effects[current_row], self.selected_effects[current_row - 1] = \
            self.selected_effects[current_row - 1], self.selected_effects[current_row]
        
        # Update priorities
        for i, effect in enumerate(self.selected_effects):
            effect['priority'] = i + 1
        
        self.populate_lists()
        self.selected_list.setCurrentRow(current_row - 1)
        self.update_button_states()
    
    def move_down(self):
        """Move selected effect down in priority"""
        current_row = self.selected_list.currentRow()
        if current_row < 0 or current_row >= len(self.selected_effects) - 1:
            return
        
        # Swap effects
        self.selected_effects[current_row], self.selected_effects[current_row + 1] = \
            self.selected_effects[current_row + 1], self.selected_effects[current_row]
        
        # Update priorities
        for i, effect in enumerate(self.selected_effects):
            effect['priority'] = i + 1
        
        self.populate_lists()
        self.selected_list.setCurrentRow(current_row + 1)
        self.update_button_states()
    
    def update_button_states(self):
        """Update button enabled states based on selections"""
        has_available = self.available_list.currentItem() is not None
        has_selected = self.selected_list.currentItem() is not None
        selected_row = self.selected_list.currentRow()
        
        self.add_button.setEnabled(has_available)
        self.remove_button.setEnabled(has_selected)
        self.move_up_button.setEnabled(has_selected and selected_row > 0)
        self.move_down_button.setEnabled(has_selected and selected_row < len(self.selected_effects) - 1)
    
    def preview_order(self):
        """Show preview of effect order"""
        if not self.selected_effects:
            QMessageBox.information(self, "Preview", "No effects selected.")
            return
        
        order_text = "Effect Order (Bottom to Top):\n\n"
        for i, effect in enumerate(self.selected_effects):
            order_text += f"{i+1}. {effect['name']} ({effect['type']})\n"
        
        QMessageBox.information(self, "Effect Order Preview", order_text)
    
    def accept_changes(self):
        """Accept changes and emit signal"""
        self.effects_changed.emit(self.selected_effects.copy())
        self.accept()
    
    def get_selected_effects(self):
        """Get the current selected effects"""
        return self.selected_effects.copy()