import cv2
import numpy as np
from utils.config import Config


class FaceDetector:
    """Detektor wajah menggunakan Haar Cascade"""

    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(Config.CASCADE_PATH)
        self.scale_factor = Config.SCALE_FACTOR
        self.min_neighbors = Config.MIN_NEIGHBORS
        self.min_size = Config.MIN_FACE_SIZE
        self.face_size = Config.FACE_SIZE_TRAINING

    def detect_faces(self, frame):
        """Mendeteksi wajah dalam frame"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=self.scale_factor,
            minNeighbors=self.min_neighbors,
            minSize=self.min_size,
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        return faces

    def get_largest_face(self, frame):
        """Mendapatkan wajah terbesar dalam frame"""
        faces = self.detect_faces(frame)
        if len(faces) == 0:
            return None

        largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
        return largest_face

    def draw_face_box(self, frame, face, color=(0, 255, 0), thickness=2):
        """Menggambar kotak di sekitar wajah"""
        x, y, w, h = face
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness)
        return frame

    def extract_face_roi(self, frame, face):
        """Ekstrak ROI wajah dari frame"""
        x, y, w, h = face

        # Tambahkan margin 10% untuk memastikan seluruh wajah terambil
        margin_w = int(w * 0.1)
        margin_h = int(h * 0.1)

        x = max(0, x - margin_w)
        y = max(0, y - margin_h)
        w = min(frame.shape[1] - x, w + 2 * margin_w)
        h = min(frame.shape[0] - y, h + 2 * margin_h)

        face_roi = frame[y:y + h, x:x + w]
        return face_roi

    def preprocess_face(self, face_roi, equalize_hist=True):
        """
        Preprocessing wajah untuk training/prediksi
        PENTING: Proses ini HARUS SAMA untuk training dan recognition!
        """
        if face_roi is None or face_roi.size == 0:
            return None

        # Convert ke grayscale
        if len(face_roi.shape) == 3:
            gray_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        else:
            gray_face = face_roi.copy()

        # Resize ke ukuran training
        resized_face = cv2.resize(gray_face, self.face_size, interpolation=cv2.INTER_LINEAR)

        # Equalize histogram (HARUS SAMA untuk training dan recognition)
        if equalize_hist:
            resized_face = cv2.equalizeHist(resized_face)

        # Normalisasi intensitas (tambahan untuk konsistensi)
        resized_face = cv2.normalize(resized_face, None, 0, 255, cv2.NORM_MINMAX)

        return resized_face

    def extract_and_preprocess(self, frame, face, equalize_hist=True):
        """Ekstrak dan preprocess wajah sekaligus"""
        face_roi = self.extract_face_roi(frame, face)
        return self.preprocess_face(face_roi, equalize_hist)