import cv2
import threading
import time
from utils.config import Config
from utils.logger import Logger


class CameraHandler:
    """Handler untuk mengelola kamera"""

    def __init__(self, camera_id=0, width=Config.CAMERA_WIDTH, height=Config.CAMERA_HEIGHT):
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.cap = None
        self.is_running = False
        self.frame = None
        self.lock = threading.Lock()
        self.logger = Logger("CameraHandler")
        self.thread = None
        self.frame_count = 0
        self.error_count = 0
        self.max_errors = 10

    def start(self):
        """Memulai kamera dengan DirectShow backend"""
        # Gunakan DirectShow (cv2.CAP_DSHOW) untuk Windows
        try:
            self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_DSHOW)
        except:
            # Fallback ke default jika DirectShow tidak tersedia
            self.cap = cv2.VideoCapture(self.camera_id)

        if not self.cap.isOpened():
            self.logger.error("Cannot open camera")
            return False

        # Set resolusi
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 10)

        # Verifikasi resolusi
        actual_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.logger.info(f"Camera started with resolution {actual_width}x{actual_height}")

        self.is_running = True
        self.error_count = 0

        # Start thread
        self.thread = threading.Thread(target=self._update_frame, daemon=True)
        self.thread.start()

        return True

    def _update_frame(self):
        """Update frame secara kontinu dalam thread terpisah"""
        while self.is_running:
            try:
                if self.cap is None or not self.cap.isOpened():
                    self.logger.error("Camera disconnected")
                    break

                ret, frame = self.cap.read()

                if ret and frame is not None:
                    with self.lock:
                        self.frame = frame.copy()
                    self.frame_count += 1
                    self.error_count = 0  # Reset error count
                else:
                    self.error_count += 1
                    self.logger.warning(f"Failed to grab frame (error {self.error_count})")

                    # Jika terlalu banyak error, coba reconnect
                    if self.error_count > self.max_errors:
                        self.logger.error("Too many errors, reconnecting camera...")
                        self._reconnect()
                        self.error_count = 0

                    time.sleep(0.1)

            except Exception as e:
                self.logger.error(f"Camera error: {e}")
                time.sleep(0.1)

    def _reconnect(self):
        """Mencoba reconnect kamera"""
        try:
            if self.cap:
                self.cap.release()

            time.sleep(1)
            self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_DSHOW)

            if self.cap.isOpened():
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                self.logger.info("Camera reconnected")
                return True
        except Exception as e:
            self.logger.error(f"Reconnect failed: {e}")

        return False

    def get_frame(self):
        """Mendapatkan frame terbaru"""
        with self.lock:
            if self.frame is not None:
                return self.frame.copy()

            # Jika frame kosong, coba baca langsung
            if self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    self.frame = frame.copy()
                    return self.frame.copy()

            return None

    def get_preview_frame(self, width=Config.PREVIEW_WIDTH, height=Config.PREVIEW_HEIGHT):
        """Mendapatkan frame untuk preview"""
        frame = self.get_frame()
        if frame is not None:
            return cv2.resize(frame, (width, height))
        return None

    def stop(self):
        """Menghentikan kamera dengan benar"""
        print("CameraHandler: Stopping camera...")
        self.is_running = False

        # Tunggu thread selesai
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)

        # Release camera
        if self.cap:
            self.cap.release()
            self.cap = None

        # Tunggu sebentar untuk memastikan kamera benar-benar released
        time.sleep(0.5)

        print("CameraHandler: Camera stopped")

    def is_available(self):
        """Cek apakah kamera tersedia"""
        return self.cap is not None and self.cap.isOpened()

    def save_image(self, frame, filepath):
        """Menyimpan frame ke file"""
        if frame is not None:
            cv2.imwrite(filepath, frame)
            return True
        return False