import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, QLineEdit, QShortcut
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt

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
        self.height = 500
        self.setWindowFlags(Qt.Window)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle('Microscope Camera Control')
        
        self.preview_running = False
        
        self.microscope = Microscope()

        layout = QVBoxLayout()

        # Mode box
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(['image', 'video'])
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
        

        # Framerate (video only)
        self.framerate_edit = QLineEdit()
        layout.addWidget(QLabel('Enter Framerate (or "default" for max possible FPS)'))
        layout.addWidget(self.framerate_edit)

        # Duration (video only)
        self.duration_edit = QLineEdit()
        layout.addWidget(QLabel('Enter Duration (seconds)'))
        layout.addWidget(self.duration_edit)
        
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
            self.duration_edit.setEnabled(True)
        else:
            self.framerate_edit.setEnabled(False)
            self.duration_edit.setEnabled(False)
               
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
        # First stop the current preview 
        self.microscope.stop_preview()
        self.preview_running = False
        self.preview_button.setText('Start Preview [P]')
        
        mode = self.mode_combo.currentText()
        resolution = self.resolution_combo.currentText().split(':')[0]
        filename = self.filename_edit.text()
        framerate = self.framerate_edit.text() if self.framerate_edit.text() else 'default'
        duration = int(self.duration_edit.text()) if self.duration_edit.text() else 10

        if mode == 'video':
            self.microscope.record_video(resolution, framerate, duration, filename)
        else:
            self.microscope.capture_image(resolution, filename)
        self.microscope.stop_preview()
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ControlGUI()
    ex.show()
    sys.exit(app.exec_())
