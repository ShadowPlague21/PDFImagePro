import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import fitz  # PyMuPDF
from PIL import Image
import psutil
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import threading
import queue
import torch
import numpy as np
import io

class PDFExtractor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PDF Extractor")
        self.geometry("600x500")
        self.resizable(True, True)  # Make window resizable

        # Apply a modern theme
        style = ttk.Style(self)
        style.theme_use('clam')  # or 'alt', 'default', etc.

        self.mode_var = tk.StringVar(value="Whole PDF")
        self.format_var = tk.StringVar(value="PNG")
        self.gpu_var = tk.BooleanVar(value=False)
        self.pdf_paths = []
        self.output_dir = ""
        self.stop_extraction = False  # Flag for cancellation

        # Main frame with padding
        main_frame = ttk.Frame(self, padding="10 10 10 10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Mode selection
        ttk.Label(main_frame, text="Extraction Mode:").grid(row=0, column=0, sticky=tk.W, pady=5)
        modes = ["Single Page", "Page Range", "Whole PDF", "Batch PDFs"]
        self.mode_menu = ttk.OptionMenu(main_frame, self.mode_var, "Whole PDF", *modes, command=self.update_inputs)
        self.mode_menu.grid(row=0, column=1, sticky=tk.EW, pady=5)
        ttk.Label(main_frame, text="(Choose how to extract pages)").grid(row=0, column=2, sticky=tk.W, pady=5)

        # Input frame
        self.input_frame = ttk.Frame(main_frame)
        self.input_frame.grid(row=1, column=0, columnspan=3, sticky=tk.EW, pady=5)

        # PDF selection
        self.pdf_button = ttk.Button(main_frame, text="Select PDF(s)", command=self.select_pdfs)
        self.pdf_button.grid(row=2, column=0, columnspan=2, sticky=tk.EW, pady=5)
        self.pdf_label = ttk.Label(main_frame, text="No PDF selected")
        self.pdf_label.grid(row=2, column=2, sticky=tk.W, pady=5)

        # Output directory
        ttk.Button(main_frame, text="Select Output Directory", command=self.select_output_dir).grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=5)
        self.output_label = ttk.Label(main_frame, text="No directory selected")
        self.output_label.grid(row=3, column=2, sticky=tk.W, pady=5)

        # Format selection
        ttk.Label(main_frame, text="Output Format:").grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.OptionMenu(main_frame, self.format_var, "PNG", "PNG", "JPEG").grid(row=4, column=1, sticky=tk.EW, pady=5)
        ttk.Label(main_frame, text="(PNG for lossless, JPEG for smaller files)").grid(row=4, column=2, sticky=tk.W, pady=5)

        # GPU checkbox
        ttk.Checkbutton(main_frame, text="Use GPU Acceleration (if available)", variable=self.gpu_var).grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=5)

        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=6, column=0, columnspan=3, sticky=tk.EW, pady=10)
        self.extract_button = ttk.Button(buttons_frame, text="Extract", command=self.start_extraction)
        self.extract_button.pack(side=tk.LEFT, expand=True)
        self.cancel_button = ttk.Button(buttons_frame, text="Cancel", command=self.cancel_extraction, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT, expand=True)

        # Progress
        self.progress = ttk.Progressbar(main_frame, mode="determinate")
        self.progress.grid(row=7, column=0, columnspan=3, sticky=tk.EW, pady=5)
        self.status_label = ttk.Label(main_frame, text="")
        self.status_label.grid(row=8, column=0, columnspan=3, sticky=tk.W, pady=5)

        self.update_inputs(self.mode_var.get())

    def update_inputs(self, mode):
        for widget in self.input_frame.winfo_children():
            widget.destroy()

        if mode == "Single Page":
            ttk.Label(self.input_frame, text="Page Number:").grid(row=0, column=0, sticky=tk.W)
            self.page_entry = ttk.Entry(self.input_frame, validate="key")
            self.page_entry['validatecommand'] = (self.register(self.validate_number), '%P')
            self.page_entry.grid(row=0, column=1, sticky=tk.EW)
            ttk.Label(self.input_frame, text="(Enter a positive integer)").grid(row=0, column=2, sticky=tk.W)
        elif mode == "Page Range":
            ttk.Label(self.input_frame, text="Page Range (e.g., 1-5):").grid(row=0, column=0, sticky=tk.W)
            self.range_entry = ttk.Entry(self.input_frame, validate="key")
            self.range_entry['validatecommand'] = (self.register(self.validate_range), '%P')
            self.range_entry.grid(row=0, column=1, sticky=tk.EW)
            ttk.Label(self.input_frame, text="(Format: start-end, positive integers)").grid(row=0, column=2, sticky=tk.W)
        # Whole and Batch need no extra inputs

    def validate_number(self, value):
        return value.isdigit() or value == ""

    def validate_range(self, value):
        if value == "": return True
        parts = value.split("-")
        if len(parts) > 2: return False
        return all(p.isdigit() for p in parts)

    def select_pdfs(self):
        mode = self.mode_var.get()
        if mode == "Batch PDFs":
            files = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
            self.pdf_paths = list(files)
            if self.pdf_paths:
                self.pdf_label.config(text=f"{len(self.pdf_paths)} PDFs selected")
            else:
                self.pdf_label.config(text="No PDF selected")
        else:
            file = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
            self.pdf_paths = [file] if file else []
            self.pdf_label.config(text=os.path.basename(file) if file else "No PDF selected")

    def select_output_dir(self):
        self.output_dir = filedialog.askdirectory()
        self.output_label.config(text=self.output_dir if self.output_dir else "No directory selected")

    def start_extraction(self):
        if not self.pdf_paths or not self.output_dir:
            messagebox.showerror("Error", "Please select PDF(s) and output directory.")
            return

        mode = self.mode_var.get()
        if mode == "Single Page" and not self.page_entry.get().isdigit():
            messagebox.showerror("Error", "Invalid page number.")
            return
        if mode == "Page Range":
            try:
                start, end = map(int, self.range_entry.get().split("-"))
                if start > end or start < 1:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Invalid page range.")
                return

        self.stop_extraction = False
        self.extract_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.progress["value"] = 0
        self.status_label.config(text="Starting extraction...")

        self.progress_queue = queue.Queue()
        threading.Thread(target=self.perform_extraction, daemon=True).start()
        self.after(100, self.check_progress)

    def cancel_extraction(self):
        self.stop_extraction = True
        self.status_label.config(text="Cancelling extraction...")
        self.extract_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)

    def check_progress(self):
        try:
            while not self.progress_queue.empty():
                total, done = self.progress_queue.get_nowait()
                self.progress["maximum"] = total
                self.progress["value"] = done
                self.status_label.config(text=f"Processed {done}/{total} pages")
            if self.progress["value"] < self.progress["maximum"] and not self.stop_extraction:
                self.after(100, self.check_progress)
            else:
                if self.stop_extraction:
                    self.status_label.config(text="Extraction cancelled.")
                    messagebox.showinfo("Cancelled", "Extraction process stopped.")
                else:
                    self.status_label.config(text="Extraction completed!")
                    messagebox.showinfo("Done", "Extraction finished.")
                self.extract_button.config(state=tk.NORMAL)
                self.cancel_button.config(state=tk.DISABLED)
        except queue.Empty:
            if not self.stop_extraction:
                self.after(100, self.check_progress)
            else:
                self.extract_button.config(state=tk.NORMAL)
                self.cancel_button.config(state=tk.DISABLED)

    def perform_extraction(self):
        device = "cuda" if self.gpu_var.get() and torch.cuda.is_available() else "cpu"
        fmt = self.format_var.get()
        mode = self.mode_var.get()

        total_pages = 0
        for pdf_path in self.pdf_paths:
            if self.stop_extraction:
                return
            doc = fitz.open(pdf_path)
            if mode == "Single Page":
                try:
                    page_num = int(self.page_entry.get()) - 1
                    pages = [page_num] if 0 <= page_num < doc.page_count else []
                except ValueError:
                    pages = []
            elif mode == "Page Range":
                try:
                    start, end = map(int, self.range_entry.get().split("-"))
                    pages = list(range(start-1, end))
                except ValueError:
                    pages = []
            else:  # Whole or Batch (whole per PDF)
                pages = list(range(doc.page_count))
            total_pages += len(pages)
            doc.close()

        self.progress_queue.put((total_pages, 0))

        avail_ram_gb = psutil.virtual_memory().available / (1024 ** 3)
        max_workers = max(1, min(os.cpu_count() or 4, int(avail_ram_gb / 0.5)))  # Assume 0.5GB per thread

        done = 0
        for pdf_path in self.pdf_paths:
            if self.stop_extraction:
                return
            doc = fitz.open(pdf_path)
            if mode == "Batch PDFs":
                pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
                pdf_output_dir = os.path.join(self.output_dir, pdf_name)
                os.makedirs(pdf_output_dir, exist_ok=True)
            else:
                pdf_output_dir = self.output_dir

            # Get pages for this PDF
            if mode == "Single Page":
                page_num = int(self.page_entry.get()) - 1
                pages = [page_num] if 0 <= page_num < doc.page_count else []
            elif mode == "Page Range":
                start, end = map(int, self.range_entry.get().split("-"))
                pages = [p for p in range(start-1, end) if 0 <= p < doc.page_count]
            else:
                pages = list(range(doc.page_count))

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_page = {executor.submit(self.extract_page, doc, p, pdf_output_dir, fmt, device): p for p in pages}
                for future in as_completed(future_to_page):
                    if self.stop_extraction:
                        for f in future_to_page:
                            f.cancel()
                        doc.close()
                        return
                    try:
                        future.result()
                        done += 1
                        self.progress_queue.put((total_pages, done))
                    except Exception as e:
                        print(f"Error extracting page: {e}")
                        self.progress_queue.put((total_pages, done))  # Continue but log error

            doc.close()

    @staticmethod
    def extract_page(doc, page_num, output_dir, fmt, device):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=300)  # High quality
        img_data = pix.tobytes("ppm")
        img = Image.open(io.BytesIO(img_data))

        if device == "cuda":
            # Dummy GPU usage
            arr = np.array(img)
            tensor = torch.from_numpy(arr).to(device)
            arr = tensor.cpu().numpy()
            img = Image.fromarray(arr)

        filepath = os.path.join(output_dir, f"page_{page_num + 1}.{fmt.lower()}")
        if fmt == "JPEG":
            img.save(filepath, "JPEG", quality=95)
        else:
            img.save(filepath, "PNG")

if __name__ == "__main__":
    app = PDFExtractor()
    app.mainloop() 