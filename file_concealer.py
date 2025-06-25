import sys
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                             QLabel, QPushButton, QGridLayout, QFrame, 
                             QMessageBox, QGroupBox, QTextEdit, QLineEdit,
                             QFileDialog, QTabWidget, QProgressBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from PIL import Image
import numpy as np


class ConcealThread(QThread):
    """Thread for concealing files to avoid UI freezing"""
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    
    def __init__(self, file_path, image_path, key, output_dir):
        super().__init__()
        self.file_path = file_path
        self.image_path = image_path
        self.key = key
        self.output_dir = output_dir
    
    def run(self):
        try:
            self.status.emit("🔄 Reading input file...")
            self.progress.emit(10)
            
            # Read the file to be concealed
            with open(self.file_path, 'rb') as f:
                file_data = f.read()
            
            self.status.emit("🔐 Encrypting file data...")
            self.progress.emit(25)
            
            # Encrypt the file data if key is provided
            if self.key:
                # Generate a key from the password
                salt = os.urandom(16)
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,
                )
                key = base64.urlsafe_b64encode(kdf.derive(self.key.encode()))
                f = Fernet(key)
                file_data = salt + f.encrypt(file_data)
            
            self.status.emit("📷 Loading cover image...")
            self.progress.emit(40)
            
            # Load the cover image
            img = Image.open(self.image_path).convert('RGB')
            img_array = np.array(img)
            
            # Convert file data to binary string
            file_data_bits = ''.join(format(byte, '08b') for byte in file_data)
            
            # Add a delimiter to mark the end of the hidden data
            delimiter = '1111111111111110'  # 16-bit delimiter
            file_data_bits += delimiter
            
            self.status.emit("🔄 Concealing data in image...")
            self.progress.emit(60)
            
            # Check if the image can hold the data
            total_pixels = img_array.shape[0] * img_array.shape[1] * img_array.shape[2]
            if len(file_data_bits) > total_pixels:
                self.finished_signal.emit(False, "Image is too small to hold the file data!")
                return
            
            # Hide the data in the least significant bits
            flat_img = img_array.flatten()
            data_index = 0
            
            for i in range(len(file_data_bits)):
                if data_index < len(flat_img):
                    # Modify the least significant bit
                    flat_img[data_index] = (flat_img[data_index] & 0xFE) | int(file_data_bits[i])
                    data_index += 1
            
            self.status.emit("💾 Saving concealed image...")
            self.progress.emit(80)
            
            # Reshape and save the image
            concealed_img_array = flat_img.reshape(img_array.shape)
            concealed_img = Image.fromarray(concealed_img_array.astype('uint8'))
            
            # Generate output filename
            base_name = os.path.splitext(os.path.basename(self.image_path))[0]
            output_path = os.path.join(self.output_dir, f"{base_name}_concealed.png")
            
            concealed_img.save(output_path, 'PNG')
            
            self.progress.emit(100)
            self.status.emit("✅ File concealed successfully!")
            self.finished_signal.emit(True, f"File concealed successfully!\nOutput: {output_path}")
            
        except Exception as e:
            self.finished_signal.emit(False, f"Error concealing file: {str(e)}")


class RevealThread(QThread):
    """Thread for revealing files to avoid UI freezing"""
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    
    def __init__(self, image_path, key, output_dir):
        super().__init__()
        self.image_path = image_path
        self.key = key
        self.output_dir = output_dir
    
    def run(self):
        try:
            self.status.emit("📷 Loading concealed image...")
            self.progress.emit(10)
            
            # Load the concealed image
            img = Image.open(self.image_path).convert('RGB')
            img_array = np.array(img)
            flat_img = img_array.flatten()
            
            self.status.emit("🔍 Extracting hidden data...")
            self.progress.emit(30)
            
            # Extract bits from the least significant bits
            binary_data = ''
            delimiter = '1111111111111110'  # 16-bit delimiter
            
            for pixel_value in flat_img:
                binary_data += str(pixel_value & 1)
                
                # Check for delimiter
                if binary_data.endswith(delimiter):
                    # Remove delimiter from the end
                    binary_data = binary_data[:-len(delimiter)]
                    break
            
            if not binary_data.endswith(delimiter.replace(delimiter, '')) and not binary_data:
                self.finished_signal.emit(False, "No hidden data found in the image!")
                return
            
            self.status.emit("🔄 Converting binary data...")
            self.progress.emit(50)
            
            # Convert binary string back to bytes
            # Ensure the binary string length is a multiple of 8
            if len(binary_data) % 8 != 0:
                binary_data = binary_data[:-(len(binary_data) % 8)]
            
            file_data = bytearray()
            for i in range(0, len(binary_data), 8):
                byte = binary_data[i:i+8]
                if len(byte) == 8:
                    file_data.append(int(byte, 2))
            
            file_data = bytes(file_data)
            
            self.status.emit("🔐 Decrypting file data...")
            self.progress.emit(70)
            
            # Decrypt the file data if key is provided
            if self.key:
                try:
                    # Extract salt and encrypted data
                    salt = file_data[:16]
                    encrypted_data = file_data[16:]
                    
                    # Generate key from password
                    kdf = PBKDF2HMAC(
                        algorithm=hashes.SHA256(),
                        length=32,
                        salt=salt,
                        iterations=100000,
                    )
                    key = base64.urlsafe_b64encode(kdf.derive(self.key.encode()))
                    f = Fernet(key)
                    file_data = f.decrypt(encrypted_data)
                except Exception as e:
                    self.finished_signal.emit(False, "Incorrect key/password or corrupted data!")
                    return
            
            self.status.emit("💾 Saving revealed file...")
            self.progress.emit(90)
            
            # Save the revealed file
            base_name = os.path.splitext(os.path.basename(self.image_path))[0]
            output_path = os.path.join(self.output_dir, f"{base_name}_revealed.bin")
            
            # Try to determine the original file extension from the file data
            # Check for common file signatures
            if file_data.startswith(b'PK'):  # ZIP file
                output_path = output_path.replace('.bin', '.zip')
            elif file_data.startswith(b'\x89PNG'):  # PNG file
                output_path = output_path.replace('.bin', '.png')
            elif file_data.startswith(b'\xff\xd8\xff'):  # JPEG file
                output_path = output_path.replace('.bin', '.jpg')
            elif file_data.startswith(b'%PDF'):  # PDF file
                output_path = output_path.replace('.bin', '.pdf')
            elif file_data.startswith(b'\x50\x4b\x03\x04'):  # Another ZIP signature
                output_path = output_path.replace('.bin', '.zip')
            
            with open(output_path, 'wb') as f:
                f.write(file_data)
            
            self.progress.emit(100)
            self.status.emit("✅ File revealed successfully!")
            self.finished_signal.emit(True, f"File revealed successfully!\nOutput: {output_path}")
            
        except Exception as e:
            self.finished_signal.emit(False, f"Error revealing file: {str(e)}")


class FileConcealer(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.conceal_thread = None
        self.reveal_thread = None
        self.init_ui()
    
    def init_ui(self):
        # Set window properties
        self.setWindowTitle("File Concealer - Utility Tools")
        self.setGeometry(150, 150, 900, 960)
        self.setFixedSize(900, 960)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Create title label
        title_label = QLabel("File Concealer")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 10, QFont.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 15px;
                border-bottom: 2px solid #9b59b6;
                margin-bottom: 20px;
            }
        """)
        
        # Create description label
        desc_label = QLabel("Hide files inside images using steganography with optional encryption")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setFont(QFont("Arial", 8))
        desc_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                padding: 10px;
                margin-bottom: 20px;
            }
        """)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 10px;
                background-color: white;
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                border: 2px solid #bdc3c7;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                min-width: 150px;
                padding: 12px;
                margin-right: 2px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #9b59b6;
                color: white;
                border-color: #8e44ad;
            }
            QTabBar::tab:hover:!selected {
                background-color: #d5dbdb;
            }
        """)
        
        # Create conceal tab
        self.conceal_tab = self.create_conceal_tab()
        self.tab_widget.addTab(self.conceal_tab, "🔒 Conceal File")
        
        # Create reveal tab
        self.reveal_tab = self.create_reveal_tab()
        self.tab_widget.addTab(self.reveal_tab, "🔓 Reveal File")
        
        # Status area
        status_frame = QGroupBox("Status")
        status_frame.setFont(QFont("Arial", 8, QFont.Bold))
        status_frame.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        status_layout = QVBoxLayout(status_frame)
        
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(100)
        self.status_text.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #34495e;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 8px;
            }
        """)
        self.status_text.append("Ready to conceal or reveal files...")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #9b59b6;
                border-radius: 3px;
            }
        """)
        
        status_layout.addWidget(self.status_text)
        status_layout.addWidget(self.progress_bar)
        
        # Back button
        self.back_btn = QPushButton("Back to Main Menu")
        self.back_btn.setMinimumHeight(40)
        self.back_btn.setFont(QFont("Arial", 8, QFont.Bold))
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c7b7d;
            }
        """)
        self.back_btn.clicked.connect(self.go_back)
        
        # Add widgets to main layout
        main_layout.addWidget(title_label)
        main_layout.addWidget(desc_label)
        main_layout.addWidget(self.tab_widget, 1)
        main_layout.addWidget(status_frame)
        main_layout.addWidget(self.back_btn)
        
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
        """)
    
    def create_conceal_tab(self):
        """Create the conceal tab widget"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # File selection
        file_group = QGroupBox("1. Select File to Conceal")
        file_group.setFont(QFont("Arial", 8, QFont.Bold))
        file_layout = QVBoxLayout(file_group)
        
        file_selection_layout = QHBoxLayout()
        self.conceal_file_path = QLineEdit()
        self.conceal_file_path.setPlaceholderText("Select a file to conceal (preferably ZIP archives)")
        self.conceal_file_path.setReadOnly(True)
        self.conceal_file_path.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: #f8f9fa;
            }
        """)
        
        self.browse_file_btn = QPushButton("Browse File")
        self.browse_file_btn.setMinimumHeight(35)
        self.browse_file_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.browse_file_btn.clicked.connect(self.browse_conceal_file)
        
        file_selection_layout.addWidget(self.conceal_file_path)
        file_selection_layout.addWidget(self.browse_file_btn)
        file_layout.addLayout(file_selection_layout)
        
        # Image selection
        image_group = QGroupBox("2. Select Cover Image")
        image_group.setFont(QFont("Arial", 8, QFont.Bold))
        image_layout = QVBoxLayout(image_group)
        
        image_selection_layout = QHBoxLayout()
        self.conceal_image_path = QLineEdit()
        self.conceal_image_path.setPlaceholderText("Select an image to hide the file in")
        self.conceal_image_path.setReadOnly(True)
        self.conceal_image_path.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: #f8f9fa;
            }
        """)
        
        self.browse_image_btn = QPushButton("Browse Image")
        self.browse_image_btn.setMinimumHeight(35)
        self.browse_image_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.browse_image_btn.clicked.connect(self.browse_conceal_image)
        
        image_selection_layout.addWidget(self.conceal_image_path)
        image_selection_layout.addWidget(self.browse_image_btn)
        image_layout.addLayout(image_selection_layout)
        
        # Key/Password
        key_group = QGroupBox("3. Encryption Key (Optional)")
        key_group.setFont(QFont("Arial", 8, QFont.Bold))
        key_layout = QVBoxLayout(key_group)
        
        self.conceal_key = QLineEdit()
        self.conceal_key.setPlaceholderText("Enter encryption password (leave empty for no encryption)")
        self.conceal_key.setEchoMode(QLineEdit.Password)
        self.conceal_key.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
            }
            QLineEdit:focus {
                border-color: #9b59b6;
            }
        """)
        
        key_layout.addWidget(self.conceal_key)
        
        # Output directory
        output_group = QGroupBox("4. Output Directory")
        output_group.setFont(QFont("Arial", 8, QFont.Bold))
        output_layout = QVBoxLayout(output_group)
        
        output_selection_layout = QHBoxLayout()
        self.conceal_output_path = QLineEdit()
        self.conceal_output_path.setPlaceholderText("Select output directory for concealed image")
        self.conceal_output_path.setReadOnly(True)
        self.conceal_output_path.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: #f8f9fa;
            }
        """)
        
        self.browse_output_btn = QPushButton("Browse Directory")
        self.browse_output_btn.setMinimumHeight(35)
        self.browse_output_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.browse_output_btn.clicked.connect(self.browse_conceal_output)
        
        output_selection_layout.addWidget(self.conceal_output_path)
        output_selection_layout.addWidget(self.browse_output_btn)
        output_layout.addLayout(output_selection_layout)
        
        # Conceal button
        self.conceal_btn = QPushButton("🔒 Conceal File")
        self.conceal_btn.setMinimumHeight(50)
        self.conceal_btn.setFont(QFont("Arial", 8, QFont.Bold))
        self.conceal_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
            QPushButton:pressed {
                background-color: #7d3c98;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        self.conceal_btn.clicked.connect(self.conceal_file)
        
        # Add widgets to layout
        layout.addWidget(file_group)
        layout.addWidget(image_group)
        layout.addWidget(key_group)
        layout.addWidget(output_group)
        layout.addStretch()
        layout.addWidget(self.conceal_btn)
        
        return tab
    
    def create_reveal_tab(self):
        """Create the reveal tab widget"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Image selection
        image_group = QGroupBox("1. Select Concealed Image")
        image_group.setFont(QFont("Arial", 8, QFont.Bold))
        image_layout = QVBoxLayout(image_group)
        
        image_selection_layout = QHBoxLayout()
        self.reveal_image_path = QLineEdit()
        self.reveal_image_path.setPlaceholderText("Select image containing hidden file")
        self.reveal_image_path.setReadOnly(True)
        self.reveal_image_path.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: #f8f9fa;
            }
        """)
        
        self.browse_reveal_image_btn = QPushButton("Browse Image")
        self.browse_reveal_image_btn.setMinimumHeight(35)
        self.browse_reveal_image_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.browse_reveal_image_btn.clicked.connect(self.browse_reveal_image)
        
        image_selection_layout.addWidget(self.reveal_image_path)
        image_selection_layout.addWidget(self.browse_reveal_image_btn)
        image_layout.addLayout(image_selection_layout)
        
        # Key/Password
        key_group = QGroupBox("2. Decryption Key")
        key_group.setFont(QFont("Arial", 8, QFont.Bold))
        key_layout = QVBoxLayout(key_group)
        
        self.reveal_key = QLineEdit()
        self.reveal_key.setPlaceholderText("Enter decryption password (leave empty if no encryption was used)")
        self.reveal_key.setEchoMode(QLineEdit.Password)
        self.reveal_key.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
            }
            QLineEdit:focus {
                border-color: #e74c3c;
            }
        """)
        
        key_layout.addWidget(self.reveal_key)
        
        # Output directory
        output_group = QGroupBox("3. Output Directory")
        output_group.setFont(QFont("Arial", 8, QFont.Bold))
        output_layout = QVBoxLayout(output_group)
        
        output_selection_layout = QHBoxLayout()
        self.reveal_output_path = QLineEdit()
        self.reveal_output_path.setPlaceholderText("Select output directory for revealed file")
        self.reveal_output_path.setReadOnly(True)
        self.reveal_output_path.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: #f8f9fa;
            }
        """)
        
        self.browse_reveal_output_btn = QPushButton("Browse Directory")
        self.browse_reveal_output_btn.setMinimumHeight(35)
        self.browse_reveal_output_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.browse_reveal_output_btn.clicked.connect(self.browse_reveal_output)
        
        output_selection_layout.addWidget(self.reveal_output_path)
        output_selection_layout.addWidget(self.browse_reveal_output_btn)
        output_layout.addLayout(output_selection_layout)
        
        # Reveal button
        self.reveal_btn = QPushButton("🔓 Reveal File")
        self.reveal_btn.setMinimumHeight(50)
        self.reveal_btn.setFont(QFont("Arial", 8, QFont.Bold))
        self.reveal_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        self.reveal_btn.clicked.connect(self.reveal_file)
        
        # Add widgets to layout
        layout.addWidget(image_group)
        layout.addWidget(key_group)
        layout.addWidget(output_group)
        layout.addStretch()
        layout.addWidget(self.reveal_btn)
        
        return tab
    
    def browse_conceal_file(self):
        """Browse for file to conceal"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select File to Conceal",
            "",
            "All Files (*);;ZIP Files (*.zip);;Archive Files (*.zip *.rar *.7z);;Documents (*.pdf *.doc *.docx)"
        )
        if file_path:
            self.conceal_file_path.setText(file_path)
            self.status_text.append(f"📁 Selected file: {os.path.basename(file_path)}")
    
    def browse_conceal_image(self):
        """Browse for cover image"""
        image_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Cover Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff);;PNG Files (*.png);;JPEG Files (*.jpg *.jpeg)"
        )
        if image_path:
            self.conceal_image_path.setText(image_path)
            self.status_text.append(f"🖼️ Selected image: {os.path.basename(image_path)}")
    
    def browse_conceal_output(self):
        """Browse for output directory"""
        output_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory"
        )
        if output_dir:
            self.conceal_output_path.setText(output_dir)
            self.status_text.append(f"📂 Output directory: {output_dir}")
    
    def browse_reveal_image(self):
        """Browse for concealed image"""
        image_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Concealed Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff);;PNG Files (*.png);;JPEG Files (*.jpg *.jpeg)"
        )
        if image_path:
            self.reveal_image_path.setText(image_path)
            self.status_text.append(f"🖼️ Selected concealed image: {os.path.basename(image_path)}")
    
    def browse_reveal_output(self):
        """Browse for reveal output directory"""
        output_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory for Revealed File"
        )
        if output_dir:
            self.reveal_output_path.setText(output_dir)
            self.status_text.append(f"📂 Output directory: {output_dir}")
    
    def conceal_file(self):
        """Start the file concealing process"""
        # Validate inputs
        if not self.conceal_file_path.text():
            QMessageBox.warning(self, "Missing Input", "Please select a file to conceal.")
            return
        
        if not self.conceal_image_path.text():
            QMessageBox.warning(self, "Missing Input", "Please select a cover image.")
            return
        
        if not self.conceal_output_path.text():
            QMessageBox.warning(self, "Missing Input", "Please select an output directory.")
            return
        
        if not os.path.exists(self.conceal_file_path.text()):
            QMessageBox.warning(self, "File Not Found", "The selected file does not exist.")
            return
        
        if not os.path.exists(self.conceal_image_path.text()):
            QMessageBox.warning(self, "Image Not Found", "The selected image does not exist.")
            return
        
        if not os.path.exists(self.conceal_output_path.text()):
            QMessageBox.warning(self, "Directory Not Found", "The selected output directory does not exist.")
            return
        
        # Disable UI during processing
        self.conceal_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Start the concealing thread
        self.conceal_thread = ConcealThread(
            self.conceal_file_path.text(),
            self.conceal_image_path.text(),
            self.conceal_key.text(),
            self.conceal_output_path.text()
        )
        
        self.conceal_thread.progress.connect(self.progress_bar.setValue)
        self.conceal_thread.status.connect(self.status_text.append)
        self.conceal_thread.finished_signal.connect(self.conceal_finished)
        
        self.conceal_thread.start()
    
    def conceal_finished(self, success, message):
        """Handle concealing completion"""
        self.conceal_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", message)
    
    def reveal_file(self):
        """Start the file revealing process"""
        # Validate inputs
        if not self.reveal_image_path.text():
            QMessageBox.warning(self, "Missing Input", "Please select a concealed image.")
            return
        
        if not self.reveal_output_path.text():
            QMessageBox.warning(self, "Missing Input", "Please select an output directory.")
            return
        
        if not os.path.exists(self.reveal_image_path.text()):
            QMessageBox.warning(self, "Image Not Found", "The selected image does not exist.")
            return
        
        if not os.path.exists(self.reveal_output_path.text()):
            QMessageBox.warning(self, "Directory Not Found", "The selected output directory does not exist.")
            return
        
        # Disable UI during processing
        self.reveal_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Start the revealing thread
        self.reveal_thread = RevealThread(
            self.reveal_image_path.text(),
            self.reveal_key.text(),
            self.reveal_output_path.text()
        )
        
        self.reveal_thread.progress.connect(self.progress_bar.setValue)
        self.reveal_thread.status.connect(self.status_text.append)
        self.reveal_thread.finished_signal.connect(self.reveal_finished)
        
        self.reveal_thread.start()
    
    def reveal_finished(self, success, message):
        """Handle revealing completion"""
        self.reveal_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", message)
    
    def go_back(self):
        """Return to the main window"""
        # Stop any running threads
        if self.conceal_thread and self.conceal_thread.isRunning():
            self.conceal_thread.terminate()
        if self.reveal_thread and self.reveal_thread.isRunning():
            self.reveal_thread.terminate()
        
        self.close()
        if self.parent_window:
            self.parent_window.show()
