import sys
import subprocess
import random
import string
import tempfile
import os
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                             QHBoxLayout, QWidget, QLabel, QPushButton, 
                             QGridLayout, QFrame, QCalendarWidget, QTimeEdit,
                             QMessageBox, QGroupBox, QTextEdit, QLineEdit,
                             QCheckBox, QSpinBox, QComboBox, QSlider)
from PyQt5.QtCore import Qt, QTime, QDate, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor, QClipboard


class ShutdownTimerWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.shutdown_process = None
        self.init_ui()
    
    def init_ui(self):
        # Set window properties
        self.setWindowTitle("Shutdown Timer - Utility Tools")
        self.setGeometry(150, 150, 700, 600)
        self.setFixedSize(700, 600)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Create title label
        title_label = QLabel("Shutdown Timer")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 15px;
                border-bottom: 2px solid #e74c3c;
                margin-bottom: 20px;
            }
        """)
        
        # Create description label
        desc_label = QLabel("Schedule your computer to shutdown at a specific date and time")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setFont(QFont("Arial", 11))
        desc_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                padding: 10px;
                margin-bottom: 20px;
            }
        """)
        
        # Create main content layout
        content_layout = QHBoxLayout()
        
        # Left side - Calendar and Time selection
        left_frame = QGroupBox("Select Date & Time")
        left_frame.setFont(QFont("Arial", 12, QFont.Bold))
        left_frame.setStyleSheet("""
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
        
        left_layout = QVBoxLayout(left_frame)
        
        # Calendar widget
        self.calendar = QCalendarWidget()
        self.calendar.setMinimumDate(QDate.currentDate())
        self.calendar.setSelectedDate(QDate.currentDate())
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QCalendarWidget QToolButton {
                height: 30px;
                width: 120px;
                color: #2c3e50;
                font-size: 12px;
                icon-size: 16px;
                background-color: #ecf0f1;
                border: none;
                border-radius: 3px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #3498db;
                color: white;
            }
            QCalendarWidget QMenu {
                width: 120px;
                left: 20px;
                color: #2c3e50;
                font-size: 12px;
                background-color: white;
                selection-background-color: #3498db;
            }
            QCalendarWidget QSpinBox {
                width: 60px;
                font-size: 12px;
                color: #2c3e50;
                background-color: white;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QCalendarWidget QSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 16px;
            }
            QCalendarWidget QSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 16px;
            }
            QCalendarWidget QAbstractItemView:enabled {
                font-size: 11px;
                color: #2c3e50;
                background-color: white;
                selection-background-color: #3498db;
                selection-color: white;
            }
        """)
        
        # Time selection
        time_layout = QHBoxLayout()
        time_label = QLabel("Time:")
        time_label.setFont(QFont("Arial", 11, QFont.Bold))
        
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime.currentTime().addSecs(3600))  # Default to 1 hour from now
        self.time_edit.setDisplayFormat("hh:mm:ss AP")
        self.time_edit.setStyleSheet("""
            QTimeEdit {
                font-size: 14px;
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                min-width: 120px;
            }
            QTimeEdit:focus {
                border-color: #3498db;
            }
        """)
        
        time_layout.addWidget(time_label)
        time_layout.addWidget(self.time_edit)
        time_layout.addStretch()
        
        left_layout.addWidget(self.calendar)
        left_layout.addLayout(time_layout)
        
        # Right side - Status and Controls
        right_frame = QGroupBox("Status & Controls")
        right_frame.setFont(QFont("Arial", 12, QFont.Bold))
        right_frame.setStyleSheet("""
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
        
        right_layout = QVBoxLayout(right_frame)
        
        # Status display
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(200)
        self.status_text.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #34495e;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
            }
        """)
        self.status_text.append("Ready to schedule shutdown...")
        
        # Control buttons
        button_layout = QVBoxLayout()
        
        self.schedule_btn = QPushButton("Schedule Shutdown")
        self.schedule_btn.setMinimumHeight(45)
        self.schedule_btn.setFont(QFont("Arial", 11, QFont.Bold))
        self.schedule_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        self.schedule_btn.clicked.connect(self.schedule_shutdown)
        
        self.cancel_btn = QPushButton("Cancel Shutdown")
        self.cancel_btn.setMinimumHeight(45)
        self.cancel_btn.setFont(QFont("Arial", 11, QFont.Bold))
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
            QPushButton:pressed {
                background-color: #d35400;
            }
        """)
        self.cancel_btn.clicked.connect(self.cancel_shutdown)
        self.cancel_btn.setEnabled(False)
        
        self.back_btn = QPushButton("Back to Main Menu")
        self.back_btn.setMinimumHeight(45)
        self.back_btn.setFont(QFont("Arial", 11, QFont.Bold))
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
        
        button_layout.addWidget(self.schedule_btn)
        button_layout.addWidget(self.cancel_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.back_btn)
        
        right_layout.addWidget(self.status_text)
        right_layout.addLayout(button_layout)
        
        # Add frames to content layout
        content_layout.addWidget(left_frame, 1)
        content_layout.addWidget(right_frame, 1)
        
        # Add widgets to main layout
        main_layout.addWidget(title_label)
        main_layout.addWidget(desc_label)
        main_layout.addLayout(content_layout)
        
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
        """)
    
    def schedule_shutdown(self):
        """Schedule the shutdown at the selected date and time"""
        try:
            # Get selected date and time
            selected_date = self.calendar.selectedDate()
            selected_time = self.time_edit.time()
            
            # Combine date and time
            shutdown_datetime = datetime.combine(
                selected_date.toPyDate(),
                selected_time.toPyTime()
            )
            
            current_datetime = datetime.now()
            
            # Check if the selected time is in the future
            if shutdown_datetime <= current_datetime:
                QMessageBox.warning(self, "Invalid Time", 
                                  "Please select a future date and time!")
                return
            
            # Calculate seconds until shutdown
            time_diff = shutdown_datetime - current_datetime
            seconds_until_shutdown = int(time_diff.total_seconds())
            
            # Execute shutdown command
            try:
                # Cancel any existing shutdown
                subprocess.run(['shutdown', '/a'], capture_output=True)
                
                # Schedule new shutdown
                result = subprocess.run([
                    'shutdown', '/s', '/t', str(seconds_until_shutdown),
                    '/c', f'Scheduled shutdown by Utility Tools - {shutdown_datetime.strftime("%Y-%m-%d %H:%M:%S")}'
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.status_text.append(f"✅ Shutdown scheduled successfully!")
                    self.status_text.append(f"📅 Date: {shutdown_datetime.strftime('%Y-%m-%d')}")
                    self.status_text.append(f"⏰ Time: {shutdown_datetime.strftime('%H:%M:%S')}")
                    self.status_text.append(f"⏳ Time remaining: {self.format_time_remaining(seconds_until_shutdown)}")
                    self.status_text.append(f"💡 Your computer will shutdown automatically at the scheduled time.")
                    self.status_text.append("="*50)
                    
                    self.schedule_btn.setEnabled(False)
                    self.cancel_btn.setEnabled(True)
                    
                    # Show success message
                    QMessageBox.information(self, "Shutdown Scheduled", 
                                          f"Your computer will shutdown on:\n"
                                          f"{shutdown_datetime.strftime('%Y-%m-%d at %H:%M:%S')}\n\n"
                                          f"Time remaining: {self.format_time_remaining(seconds_until_shutdown)}")
                else:
                    raise Exception(f"Command failed with return code {result.returncode}")
                    
            except Exception as e:
                self.status_text.append(f"❌ Error scheduling shutdown: {str(e)}")
                QMessageBox.critical(self, "Error", f"Failed to schedule shutdown:\n{str(e)}")
                
        except Exception as e:
            self.status_text.append(f"❌ Unexpected error: {str(e)}")
            QMessageBox.critical(self, "Error", f"An unexpected error occurred:\n{str(e)}")
    
    def cancel_shutdown(self):
        """Cancel the scheduled shutdown"""
        try:
            result = subprocess.run(['shutdown', '/a'], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.status_text.append("🚫 Shutdown cancelled successfully!")
                self.status_text.append("="*50)
                
                self.schedule_btn.setEnabled(True)
                self.cancel_btn.setEnabled(False)
                
                QMessageBox.information(self, "Shutdown Cancelled", 
                                      "The scheduled shutdown has been cancelled.")
            else:
                self.status_text.append(f"❌ Error cancelling shutdown: {result.stderr}")
                QMessageBox.warning(self, "Error", 
                                  "Could not cancel shutdown. There might not be a scheduled shutdown.")
                
        except Exception as e:
            self.status_text.append(f"❌ Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to cancel shutdown:\n{str(e)}")
    
    def format_time_remaining(self, seconds):
        """Format seconds into a readable time format"""
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        parts = []
        if days > 0:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        if seconds > 0 and len(parts) < 2:  # Only show seconds if total time is small
            parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
        
        return ", ".join(parts) if parts else "0 seconds"
    
    def go_back(self):
        """Return to the main window"""
        self.close()
        if self.parent_window:
            self.parent_window.show()


class PasswordGeneratorWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        
        # Word lists for generating memorable passwords
        self.common_names = [
            "Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery", "Cameron",
            "Dakota", "Phoenix", "Sage", "River", "Skyler", "Quinn", "Rowan", "Blake",
            "Emery", "Hayden", "Kendall", "Logan", "Parker", "Reese", "Sydney", "Drew",
            "Charlie", "Finley", "Harper", "Indigo", "Kai", "Lane", "Marlowe", "Nova",
            "Ocean", "Presley", "Rain", "Sage", "True", "Vale", "Winter", "Zion"
        ]
        
        self.adjectives = [
            "Swift", "Bright", "Strong", "Clever", "Bold", "Quick", "Smart", "Brave",
            "Sharp", "Wise", "Fast", "Cool", "Fire", "Storm", "Thunder", "Lightning",
            "Shadow", "Steel", "Diamond", "Golden", "Silver", "Cosmic", "Stellar", "Nova",
            "Quantum", "Cyber", "Digital", "Mystic", "Royal", "Elite", "Prime", "Ultra",
            "Mega", "Super", "Hyper", "Turbo", "Nitro", "Blaze", "Frost", "Neon"
        ]
        
        self.nouns = [
            "Lion", "Eagle", "Tiger", "Wolf", "Bear", "Hawk", "Fox", "Shark", "Dragon",
            "Phoenix", "Falcon", "Panther", "Cobra", "Viper", "Raven", "Stallion", "Warrior",
            "Knight", "Guardian", "Hunter", "Ranger", "Scout", "Pilot", "Captain", "Admiral",
            "Chief", "Master", "Expert", "Genius", "Legend", "Hero", "Champion", "Winner",
            "Star", "Comet", "Planet", "Galaxy", "Universe", "Cosmos", "Nebula", "Void"
        ]
        
        self.words = [
            "Apple", "River", "Mountain", "Ocean", "Forest", "Desert", "Island", "Valley",
            "Bridge", "Castle", "Tower", "Garden", "Flower", "Tree", "Stone", "Crystal",
            "Fire", "Water", "Earth", "Wind", "Light", "Dark", "Moon", "Sun", "Star",
            "Cloud", "Rain", "Snow", "Ice", "Thunder", "Lightning", "Storm", "Calm",
            "Peace", "Joy", "Hope", "Dream", "Wish", "Magic", "Wonder", "Miracle"
        ]
        
        self.separators = ["_", "-", ".", ""]
        
        self.init_ui()
    
    def init_ui(self):
        # Set window properties
        self.setWindowTitle("Password Generator - Utility Tools")
        self.setGeometry(150, 150, 1000, 800)
        self.setFixedSize(1000, 800)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Create title label
        title_label = QLabel("Smart Password Generator")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 15px;
                border-bottom: 2px solid #27ae60;
                margin-bottom: 20px;
            }
        """)
        
        # Create description label
        desc_label = QLabel("Generate memorable yet secure passwords using real words and smart patterns")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setFont(QFont("Arial", 11))
        desc_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                padding: 10px;
                margin-bottom: 20px;
            }
        """)
        
        # Create main content layout
        content_layout = QHBoxLayout()
        
        # Left side - Password Options
        left_frame = QGroupBox("Password Options")
        left_frame.setFont(QFont("Arial", 12, QFont.Bold))
        left_frame.setStyleSheet("""
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
        
        left_layout = QVBoxLayout(left_frame)
        
        # Password Pattern Selection
        pattern_label = QLabel("Password Pattern:")
        pattern_label.setFont(QFont("Arial", 11, QFont.Bold))
        
        self.pattern_combo = QComboBox()
        self.pattern_combo.addItems([
            "Name + Numbers (e.g., Alex_1234)",
            "Adjective + Noun + Numbers (e.g., SwiftEagle42)",
            "Two Words + Numbers (e.g., FireStorm2024)",
            "Name + Adjective + Numbers (e.g., Jordan_Bold_88)",
            "Word + Name + Symbol + Numbers (e.g., River.Taylor#99)"
        ])
        self.pattern_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                font-size: 11px;
            }
            QComboBox:focus {
                border-color: #27ae60;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-style: solid;
                border-width: 4px 4px 0 4px;
                border-color: #7f8c8d transparent transparent transparent;
            }
        """)
        
        # Number Range
        number_label = QLabel("Number Range:")
        number_label.setFont(QFont("Arial", 11, QFont.Bold))
        
        number_layout = QHBoxLayout()
        self.min_number = QSpinBox()
        self.min_number.setRange(0, 9999)
        self.min_number.setValue(10)
        self.min_number.setStyleSheet("""
            QSpinBox {
                padding: 5px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
            }
            QSpinBox:focus {
                border-color: #27ae60;
            }
        """)
        
        to_label = QLabel("to")
        to_label.setAlignment(Qt.AlignCenter)
        
        self.max_number = QSpinBox()
        self.max_number.setRange(0, 9999)
        self.max_number.setValue(9999)
        self.max_number.setStyleSheet("""
            QSpinBox {
                padding: 5px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
            }
            QSpinBox:focus {
                border-color: #27ae60;
            }
        """)
        
        number_layout.addWidget(self.min_number)
        number_layout.addWidget(to_label)
        number_layout.addWidget(self.max_number)
        
        # Options
        self.include_symbols = QCheckBox("Include symbols (!@#$%)")
        self.include_symbols.setFont(QFont("Arial", 10))
        self.include_symbols.setStyleSheet("""
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #bdc3c7;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #27ae60;
                border-color: #27ae60;
            }
        """)
        
        self.capitalize_random = QCheckBox("Random capitalization")
        self.capitalize_random.setFont(QFont("Arial", 10))
        self.capitalize_random.setChecked(True)
        self.capitalize_random.setStyleSheet("""
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #bdc3c7;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #27ae60;
                border-color: #27ae60;
            }
        """)
        
        self.leet_speak = QCheckBox("Leet speak (replace some letters with numbers)")
        self.leet_speak.setFont(QFont("Arial", 10))
        self.leet_speak.setStyleSheet("""
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #bdc3c7;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #27ae60;
                border-color: #27ae60;
            }
        """)
        
        # Generate button
        self.generate_btn = QPushButton("Generate Password")
        self.generate_btn.setMinimumHeight(45)
        self.generate_btn.setFont(QFont("Arial", 11, QFont.Bold))
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        self.generate_btn.clicked.connect(self.generate_password)
        
        left_layout.addWidget(pattern_label)
        left_layout.addWidget(self.pattern_combo)
        left_layout.addWidget(number_label)
        left_layout.addLayout(number_layout)
        left_layout.addWidget(self.include_symbols)
        left_layout.addWidget(self.capitalize_random)
        left_layout.addWidget(self.leet_speak)
        left_layout.addStretch()
        left_layout.addWidget(self.generate_btn)
        
        # Right side - Generated Passwords
        right_frame = QGroupBox("Generated Passwords")
        right_frame.setFont(QFont("Arial", 12, QFont.Bold))
        right_frame.setStyleSheet("""
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
        
        right_layout = QVBoxLayout(right_frame)
        
        # Current password display
        current_label = QLabel("Current Password:")
        current_label.setFont(QFont("Arial", 11, QFont.Bold))
        
        password_display_layout = QHBoxLayout()
        self.password_display = QLineEdit()
        self.password_display.setReadOnly(True)
        self.password_display.setFont(QFont("Consolas",8, QFont.Bold))
        self.password_display.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #27ae60;
                border-radius: 5px;
                background-color: #f8f9fa;
                color: #2c3e50;
                font-family: 'Consolas', 'Monaco', monospace;
            }
        """)
        self.password_display.setPlaceholderText("Click 'Generate Password' to create a new password")
        
        self.copy_btn = QPushButton("📋 Copy")
        self.copy_btn.setMinimumHeight(45)
        self.copy_btn.setMinimumWidth(80)
        self.copy_btn.setFont(QFont("Arial", 10, QFont.Bold))
        self.copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        self.copy_btn.clicked.connect(self.copy_password)
        self.copy_btn.setEnabled(False)
        
        password_display_layout.addWidget(self.password_display)
        password_display_layout.addWidget(self.copy_btn)
        
        # Password history
        history_label = QLabel("Password History:")
        history_label.setFont(QFont("Arial", 11, QFont.Bold))
        
        self.password_history = QTextEdit()
        self.password_history.setReadOnly(True)
        self.password_history.setMaximumHeight(200)
        self.password_history.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                color: #2c3e50;
            }
        """)
        self.password_history.append("Password generation history will appear here...")
        
        # Password strength indicator
        strength_label = QLabel("Password Strength:")
        strength_label.setFont(QFont("Arial", 11, QFont.Bold))
        
        self.strength_bar = QLabel("Not generated yet")
        self.strength_bar.setAlignment(Qt.AlignCenter)
        self.strength_bar.setMinimumHeight(30)
        self.strength_bar.setStyleSheet("""
            QLabel {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: #ecf0f1;
                color: #7f8c8d;
                font-weight: bold;
                padding: 5px;
            }
        """)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        self.regenerate_btn = QPushButton("Generate Another")
        self.regenerate_btn.setMinimumHeight(40)
        self.regenerate_btn.setFont(QFont("Arial", 10, QFont.Bold))
        self.regenerate_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
            QPushButton:pressed {
                background-color: #d35400;
            }
        """)
        self.regenerate_btn.clicked.connect(self.generate_password)
        self.regenerate_btn.setEnabled(False)
        
        self.back_btn = QPushButton("Back to Main Menu")
        self.back_btn.setMinimumHeight(40)
        self.back_btn.setFont(QFont("Arial", 10, QFont.Bold))
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
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
        
        control_layout.addWidget(self.regenerate_btn)
        control_layout.addWidget(self.back_btn)
        
        right_layout.addWidget(current_label)
        right_layout.addLayout(password_display_layout)
        right_layout.addWidget(history_label)
        right_layout.addWidget(self.password_history)
        right_layout.addWidget(strength_label)
        right_layout.addWidget(self.strength_bar)
        right_layout.addStretch()
        right_layout.addLayout(control_layout)
        
        # Add frames to content layout
        content_layout.addWidget(left_frame, 1)
        content_layout.addWidget(right_frame, 1)
        
        # Add widgets to main layout
        main_layout.addWidget(title_label)
        main_layout.addWidget(desc_label)
        main_layout.addLayout(content_layout)
        
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
        """)
    
    def apply_leet_speak(self, text):
        """Apply leet speak transformations to text"""
        leet_map = {
            'a': '4', 'A': '4',
            'e': '3', 'E': '3',
            'i': '1', 'I': '1',
            'o': '0', 'O': '0',
            's': '5', 'S': '5',
            't': '7', 'T': '7'
        }
        
        # Only replace some characters randomly
        result = ""
        for char in text:
            if char in leet_map and random.random() < 0.3:  # 30% chance to replace
                result += leet_map[char]
            else:
                result += char
        return result
    
    def apply_random_capitalization(self, text):
        """Apply random capitalization to text"""
        result = ""
        for char in text:
            if char.isalpha():
                if random.random() < 0.5:
                    result += char.upper()
                else:
                    result += char.lower()
            else:
                result += char
        return result
    
    def calculate_password_strength(self, password):
        """Calculate password strength and return color and text"""
        score = 0
        length = len(password)
        
        # Length scoring
        if length >= 8:
            score += 1
        if length >= 12:
            score += 1
        if length >= 16:
            score += 1
        
        # Character variety scoring
        if any(c.islower() for c in password):
            score += 1
        if any(c.isupper() for c in password):
            score += 1
        if any(c.isdigit() for c in password):
            score += 1
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 1
        
        # Pattern scoring (memorable passwords are good)
        if any(word.lower() in password.lower() for word in self.common_names + self.adjectives + self.nouns + self.words):
            score += 1
        
        if score <= 3:
            return "#e74c3c", "Weak"
        elif score <= 5:
            return "#f39c12", "Fair"
        elif score <= 7:
            return "#f1c40f", "Good"
        else:
            return "#27ae60", "Strong"
    
    def generate_password(self):
        """Generate a new password based on selected options"""
        try:
            pattern = self.pattern_combo.currentIndex()
            min_num = self.min_number.value()
            max_num = self.max_number.value()
            
            if min_num > max_num:
                min_num, max_num = max_num, min_num
            
            number = random.randint(min_num, max_num)
            separator = random.choice(self.separators)
            
            # Generate password based on pattern
            if pattern == 0:  # Name + Numbers
                name = random.choice(self.common_names)
                password = f"{name}{separator}{number}"
                
            elif pattern == 1:  # Adjective + Noun + Numbers
                adj = random.choice(self.adjectives)
                noun = random.choice(self.nouns)
                password = f"{adj}{noun}{number}"
                
            elif pattern == 2:  # Two Words + Numbers
                word1 = random.choice(self.words)
                word2 = random.choice(self.words)
                password = f"{word1}{word2}{number}"
                
            elif pattern == 3:  # Name + Adjective + Numbers
                name = random.choice(self.common_names)
                adj = random.choice(self.adjectives)
                password = f"{name}{separator}{adj}{separator}{number}"
                
            else:  # Word + Name + Symbol + Numbers
                word = random.choice(self.words)
                name = random.choice(self.common_names)
                symbol = random.choice(['#', '!', '@', '$', '%']) if self.include_symbols.isChecked() else ''
                password = f"{word}.{name}{symbol}{number}"
            
            # Add symbols if requested
            if self.include_symbols.isChecked() and pattern != 4:
                symbols = ['!', '@', '#', '$', '%', '^', '&', '*']
                if random.random() < 0.7:  # 70% chance to add symbol
                    password += random.choice(symbols)
            
            # Apply leet speak if requested
            if self.leet_speak.isChecked():
                password = self.apply_leet_speak(password)
            
            # Apply random capitalization if requested
            if self.capitalize_random.isChecked():
                password = self.apply_random_capitalization(password)
            
            # Display the password
            self.password_display.setText(password)
            self.copy_btn.setEnabled(True)
            self.regenerate_btn.setEnabled(True)
            
            # Update strength indicator
            color, strength_text = self.calculate_password_strength(password)
            self.strength_bar.setText(f"{strength_text} - Length: {len(password)} characters")
            self.strength_bar.setStyleSheet(f"""
                QLabel {{
                    border: 2px solid {color};
                    border-radius: 5px;
                    background-color: {color};
                    color: white;
                    font-weight: bold;
                    padding: 5px;
                }}
            """)
            
            # Add to history
            timestamp = datetime.now().strftime("%H:%M:%S")
            pattern_names = [
                "Name + Numbers", "Adjective + Noun + Numbers", "Two Words + Numbers",
                "Name + Adjective + Numbers", "Word + Name + Symbol + Numbers"
            ]
            pattern_name = pattern_names[pattern]
            
            self.password_history.append(f"[{timestamp}] {password} ({pattern_name}, {strength_text})")
            
            # Scroll to bottom
            scrollbar = self.password_history.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate password:\n{str(e)}")
    
    def copy_password(self):
        """Copy the current password to clipboard"""
        try:
            password = self.password_display.text()
            if password:
                clipboard = QApplication.clipboard()
                clipboard.setText(password)
                
                # Show temporary feedback
                original_text = self.copy_btn.text()
                self.copy_btn.setText("✓ Copied!")
                self.copy_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #27ae60;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        padding: 8px;
                        font-weight: bold;
                    }
                """)
                
                # Reset button after 2 seconds
                QTimer.singleShot(2000, lambda: self.reset_copy_button(original_text))
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to copy password:\n{str(e)}")
    
    def reset_copy_button(self, original_text):
        """Reset the copy button to its original state"""
        self.copy_btn.setText(original_text)
        self.copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
    
    def go_back(self):
        """Return to the main window"""
        self.close()
        if self.parent_window:
            self.parent_window.show()


class ChrisTitusToolsWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.init_ui()
    
    def init_ui(self):
        # Set window properties
        self.setWindowTitle("Chris Titus Tools - Utility Tools")
        self.setGeometry(150, 150, 800, 920)
        self.setFixedSize(800, 920)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Create title label
        title_label = QLabel("Chris Titus Tech's Windows Utility")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 12px;
                border-bottom: 2px solid #e67e22;
                margin-bottom: 15px;
            }
        """)
        
        # Create description section
        desc_frame = QFrame()
        desc_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                border-left: 4px solid #e67e22;
                padding: 12px;
            }
        """)
        
        desc_layout = QVBoxLayout(desc_frame)
        desc_layout.setSpacing(8)
        
        desc_title = QLabel("About Chris Titus Tech's Windows Utility")
        desc_title.setFont(QFont("Arial", 12, QFont.Bold))
        desc_title.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        
        desc_text = QLabel("""This tool provides a comprehensive set of Windows utilities and tweaks including:
• System debloating and cleanup • Privacy settings optimization • Performance tweaks
• Software installation and management • Registry fixes and system repairs • Gaming optimizations

The tool will open in an elevated PowerShell window with administrative privileges.""")
        desc_text.setFont(QFont("Arial", 10))
        desc_text.setStyleSheet("color: #34495e; line-height: 1.4;")
        desc_text.setWordWrap(True)
        
        desc_layout.addWidget(desc_title)
        desc_layout.addWidget(desc_text)
        
        # Create warning section
        warning_frame = QFrame()
        warning_frame.setStyleSheet("""
            QFrame {
                background-color: #fff3cd;
                border: 1px solid #ffeaa7; 
                border-radius: 8px;
                padding: 12px;
            }
        """)
        
        warning_layout = QVBoxLayout(warning_frame)
        warning_layout.setSpacing(5)
        
        warning_title = QLabel("⚠️ Important Notice")
        warning_title.setFont(QFont("Arial", 11, QFont.Bold))
        warning_title.setStyleSheet("color: #856404;")
        
        warning_text = QLabel("""• Requires Administrator privileges • Makes system-level changes to Windows
• Create a system restore point before proceeding • Close other applications to avoid conflicts""")
        warning_text.setFont(QFont("Arial", 9))
        warning_text.setStyleSheet("color: #856404; margin-top: 3px;")
        warning_text.setWordWrap(True)
        
        warning_layout.addWidget(warning_title)
        warning_layout.addWidget(warning_text)
        
        # Create command display
        command_frame = QGroupBox("Command to be executed:")
        command_frame.setFont(QFont("Arial", 10, QFont.Bold))
        command_frame.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        command_layout = QVBoxLayout(command_frame)
        command_layout.setSpacing(8)
        
        self.command_display = QLineEdit()
        self.command_display.setText("iwr -useb https://christitus.com/win | iex")
        self.command_display.setReadOnly(True)
        self.command_display.setFont(QFont("Consolas", 11, QFont.Bold))
        self.command_display.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #e67e22;
                border-radius: 5px;
                background-color: #2c3e50;
                color: #ecf0f1;
                font-family: 'Consolas', 'Monaco', monospace;
            }
        """)
        
        copy_cmd_btn = QPushButton("📋 Copy Command")
        copy_cmd_btn.setMinimumHeight(32)
        copy_cmd_btn.setFont(QFont("Arial", 9, QFont.Bold))
        copy_cmd_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c7b7d;
            }
        """)
        copy_cmd_btn.clicked.connect(self.copy_command)
        
        command_layout.addWidget(self.command_display)
        command_layout.addWidget(copy_cmd_btn)
        
        # Create status display
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(100)
        self.status_text.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #34495e;
                border-radius: 5px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 9px;
            }
        """)
        self.status_text.append("Ready to launch Chris Titus Tech's Windows Utility...")
        
        # Create control buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.launch_btn = QPushButton("🚀 Launch Chris Titus Tools")
        self.launch_btn.setMinimumHeight(45)
        self.launch_btn.setFont(QFont("Arial", 11, QFont.Bold))
        self.launch_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
            QPushButton:pressed {
                background-color: #ba4a00;
            }
        """)
        self.launch_btn.clicked.connect(self.launch_chris_titus_tools)
        
        self.back_btn = QPushButton("Back to Main Menu")
        self.back_btn.setMinimumHeight(45)
        self.back_btn.setFont(QFont("Arial", 10, QFont.Bold))
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
        
        button_layout.addWidget(self.launch_btn, 2)
        button_layout.addWidget(self.back_btn, 1)
        
        # Add widgets to main layout
        main_layout.addWidget(title_label)
        main_layout.addWidget(desc_frame)
        main_layout.addWidget(warning_frame)
        main_layout.addWidget(command_frame)
        main_layout.addWidget(self.status_text)
        main_layout.addStretch()  # Add stretch to push buttons to bottom
        main_layout.addLayout(button_layout)
        
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
        """)
    
    def copy_command(self):
        """Copy the PowerShell command to clipboard"""
        try:
            command = self.command_display.text()
            clipboard = QApplication.clipboard()
            clipboard.setText(command)
            
            self.status_text.append(f"📋 Command copied to clipboard: {command}")
            
            QMessageBox.information(self, "Command Copied", 
                                  "The PowerShell command has been copied to your clipboard!\n\n"
                                  "You can paste it manually in an elevated PowerShell window if needed.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to copy command:\n{str(e)}")
    
    def launch_chris_titus_tools(self):
        """Launch Chris Titus Tools by opening PowerShell as admin and running the command"""
        try:
            self.status_text.append("🔄 Launching Chris Titus Tech's Windows Utility...")
            self.status_text.append("📝 Opening elevated PowerShell window...")
            
            # The command to run
            command = "iwr -useb https://christitus.com/win | iex"
            
            # PowerShell command to run as administrator
            # We use Start-Process with -Verb RunAs to request elevation
            powershell_command = [
                'powershell.exe',
                '-Command',
                f'Start-Process powershell -ArgumentList "-NoExit", "-Command", "{command}" -Verb RunAs'
            ]
            
            try:
                # Execute the command
                result = subprocess.run(powershell_command, 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=10)
                
                if result.returncode == 0:
                    self.status_text.append("✅ PowerShell window launched successfully!")
                    self.status_text.append("💡 Please check the elevated PowerShell window that opened.")
                    self.status_text.append("🔧 The Chris Titus utility should be loading...")
                    self.status_text.append("="*50)
                    
                    QMessageBox.information(self, "Launch Successful", 
                                          "Chris Titus Tools has been launched!\n\n"
                                          "An elevated PowerShell window should have opened with the utility.\n"
                                          "If you don't see it, check your taskbar or try running manually.")
                else:
                    self.status_text.append(f"⚠️ PowerShell returned code: {result.returncode}")
                    if result.stderr:
                        self.status_text.append(f"❌ Error: {result.stderr}")
                    
                    # Fallback method
                    self.launch_fallback_method()
                    
            except subprocess.TimeoutExpired:
                self.status_text.append("⏱️ PowerShell launch timed out (this is usually normal)")
                self.status_text.append("💡 Check if an elevated PowerShell window opened")
                
                QMessageBox.information(self, "Launch Initiated", 
                                      "The launch process has been initiated.\n\n"
                                      "Please check if an elevated PowerShell window opened.\n"
                                      "You may need to approve the UAC prompt.")
                                      
            except Exception as e:
                self.status_text.append(f"❌ Error launching PowerShell: {str(e)}")
                self.launch_fallback_method()
                
        except Exception as e:
            self.status_text.append(f"❌ Unexpected error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to launch Chris Titus Tools:\n{str(e)}")
    
    def launch_fallback_method(self):
        """Fallback method using different approach"""
        try:
            self.status_text.append("🔄 Trying alternative launch method...")
            
            # Alternative method using runas
            command = "iwr -useb https://christitus.com/win | iex"
            
            # Create a temporary PowerShell script
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False) as f:
                f.write(f"""
# Chris Titus Tech Windows Utility Launcher
Write-Host "Launching Chris Titus Tech Windows Utility..." -ForegroundColor Green
Write-Host "Please wait while the utility downloads and initializes..." -ForegroundColor Yellow
Write-Host ""

try {{
    {command}
}} catch {{
    Write-Host "Error occurred: $_" -ForegroundColor Red
    Write-Host "Press any key to continue..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}}
""")
                script_path = f.name
            
            # Execute the script with elevated privileges
            result = subprocess.run([
                'powershell.exe',
                '-Command',
                f'Start-Process powershell -ArgumentList "-ExecutionPolicy", "Bypass", "-File", "{script_path}" -Verb RunAs'
            ], capture_output=True, text=True, timeout=15)
            
            self.status_text.append("📝 Alternative launch method executed")
            self.status_text.append("💡 Please check for elevated PowerShell window")
            
            # Clean up the temporary file after a delay
            QTimer.singleShot(30000, lambda: self.cleanup_temp_file(script_path))
            
            QMessageBox.information(self, "Launch Attempted", 
                                  "Alternative launch method has been executed.\n\n"
                                  "Please check if an elevated PowerShell window opened.\n"
                                  "You may need to approve the UAC (User Account Control) prompt.")
            
        except Exception as e:
            self.status_text.append(f"❌ Fallback method failed: {str(e)}")
            
            QMessageBox.critical(self, "Launch Failed", 
                               f"Unable to launch Chris Titus Tools automatically.\n\n"
                               f"Please manually:\n"
                               f"1. Open PowerShell as Administrator\n"
                               f"2. Run this command:\n"
                               f"   iwr -useb https://christitus.com/win | iex\n\n"
                               f"Error: {str(e)}")
    
    def cleanup_temp_file(self, file_path):
        """Clean up temporary PowerShell script file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                self.status_text.append("🗑️ Temporary script file cleaned up")
        except Exception as e:
            self.status_text.append(f"⚠️ Could not clean up temp file: {str(e)}")
    
    def go_back(self):
        """Return to the main window"""
        self.close()
        if self.parent_window:
            self.parent_window.show()


class UtilityToolsMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        # Set window properties
        self.setWindowTitle("Utility Tools by CodeKokeshi")
        self.setGeometry(100, 100, 800, 600)
        self.setMinimumSize(600, 500)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Create title label
        title_label = QLabel("Utility Tools by CodeKokeshi")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 20px;
                border-bottom: 3px solid #3498db;
                margin-bottom: 20px;
            }
        """)
        
        # Create subtitle
        subtitle_label = QLabel("Select a utility tool to get started")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setFont(QFont("Arial", 12))
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                padding: 10px;
                margin-bottom: 20px;
            }
        """)
        
        # Create buttons container
        buttons_frame = QFrame()
        buttons_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        # Create grid layout for buttons
        buttons_layout = QGridLayout(buttons_frame)
        buttons_layout.setSpacing(15)
        
        # Define button data (text, row, column)
        button_data = [
            ("Shutdown Timer", 0, 0),
            ("Chris Titus Tools", 0, 1),
            ("Password Generator", 1, 0),
            ("File Concealer", 1, 1),
            ("Accurate File Deletion Tool", 2, 0),
            ("Account Manager", 2, 1),
            ("Java Array List Generator", 3, 0),
            ("Coming Soon...", 3, 1)  # Placeholder for future tools
        ]
        
        # Create and add buttons
        for button_text, row, col in button_data:
            button = self.create_tool_button(button_text)
            buttons_layout.addWidget(button, row, col)
        
        # Add widgets to main layout
        main_layout.addWidget(title_label)
        main_layout.addWidget(subtitle_label)
        main_layout.addWidget(buttons_frame)
        main_layout.addStretch()  # Add stretch to push everything to top
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
        """)
    
    def create_tool_button(self, text):
        """Create a styled button for utility tools"""
        button = QPushButton(text)
        button.setMinimumSize(250, 80)
        button.setFont(QFont("Arial", 11, QFont.Medium))
        
        # Different style for placeholder button
        if text == "Coming Soon...":
            button.setStyleSheet("""
                QPushButton {
                    background-color: #ecf0f1;
                    border: 2px solid #bdc3c7;
                    border-radius: 8px;
                    color: #95a5a6;
                    padding: 15px;
                    text-align: center;
                    font-style: italic;
                }
                QPushButton:hover {
                    background-color: #d5dbdb;
                    border-color: #95a5a6;
                }
            """)
            button.setEnabled(False)
        else:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    border: none;
                    border-radius: 8px;
                    color: white;
                    padding: 15px;
                    text-align: center;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                    transform: translateY(-2px);
                }
                QPushButton:pressed {
                    background-color: #21618c;
                    transform: translateY(0px);
                }
            """)
        
        # Connect button to placeholder function
        if text != "Coming Soon...":
            button.clicked.connect(lambda checked, btn_text=text: self.on_tool_button_clicked(btn_text))
        
        return button
    
    def on_tool_button_clicked(self, tool_name):
        """Handle button clicks and open appropriate tool windows"""
        print(f"Button clicked: {tool_name}")
        
        if tool_name == "Shutdown Timer":
            self.open_shutdown_timer()
        elif tool_name == "Password Generator":
            self.open_password_generator()
        elif tool_name == "Chris Titus Tools":
            self.open_chris_titus_tools()
        else:
            # TODO: Implement functionality for other tools
            QMessageBox.information(self, "Coming Soon", 
                                  f"{tool_name} functionality will be implemented soon!")
    
    def open_shutdown_timer(self):
        """Open the shutdown timer window"""
        self.shutdown_timer_window = ShutdownTimerWindow(self)
        self.shutdown_timer_window.show()
        self.hide()  # Hide main window while shutdown timer is open
    
    def open_password_generator(self):
        """Open the password generator window"""
        self.password_generator_window = PasswordGeneratorWindow(self)
        self.password_generator_window.show()
        self.hide()  # Hide main window while password generator is open
    
    def open_chris_titus_tools(self):
        """Open the Chris Titus Tools window"""
        self.chris_titus_window = ChrisTitusToolsWindow(self)
        self.chris_titus_window.show()
        self.hide()  # Hide main window while Chris Titus Tools is open


def main():
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Utility Tools by CodeKokeshi")
    app.setApplicationVersion("1.0")
    
    # Create and show main window
    window = UtilityToolsMainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()