"""
YouTube Configuration Dialog for setting up upload parameters
"""

import logging
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QTextEdit, QPushButton, QComboBox,
                              QGroupBox, QFormLayout, QMessageBox, QProgressBar,
                              QSpinBox, QListWidget, QCalendarWidget, QCheckBox,
                              QScrollArea, QFrame, QWidget)
from PySide6.QtCore import Qt, QThread, Signal, QDate
from datetime import datetime, timedelta
from youtube_uploader import YouTubeUploader


class AuthenticationThread(QThread):
    """Thread for YouTube authentication to avoid blocking UI"""
    
    authentication_completed = Signal(bool, str)  # success, message
    
    def __init__(self, uploader):
        super().__init__()
        self.uploader = uploader
        
    def run(self):
        """Run authentication process"""
        try:
            success, channel_name = self.uploader.authenticate()
            if success:
                self.authentication_completed.emit(True, f"Autenticado como: {channel_name}")
            else:
                self.authentication_completed.emit(False, "Error en la autenticación")
        except Exception as e:
            self.authentication_completed.emit(False, f"Error: {str(e)}")


class YouTubeConfigDialog(QDialog):
    """Dialog for configuring YouTube upload settings"""
    
    def __init__(self, video_count, parent=None, mock_mode=False):
        super().__init__(parent)
        self.video_count = video_count
        self.mock_mode = mock_mode
        self.uploader = YouTubeUploader(mock_mode=mock_mode)
        self.authenticated = False
        self.logger = logging.getLogger(__name__)
        
        self.setup_ui()
        self.setup_default_values()
        
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("Configuración de YouTube")
        self.setModal(True)
        self.setMinimumSize(900, 1000)
        self.resize(950, 1050)
        
        layout = QVBoxLayout(self)
        
        # Authentication section
        auth_group = QGroupBox("Autenticación de YouTube")
        auth_layout = QVBoxLayout(auth_group)
        
        auth_button_layout = QHBoxLayout()
        self.auth_button = QPushButton("Iniciar Sesión en YouTube")
        self.auth_button.clicked.connect(self.authenticate_youtube)
        auth_button_layout.addWidget(self.auth_button)
        
        self.logout_button = QPushButton("Cerrar Sesión")
        self.logout_button.clicked.connect(self.logout_youtube)
        self.logout_button.setEnabled(False)
        auth_button_layout.addWidget(self.logout_button)
        
        auth_layout.addLayout(auth_button_layout)
        
        self.auth_status_label = QLabel("No autenticado")
        self.auth_status_label.setStyleSheet("color: red;")
        auth_layout.addWidget(self.auth_status_label)
        
        # Authentication progress bar
        self.auth_progress = QProgressBar()
        self.auth_progress.setVisible(False)
        auth_layout.addWidget(self.auth_progress)
        
        layout.addWidget(auth_group)
        
        # Upload mode selection
        mode_group = QGroupBox("Modo de Subida")
        mode_layout = QVBoxLayout(mode_group)
        
        self.immediate_radio = QCheckBox("Subir inmediatamente después de generar cada video")
        self.immediate_radio.setChecked(True)
        self.immediate_radio.toggled.connect(self.on_mode_changed)
        mode_layout.addWidget(self.immediate_radio)
        
        self.scheduled_radio = QCheckBox("Programar subidas con calendario y horarios")
        self.scheduled_radio.toggled.connect(self.on_mode_changed)
        mode_layout.addWidget(self.scheduled_radio)
        
        layout.addWidget(mode_group)
        
        # Video metadata section
        metadata_group = QGroupBox("Configuración de Videos")
        metadata_layout = QFormLayout(metadata_group)
        
        # Title sequence
        self.title_sequence_edit = QLineEdit()
        self.title_sequence_edit.setPlaceholderText("Mi Serie Musical #{}")
        metadata_layout.addRow("Título base (use {} para numeración):", self.title_sequence_edit)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(150)
        self.description_edit.setPlaceholderText("Descripción que se aplicará a todos los videos...")
        metadata_layout.addRow("Descripción:", self.description_edit)
        
        # Tags
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("música, video, serie, tag1, tag2")
        metadata_layout.addRow("Tags (separados por comas):", self.tags_edit)
        
        # Category
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "Música",
            "Entretenimiento", 
            "Videojuegos",
            "Educación"
        ])
        metadata_layout.addRow("Categoría:", self.category_combo)
        
        # Privacy
        self.privacy_combo = QComboBox()
        self.privacy_combo.addItems([
            "public",
            "unlisted", 
            "private"
        ])
        self.privacy_combo.setCurrentText("public")
        metadata_layout.addRow("Privacidad:", self.privacy_combo)
        
        layout.addWidget(metadata_group)
        
        # Scheduling section (initially hidden)
        self.scheduling_group = QGroupBox("Programación de Subidas")
        self.setup_scheduling_section()
        self.scheduling_group.setVisible(False)
        layout.addWidget(self.scheduling_group)
        
        # Video information
        info_group = QGroupBox("Información")
        info_layout = QVBoxLayout(info_group)
        
        self.video_info_label = QLabel(f"Se subirán {self.video_count} videos")
        info_layout.addWidget(self.video_info_label)
        
        self.quota_info_label = QLabel("Límite diario: 6 videos (API no verificada)")
        info_layout.addWidget(self.quota_info_label)
        
        layout.addWidget(info_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QPushButton("Cancelar")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        self.accept_button = QPushButton("Aceptar")
        self.accept_button.clicked.connect(self.accept_config)
        self.accept_button.setEnabled(False)
        self.accept_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        button_layout.addWidget(self.accept_button)
        
        layout.addLayout(button_layout)
        
    def setup_default_values(self):
        """Setup default values for the form"""
        self.title_sequence_edit.setText("Mi Serie Musical #{}")
        self.description_edit.setPlainText(
            "Serie de videos musicales generados automáticamente.\n\n"
            "🎵 Música original\n"
            "🎬 Video generado con IA\n"
            "✨ Efectos visuales sincronizados\n\n"
            "#música #videosmusical #ai #generativo"
        )
        self.tags_edit.setText("música, video musical, ai, generativo, serie musical, efectos visuales, audio reactivo")
        
    def authenticate_youtube(self):
        """Start YouTube authentication process"""
        self.auth_button.setEnabled(False)
        self.auth_progress.setVisible(True)
        self.auth_progress.setRange(0, 0)  # Indeterminate progress
        self.auth_status_label.setText("Autenticando...")
        self.auth_status_label.setStyleSheet("color: orange;")
        
        # Start authentication in separate thread
        self.auth_thread = AuthenticationThread(self.uploader)
        self.auth_thread.authentication_completed.connect(self.on_authentication_completed)
        self.auth_thread.start()
        
    def on_authentication_completed(self, success, message):
        """Handle authentication completion"""
        self.auth_progress.setVisible(False)
        self.auth_button.setEnabled(True)
        
        if success:
            self.authenticated = True
            self.auth_status_label.setText(message)
            self.auth_status_label.setStyleSheet("color: green;")
            self.logout_button.setEnabled(True)
            self.accept_button.setEnabled(True)
            self.logger.info("YouTube authentication successful")
        else:
            self.authenticated = False
            self.auth_status_label.setText(message)
            self.auth_status_label.setStyleSheet("color: red;")
            self.logout_button.setEnabled(False)
            self.accept_button.setEnabled(False)
            self.logger.error(f"YouTube authentication failed: {message}")
            
            # Show error dialog
            QMessageBox.warning(
                self,
                "Error de Autenticación",
                f"No se pudo autenticar con YouTube:\n\n{message}\n\n"
                "Asegúrate de tener configurado correctamente el archivo client_secret.json"
            )
            
    def logout_youtube(self):
        """Logout from YouTube"""
        self.uploader.logout()
        self.authenticated = False
        self.auth_status_label.setText("Sesión cerrada")
        self.auth_status_label.setStyleSheet("color: red;")
        self.logout_button.setEnabled(False)
        self.accept_button.setEnabled(False)
        self.logger.info("YouTube logout successful")
        
    def accept_config(self):
        """Accept the configuration and close dialog"""
        # Validate form
        if not self.authenticated:
            QMessageBox.warning(self, "Error", "Debe autenticarse con YouTube primero")
            return
            
        title_base = self.title_sequence_edit.text().strip()
        if not title_base:
            QMessageBox.warning(self, "Error", "Debe especificar un título base")
            return
            
        if "{}" not in title_base:
            QMessageBox.warning(
                self, 
                "Error", 
                "El título debe contener {} para la numeración automática\n\n"
                "Ejemplo: Mi Serie Musical #{}"
            )
            return
            
        description = self.description_edit.toPlainText().strip()
        if not description:
            QMessageBox.warning(self, "Error", "Debe especificar una descripción")
            return
            
        tags = self.tags_edit.text().strip()
        if not tags:
            QMessageBox.warning(self, "Error", "Debe especificar al menos un tag")
            return
            
        # Check quota warning
        if self.video_count > 6:
            reply = QMessageBox.question(
                self,
                "Advertencia de Cuota",
                f"Planea subir {self.video_count} videos, pero el límite diario es de 6.\n\n"
                "El proceso se pausará automáticamente después de 6 videos y esperará 24.5 horas "
                "antes de continuar.\n\n¿Desea continuar?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
                
        self.accept()
        
    def get_config(self):
        """Get the YouTube configuration"""
        if not self.authenticated:
            return None
            
        # Map category names to YouTube category IDs
        category_map = {
            "Música": "10",
            "Entretenimiento": "24",
            "Videojuegos": "20", 
            "Educación": "27"
        }
        
        return {
            'title_base': self.title_sequence_edit.text().strip(),
            'description': self.description_edit.toPlainText().strip(),
            'tags': self.tags_edit.text().strip(),
            'category_id': category_map.get(self.category_combo.currentText(), "10"),
            'privacy_status': self.privacy_combo.currentText(),
            'uploader': self.uploader,  # Pass the authenticated uploader
            'immediate_mode': self.immediate_radio.isChecked(),
            'scheduling': self.get_scheduling_config() if self.scheduled_radio.isChecked() else None
        }
        
    def setup_scheduling_section(self):
        """Setup the scheduling configuration section"""
        scheduling_layout = QVBoxLayout(self.scheduling_group)
        
        # Videos per day configuration
        videos_per_day_layout = QHBoxLayout()
        videos_per_day_layout.addWidget(QLabel("Videos por día:"))
        self.videos_per_day_spinbox = QSpinBox()
        self.videos_per_day_spinbox.setMinimum(1)
        self.videos_per_day_spinbox.setMaximum(6)  # YouTube API limit
        self.videos_per_day_spinbox.setValue(2)
        self.videos_per_day_spinbox.valueChanged.connect(self.update_time_slots)
        videos_per_day_layout.addWidget(self.videos_per_day_spinbox)
        videos_per_day_layout.addStretch()
        scheduling_layout.addLayout(videos_per_day_layout)
        
        # Time slots
        self.time_slots_group = QGroupBox("Horarios de Subida")
        self.time_slots_layout = QVBoxLayout(self.time_slots_group)
        self.time_slots = []
        self.update_time_slots()
        scheduling_layout.addWidget(self.time_slots_group)
        
        # Date range selection
        date_range_layout = QHBoxLayout()
        
        # Start date
        start_date_layout = QVBoxLayout()
        start_date_layout.addWidget(QLabel("Fecha de inicio:"))
        self.start_date_edit = QLineEdit()
        self.start_date_edit.setReadOnly(True)
        self.start_date_edit.setText(datetime.now().strftime('%d/%m/%Y'))
        start_date_layout.addWidget(self.start_date_edit)
        
        self.start_date_button = QPushButton("Seleccionar")
        self.start_date_button.clicked.connect(lambda: self.show_calendar(self.start_date_edit))
        start_date_layout.addWidget(self.start_date_button)
        
        # End date
        end_date_layout = QVBoxLayout()
        end_date_layout.addWidget(QLabel("Fecha de fin:"))
        self.end_date_edit = QLineEdit()
        self.end_date_edit.setReadOnly(True)
        # Default to 7 days from now
        end_date = datetime.now() + timedelta(days=7)
        self.end_date_edit.setText(end_date.strftime('%d/%m/%Y'))
        end_date_layout.addWidget(self.end_date_edit)
        
        self.end_date_button = QPushButton("Seleccionar")
        self.end_date_button.clicked.connect(lambda: self.show_calendar(self.end_date_edit))
        end_date_layout.addWidget(self.end_date_button)
        
        date_range_layout.addLayout(start_date_layout)
        date_range_layout.addLayout(end_date_layout)
        scheduling_layout.addLayout(date_range_layout)
        
        # Preview button
        self.preview_button = QPushButton("Vista Previa de Programación")
        self.preview_button.clicked.connect(self.show_scheduling_preview)
        scheduling_layout.addWidget(self.preview_button)
        
        # Preview list
        self.schedule_preview = QListWidget()
        self.schedule_preview.setMaximumHeight(150)
        scheduling_layout.addWidget(QLabel("Vista previa:"))
        scheduling_layout.addWidget(self.schedule_preview)
        
    def update_time_slots(self):
        """Update time slot selectors based on videos per day"""
        # Clear existing time slots and layouts
        for slot in self.time_slots:
            slot.setParent(None)
            slot.deleteLater()
        self.time_slots.clear()
        
        # Clear existing layouts
        while self.time_slots_layout.count():
            child = self.time_slots_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_layout(child.layout())
        
        # Generate time intervals (15-minute intervals)
        time_intervals = []
        for hour in range(24):
            for minute in [0, 15, 30, 45]:
                time_intervals.append(f"{hour:02d}:{minute:02d}")
        
        # Create time slot selectors
        videos_per_day = self.videos_per_day_spinbox.value()
        for i in range(videos_per_day):
            slot_widget = QWidget()
            slot_layout = QHBoxLayout(slot_widget)
            slot_layout.setContentsMargins(0, 0, 0, 0)
            
            slot_layout.addWidget(QLabel(f"Horario {i+1}:"))
            
            time_combo = QComboBox()
            time_combo.addItems(time_intervals)
            # Set default times spread throughout the day
            default_hour = int(8 + (i * 12 / videos_per_day))  # Spread from 8 AM
            default_time = f"{default_hour:02d}:00"
            if default_time in time_intervals:
                time_combo.setCurrentText(default_time)
            
            slot_layout.addWidget(time_combo)
            slot_layout.addStretch()
            
            self.time_slots.append(time_combo)
            self.time_slots_layout.addWidget(slot_widget)
    
    def _clear_layout(self, layout):
        """Helper method to clear a layout completely"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_layout(child.layout())
    
    def show_calendar(self, target_edit):
        """Show calendar widget for date selection"""
        calendar_dialog = QDialog(self)
        calendar_dialog.setWindowTitle("Seleccionar Fecha")
        calendar_dialog.setModal(True)
        
        layout = QVBoxLayout(calendar_dialog)
        
        calendar = QCalendarWidget()
        calendar.setMinimumDate(QDate.currentDate())  # Can't select past dates
        layout.addWidget(calendar)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QPushButton("Cancelar")
        cancel_button.clicked.connect(calendar_dialog.reject)
        button_layout.addWidget(cancel_button)
        
        select_button = QPushButton("Seleccionar")
        def on_select():
            selected_date = calendar.selectedDate()
            target_edit.setText(selected_date.toString("dd/MM/yyyy"))
            calendar_dialog.accept()
        select_button.clicked.connect(on_select)
        button_layout.addWidget(select_button)
        
        layout.addLayout(button_layout)
        calendar_dialog.exec()
    
    def show_scheduling_preview(self):
        """Show preview of scheduled uploads"""
        try:
            schedule = self.generate_upload_schedule()
            
            self.schedule_preview.clear()
            for item in schedule:
                self.schedule_preview.addItem(
                    f"{item['date']} {item['time']} - {item['title']}"
                )
                
            if len(schedule) > self.video_count:
                QMessageBox.warning(
                    self,
                    "Advertencia",
                    f"La programación generará {len(schedule)} slots pero solo hay {self.video_count} videos."
                )
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error generando vista previa: {str(e)}")
    
    def generate_upload_schedule(self):
        """Generate the upload schedule based on configuration"""
        try:
            start_date = datetime.strptime(self.start_date_edit.text(), '%d/%m/%Y')
            end_date = datetime.strptime(self.end_date_edit.text(), '%d/%m/%Y')
        except ValueError:
            raise Exception("Fechas inválidas")
            
        if start_date > end_date:
            raise Exception("La fecha de inicio debe ser anterior a la fecha de fin")
            
        schedule = []
        current_date = start_date
        video_number = 1
        
        while current_date <= end_date and video_number <= self.video_count:
            for time_slot in self.time_slots:
                if video_number > self.video_count:
                    break
                    
                time_str = time_slot.currentText()
                title_base = self.title_sequence_edit.text().strip()
                title = title_base.replace('{}', str(video_number))
                
                # Convert to UTC for YouTube API
                publish_at = self.convert_to_utc_rfc3339(
                    current_date.strftime('%Y-%m-%d'), 
                    time_str
                )
                
                schedule.append({
                    'video_number': video_number,
                    'date': current_date.strftime('%Y-%m-%d'),
                    'time': time_str,
                    'title': title,
                    'publish_at': publish_at
                })
                
                video_number += 1
                
            current_date += timedelta(days=1)
            
        return schedule
    
    def convert_to_utc_rfc3339(self, date_str, time_str, timezone='America/Argentina/Buenos_Aires'):
        """Convert local date/time to UTC RFC3339 format"""
        import pytz
        
        # Combine date and time
        datetime_str = f'{date_str} {time_str}'
        local_dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
        
        # Localize to specified timezone
        local_tz = pytz.timezone(timezone)
        local_dt = local_tz.localize(local_dt, is_dst=None)
        
        # Convert to UTC
        utc_dt = local_dt.astimezone(pytz.utc)
        
        # Return RFC3339 format
        return utc_dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    
    def get_scheduling_config(self):
        """Get scheduling configuration"""
        if not self.scheduled_radio.isChecked():
            return None
            
        try:
            return {
                'schedule': self.generate_upload_schedule(),
                'videos_per_day': self.videos_per_day_spinbox.value(),
                'start_date': self.start_date_edit.text(),
                'end_date': self.end_date_edit.text()
            }
        except Exception as e:
            return None
    
    def on_mode_changed(self):
        """Handle mode change between immediate and scheduled"""
        sender = self.sender()
        
        if sender == self.immediate_radio and self.immediate_radio.isChecked():
            self.scheduled_radio.setChecked(False)
            self.scheduling_group.setVisible(False)
        elif sender == self.scheduled_radio and self.scheduled_radio.isChecked():
            self.immediate_radio.setChecked(False)
            self.scheduling_group.setVisible(True)
        elif sender == self.immediate_radio and not self.immediate_radio.isChecked():
            # If immediate unchecked, auto-check scheduled if not already checked
            if not self.scheduled_radio.isChecked():
                self.scheduled_radio.setChecked(True)
                self.scheduling_group.setVisible(True)
        elif sender == self.scheduled_radio and not self.scheduled_radio.isChecked():
            # If scheduled unchecked, auto-check immediate if not already checked
            if not self.immediate_radio.isChecked():
                self.immediate_radio.setChecked(True)
                self.scheduling_group.setVisible(False)