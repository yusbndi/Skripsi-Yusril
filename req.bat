import cv2
import PIL
import numpy as np
import pandas as pd
import openpyxl
import sklearn

# Tkinter biasanya sudah terpasang dengan Python
import tkinter

print("OpenCV:", cv2.__version__)
print("OpenCV-contrib (cv2):", cv2.__version__)  # sama dengan OpenCV utama
print("Pillow (PIL):", PIL.__version__)
print("NumPy:", np.__version__)
print("Tkinter:", tkinter.TkVersion)
print("Pandas:", pd.__version__)
print("OpenPyXL:", openpyxl.__version__)
print("Scikit-learn:", sklearn.__version__)
