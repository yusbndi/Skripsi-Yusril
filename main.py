#!/usr/bin/env python3
"""
Sistem Gerbang Otomatis Berbasis Pengenalan Wajah
Menggunakan Haar Cascade dan LBPH dengan OpenCV
"""

import sys
import os
from pathlib import Path

# Set encoding untuk Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Tambahkan path proyek ke sys.path
sys.path.insert(0, str(Path(__file__).parent))

from utils.config import Config
from utils.logger import Logger


def main():
    """Fungsi utama"""
    print("Memulai Sistem Gerbang Otomatis...")

    try:
        # Inisialisasi direktori TERLEBIH DAHULU
        print("Membuat struktur direktori...")
        Config.initialize_directories()

        # Inisialisasi logger SETELAH direktori dibuat
        print("Inisialisasi logger...")
        logger = Logger("Main")
        logger.info("Sistem Gerbang Otomatis dimulai")

        # Import GUI setelah inisialisasi
        from gui.main_gui import MainGUI

        # Jalankan GUI utama
        app = MainGUI()
        app.run()

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

        try:
            logger.error(f"Error: {str(e)}")
        except:
            pass

    print("Sistem Gerbang Otomatis dihentikan")


if __name__ == "__main__":
    main()