# File Concealer

The File Concealer is a steganography tool that allows you to hide files inside images using least significant bit (LSB) steganography with optional encryption.

## Features

- **Hide any file inside an image**: Conceal ZIP archives, documents, or any file type within image files
- **Encryption support**: Optional password protection using industry-standard cryptography
- **User-friendly interface**: Separate tabs for concealing and revealing files
- **Progress tracking**: Real-time progress updates during operations
- **Automatic file type detection**: Attempts to restore original file extensions when revealing

## How to Use

### Concealing a File

1. **Select File to Conceal**: Choose any file you want to hide (ZIP files recommended for multiple files)
2. **Select Cover Image**: Choose an image file (PNG, JPG, BMP, TIFF) to hide the file in
3. **Set Encryption Key (Optional)**: Enter a password for additional security (leave empty for no encryption)
4. **Choose Output Directory**: Select where to save the concealed image
5. **Click "Conceal File"**: The process will start and show progress

### Revealing a File

1. **Select Concealed Image**: Choose the image that contains the hidden file
2. **Enter Decryption Key**: If encryption was used, enter the correct password
3. **Choose Output Directory**: Select where to save the revealed file
4. **Click "Reveal File"**: The process will start and extract the hidden file

## Technical Details

- **Steganography Method**: Least Significant Bit (LSB) modification
- **Encryption**: AES encryption using PBKDF2 key derivation
- **Supported Image Formats**: PNG, JPEG, BMP, TIFF
- **Image Requirements**: The image must be large enough to hold the file data
- **File Size Limit**: Depends on image size (each pixel can store 3 bits of data)

## Security Notes

- **Use strong passwords**: If using encryption, choose a strong, unique password
- **Image quality**: The concealed image will look identical to the original
- **File detection**: Without the key, the hidden file is extremely difficult to detect
- **Backup original files**: Keep backups of both the original file and image

## Requirements

- Python 3.7+
- PyQt5
- Pillow (PIL)
- NumPy
- Cryptography

## Installation

Install the required packages:

```bash
pip install -r requirements.txt
```

## Tips

- **ZIP files recommended**: For hiding multiple files, create a ZIP archive first
- **Large images work better**: Larger images can hold more data
- **PNG format preferred**: PNG provides lossless compression, maintaining data integrity
- **Remember your password**: Without the correct key, encrypted files cannot be recovered

## Troubleshooting

- **"Image too small" error**: Use a larger image or compress your file
- **"Incorrect key" error**: Verify the password is exactly as entered during concealment
- **"No hidden data found"**: Ensure the image actually contains concealed data
- **Import errors**: Make sure all required packages are installed

## Example Workflow

1. Create a ZIP file with documents you want to hide
2. Choose a high-resolution photo as your cover image
3. Set a strong password for encryption
4. Conceal the ZIP file in the image
5. Share the concealed image normally
6. Later, use the File Concealer to reveal the hidden ZIP file with your password
