import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QProgressBar, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QFont, QKeyEvent
from PySide6.QtWidgets import QMessageBox
import subprocess
from PySide6.QtWidgets import QFileDialog, QMessageBox
FREECAD_PYTHON = r"E:\FreeCAD\bin\python.exe"   ## CHANGGEEE____________________________

class GrashofApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Grashof Linkage generator")
        self.setStyleSheet("background-color: #A9A9A9;") 
        self.setWindowFlag(Qt.FramelessWindowHint)  
        self.showFullScreen()
        

    
         # Background label with image at 30% opacity
        self.bg_label = QLabel(self)
        pixmap = QPixmap(r"C:\Users\aadia\Downloads\360_F_766665129_7Hd9T63kdA76k7Z2RmIE1yumK6bW239p.jpg")
        self.bg_label.setPixmap(pixmap)
        self.bg_label.setScaledContents(True)
        self.bg_label.setGeometry(0, 0, self.width(), self.height())

        
       

        # Container widget with white transparent background
        self.container = QWidget(self)
        self.container.setStyleSheet(
            "background-color: rgba(255, 255, 255, 180);"
            "border-radius: 15px;"
        )
        self.container.setFixedWidth(500)

        # Layouts inside container
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(30, 30, 30, 30)
        container_layout.setSpacing(20)

        # Heading label
        heading = QLabel("Enter Length of Links")
        heading.setStyleSheet("color: black;")
        heading.setFont(QFont("Arial", 24, QFont.Bold))
        heading.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(heading)

        # Input fields for 4 links
        self.inputs = []
        for i in range(1, 5):
            hbox = QHBoxLayout()
            label = QLabel(f"Length of Link {i}:")
            label.setFont(QFont("Arial", 14))
            label.setStyleSheet("color: black;")
            input_box = QLineEdit()
            input_box.setFont(QFont("Arial", 14))
            input_box.setPlaceholderText("Enter length")
            input_box.setStyleSheet("color: black; background-color: white;")
            self.inputs.append(input_box)
            hbox.addWidget(label)
            hbox.addWidget(input_box)
            container_layout.addLayout(hbox)

        # Generate button
        self.generate_btn = QPushButton("Generate")
        self.generate_btn.setStyleSheet("color: black; background-color: lightgrey;")
        self.generate_btn.setFont(QFont("Arial", 16, QFont.Bold))
        self.generate_btn.setFixedHeight(40)
        container_layout.addWidget(self.generate_btn)

        # Loading bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(25)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.hide()
        container_layout.addWidget(self.progress_bar)

        # Main layout to center container
        main_layout = QHBoxLayout(self)
        main_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        main_layout.addWidget(self.container)
        main_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.generate_btn.clicked.connect(self.start_loading)

    def resizeEvent(self, event):
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        self.container.move(
            (self.width() - self.container.width()) // 2,
            (self.height() - self.container.height()) // 2
        )
        super().resizeEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            self.showNormal()  
            self.setWindowFlag(Qt.FramelessWindowHint, False)  
            self.setGeometry(100, 100, 800, 600)  
            self.show()  
        else:
            super().keyPressEvent(event)

    
    def start_loading(self):
        try:
            # Read and convert input values to float
            lengths = [float(input_box.text()) for input_box in self.inputs]

            if len(lengths) != 4:
                raise ValueError("Exactly 4 links are required.")

            sorted_lengths = sorted(lengths)
            s = sorted_lengths[0] + sorted_lengths[3]  
            m = sorted_lengths[1] + sorted_lengths[2]
            
            if s > m:
                # Not a Grashof linkage
                QMessageBox.warning(self, "Invalid Linkage", "Please enter a Grashof Linkage.")
                return

            # Passed Grashof condition, start progress
            self.generate_btn.setEnabled(False)
            self.progress_bar.setValue(0)
            self.progress_bar.show()

            self.timer = QTimer()
            self.timer.timeout.connect(self.update_progress)
            self.progress_value = 0
            self.timer.start(30)

        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid numeric lengths for all links.")
    '''
    def update_progress(self):
        self.progress_value += 1
        self.progress_bar.setValue(self.progress_value)
        if self.progress_value >= 100:
            self.timer.stop()
            self.generate_btn.setEnabled(True)
            self.progress_bar.hide()
    '''


    def update_progress(self):
        self.progress_value += 1
        self.progress_bar.setValue(self.progress_value)
        if self.progress_value >= 100:
            self.timer.stop()
            self.generate_btn.setEnabled(True)
            self.progress_bar.hide()

            # Ask where to save the CAD file
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save CAD File", "", "STEP Files (*.step)"
            )
            if not file_path:
                return  # user cancelled

            # Collect link lengths
            lengths = [float(input_box.text()) for input_box in self.inputs]

            # Call FreeCAD's Python to generate the file
            try:
                subprocess.run(
                    [FREECAD_PYTHON, "myfirstscript.py",              ## CHANGGEEE____________________________
                     str(lengths[0]), str(lengths[1]), str(lengths[2]), str(lengths[3]),
                     file_path],
                    check=True
                )
                QMessageBox.information(self, "Success", f"CAD file saved:\n{file_path}")
            except subprocess.CalledProcessError as e:
                QMessageBox.critical(self, "Error", f"CAD generation failed:\n{e}")

            

if __name__ == "__main__":
    from PySide6 import QtGui

    app = QApplication(sys.argv)
    window = GrashofApp()
    window.show()
    sys.exit(app.exec())
