import cv2
from ultralytics import YOLO
model = YOLO('yolov8n.pt')

def run_yolo(frame):

            # Run YOLOv8 tracking on the frame, persisting tracks between frames
            #results = model.track(source=video_path,save=True,  project='./results',show=True, tracker="bytetrack.yaml", classes=[0,1,2])
            results = model.track(source=frame,save=False,  project='./results',show=False, tracker="bytetrack.yaml")

            # Visualize the results on the frame
            annotated_frame = results[0].plot()

            return annotated_frame
   



# Exemple d'utilisation de la fonction
if __name__ == '__main__':
    run_yolo(frame)