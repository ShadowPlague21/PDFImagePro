# PDFImagePro

🚀 A high-performance Python GUI application for converting PDF pages to images with GPU acceleration, intelligent multi-threading, and advanced memory optimization.

## Features
✨ **Multiple Extraction Modes**: Single Page, Page Range, Whole PDF, Batch PDFs  
🖼️ **High-Quality Output**: PNG (lossless) or JPEG formats at 300 DPI  
⚡ **Performance Optimized**: Multi-threading with intelligent RAM management  
🚀 **GPU Acceleration**: Optional CUDA support for faster processing  
📊 **Real-time Feedback**: Progress bars and detailed status updates  
🎯 **Smart Memory Management**: Automatically adjusts thread count based on available RAM  
📁 **Batch Processing**: Process multiple PDFs with organized output folders

## Requirements
- **Python 3.8+** (3.10+ recommended for best performance)
- **Windows, macOS, or Linux**
- **Dependencies**: Listed in `requirements.txt`
- **Optional**: CUDA-compatible GPU for acceleration

## Installation

### Quick Start
1. **Clone the repository**:
   ```bash
   git clone https://github.com/ShadowPlague21/PDFImagePro.git
   cd PDFImagePro
   ```

2. **Create and activate a virtual environment**:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### GPU Support
- **Automatic Detection**: PyTorch will automatically install the appropriate version for your system
- **CUDA Support**: Ensure you have CUDA-compatible GPU drivers installed
- **Fallback**: The application automatically falls back to CPU if GPU is unavailable

## Usage

### Running the Application
```bash
python pdf_extractor.py
```

### Using the GUI
1. **Select Extraction Mode**:
   - 🔹 **Single Page**: Extract one specific page
   - 📄 **Page Range**: Extract pages within a range (e.g., 1-10)
   - 📚 **Whole PDF**: Convert entire PDF to images
   - 📁 **Batch PDFs**: Process multiple PDF files at once

2. **Choose Input & Output**:
   - Select PDF file(s) using the file browser
   - Choose output directory for generated images

3. **Configure Settings**:
   - **Format**: PNG (lossless) or JPEG (compressed)
   - **GPU Acceleration**: Enable for faster processing (if available)

4. **Start Extraction**:
   - Click "Extract" and monitor progress
   - Cancel anytime if needed

## Technical Details
- **Image Quality**: 300 DPI for professional-grade output
- **Memory Management**: Intelligent thread allocation based on available RAM
- **Batch Organization**: Creates organized subfolders for each PDF
- **Error Handling**: Graceful fallback and detailed error reporting
- **Performance**: Multi-threaded processing with optional GPU acceleration

## Troubleshooting
- **GPU Issues**: Application automatically falls back to CPU if CUDA is unavailable
- **Memory Errors**: Thread count is automatically reduced for large files
- **Dependencies**: Run `pip install --upgrade -r requirements.txt` if issues occur 