# PDF Extractor

A Python GUI application for extracting images from PDFs with multi-threading, RAM optimization, optional GPU acceleration, and support for various extraction modes.

## Features
- Extraction Modes: Single Page, Page Range, Whole PDF, Batch PDFs.
- Output Formats: PNG (lossless) or JPEG (high quality).
- Multi-threading for faster extraction, adjusted based on available RAM.
- Checkbox for GPU acceleration (using PyTorch CUDA if available).
- Progress bar and status updates.

## Requirements
- Python 3.x
- Dependencies listed in `requirements.txt`

## Installation
1. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
   Note: For GPU support, ensure you have a CUDA-compatible GPU and drivers. The torch installation assumes CUDA 11.8; adjust if needed.

## Usage
1. Run the application:
   ```
   python pdf_extractor.py
   ```
2. In the GUI:
   - Select extraction mode.
   - Choose PDF(s) and output directory.
   - Select format and GPU option.
   - Click "Extract".

## Notes
- Extracts images at high quality (300 DPI).
- Batch mode creates subfolders per PDF.
- If GPU is selected but unavailable, falls back to CPU. 