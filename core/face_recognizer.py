import cv2
import numpy as np
from utils.config import Config
from utils.logger import Logger
from core.trainer import FaceTrainer
from core.face_detector import FaceDetector


class FaceRecognizer:
    """Face recognizer menggunakan LBPH"""

    def __init__(self):
        self.trainer = FaceTrainer()
        self.detector = FaceDetector()
        self.logger = Logger("Recognizer")
        self.threshold = Config.LBPH_THRESHOLD
        self.model_loaded = False
        self.frame_count = 0

    def initialize(self):
        """Inisialisasi recognizer dengan model yang sudah dilatih"""
        self.model_loaded = self.trainer.load_model()

        if not self.model_loaded:
            self.logger.warning("No trained model available. Please train first.")
        else:
            self.logger.info(f"Model loaded. Users: {self.trainer.get_all_users()}")
            self.logger.info(f"Threshold: {self.threshold}")

        return self.model_loaded

    def predict_face(self, face_image):
        """Memprediksi identitas dari gambar wajah"""
        if not self.model_loaded:
            return -1, 100

        try:
            label_id, confidence = self.trainer.recognizer.predict(face_image)
            return label_id, confidence
        except Exception as e:
            self.logger.error(f"Prediction error: {e}")
            return -1, 100

    def recognize(self, frame):
        """Mengenali wajah dalam frame"""
        self.frame_count += 1

        # Deteksi wajah terbesar
        face = self.detector.get_largest_face(frame)

        if face is None:
            return "No Face", 0, None

        face_roi = self.detector.extract_face_roi(frame, face)

        if face_roi.size == 0:
            return "Error", 0, face

        processed_face = self.detector.preprocess_face(face_roi, equalize_hist=True)

        if processed_face is None:
            return "Error", 0, face

        # Prediksi
        if not self.model_loaded:
            return "No Model", 0, face

        label_id, confidence = self.trainer.recognizer.predict(processed_face)

        # Debug setiap 30 frame
        if self.frame_count % 30 == 0:
            self.logger.debug(f"Prediction - Label: {label_id}, Confidence: {confidence:.2f}")

        # Konversi confidence ke persentase
        confidence_percent = max(0, min(100, 100 - confidence))

        # Cek threshold dan label
        if confidence < self.threshold and label_id in self.trainer.labels_dict:
            name = self.trainer.labels_dict[label_id]
            if self.frame_count % 30 == 0:
                self.logger.info(f"✅ Recognized: {name} ({confidence_percent:.1f}%)")
        else:
            name = "Unknown"
            if self.frame_count % 30 == 0:
                self.logger.debug(f"❌ Unknown - Label: {label_id}, Conf: {confidence:.2f}, Thresh: {self.threshold}")

        return name, confidence_percent, face

    def draw_recognition_result(self, frame, name, confidence, face,
                                known_color=(0, 255, 0), unknown_color=(0, 0, 255)):
        """Menggambar hasil pengenalan pada frame"""
        if face is None:
            return frame

        x, y, w, h = face

        # Tentukan warna
        if name == "Unknown":
            color = unknown_color
            label = f"Unknown ({confidence:.1f}%)"
        elif name in ["No Face", "Error", "No Model"]:
            color = unknown_color
            label = name
        else:
            color = known_color
            label = f"{name} ({confidence:.1f}%)"

        # Gambar kotak
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

        # Background label
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        cv2.rectangle(frame, (x, y - 35), (x + label_size[0] + 10, y), color, -1)

        # Teks label
        cv2.putText(frame, label, (x + 5, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        return frame

    def retrain(self):
        """Melatih ulang model"""
        success = self.trainer.train()
        if success:
            self.initialize()
        return success