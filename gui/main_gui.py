import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from pathlib import Path
from utils.config import Config


class MainGUI:
    """GUI Utama sistem"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistem Gerbang Pengenal Wajah")
        self.root.geometry("900x650")
        self.root.configure(bg='#1a1a2e')

        # Center window on screen
        self.center_window()

        # Inisialisasi direktori
        Config.initialize_directories()

        # Variabel GUI
        self.registration_gui = None
        self.recognition_gui = None
        self.analysis_gui = None
        self.logo_image = None

        self.setup_ui()

    def center_window(self):
        """Menempatkan window di tengah layar"""
        self.root.update_idletasks()
        width = 900
        height = 650
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def setup_ui(self):
        """Setup UI utama"""
        # Main container dengan gradient background
        main_container = tk.Frame(self.root, bg='#1a1a2e')
        main_container.pack(fill='both', expand=True)

        # Content frame (centered)
        content_frame = tk.Frame(main_container, bg='#16213e')
        content_frame.pack(expand=True, fill='both', padx=40, pady=30)

        # Title
        title_label = tk.Label(
            content_frame,
            text="SISTEM GERBANG PENGENAL WAJAH",
            font=('Arial', 28, 'bold'),
            fg='#e94560',
            bg='#16213e'
        )
        title_label.pack(pady=(30, 10))

        # Subtitle
        subtitle_label = tk.Label(
            content_frame,
            text="Universitas Negeri Semarang",
            font=('Arial', 14, 'italic'),
            fg='#ffffff',
            bg='#16213e'
        )
        subtitle_label.pack(pady=(0, 10))

        # Separator line
        separator = tk.Frame(content_frame, height=2, width=400, bg='#e94560')
        separator.pack(pady=10)
        separator.pack_propagate(False)

        # Logo
        try:
            logo_path = Config.BASE_DIR / "assets" / "unnes.png"
            if logo_path.exists():
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((120, 156), Image.Resampling.LANCZOS)

                # Buat logo dengan transparansi
                if logo_img.mode != 'RGBA':
                    logo_img = logo_img.convert('RGBA')

                self.logo_image = ImageTk.PhotoImage(logo_img)

                logo_label = tk.Label(content_frame, image=self.logo_image, bg='#16213e')
                logo_label.pack(pady=10)
        except Exception as e:
            print(f"Logo tidak ditemukan: {e}")
            logo_placeholder = tk.Label(
                content_frame,
                text="UNNES",
                font=('Arial', 20, 'bold'),
                fg='#e94560',
                bg='#16213e'
            )
            logo_placeholder.pack(pady=10)

        # Button frame
        button_frame = tk.Frame(content_frame, bg='#16213e')
        button_frame.pack(pady=10)

        # Button style
        button_style = {
            'font': ('Arial', 13, 'bold'),
            'bg': '#0f3460',
            'fg': '#ffffff',
            'activebackground': '#e94560',
            'activeforeground': '#ffffff',
            'bd': 0,
            'padx': 40,
            'pady': 10,
            'width': 20,
            'cursor': 'hand2'
        }

        # Registration button
        reg_button = tk.Button(
            button_frame,
            text="📋 Pendaftaran Wajah",
            command=self.open_registration,
            **button_style
        )
        reg_button.pack(pady=10)

        # Recognition button
        recog_button = tk.Button(
            button_frame,
            text="🔓 Pengenalan Wajah",
            command=self.open_recognition,
            **button_style
        )
        recog_button.pack(pady=10)

        # Analysis button
        analysis_button = tk.Button(
            button_frame,
            text="📊 Analisis Performa",
            command=self.open_analysis,
            **button_style
        )
        analysis_button.pack(pady=10)

        # Hover effects
        for btn in [reg_button, recog_button, analysis_button]:
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg='#e94560'))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg='#0f3460'))

        # Footer
        footer_frame = tk.Frame(content_frame, bg='#16213e')
        footer_frame.pack(side='bottom', pady=10)

        tk.Label(
            footer_frame,
            text="©2026 - Skripsi Yusril Subhanandi - Teknik Elektro",
            font=('Arial', 9),
            fg='#888888',
            bg='#16213e'
        ).pack()

        # Version
        tk.Label(
            footer_frame,
            text="v1.0.0 | OpenCV | Haar Cascade | LBPH",
            font=('Arial', 8),
            fg='#666666',
            bg='#16213e'
        ).pack()

    def open_registration(self):
        """Membuka GUI pendaftaran"""
        from gui.registration_gui import RegistrationGUI
        self.registration_gui = RegistrationGUI(self.root)
        self.registration_gui.show()

    def open_recognition(self):
        """Membuka GUI pengenalan"""
        from gui.recognition_gui import RecognitionGUI
        self.recognition_gui = RecognitionGUI(self.root)
        self.recognition_gui.show()

    def open_analysis(self):
        """Membuka GUI analisis"""
        from gui.analysis_gui import AnalysisGUI
        self.analysis_gui = AnalysisGUI(self.root)
        self.analysis_gui.show()

    def run(self):
        """Menjalankan aplikasi"""
        self.root.mainloop()