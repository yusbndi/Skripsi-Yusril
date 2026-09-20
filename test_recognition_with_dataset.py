"""
DEBUG: Test Recognition Menggunakan Dataset Images (FIXED)
Simpan sebagai test_recognition_with_dataset.py di root folder proyek
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import cv2
import numpy as np
from utils.config import Config
from core.face_recognizer import FaceRecognizer
from core.face_detector import FaceDetector
from core.trainer import FaceTrainer


def test_recognition_with_dataset():
    """Test recognition menggunakan gambar dataset"""

    print("=" * 70)
    print("🧪 TEST RECOGNITION MENGGUNAKAN DATASET IMAGES")
    print("=" * 70)

    # Inisialisasi
    Config.initialize_directories()
    recognizer = FaceRecognizer()

    # Load model
    print("\n📂 Loading model...")
    if not recognizer.initialize():
        print("❌ Model belum dilatih! Latih model terlebih dahulu.")
        return

    # ===== PERBAIKAN: Gunakan recognizer.trainer.labels_dict =====
    labels_dict = recognizer.trainer.labels_dict  # ⬅️ AMBIL DARI RECOGNIZER!

    print(f"✅ Model loaded. Users: {recognizer.trainer.get_all_users()}")
    print(f"   Threshold: {recognizer.threshold}")
    print(f"   Labels: {labels_dict}")

    dataset_path = Config.DATASET_DIR

    if not dataset_path.exists():
        print("❌ Dataset folder tidak ditemukan!")
        return

    # ===== TEST Recognition =====
    print("\n" + "=" * 70)
    print("📊 HASIL RECOGNITION PER USER")
    print("=" * 70)

    total_correct = 0
    total_tested = 0
    all_confidences = []
    user_results = {}

    for user_dir in sorted(dataset_path.iterdir()):
        if not user_dir.is_dir():
            continue

        user_name = user_dir.name
        print(f"\n👤 User: {user_name}")
        print("-" * 50)

        # Skip folder original dan faces
        if user_name in ['original', 'faces']:
            print(f"   ⏭️ Skipping subfolder: {user_name}")
            continue

        # Ambil SEMUA gambar .jpg di root folder user (BUKAN di subfolder)
        images = sorted([f for f in user_dir.glob("*.jpg") if f.parent == user_dir])

        if not images:
            print(f"   ❌ Tidak ada gambar di folder {user_name}")
            continue

        correct = 0
        wrong = 0
        unknown = 0
        confidences = []
        detail_results = []

        for img_path in images:
            # Baca gambar (SUDAH grayscale 200x200)
            img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)

            if img is None:
                print(f"   ⚠️ Cannot read: {img_path.name}")
                continue

            # Verifikasi ukuran
            if img.shape != (200, 200):
                img = cv2.resize(img, (200, 200))

            # ===== PREDIKSI =====
            label_id, confidence = recognizer.predict_face(img)

            # ===== PERBAIKAN: Gunakan labels_dict dari recognizer =====
            predicted_name = labels_dict.get(label_id, "Unknown")

            confidence_pct = max(0, min(100, 100 - confidence))
            confidences.append(confidence)
            all_confidences.append(confidence)
            total_tested += 1

            # Cek benar/salah
            if confidence < recognizer.threshold:
                # Di bawah threshold = dikenali
                if predicted_name == user_name:
                    correct += 1
                    total_correct += 1
                    status_icon = "✅"
                    is_correct = True
                else:
                    wrong += 1
                    status_icon = "❌"
                    is_correct = False
            else:
                # Di atas threshold = Unknown
                unknown += 1
                status_icon = "⚠️"
                is_correct = False
                predicted_name = "Unknown"

            detail_results.append({
                'filename': img_path.name,
                'predicted': predicted_name,
                'confidence_raw': confidence,
                'confidence_pct': confidence_pct,
                'correct': is_correct,
                'status': status_icon
            })

        # Hitung statistik per user
        total_user = correct + wrong + unknown
        accuracy = (correct / total_user * 100) if total_user > 0 else 0

        if confidences:
            avg_conf = np.mean(confidences)
            avg_conf_pct = max(0, 100 - avg_conf)
            min_conf = np.min(confidences)
            max_conf = np.max(confidences)
        else:
            avg_conf = 0
            avg_conf_pct = 0
            min_conf = 0
            max_conf = 0

        user_results[user_name] = {
            'total': total_user,
            'correct': correct,
            'wrong': wrong,
            'unknown': unknown,
            'accuracy': accuracy,
            'avg_confidence': avg_conf,
            'avg_confidence_pct': avg_conf_pct,
            'min_confidence': min_conf,
            'max_confidence': max_conf,
            'details': detail_results
        }

        # Tampilkan hasil per user
        print(f"   Total: {total_user} | Benar: {correct} | Salah: {wrong} | Unknown: {unknown}")
        print(f"   Akurasi: {accuracy:.1f}%")
        print(f"   Confidence: Avg={avg_conf:.1f} ({avg_conf_pct:.1f}%) | Min={min_conf:.1f} | Max={max_conf:.1f}")
        print(f"   Threshold: {recognizer.threshold}")

        # Tampilkan 5 gambar pertama (detail)
        if detail_results:
            print(f"\n   Detail (5 pertama):")
            for i, detail in enumerate(detail_results[:5]):
                print(f"   {detail['status']} {detail['filename']}: -> {detail['predicted']} "
                      f"(raw={detail['confidence_raw']:.1f}, {detail['confidence_pct']:.1f}%)")

        # Tampilkan gambar yang SALAH (jika ada)
        wrong_details = [d for d in detail_results if not d['correct']]
        if wrong_details:
            print(f"\n   ⚠️ Gambar TIDAK TEPAT ({len(wrong_details)}):")
            for detail in wrong_details[:10]:  # Max 10
                print(f"   {detail['status']} {detail['filename']}: -> '{detail['predicted']}' "
                      f"(raw={detail['confidence_raw']:.1f})")
        else:
            print(f"\n   ✅ SEMUA BENAR! Tidak ada kesalahan.")

    # ===== RINGKASAN =====
    print("\n" + "=" * 70)
    print("📊 RINGKASAN AKHIR")
    print("=" * 70)

    if total_tested == 0:
        print("❌ Tidak ada gambar yang diuji!")
        return

    overall_accuracy = (total_correct / total_tested * 100)

    print(f"\nTotal gambar diuji: {total_tested}")
    print(f"Total benar: {total_correct}")
    print(f"Total salah/unknown: {total_tested - total_correct}")
    print(f"Overall Accuracy: {overall_accuracy:.1f}%")
    print(f"Threshold: {recognizer.threshold}")

    if user_results:
        print(f"\n{'User':<15} {'Total':<8} {'Benar':<8} {'Salah':<8} {'Unknown':<8} {'Akurasi':<10} {'Avg Conf':<12}")
        print("-" * 75)
        for user_name, result in user_results.items():
            print(f"{user_name:<15} {result['total']:<8} {result['correct']:<8} "
                  f"{result['wrong']:<8} {result['unknown']:<8} "
                  f"{result['accuracy']:.1f}%{'':<5} {result['avg_confidence_pct']:.1f}%")

    # Analisis
    print("\n" + "=" * 70)
    print("🔍 ANALISIS")
    print("=" * 70)

    # Cek confidence vs threshold
    if all_confidences:
        avg_all_conf = np.mean(all_confidences)
        min_all_conf = np.min(all_confidences)
        max_all_conf = np.max(all_confidences)

        print(f"\n📊 Statistik Confidence (Raw LBPH Distance):")
        print(f"   Mean: {avg_all_conf:.1f}")
        print(f"   Range: {min_all_conf:.1f} - {max_all_conf:.1f}")
        print(f"   Threshold saat ini: {recognizer.threshold}")

        if max_all_conf < recognizer.threshold:
            print(f"\n✅ SEMUA confidence di bawah threshold!")
            print(f"   Max confidence: {max_all_conf:.1f} < Threshold: {recognizer.threshold}")
        else:
            above_threshold = sum(1 for c in all_confidences if c >= recognizer.threshold)
            print(f"\n⚠️ {above_threshold}/{len(all_confidences)} gambar di ATAS threshold (dianggap Unknown)")

    # Rekomendasi
    if overall_accuracy >= 90:
        print("\n✅ SANGAT BAIK! Model bekerja dengan sangat baik pada dataset training.")
    elif overall_accuracy >= 70:
        print("\n⚠️ CUKUP BAIK. Ada beberapa kesalahan, cek detail di atas.")
        print("   Kemungkinan penyebab:")
        print("   - Beberapa gambar outlier (terlalu berbeda)")
        print("   - Threshold perlu disesuaikan")
    elif overall_accuracy >= 50:
        print("\n⚠️ KURANG BAIK. Banyak kesalahan recognition.")
        print("   Kemungkinan penyebab:")
        print("   - Preprocessing tidak konsisten")
        print("   - Dataset perlu ditambah/diperbaiki")
    else:
        print("\n❌ BURUK. Model tidak bisa mengenali dataset sendiri!")
        print("   Kemungkinan penyebab:")
        print("   - Preprocessing training vs testing BERBEDA")
        print("   - Model rusak atau tidak terlatih")

    print("\n" + "=" * 70)
    print("✅ TEST SELESAI")
    print("=" * 70)

if __name__ == "__main__":
    test_recognition_with_dataset()
    input("\nTekan Enter untuk keluar...")