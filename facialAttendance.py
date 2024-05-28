import cv2
import face_recognition
import os
import pickle
import tkinter as tk
from tkinter import simpledialog, filedialog
import pandas as pd
from datetime import datetime

def kodlari_yukle():
    if os.path.exists('encodings.pickle'):
        with open('encodings.pickle', 'rb') as f:
            encodings = pickle.load(f)
        return encodings
    else:
        return {}

def kodlari_kaydet(encodings):
    with open('encodings.pickle', 'wb') as f:
        pickle.dump(encodings, f)

def kullanici_girdisi(prompt):
    return simpledialog.askstring("Input", prompt)

def resimden_yuz_ekle():
    while True:
        image_path = filedialog.askopenfilename(title="Bir fotoğraf seçin ")
        if not image_path:
            return

        image = face_recognition.load_image_file(image_path)
        image_face_encodings = face_recognition.face_encodings(image)

        if len(image_face_encodings) > 0:

            isim = kullanici_girdisi("Bu yüz için bir isim girin:")
            ogrenci_no = kullanici_girdisi("Bu yüz için bir öğrenci numarası girin:")
            face_encodings[(isim, ogrenci_no)] = image_face_encodings[0]
            kodlari_kaydet(face_encodings)
            print(f" {isim} (ID: {ogrenci_no}) başarılı bir şekilde kaydedildi.")
        else:
            print("Yüz bulunamadı. Farklı bir resim seçin")

        if kullanici_girdisi("Yeni bir yüz eklemek istiyor musunuz ?(evet/hayır)") != 'evet':
            break


face_encodings = kodlari_yukle()

# Set to store names of faces for which attendance has been logged
attendance_logged_faces = set()

# Tkinter setup for initial dialogs
root = tk.Tk()
root.withdraw()  # Hide the main window

fileName = kullanici_girdisi("Yoklama tarihini giriniz:")

excel_file = fileName + ' tarihli yoklama.xlsx'
if not os.path.exists(excel_file):
    df = pd.DataFrame(columns=["İsim", "Öğrenci No", "Zaman"])
    df.to_excel(excel_file, index=False)

if kullanici_girdisi("Yeni bir yüz eklemek istiyor musunuz ?(evet/hayır)") == 'evet':
    resimden_yuz_ekle()

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while True:
    ret, frame = cap.read()

    face_locations = face_recognition.face_locations(frame)
    current_face_encodings = face_recognition.face_encodings(frame, face_locations)

    for face_encoding, face_location in zip(current_face_encodings, face_locations):
        matches = face_recognition.compare_faces(list(face_encodings.values()), face_encoding)
        isim = "Tanimlanmamis yuz"
        ogrenci_no = ""

        if True in matches:
            first_match_index = matches.index(True)
            isim, ogrenci_no = list(face_encodings.keys())[first_match_index]

        box_color = (0, 255, 0) if isim != "Tanimlanmamis yuz" else (0, 0, 255)

        top, right, bottom, left = face_location
        cv2.rectangle(frame, (left, top), (right, bottom), box_color, 2)
        display_text = isim if isim == "Tanimlanmamis yuz" else f"{isim} ({ogrenci_no})"
        cv2.putText(frame, display_text, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, box_color, 2)

        if isim != "Tanimlanmamis yuz" and (isim, ogrenci_no) not in attendance_logged_faces:

            current_time = datetime.now().strftime('%d-%m-%y %H:%M:%S')
            new_entry = pd.DataFrame([[isim, ogrenci_no, current_time]], columns=["İsim", "Öğrenci No", "Zaman"])
            if not new_entry.empty and not new_entry.isna().all(axis=None):
                df = pd.read_excel(excel_file)
                df = pd.concat([df, new_entry], ignore_index=True)
                df.to_excel(excel_file, index=False)
                attendance_logged_faces.add((isim, ogrenci_no))

    cv2.imshow('yoklama', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
