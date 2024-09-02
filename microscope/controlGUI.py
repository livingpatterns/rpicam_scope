#!/usr/bin/env python3

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, QLineEdit, QShortcut, QMessageBox, QSpinBox, QHBoxLayout, QFileDialog
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt
import os

from microscope_control import Microscope


class ControlGUI(QWidget):
    """ ControlGUI class
    
    A PyQt5 QWidget-based class that provides a user interface for controlling a microscope camera. The GUI
    supports switching between image and video modes, selecting resolutions, adjusting framerate and duration
    for video capture, starting/stopping previews, and capturing images or videos based on the selected settings.
    """
    
    def __init__(self):
        super().__init__()
        self.left = 100
        self.top = 100
        self.width = 400
        self.height = 700
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle('Microscope Camera Control')

        self.preview_running = False
        
        self.microscope = Microscope()
        
        self.save_folder = os.path.join(os.path.expanduser('~'), 'Desktop')

        layout = QVBoxLayout()
        self.pi_model = QLabel(f"Raspberry Pi Model: {self.microscope.get_pi_model()}")
        layout.addWidget(self.pi_model)

        # Mode box
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(['image', 'video', 'timelapse'])
        self.mode_combo.currentIndexChanged.connect(self.update_fields)
        layout.addWidget(QLabel('Select Mode:'))
        layout.addWidget(self.mode_combo)

        # Resolution box
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(['1: 1332x990 - Max 120 FPS', '2: 2028x1080 - Max 50 FPS', '3: 2028x1520 - Max 40 FPS', '4: 4056x3040 - Max 10 FPS'])
        self.resolution_combo.currentIndexChanged.connect(self.resolution_changed)
        layout.addWidget(QLabel('Select Resolution:'))
        layout.addWidget(self.resolution_combo)
        
        # Preview button
        self.preview_running = False 
        self.preview_button = QPushButton('Start Preview [P]')
        self.preview_button.clicked.connect(self.toggle_preview)
        layout.addWidget(self.preview_button)
        QShortcut(QKeySequence("P"), self, activated=self.toggle_preview)

        # Filename 
        self.filename_edit = QLineEdit()
        layout.addWidget(QLabel('Enter Filename:'))
        layout.addWidget(self.filename_edit)
        
        # Browse button
        self.browse_button = QPushButton('Browse Folder')
        self.browse_button.clicked.connect(self.browse_folder)
        layout.addWidget(self.browse_button)
        self.path_display = QLabel(f"Save Path: {self.save_folder}")
        layout.addWidget(self.path_display)
        
        # Interval box for timelapse
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 3600)
        self.interval_spin.setSuffix(' s/frame')
        layout.addWidget(QLabel('Enter Interval (seconds per frame):'))
        layout.addWidget(self.interval_spin)

        # Framerate (video only)
        self.framerate_edit = QLineEdit()
        layout.addWidget(QLabel('Enter desired Framerate (leave blank for max possible FPS)'))

        layout.addWidget(self.framerate_edit)

        # Duration (video only) with hours, minutes, seconds
        self.duration_hours_spin = QSpinBox()
        self.duration_hours_spin.setRange(0, 23)
        self.duration_hours_spin.setSuffix('h')

        self.duration_minutes_spin = QSpinBox()
        self.duration_minutes_spin.setRange(0, 59)
        self.duration_minutes_spin.setSuffix('m')

        self.duration_seconds_spin = QSpinBox()
        self.duration_seconds_spin.setRange(0, 59)
        self.duration_seconds_spin.setSuffix('s')
        self.duration_seconds_spin.setValue(10)  # Set default duration to 10 seconds


        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel('Enter Duration:'))
        duration_layout.addWidget(self.duration_hours_spin)
        duration_layout.addWidget(self.duration_minutes_spin)
        duration_layout.addWidget(self.duration_seconds_spin)
        layout.addLayout(duration_layout)
        
        # Capture button
        self.capture_button = QPushButton('Capture [Enter]')
        self.capture_button.clicked.connect(self.capture)
        layout.addWidget(self.capture_button)
        QShortcut(QKeySequence(Qt.Key_Return), self, activated=self.capture)

        self.setLayout(layout)
        self.update_fields()

        
    def update_fields(self):
        """
        Updates the availability of framerate and duration input fields based on the selected mode. 
        Disables these fields if the 'image' mode is selected, enables them if 'video' is selected.
        """
        mode = self.mode_combo.currentText()
            
        if mode == 'video':
            self.framerate_edit.setEnabled(True)
            self.interval_spin.setEnabled(False)
            self.duration_hours_spin.setEnabled(True)
            self.duration_minutes_spin.setEnabled(True)
            self.duration_seconds_spin.setEnabled(True)
        elif mode == 'timelapse':
            self.framerate_edit.setEnabled(False)
            self.interval_spin.setEnabled(True)
            self.duration_hours_spin.setEnabled(True)
            self.duration_minutes_spin.setEnabled(True)
            self.duration_seconds_spin.setEnabled(True)
        else:
            self.framerate_edit.setEnabled(False)
            self.interval_spin.setEnabled(False)
            self.duration_hours_spin.setEnabled(False)
            self.duration_minutes_spin.setEnabled(False)
            self.duration_seconds_spin.setEnabled(False)
            
    def parse_duration(self, duration_text):
        """
        Converts a duration in hours:minutes:seconds format to total seconds.

        Params:
            duration_text (str): Duration in hours:minutes:seconds format.

        Return:
            int: Total duration in seconds, or None if the format is invalid.
        """
        try:
            parts = duration_text.split(':')
            if len(parts) == 3:
                hours, minutes, seconds = map(int, parts)
                return hours * 3600 + minutes * 60 + seconds
            return None
        except ValueError:
            return None
               
    def toggle_preview(self):
        """
        Toggles the preview state of the microscope camera. If preview is running, it stops it;
        otherwise, it starts it based on the currently selected resolution.
        """
        if self.preview_running:
            self.microscope.stop_preview()
            self.preview_running = False
            self.preview_button.setText('Start Preview [P]')
        else:
            self.set_preview()

    def set_preview(self):
        """
        Starts the preview of the microscope camera using the selected resolution key from the resolution combo box.
        """
        res_key = self.resolution_combo.currentText().split(':')[0]
        self.microscope.start_preview(res_key)
        self.preview_running = True
        self.preview_button.setText('Stop Preview [P]')
        
    def resolution_changed(self):        
        """
        Handles the action of changing resolution. If the preview is currently running, it stops and restarts the preview
        with the new resolution.
        """
        if self.preview_running:
            self.microscope.stop_preview()
            self.set_preview()

    def capture(self):
        """
        Handles capturing an image or recording a video. If preview is running, it first stops the preview.
        Captures based on the current mode, resolution, filename, framerate, and duration settings.
        """
        try:
            self.microscope.stop_preview()
            self.preview_running = False
            self.preview_button.setText('Start Preview [P]')
            
            mode = self.mode_combo.currentText()
            resolution = self.resolution_combo.currentText().split(':')[0]
            filename = self.filename_edit.text() 
            framerate = self.framerate_edit.text() if self.framerate_edit.text() else None
            
            duration_str = f'{self.duration_hours_spin.value():02}:{self.duration_minutes_spin.value():02}:{self.duration_seconds_spin.value():02}'
            duration = self.parse_duration(duration_str)

            if duration is None:
                raise ValueError("Invalid duration format. Use hours:minutes:seconds.")

            # Construct the full file path
            full_filename = os.path.join(self.save_folder, filename)
            
            if mode == 'video':
                self.microscope.record_video(resolution, framerate, duration, full_filename)
            elif mode == 'timelapse':
                interval = self.interval_spin.value()
                self.microscope.capture_timelapse(resolution, interval, duration, full_filename)
            else:
                self.microscope.capture_image(resolution, full_filename)
        except ValueError as e:
            QMessageBox.warning(self, 'Input Error', str(e))
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An unexpected error occurred: \n {str(e)}')
            
    def browse_folder(self):
        """
        Opens a dialog to select a folder for saving files.
        """
        folder = QFileDialog.getExistingDirectory(self, "Select Directoryr", self.save_folder)
        if folder:
            self.save_folder = folder
            self.path_display.setText(f"Save Path: {self.save_folder}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ControlGUI()
    ex.show()
    sys.exit(app.exec_())
