import cv2
import os
import json
from datetime import datetime
from pathlib import Path
import numpy as np


def create_directory(path):
    """Membuat direktori jika belum ada"""
    Path(path).mkdir(parents=True, exist_ok=True)


def get_timestamp():
    """Mendapatkan timestamp format string"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def validate_name(name):
    """Validasi nama pengguna"""
    if not name or len(name.strip()) == 0:
        return False, "Nama tidak boleh kosong"

    if len(name) > 50:
        return False, "Nama terlalu panjang (maksimal 50 karakter)"

    invalid_chars = '<>:"/\\|?*'
    if any(char in name for char in invalid_chars):
        return False, f"Nama mengandung karakter tidak valid: {invalid_chars}"

    return True, "Valid"


def resize_image(image, width=None, height=None):
    """Resize gambar dengan mempertahankan aspek rasio"""
    if width is None and height is None:
        return image

    h, w = image.shape[:2]

    if width is not None and height is not None:
        return cv2.resize(image, (width, height))
    elif width is not None:
        ratio = width / w
        new_height = int(h * ratio)
        return cv2.resize(image, (width, new_height))
    else:
        ratio = height / h
        new_width = int(w * ratio)
        return cv2.resize(image, (new_width, height))


def draw_text_with_background(img, text, pos, font_scale=0.7,
                              text_color=(255, 255, 255),
                              bg_color=(0, 0, 0), thickness=2):
    """Menggambar teks dengan background"""
    font = cv2.FONT_HERSHEY_SIMPLEX
    (text_w, text_h), _ = cv2.getTextSize(text, font, font_scale, thickness)

    x, y = pos
    cv2.rectangle(img, (x, y - text_h - 10), (x + text_w + 10, y + 10), bg_color, -1)
    cv2.putText(img, text, (x + 5, y), font, font_scale, text_color, thickness)

    return img


def save_labels(labels_dict, filepath):
    """Menyimpan dictionary label ke file"""
    # Pastikan keys adalah string untuk JSON
    labels_dict_str_keys = {str(k): v for k, v in labels_dict.items()}

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(labels_dict_str_keys, f, ensure_ascii=False, indent=2)

    print(f"✅ Labels saved to {filepath}: {labels_dict_str_keys}")


def load_labels(filepath):
    """Memuat dictionary label dari file"""
    if not os.path.exists(filepath):
        print(f"⚠️ Labels file not found: {filepath}")
        return {}

    with open(filepath, 'r', encoding='utf-8') as f:
        labels_dict_str_keys = json.load(f)

    # Konversi keys ke integer
    labels_dict = {int(k): v for k, v in labels_dict_str_keys.items()}

    print(f"✅ Labels loaded from {filepath}: {labels_dict}")
    return labels_dict