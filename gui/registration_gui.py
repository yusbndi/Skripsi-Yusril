import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
import os
import time
from pathlib import Path
from utils.config import Config
from utils.helpers import validate_name, create_directory
from core.camera_handler import CameraHandler
from core.face_detector import FaceDetector
from gui.lighting_gui import LightingGUI
from gui.dataset_viewer import DatasetViewer


class RegistrationGUI:
    """GUI untuk pendaftaran wajah"""

    def __init__(self, parent):
        self.parent = parent
        self.window = None
        self.camera = None
        self.detector = FaceDetector()
        self.lighting_gui = None
        self.dataset_viewer = None

        # Registration state
        self.is_registering = False
        self.user_name = ""
        self.current_distance = ""
        self.current_contrast = ""
        self.capture_count = 0
        self.preview_label = None
        self.status_label = None
        self.progress_var = None
        self.progress_label = None
        self.name_entry = None
        self.start_button = None
        self.is_running = False

    def show(self):
        """Menampilkan GUI pendaftaran"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Pendaftaran Wajah")
        self.window.geometry("1050x550")
        self.window.configure(bg='#f5f5f5')
        self.window.resizable(False, False)  # Fixed size

        # Center window
        self.window.update_idletasks()
        width = 1050
        height = 550
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Inisialisasi kamera
        self.camera = CameraHandler()
        if not self.camera.start():
            messagebox.showerror("Error", "Tidak dapat membuka kamera!")
            self.window.destroy()
            return

        self.is_running = True

        # Main container
        main_container = tk.Frame(self.window, bg='#f5f5f5')
        main_container.pack(fill='both', expand=True, padx=15, pady=15)

        # ========== LEFT PANEL ==========
        left_panel = tk.Frame(main_container, bg='#ffffff', relief=tk.RIDGE, bd=1, width=340)
        left_panel.pack(side='left', fill='y', padx=(0, 10))
        left_panel.pack_propagate(False)

        # Title
        title_frame = tk.Frame(left_panel, bg='#4CAF50', height=40)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)

        tk.Label(title_frame, text="Pendaftaran Wajah", font=('Arial', 14, 'bold'),
                 bg='#4CAF50', fg='white').pack(pady=8)

        # Control content
        control_content = tk.Frame(left_panel, bg='#ffffff', padx=20, pady=20)
        control_content.pack(fill='both', expand=True)

        # Nama
        tk.Label(control_content, text="Nama Pendaftar:", font=('Arial', 11, 'bold'),
                 bg='#ffffff').pack(anchor='w', pady=5)

        self.name_entry = tk.Entry(control_content, font=('Arial', 11), width=30)
        self.name_entry.pack(anchor='w', pady=5)

        # Separator
        ttk.Separator(control_content, orient='horizontal').pack(fill='x', pady=15)

        # Info pendaftaran
        tk.Label(control_content, text="Informasi Pendaftaran:", font=('Arial', 11, 'bold'),
                 bg='#ffffff').pack(anchor='w', pady=5)

        info_text = """• 100 gambar akan diambil
• 2 jarak: Dekat & Jauh
• 5 variasi pencahayaan
• Total 50 gambar per jarak"""

        tk.Label(control_content, text=info_text, font=('Arial', 9),
                 bg='#ffffff', fg='#666666', justify='left').pack(anchor='w', pady=5)

        # Separator
        ttk.Separator(control_content, orient='horizontal').pack(fill='x', pady=15)

        # Tombol kontrol
        btn_frame = tk.Frame(control_content, bg='#ffffff')
        btn_frame.pack(pady=10)

        self.start_button = tk.Button(btn_frame, text="▶ Mulai Pendaftaran",
                                      font=('Arial', 11, 'bold'),
                                      bg='#4CAF50', fg='white', padx=15, pady=8,
                                      command=self.start_registration)
        self.start_button.pack(side='left', padx=5)

        tk.Button(btn_frame, text="📁 Lihat Dataset", font=('Arial', 11),
                  bg='#2196F3', fg='white', padx=15, pady=8,
                  command=self.show_dataset_viewer).pack(side='left', padx=5)

        # Progress frame
        progress_frame = tk.Frame(control_content, bg='#ffffff')
        progress_frame.pack(fill='x', pady=15)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                            maximum=100, length=280)
        self.progress_bar.pack(pady=5)

        self.progress_label = tk.Label(progress_frame, text="0 / 100 gambar",
                                       font=('Arial', 10, 'bold'), bg='#ffffff', fg='#4CAF50')
        self.progress_label.pack()

        # Status
        self.status_label = tk.Label(control_content, text="Status: Siap",
                                     font=('Arial', 10), bg='#ffffff', fg='#2196F3')
        self.status_label.pack(pady=10)

        # Instruksi
        inst_frame = tk.Frame(control_content, bg='#e8f5e9', relief=tk.RIDGE, bd=1)
        inst_frame.pack(fill='x', pady=10)

        inst_text = """Instruksi:
1. Masukkan nama pendaftar
2. Klik 'Mulai Pendaftaran'
3. Ikuti petunjuk layar pencahayaan
4. Pastikan wajah terlihat jelas"""

        tk.Label(inst_frame, text=inst_text, font=('Arial', 9),
                 bg='#e8f5e9', fg='#333333', justify='left').pack(padx=10, pady=10, anchor='w')

        # ========== RIGHT PANEL ==========
        right_panel = tk.Frame(main_container, bg='#ffffff', relief=tk.RIDGE, bd=1)
        right_panel.pack(side='right', fill='both', expand=True)

        # Preview Title
        preview_title = tk.Frame(right_panel, bg='#4CAF50', height=40)
        preview_title.pack(fill='x')
        preview_title.pack_propagate(False)

        tk.Label(preview_title, text="Preview Kamera", font=('Arial', 14, 'bold'),
                 bg='#4CAF50', fg='white').pack(pady=8)

        # Preview Container dengan ukuran fixed 640x360
        preview_container = tk.Frame(right_panel, bg='#000000')
        preview_container.pack(expand=True, pady=10)

        # Label preview dengan ukuran fixed 640x360
        self.preview_label = tk.Label(preview_container, bg='#000000',
                                      width=640, height=360)
        self.preview_label.pack()
        self.preview_label.pack_propagate(False)

        # Preview info
        preview_info = tk.Frame(right_panel, bg='#ffffff', pady=5)
        preview_info.pack(fill='x')

        tk.Label(preview_info, text=f"Resolusi Kamera: {Config.CAMERA_WIDTH}x{Config.CAMERA_HEIGHT} | "
                                    f"Preview: 640x360",
                 font=('Arial', 8), bg='#ffffff', fg='#999999').pack()

        # Start preview update
        self.update_preview()

    def update_preview(self):
        """Update preview kamera dengan ukuran fixed 640x360"""
        if self.is_running and self.window and self.camera and self.camera.is_available():
            frame = self.camera.get_frame()

            if frame is not None:
                # Deteksi wajah
                face = self.detector.get_largest_face(frame)
                if face is not None:
                    self.detector.draw_face_box(frame, face, (0, 255, 0))

                # Resize ke 640x360
                display_frame = cv2.resize(frame, (640, 360))
                frame_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                photo = ImageTk.PhotoImage(img)

                self.preview_label.config(image=photo)
                self.preview_label.image = photo

            self.window.after(30, self.update_preview)

    def start_registration(self):
        """Memulai proses pendaftaran"""
        name = self.name_entry.get().strip()
        is_valid, message = validate_name(name)

        if not is_valid:
            messagebox.showerror("Error", message)
            return

        user_dir = Config.DATASET_DIR / name
        if user_dir.exists():
            if not messagebox.askyesno("Konfirmasi", f"User '{name}' sudah ada. Lanjutkan untuk menambah data?"):
                return

        self.user_name = name
        create_directory(user_dir)

        self.capture_count = 0
        self.progress_var.set(0)
        self.progress_label.config(text="0 / 100 gambar")

        self.name_entry.config(state='disabled')
        self.start_button.config(state='disabled')

        self.lighting_gui = LightingGUI(self.window, self.on_lighting_ready)
        self.lighting_gui.show()


    def on_lighting_ready(self, distance, contrast):
        """Callback saat lighting GUI siap untuk capture"""
        if distance == "complete":
            self.finish_registration()
            return

        if contrast == "start":
            self.current_distance = distance
            self.status_label.config(
                text=f"Status: Memulai capture untuk jarak {distance}"
            )
            return

        self.current_distance = distance
        self.current_contrast = contrast

        self.status_label.config(
            text=f"Status: Mendaftarkan - Jarak: {distance}, Kontras: {contrast} ({self.capture_count + 1}/100)"
        )

        frame = self.camera.get_frame()

        if frame is not None:
            face = self.detector.get_largest_face(frame)

            if face is not None:
                # ===== 1. SIMPAN FOTO WAJAH (PREPROCESSED) UNTUK TRAINING =====
                processed_face = self.detector.extract_and_preprocess(frame, face, equalize_hist=True)

                if processed_face is not None:
                    filename = f"{self.user_name}_{self.current_distance}_{self.current_contrast}_{self.capture_count:03d}.jpg"
                    filepath = Config.DATASET_DIR / self.user_name / filename
                    cv2.imwrite(str(filepath), processed_face)

                    # ===== 2. SIMPAN FOTO ASLI (FULL FRAME - TANPA DRAW BOX) =====
                    original_dir = Config.DATASET_DIR / self.user_name / "original"
                    original_dir.mkdir(parents=True, exist_ok=True)
                    original_filepath = original_dir / f"original_{filename}"
                    cv2.imwrite(str(original_filepath), frame)

                    # ===== 3. SIMPAN FOTO WAJAH CROP (TANPA PREPROCESS) =====
                    face_crop = self.detector.extract_face_roi(frame, face)
                    face_dir = Config.DATASET_DIR / self.user_name / "faces"
                    face_dir.mkdir(parents=True, exist_ok=True)
                    face_filepath = face_dir / f"face_{filename}"
                    cv2.imwrite(str(face_filepath), face_crop)

                    self.capture_count += 1
                    self.progress_var.set(self.capture_count)
                    self.progress_label.config(text=f"{self.capture_count} / 100 gambar")
                    self.window.update()

    def finish_registration(self):
        """Selesai pendaftaran"""
        self.name_entry.config(state='normal')
        self.start_button.config(state='normal')
        self.name_entry.delete(0, tk.END)

        self.status_label.config(
            text=f"Status: Pendaftaran selesai! Total {self.capture_count} gambar",
            fg='green'
        )

        messagebox.showinfo("Sukses", f"Pendaftaran {self.user_name} selesai!\nTotal: {self.capture_count} gambar")

    def show_dataset_viewer(self):
        """Menampilkan dataset viewer"""
        self.dataset_viewer = DatasetViewer(self.window)
        self.dataset_viewer.show()

    def on_closing(self):
        """Handler saat window ditutup"""
        print("Registration GUI closing...")
        self.is_running = False

        if self.camera:
            print("Stopping camera...")
            self.camera.stop()
            self.camera = None

        if self.window:
            self.window.destroy()
            self.window = None

        print("Registration GUI closed")

    def close(self):
        """Menutup GUI pendaftaran"""
        self.on_closing()