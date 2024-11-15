import cv2
import os
# import numpy as np
# from matplotlib import pyplot as plt
# from PIL import Image
import torch
# import time
from tqdm.notebook import tqdm
# from facenet_pytorch import MTCNN

device = 'cuda:0' if torch.cuda.is_available() else 'cpu'

face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
# path_video_face = 'Project\\SIC_Project\\Data\\Dataset' # đường dẫn tới folder video
# path_frame = 'Project\\SIC_Project\\Data\\NewData' # đường dẫn tới folder ảnh cắt từ video
# path_frame_face = 'Project\\SIC_Project\\Data\\NewData' # đường dẫn tới ảnh sau khi cắt từ frame

path_video_face = 'dataset\\raw_video' # đường dẫn tới folder video
path_frame = 'dataset\\raw' # đường dẫn tới folder ảnh cắt từ video
path_frame_face = 'dataset\\processed' # đường dẫn tới ảnh sau khi cắt từ frame


# Source code cũ
# def extract_faces_from_video(video_path, output_dir, face_cascade_path):
#     print(video_path)
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)
    
#     cap = cv2.VideoCapture(video_path)
#     face_cascade = cv2.CascadeClassifier(face_cascade_path)
#     frame_count = 0

#     while cap.isOpened():
        
#         ret, frame = cap.read()
#         if not ret:
#             break
        
#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         faces = face_cascade.detectMultiScale(gray, 1.1, 4)
#         count = 0
#         for (x, y, w, h) in faces:
#             if count == 50:
#                 break
#             face = frame[y:y+h, x:x+w]
#             face_filename = os.path.join(output_dir, f"face_{frame_count}.jpg")
#             cv2.imwrite(face_filename, face)
#             frame_count += 1

#     cap.release()
#     cv2.destroyAllWindows()
#     print(video_path)

# Code mới
def extract_faces_from_video(video_path, output_dir, face_cascade_path):
    print(video_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    cap = cv2.VideoCapture(video_path)
    for i in tqdm(range(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))):
        success, image = cap.read()
        if not success:
            break
        
        image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        

    pass

if __name__ == '__main__':
    map_label = {}
    cur_label = 0
    for subdir, dirs, files in os.walk(path_video_face):
        for dir_name in dirs:
            map_label[cur_label] = dir_name
            dir_path = os.path.join(subdir, dir_name)
            
            for file in os.listdir(dir_path):
                try:
                    extract_faces_from_video(os.path.join(dir_path,file), os.path.join(path_frame_face, dir_name), face_cascade_path)
                except Exception as e:
                    print(f"Co loi")
                    print(e)

            
            cur_label += 1