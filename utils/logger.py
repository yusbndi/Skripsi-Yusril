import logging
from datetime import datetime
from pathlib import Path
import os


class Logger:
    """Sistem logging"""

    def __init__(self, name="FaceGate"):
        self.name = name
        self.setup_logger()

    def setup_logger(self):
        """Setup logger dengan file handler"""
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)

        # Pastikan direktori logs ada
        log_dir = Path(__file__).parent.parent / "data" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        # File handler
        log_file = log_dir / f"log_{datetime.now().strftime('%Y%m%d')}.log"

        try:
            fh = logging.FileHandler(log_file, encoding='utf-8')
            fh.setLevel(logging.DEBUG)

            # Console handler
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)

            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            fh.setFormatter(formatter)
            ch.setFormatter(formatter)

            self.logger.addHandler(fh)
            self.logger.addHandler(ch)

        except Exception as e:
            print(f"Warning: Tidak dapat membuat file log. Error: {e}")
            # Tetap buat console handler saja
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def debug(self, message):
        self.logger.debug(message)

    def access_log(self, name, status):
        """Log akses gerbang dengan format yang rapi"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"{timestamp} - Access - {name} - {status}"
        self.logger.info(log_message)

    def get_logs(self, limit=100):
        """Mengambil log terbaru"""
        log_dir = Path(__file__).parent.parent / "data" / "logs"
        log_files = sorted(log_dir.glob("log_*.log"), reverse=True)
        logs = []

        for log_file in log_files[:5]:  # Baca 5 file terakhir
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    logs.extend(lines[-limit:])
            except Exception as e:
                print(f"Error membaca log: {e}")

        return logs[-limit:] if logs else ["Belum ada log tersedia\n"]

    def clear_logs(self):
        """Membersihkan file log"""
        log_dir = Path(__file__).parent.parent / "data" / "logs"
        try:
            for log_file in log_dir.glob("log_*.log"):
                log_file.unlink()
            self.setup_logger()
            return True
        except Exception as e:
            print(f"Error membersihkan log: {e}")
            return False