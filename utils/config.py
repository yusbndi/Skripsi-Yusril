import os
import cv2
from pathlib import Path


class Config:
    """Konfigurasi sistem"""

    # Path configurations
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    DATASET_DIR = DATA_DIR / "dataset"
    TRAINER_DIR = DATA_DIR / "trainer"
    LOGS_DIR = DATA_DIR / "logs"
    ASSETS_DIR = BASE_DIR / "assets"

    # Camera settings
    CAMERA_WIDTH = 1280
    CAMERA_HEIGHT = 720
    PREVIEW_WIDTH = 640
    PREVIEW_HEIGHT = 360

    # Face detection settings (Haar Cascade)
    SCALE_FACTOR = 1.1
    MIN_NEIGHBORS = 8
    MIN_FACE_SIZE = (50, 50)
    FACE_SIZE_TRAINING = (150, 150)

    # LBPH settings
    LBPH_THRESHOLD = 60

    # Registration settings
    TOTAL_IMAGES_PER_USER = 100
    DISTANCES = ["dekat", "jauh"]
    CONTRASTS = ["putih", "merah", "hijau", "biru", "hitam"]
    CONTRAST_COLORS = {
        "putih": (255, 255, 255),
        "merah": (0, 0, 255),
        "hijau": (0, 255, 0),
        "biru": (255, 0, 0),
        "hitam": (0, 0, 0)
    }
    IMAGES_PER_COMBINATION = 10

    # File paths
    CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    TRAINER_FILE = TRAINER_DIR / "trainer.yml"
    LABELS_FILE = TRAINER_DIR / "labels.txt"
    LOGO_PATH = ASSETS_DIR / "unnes.png"

    @classmethod
    def initialize_directories(cls):
        """Membuat direktori yang diperlukan"""
        directories = [
            cls.DATA_DIR,
            cls.DATASET_DIR,
            cls.TRAINER_DIR,
            cls.LOGS_DIR,
            cls.ASSETS_DIR
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

        print(f"Direktori berhasil dibuat di: {cls.BASE_DIR}")
        print(f"Assets directory: {cls.ASSETS_DIR}")
        print(f"Logo path: {cls.LOGO_PATH}")
        print(f"Logo exists: {cls.LOGO_PATH.exists()}")