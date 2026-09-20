import cv2
import numpy as np
import os
from pathlib import Path
from utils.config import Config
from utils.helpers import save_labels, load_labels
from utils.logger import Logger


class FaceTrainer:
    """Trainer untuk model LBPH"""

    def __init__(self):
        self.recognizer = cv2.face.LBPHFaceRecognizer_create(
            radius=1,
            neighbors=8,
            grid_x=8,
            grid_y=8
        )
        self.logger = Logger("Trainer")
        self.labels_dict = {}
        self.current_id = 0


    def load_dataset(self, dataset_path=None):
        """Memuat dataset dari folder"""
        if dataset_path is None:
            dataset_path = Config.DATASET_DIR

        faces = []
        labels = []
        self.labels_dict = {}
        self.current_id = 0

        # Iterasi setiap user folder
        for user_dir in Path(dataset_path).iterdir():
            if not user_dir.is_dir():
                continue

            user_name = user_dir.name
            self.labels_dict[self.current_id] = user_name
            user_faces = []

            self.logger.info(f"Loading user: {user_name}")

            for img_path in sorted(user_dir.glob("*.jpg")):
                # ===== ABAIKAN FILE DI SUBFOLDER original/ dan faces/ =====
                if img_path.parent != user_dir:
                    continue

                img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)

                if img is not None:
                    # Verifikasi ukuran
                    if img.shape != Config.FACE_SIZE_TRAINING:
                        self.logger.warning(f"Resizing {img_path.name} from {img.shape} to {Config.FACE_SIZE_TRAINING}")
                        img = cv2.resize(img, Config.FACE_SIZE_TRAINING)


                    user_faces.append(img)
                    faces.append(img)
                    labels.append(self.current_id)

            self.logger.info(f"  Loaded {len(user_faces)} images for {user_name}")
            self.current_id += 1

        return faces, np.array(labels), self.labels_dict

    def train(self, dataset_path=None, save_model=True):
        """Melatih model LBPH dengan dataset"""
        self.logger.info("Starting training process...")

        # Load dataset
        faces, labels, label_names = self.load_dataset(dataset_path)

        if len(faces) == 0:
            self.logger.error("No training data found!")
            return False

        self.logger.info(f"Training with {len(faces)} faces from {len(label_names)} users")

        # Train recognizer
        try:
            self.recognizer.train(faces, labels)
        except Exception as e:
            self.logger.error(f"Training failed: {e}")
            return False

        if save_model:
            self.save_model()
            self.save_labels()

        self.logger.info(f"Training completed! Total users: {len(label_names)}")
        return True

    def save_model(self, filepath=None):
        """Menyimpan model yang sudah dilatih"""
        if filepath is None:
            filepath = Config.TRAINER_FILE

        self.recognizer.write(str(filepath))
        self.logger.info(f"Model saved to {filepath}")

    def load_model(self, filepath=None):
        """Memuat model yang sudah dilatih"""
        if filepath is None:
            filepath = Config.TRAINER_FILE

        if not os.path.exists(filepath):
            self.logger.warning("No trained model found!")
            return False

        try:
            self.recognizer.read(str(filepath))
            self.labels_dict = load_labels(Config.LABELS_FILE)
            self.logger.info(f"Model loaded from {filepath}")
            self.logger.info(f"Labels: {self.labels_dict}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            return False

    def save_labels(self):
        """Menyimpan label dictionary"""
        save_labels(self.labels_dict, Config.LABELS_FILE)

    def get_user_count(self):
        """Mendapatkan jumlah user yang terdaftar"""
        return len(self.labels_dict)

    def get_all_users(self):
        """Mendapatkan list semua user"""
        return list(self.labels_dict.values())

    def delete_user(self, user_name):
        """Menghapus user dari dataset"""
        user_dir = Config.DATASET_DIR / user_name
        if user_dir.exists():
            import shutil
            shutil.rmtree(user_dir)
            self.logger.info(f"User {user_name} deleted")
            return True
        return False