import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
from pathlib import Path
from utils.config import Config
from core.trainer import FaceTrainer


class DatasetViewer:
    """GUI untuk melihat dan mengelola dataset"""

    def __init__(self, parent):
        self.parent = parent
        self.window = None
        self.trainer = FaceTrainer()
        self.user_listbox = None

    def show(self):
        """Menampilkan dataset viewer"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Dataset Manager")
        self.window.geometry("800x600")

        # Create main container with scrollbar
        container = tk.Frame(self.window)
        container.pack(fill='both', expand=True)

        # Create canvas and scrollbar
        canvas = tk.Canvas(container, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient='vertical', command=canvas.yview)

        # Create scrollable frame
        scrollable_frame = tk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Configure grid
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Bind mouse wheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Main frame
        main_frame = tk.Frame(scrollable_frame, padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')

        # Title
        title_label = tk.Label(
            main_frame,
            text="Dataset Manager",
            font=('Arial', 18, 'bold')
        )
        title_label.pack(pady=10)

        # Frame untuk listbox dan tombol
        list_frame = tk.Frame(main_frame)
        list_frame.pack(expand=True, fill='both', pady=10)

        # Listbox untuk users dengan scrollbar
        listbox_scrollbar = tk.Scrollbar(list_frame)
        listbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.user_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=listbox_scrollbar.set,
            font=('Arial', 12),
            height=15
        )
        self.user_listbox.pack(side=tk.LEFT, expand=True, fill='both')
        listbox_scrollbar.config(command=self.user_listbox.yview)

        # Info frame
        info_frame = tk.Frame(main_frame)
        info_frame.pack(fill='x', pady=10)

        self.info_label = tk.Label(
            info_frame,
            text="",
            font=('Arial', 11)
        )
        self.info_label.pack()

        # Button frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="Hapus User",
            font=('Arial', 11),
            bg='#f44336',
            fg='white',
            padx=20,
            pady=10,
            command=self.delete_selected_user
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="Latih Ulang Model",
            font=('Arial', 11),
            bg='#2196F3',
            fg='white',
            padx=20,
            pady=10,
            command=self.retrain_model
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="Refresh",
            font=('Arial', 11),
            bg='#4CAF50',
            fg='white',
            padx=20,
            pady=10,
            command=self.refresh_list
        ).pack(side=tk.LEFT, padx=5)

        # Load dataset info
        self.refresh_list()

    def refresh_list(self):
        """Refresh list user"""
        self.user_listbox.delete(0, tk.END)

        dataset_path = Config.DATASET_DIR
        users = []
        total_images = 0

        for user_dir in Path(dataset_path).iterdir():
            if user_dir.is_dir():
                user_name = user_dir.name
                image_count = len(list(user_dir.glob("*.jpg")))
                users.append(f"{user_name} ({image_count} images)")
                total_images += image_count

        for user in sorted(users):
            self.user_listbox.insert(tk.END, user)

        self.info_label.config(
            text=f"Total Users: {len(users)} | Total Images: {total_images}"
        )

    def delete_selected_user(self):
        """Menghapus user yang dipilih"""
        selection = self.user_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Pilih user yang akan dihapus!")
            return

        user_text = self.user_listbox.get(selection[0])
        user_name = user_text.split(" (")[0]

        if messagebox.askyesno("Konfirmasi", f"Hapus user '{user_name}'?"):
            if self.trainer.delete_user(user_name):
                messagebox.showinfo("Sukses", f"User '{user_name}' berhasil dihapus!")
                self.refresh_list()
            else:
                messagebox.showerror("Error", "Gagal menghapus user!")

    def retrain_model(self):
        """Melatih ulang model"""
        if messagebox.askyesno("Konfirmasi", "Latih ulang model dengan dataset saat ini?"):
            self.window.config(cursor="watch")
            self.window.update()

            success = self.trainer.train()

            self.window.config(cursor="")

            if success:
                messagebox.showinfo("Sukses", "Model berhasil dilatih ulang!")
            else:
                messagebox.showerror("Error", "Gagal melatih model!")