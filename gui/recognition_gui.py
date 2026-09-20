import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
import time
from datetime import datetime
from pathlib import Path

from utils.config import Config
from utils.logger import Logger
from core.camera_handler import CameraHandler
from core.face_recognizer import FaceRecognizer
from core.face_detector import FaceDetector


class RecognitionGUI:
    """GUI untuk pengenalan wajah dan kontrol gerbang"""

    def __init__(self, parent):
        self.parent = parent
        self.window = None
        self.camera = None
        self.recognizer = FaceRecognizer()
        self.detector = FaceDetector()
        self.logger = Logger("RecognitionGUI")

        self.is_running = False
        self.gate_status = "TERTUTUP"
        self.current_user = "None"
        self.preview_label = None
        self.status_label = None
        self.gate_label = None
        self.user_label = None
        self.log_text = None
        self.log_window = None
        self.timer_label = None

        # State untuk kontrol gerbang
        self.gate_open_until = 0
        self.recognition_paused_until = 0
        self.showing_user_photo = False
        self.current_user_photo = None
        self.current_user_name_display = ""
        self.captured_face_frame = None  # Frame wajah yang dikenali

        # Foto user yang dikenali
        self.user_photo_label = None
        self.preview_frame = None

        # Flag untuk menghindari multiple open_gate calls
        self.is_processing_gate = False
        self.gate_timer_active = False  # Flag untuk timer

        # Preview mode
        self.preview_mode = 'camera'
        self.camera_btn = None
        self.photo_btn = None

    def show(self):
        """Menampilkan GUI pengenalan"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Pengenalan Wajah - Gerbang Otomatis")
        self.window.geometry("1050x550")
        self.window.configure(bg='#f5f5f5')
        self.window.resizable(False, False)

        # Center window
        self.window.update_idletasks()
        width = 1050
        height = 550
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        if not self.recognizer.initialize():
            if not messagebox.askyesno("Warning", "Model belum dilatih. Ingin melanjutkan?"):
                self.window.destroy()
                return

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
        title_frame = tk.Frame(left_panel, bg='#2196F3', height=40)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)

        tk.Label(title_frame, text="Kontrol Gerbang", font=('Arial', 14, 'bold'),
                 bg='#2196F3', fg='white').pack(pady=8)

        # Control content
        control_content = tk.Frame(left_panel, bg='#ffffff', padx=20, pady=20)
        control_content.pack(fill='both', expand=True)

        # Status Gerbang
        status_frame = tk.Frame(control_content, bg='#f0f0f0', relief=tk.RIDGE, bd=1)
        status_frame.pack(fill='x', pady=10)

        tk.Label(status_frame, text="STATUS GERBANG", font=('Arial', 11, 'bold'),
                 bg='#f0f0f0').pack(pady=5)

        self.gate_label = tk.Label(status_frame, text="TERTUTUP",
                                   font=('Arial', 28, 'bold'), fg='#f44336', bg='#f0f0f0')
        self.gate_label.pack(pady=10)

        # Info Pengguna
        user_frame = tk.Frame(control_content, bg='#e3f2fd', relief=tk.RIDGE, bd=1)
        user_frame.pack(fill='x', pady=10)

        tk.Label(user_frame, text="PENGGUNA", font=('Arial', 10, 'bold'),
                 bg='#e3f2fd', fg='#1565C0').pack(pady=5)

        self.user_label = tk.Label(user_frame, text="-", font=('Arial', 16, 'bold'),
                                   bg='#e3f2fd', fg='#333333')
        self.user_label.pack(pady=5)

        # Timer
        self.timer_label = tk.Label(control_content, text="", font=('Arial', 12),
                                    bg='#ffffff', fg='#2196F3')
        self.timer_label.pack(pady=5)

        # Separator
        ttk.Separator(control_content, orient='horizontal').pack(fill='x', pady=15)

        # Tombol kontrol
        btn_frame = tk.Frame(control_content, bg='#ffffff')
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="📋 Lihat Log", font=('Arial', 11),
                  bg='#2196F3', fg='white', padx=15, pady=8,
                  command=self.show_log_window).pack(side='left', padx=5)

        tk.Button(btn_frame, text="🔓 Buka Manual", font=('Arial', 11),
                  bg='#FF9800', fg='white', padx=15, pady=8,
                  command=self.open_gate_manual).pack(side='left', padx=5)

        tk.Button(btn_frame, text="🔒 Tutup", font=('Arial', 11),
                  bg='#f44336', fg='white', padx=15, pady=8,
                  command=self.close_gate).pack(side='left', padx=5)

        # Status
        self.status_label = tk.Label(control_content, text="Status: Sistem siap",
                                     font=('Arial', 10), bg='#ffffff', fg='#4CAF50')
        self.status_label.pack(pady=10)

        # Info sistem
        info_frame = tk.Frame(control_content, bg='#f5f5f5', relief=tk.RIDGE, bd=1)
        info_frame.pack(fill='x', pady=10)

        info_text = f"Threshold: {Config.LBPH_THRESHOLD} | Kamera: {Config.CAMERA_WIDTH}x{Config.CAMERA_HEIGHT}"
        tk.Label(info_frame, text=info_text, font=('Arial', 8),
                 bg='#f5f5f5', fg='#666666').pack(pady=5)

        # ========== RIGHT PANEL ==========
        right_panel = tk.Frame(main_container, bg='#ffffff', relief=tk.RIDGE, bd=1)
        right_panel.pack(side='right', fill='both', expand=True)

        # Preview Title
        preview_title = tk.Frame(right_panel, bg='#2196F3', height=40)
        preview_title.pack(fill='x')
        preview_title.pack_propagate(False)

        tk.Label(preview_title, text="Preview", font=('Arial', 14, 'bold'),
                 bg='#2196F3', fg='white').pack(pady=8)

        # Preview Container
        preview_container = tk.Frame(right_panel, bg='#000000')
        preview_container.pack(expand=True, pady=10)

        # Label preview kamera
        self.preview_label = tk.Label(preview_container, bg='#000000',
                                      width=640, height=360)
        self.preview_label.pack()
        self.preview_label.pack_propagate(False)

        # Label foto user
        self.user_photo_label = tk.Label(preview_container, bg='#000000',
                                         width=640, height=360)

        # Preview toggle
        toggle_frame = tk.Frame(right_panel, bg='#ffffff', pady=5)
        toggle_frame.pack(fill='x')

        self.camera_btn = tk.Button(toggle_frame, text="Kamera", font=('Arial', 9, 'bold'),
                                    bg='#2196F3', fg='white', padx=15, pady=3,
                                    command=self.show_camera_preview)
        self.camera_btn.pack(side='left', padx=5)

        self.photo_btn = tk.Button(toggle_frame, text="Foto Hasil", font=('Arial', 9),
                                   bg='#9E9E9E', fg='white', padx=15, pady=3,
                                   command=self.show_photo_preview, state='disabled')
        self.photo_btn.pack(side='left', padx=5)

        tk.Label(toggle_frame, text="Preview: 640x360",
                 font=('Arial', 8), bg='#ffffff', fg='#999999').pack(side='right', padx=10)

        # Start recognition
        self.update_recognition()

    def show_camera_preview(self):
        """Tampilkan preview kamera"""
        self.preview_mode = 'camera'
        self.camera_btn.config(bg='#2196F3')
        self.photo_btn.config(bg='#9E9E9E')
        self.user_photo_label.pack_forget()
        self.preview_label.pack()
        self.showing_user_photo = False

    def show_photo_preview(self):
        """Tampilkan preview foto hasil pengenalan"""
        if self.captured_face_frame is not None:
            self.preview_mode = 'photo'
            self.camera_btn.config(bg='#9E9E9E')
            self.photo_btn.config(bg='#2196F3')
            self.preview_label.pack_forget()
            self.user_photo_label.pack()
            self.showing_user_photo = True

    def update_recognition(self):
        """Update proses pengenalan"""
        if not self.is_running:
            return

        current_time = time.time()

        # Cek apakah gerbang harus ditutup (timer 5 detik)
        if self.gate_status == "TERBUKA" and current_time >= self.gate_open_until:
            print(f"[TIMER] Gate timer expired, closing gate...")
            self.close_gate()
            return

        # Cek apakah dalam masa jeda setelah gerbang tertutup
        if current_time < self.recognition_paused_until:
            remaining = int(self.recognition_paused_until - current_time)
            self.timer_label.config(text=f"Jeda: {remaining} detik")

            # Update preview kamera selama jeda
            if self.camera and self.camera.is_available():
                if self.showing_user_photo:
                    self.show_camera_preview()

                frame = self.camera.get_frame()
                if frame is not None:
                    display_frame = frame.copy()
                    cv2.putText(display_frame, f"Jeda {remaining}s", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

                    preview_frame = cv2.resize(display_frame, (640, 360))
                    frame_rgb = cv2.cvtColor(preview_frame, cv2.COLOR_BGR2RGB)
                    photo = ImageTk.PhotoImage(Image.fromarray(frame_rgb))

                    self.preview_label.config(image=photo)
                    self.preview_label.image = photo

            self.window.after(1000, self.update_recognition)
            return
        else:
            self.timer_label.config(text="")

        # Pengenalan hanya jika gerbang TERTUTUP
        if self.gate_status == "TERTUTUP" and self.camera and self.camera.is_available():
            # Pastikan preview kamera yang tampil
            if self.showing_user_photo:
                self.show_camera_preview()

            frame = self.camera.get_frame()

            if frame is not None:
                name, confidence, face = self.recognizer.recognize(frame)

                if name not in ["Unknown", "No Face", "Error", "No Model"]:
                    self.user_label.config(text=f"{name} ({confidence:.1f}%)")

                    # Buka gerbang jika belum processing
                    if not self.is_processing_gate:
                        print(f"[RECOGNITION] Face recognized: {name}, opening gate...")
                        # Simpan frame wajah yang dikenali
                        self.captured_face_frame = frame.copy()
                        self.open_gate(name)
                        return  # PENTING: Hentikan loop, nanti dilanjutkan oleh timer
                else:
                    self.user_label.config(text="-")

                # Gambar hasil pengenalan
                frame_with_result = self.recognizer.draw_recognition_result(
                    frame, name, confidence, face
                )

                preview_frame = cv2.resize(frame_with_result, (640, 360))
                frame_rgb = cv2.cvtColor(preview_frame, cv2.COLOR_BGR2RGB)
                photo = ImageTk.PhotoImage(Image.fromarray(frame_rgb))

                self.preview_label.config(image=photo)
                self.preview_label.image = photo

        # Lanjutkan loop
        self.window.after(30, self.update_recognition)

    def open_gate(self, user_name=""):
        """Membuka gerbang selama 5 detik"""
        if self.is_processing_gate:
            print("[GATE] Already processing, ignoring open_gate")
            return

        self.is_processing_gate = True
        self.gate_status = "TERBUKA"
        self.gate_label.config(text="TERBUKA", fg='#4CAF50')

        # Set timer 5 detik
        self.gate_open_until = time.time() + 5
        print(f"[GATE] Gate opened for {user_name}, will close at {self.gate_open_until}")

        self.current_user_name_display = user_name
        self.user_label.config(text=f"{user_name} (TERBUKA)")
        self.status_label.config(text=f"Gerbang terbuka untuk {user_name}")

        # Log akses
        self.logger.access_log(user_name, "TERBUKA")

        # Tampilkan foto hasil pengenalan (frame yang dicapture)
        self.show_captured_face(user_name)

        # Mulai timer update
        self.update_gate_timer()

    def show_captured_face(self, user_name):
        """Menampilkan foto wajah yang baru saja dikenali"""
        if self.captured_face_frame is not None:
            # Deteksi wajah pada frame
            face = self.detector.get_largest_face(self.captured_face_frame)

            display_frame = self.captured_face_frame.copy()

            if face is not None:
                x, y, w, h = face
                # Gambar kotak hijau
                cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                # Tambahkan label nama
                cv2.putText(display_frame, user_name, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            # Resize ke 640x360
            display_frame = cv2.resize(display_frame, (640, 360))
            frame_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            photo = ImageTk.PhotoImage(Image.fromarray(frame_rgb))

            self.current_user_photo = photo
            self.user_photo_label.config(image=photo)
            self.user_photo_label.image = photo
            self.photo_btn.config(state='normal')
            self.show_photo_preview()

            print(f"[PHOTO] Displaying captured face for {user_name}")

    def update_gate_timer(self):
        """Update timer gerbang"""
        if self.gate_status == "TERBUKA":
            remaining = max(0, int(self.gate_open_until - time.time()))

            if remaining > 0:
                self.status_label.config(text=f"Gerbang terbuka ({remaining}s)")
                self.window.after(1000, self.update_gate_timer)
                print(f"[TIMER] Gate open, {remaining}s remaining")
            else:
                # Timer habis, tutup gerbang
                print(f"[TIMER] Timer finished, closing gate")
                self.close_gate()

    def open_gate_manual(self):
        """Buka gerbang manual"""
        if self.camera and self.camera.is_available():
            frame = self.camera.get_frame()
            if frame is not None:
                self.captured_face_frame = frame.copy()
        self.open_gate("Manual")

    def close_gate(self):
        """Tutup gerbang dan mulai jeda 3 detik"""
        print(f"[GATE] Closing gate...")

        self.gate_status = "TERTUTUP"
        self.is_processing_gate = False
        self.gate_label.config(text="TERTUTUP", fg='#f44336')
        self.status_label.config(text="Gerbang tertutup - Jeda 3 detik")
        self.user_label.config(text="-")

        # Log penutupan
        self.logger.access_log("System", "TERTUTUP")

        # Set jeda 3 detik
        self.recognition_paused_until = time.time() + 3
        print(f"[GATE] Gate closed, paused until {self.recognition_paused_until}")

        # Reset foto
        self.photo_btn.config(state='disabled')
        self.captured_face_frame = None
        self.show_camera_preview()

        # Mulai kembali recognition loop
        self.window.after(100, self.update_recognition)

    def show_log_window(self):
        """Menampilkan window log"""
        self.log_window = tk.Toplevel(self.window)
        self.log_window.title("Log Akses Gerbang")
        self.log_window.geometry("700x450")
        self.log_window.configure(bg='#ffffff')

        title_frame = tk.Frame(self.log_window, bg='#2196F3', height=35)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)

        tk.Label(title_frame, text="Riwayat Buka/Tutup Gerbang", font=('Arial', 12, 'bold'),
                 bg='#2196F3', fg='white').pack(pady=6)

        text_frame = tk.Frame(self.log_window, bg='#ffffff', padx=15, pady=15)
        text_frame.pack(fill='both', expand=True)

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side='right', fill='y')

        self.log_text = tk.Text(text_frame, yscrollcommand=scrollbar.set,
                                font=('Courier', 10), wrap='word')
        self.log_text.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.log_text.yview)

        self.load_logs()

        btn_frame = tk.Frame(self.log_window, bg='#ffffff', pady=10)
        btn_frame.pack()

        tk.Button(btn_frame, text="Refresh", bg='#4CAF50', fg='white',
                  padx=15, pady=5, command=self.load_logs).pack(side='left', padx=5)

        tk.Button(btn_frame, text="Clear Log", bg='#f44336', fg='white',
                  padx=15, pady=5, command=self.clear_logs).pack(side='left', padx=5)

    def load_logs(self):
        """Memuat log"""
        if self.log_text:
            self.log_text.delete(1.0, tk.END)
            logs = self.logger.get_logs(limit=100)
            for log in logs:
                if "Akses -" in log or "Access -" in log:
                    self.log_text.insert(tk.END, log)

    def clear_logs(self):
        """Membersihkan log"""
        if messagebox.askyesno("Konfirmasi", "Hapus semua log?"):
            self.logger.clear_logs()
            self.load_logs()
            messagebox.showinfo("Sukses", "Log berhasil dibersihkan!")

    def on_closing(self):
        """Handler saat window ditutup"""
        print("Recognition GUI closing...")
        self.is_running = False

        if self.camera:
            print("Stopping camera...")
            self.camera.stop()
            self.camera = None

        if self.window:
            self.window.destroy()
            self.window = None

        print("Recognition GUI closed")

    def close(self):
        """Menutup GUI"""
        self.on_closing()