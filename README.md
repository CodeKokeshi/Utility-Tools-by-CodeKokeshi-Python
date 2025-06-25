# Utility Tools by CodeKokeshi

A comprehensive collection of Windows utility tools built with Python and PyQt5, designed to enhance productivity and provide useful system functionalities.

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)

## 🚀 Features Overview

This application provides a unified interface for multiple utility tools, each designed to solve specific tasks:

### 📋 Currently Implemented Tools

#### 1. 🕒 **Shutdown Timer**
Schedule your computer to shutdown at a specific date and time.

**Features:**
- **Calendar Interface**: Visual date selection with calendar widget
- **Time Picker**: Precise time selection with AM/PM format
- **Real-time Status**: Live progress tracking and time remaining display
- **Smart Validation**: Prevents scheduling in the past
- **Cancel Option**: Ability to cancel scheduled shutdowns
- **System Integration**: Uses Windows built-in shutdown commands

**How to Use:**
1. Select your desired shutdown date from the calendar
2. Set the exact time using the time picker
3. Click "Schedule Shutdown" to confirm
4. Monitor the countdown in the status display
5. Use "Cancel Shutdown" if you need to abort

#### 2. 🔐 **Smart Password Generator**
Generate memorable yet secure passwords using real words and smart patterns.

**Features:**
- **Multiple Patterns**: 5 different password generation patterns
  - Name + Numbers (e.g., Alex_1234)
  - Adjective + Noun + Numbers (e.g., SwiftEagle42)
  - Two Words + Numbers (e.g., FireStorm2024)
  - Name + Adjective + Numbers (e.g., Jordan_Bold_88)
  - Word + Name + Symbol + Numbers (e.g., River.Taylor#99)
- **Customizable Number Range**: Set min/max values for numbers
- **Optional Features**:
  - Symbol inclusion (!@#$%^&*)
  - Random capitalization
  - Leet speak transformation (a→4, e→3, etc.)
- **Password Strength Analysis**: Real-time strength assessment
- **History Tracking**: Keep track of generated passwords
- **One-click Copy**: Easy clipboard integration

**Security Benefits:**
- Uses real words for memorability
- Combines multiple elements for complexity
- Provides strength feedback
- Generates unique passwords each time

#### 3. 🛠️ **Chris Titus Tools Integration**
Direct integration with Chris Titus Tech's Windows Utility for system optimization.

**Features:**
- **One-click Launch**: Automatically opens Chris Titus Tools in elevated PowerShell
- **UAC Handling**: Manages User Account Control prompts
- **Command Display**: Shows the exact PowerShell command being executed
- **Status Monitoring**: Real-time feedback on launch process
- **Fallback Methods**: Multiple launch approaches for reliability

**What Chris Titus Tools Provides:**
- System debloating and cleanup
- Privacy settings optimization
- Performance tweaks and optimizations
- Software installation management
- Registry fixes and system repairs
- Gaming optimizations

**Important Notes:**
- Requires Administrator privileges
- Makes system-level changes to Windows
- Recommended to create system restore point before use

#### 4. 🔒 **File Concealer (Steganography Tool)**
Hide files inside images using advanced steganography techniques with optional encryption.

**Features:**
- **Dual Interface**: Separate tabs for concealing and revealing files
- **Universal File Support**: Hide any file type (ZIP files recommended for multiple files)
- **Image Format Support**: Works with PNG, JPEG, BMP, TIFF images
- **Optional Encryption**: AES encryption with PBKDF2 key derivation
- **Progress Tracking**: Real-time progress updates during operations
- **Smart File Detection**: Attempts to restore original file extensions
- **Thread-based Processing**: Non-blocking UI during operations

**Technical Specifications:**
- **Method**: Least Significant Bit (LSB) steganography
- **Encryption**: Industry-standard AES with 100,000 PBKDF2 iterations
- **Capacity**: Depends on image size (each pixel stores 3 bits)
- **Detection**: Extremely difficult without the correct key

**How to Use:**
- **Concealing**: Select file → Choose cover image → Set password (optional) → Choose output directory → Conceal
- **Revealing**: Select concealed image → Enter password (if used) → Choose output directory → Reveal

## 🖥️ System Requirements

- **Operating System**: Windows 10/11 (64-bit recommended)
- **Python**: 3.7 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 100MB for application + space for processed files
- **Display**: 1024x768 minimum resolution

## 📦 Installation

### Prerequisites
1. **Python 3.7+** installed on your system
2. **pip** package manager

### Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/CodeKokeshi/Utility-Tools-by-CodeKokeshi-Python.git
   cd Utility-Tools-by-CodeKokeshi-Python
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```bash
   python main.py
   ```

### Dependencies
- `PyQt5==5.15.9` - GUI framework
- `cryptography==41.0.7` - Encryption for File Concealer
- `Pillow==10.0.1` - Image processing
- `numpy==1.24.3` - Numerical operations

## 🎮 Usage Guide

### Main Interface
The application opens with a clean, modern interface showing all available tools in a grid layout. Each tool is represented by a styled button that opens the corresponding functionality.

### Navigation
- **Tool Selection**: Click any tool button to open that specific utility
- **Back Navigation**: Each tool has a "Back to Main Menu" button
- **Window Management**: Tools open in dedicated windows with the main menu hidden

### Universal Features
- **Modern UI**: Clean, professional interface with consistent styling
- **Status Feedback**: Real-time status updates and progress indicators
- **Error Handling**: Comprehensive error messages and validation
- **Tooltips**: Helpful hints and descriptions throughout

## 🔧 Technical Architecture

### Project Structure
```
Utility-Tools-by-CodeKokeshi-Python/
├── main.py                 # Main application entry point
├── file_concealer.py       # File Concealer implementation
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── README_FileConcealer.md # Detailed File Concealer documentation
└── __pycache__/           # Python cache files
```

### Code Organization
- **Main Window**: Central hub with tool selection
- **Individual Tools**: Separate classes for each utility
- **Threading**: Background processing for CPU-intensive tasks
- **Error Handling**: Comprehensive exception management
- **Resource Management**: Proper cleanup and memory management

## 🛡️ Security Considerations

### File Concealer Security
- **Encryption**: Uses AES-256 encryption with PBKDF2 key derivation
- **Key Strength**: 100,000 iterations for key derivation
- **Salt Generation**: Random salt for each encryption
- **Data Integrity**: Built-in verification mechanisms

### System Security
- **UAC Integration**: Proper handling of elevated privileges
- **Command Validation**: Secure command execution
- **Process Isolation**: Separate processes for system operations

## 🐛 Troubleshooting

### Common Issues

1. **PyQt5 Import Error**
   - Ensure virtual environment is activated
   - Reinstall PyQt5: `pip install --upgrade PyQt5`

2. **Permission Errors (Chris Titus Tools)**
   - Run as Administrator
   - Check Windows UAC settings
   - Verify PowerShell execution policy

3. **File Concealer Issues**
   - Ensure sufficient image size for file data
   - Verify image format compatibility
   - Check available disk space

4. **Application Won't Start**
   - Check Python version (3.7+ required)
   - Verify all dependencies installed
   - Review error messages in console

### Performance Tips
- Use PNG images for best File Concealer results
- Close other applications during system operations
- Ensure adequate free disk space
- Run from SSD for better performance

## 🔮 Planned Features

The following tools are planned for future releases:
- **Accurate File Deletion Tool**: Secure file deletion with multiple overwrite passes
- **Account Manager**: Password and account management system
- **Java Array List Generator**: Code generation utility for Java developers
- **Additional Utilities**: More tools based on user feedback

## 📝 Version History

### v1.0.0 (Current)
- ✅ Shutdown Timer implementation
- ✅ Smart Password Generator
- ✅ Chris Titus Tools integration
- ✅ File Concealer with steganography
- ✅ Modern PyQt5 interface
- ✅ Virtual environment support

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:
1. Fork the repository
2. Create a feature branch
3. Commit your changes with clear messages
4. Submit a pull request

### Development Setup
1. Follow installation instructions
2. Install development dependencies: `pip install -r requirements-dev.txt` (if available)
3. Make your changes
4. Test thoroughly before submitting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Chris Titus Tech** for the excellent Windows utility script
- **PyQt5 Community** for the robust GUI framework
- **Python Cryptography** team for secure encryption libraries
- **PIL/Pillow** developers for image processing capabilities

## 📧 Contact

- **Developer**: CodeKokeshi
- **GitHub**: [CodeKokeshi](https://github.com/CodeKokeshi)
- **Issues**: Please report bugs and feature requests through GitHub Issues

---

*Built with ❤️ using Python and PyQt5*
