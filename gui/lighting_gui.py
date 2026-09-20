import tkinter as tk
from tkinter import ttk
import time
from utils.config import Config


class LightingGUI:
    """GUI untuk menampilkan layar kontras saat pendaftaran"""

    def __init__(self, parent, callback):
        self.parent = parent
        self.callback = callback
        self.window = None
        self.current_contrast_index = 0
        self.current_distance_index = 0
        self.is_running = False
        self.is_capturing = False
        self.contrasts = Config.CONTRASTS
        self.distances = Config.DISTANCES
        self.colors = Config.CONTRAST_COLORS
        self.capture_count = 0
        self.max_captures = 50  # 50 foto per jarak
        self.captures_per_contrast = 10  # 5 kontras x 10 = 50 foto

    def show(self):
        """Menampilkan lighting GUI"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Pencahayaan")
        self.window.attributes('-fullscreen', True)
        self.window.configure(bg='black')

        # Bind escape key untuk keluar
        self.window.bind('<Escape>', lambda e: self.close())

        # Frame utama fullscreen
        self.main_frame = tk.Frame(self.window, bg='black')
        self.main_frame.pack(expand=True, fill='both')

        # Tombol Play (simbol segitiga)
        self.play_button = tk.Button(
            self.main_frame,
            text="▶",
            font=('Arial', 80, 'bold'),
            bg='#4CAF50',
            fg='white',
            bd=0,
            padx=40,
            pady=20,
            command=self.start_capture_sequence
        )
        self.play_button.place(relx=0.5, rely=0.5, anchor='center')

        # Label status (hidden, hanya untuk debugging jika diperlukan)
        self.status_label = tk.Label(
            self.main_frame,
            text="",
            font=('Arial', 12),
            fg='white',
            bg='black'
        )
        # Tidak ditampilkan

        self.update_display()

    def update_display(self):
        """Update tampilan berdasarkan status saat ini"""
        contrast_name = self.contrasts[self.current_contrast_index]
        distance_name = self.distances[self.current_distance_index]

        # Update background color
        color_hex = '#%02x%02x%02x' % tuple(reversed(self.colors[contrast_name]))
        self.window.configure(bg=color_hex)
        self.main_frame.configure(bg=color_hex)

        # Update button text berdasarkan status
        if self.current_distance_index == 0:
            self.play_button.config(text="▶")
        else:
            self.play_button.config(text="▶")

        # Debug info (bisa dihapus jika tidak diperlukan)
        print(f"Status: {distance_name} - {contrast_name}")

    def start_capture_sequence(self):
        """Mulai sequence capture untuk jarak saat ini"""
        if self.is_capturing:
            return

        self.is_capturing = True
        self.capture_count = 0
        self.current_contrast_index = 0
        self.play_button.config(state='disabled', text="●")  # Recording indicator

        # Mulai capture untuk jarak saat ini
        distance_name = self.distances[self.current_distance_index]
        print(f"Memulai capture untuk jarak: {distance_name}")

        # Panggil callback untuk memberi tahu GUI utama
        self.callback(distance_name, "start")

        # Mulai capture kontras pertama
        self.capture_current_contrast()

    def capture_current_contrast(self):
        """Capture gambar untuk kontras saat ini"""
        if not self.is_capturing:
            return

        contrast_name = self.contrasts[self.current_contrast_index]
        distance_name = self.distances[self.current_distance_index]

        # Update warna background
        color_hex = '#%02x%02x%02x' % tuple(reversed(self.colors[contrast_name]))
        self.window.configure(bg=color_hex)
        self.main_frame.configure(bg=color_hex)

        print(f"Capturing: {distance_name} - {contrast_name} ({self.capture_count + 1}/50)")

        # Panggil callback untuk capture
        self.callback(distance_name, contrast_name)

        self.capture_count += 1

        # Cek apakah sudah cukup untuk kontras ini
        if self.capture_count % self.captures_per_contrast == 0:
            # Pindah ke kontras berikutnya
            self.current_contrast_index += 1

            # Cek apakah semua kontras sudah selesai
            if self.current_contrast_index >= len(self.contrasts):
                # Selesai untuk jarak ini
                self.finish_distance_capture()
                return

        # Jadwalkan capture berikutnya (jeda 0.3 detik antar capture)
        self.window.after(300, self.capture_current_contrast)

    def finish_distance_capture(self):
        """Selesai capture untuk satu jarak"""
        self.is_capturing = False

        # Reset ke warna hitam
        self.window.configure(bg='black')
        self.main_frame.configure(bg='black')

        # Update tombol
        self.play_button.config(state='normal', text="▶")

        # Pindah ke jarak berikutnya
        self.current_distance_index += 1

        if self.current_distance_index >= len(self.distances):
            # Semua jarak selesai
            print("Semua capture selesai!")
            self.callback("complete", "complete")
            self.close()
        else:
            # Siap untuk jarak berikutnya
            self.current_contrast_index = 0
            self.update_display()
            print(f"Siap untuk jarak: {self.distances[self.current_distance_index]}")

    def close(self):
        """Menutup lighting GUI"""
        self.is_capturing = False
        if self.window:
            self.window.destroy()
            self.window = None