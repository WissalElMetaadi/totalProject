import cv2
import json
import os
from ultralytics import YOLO
from modele_region import ObjectCounter
import re

# MODELE DE LECTURE DE PLAQUE
model_lecture_path = r"C:\Users\Utilisateur\Desktop\finale\best7.pt"
model_lecture = YOLO(model_lecture_path)  # charger un modèle personnalisé pour la lecture
threshold_lecture = 0.1  # Ajuster ce seuil si nécessaire

# MODELE DE DETECTION DE PLAQUE
model_detect_path =  r"C:\Users\Utilisateur\Desktop\finale\license_plate_detector.pt"
model_detect = YOLO(model_detect_path)  # charger le modèle de détection
threshold_detect = 0.2


def valider_plaque(plaque):
    pattern_tn = r'^\d{2,3}(TN|TU)\d{3,4}$'
    pattern_rs = r'^\d{1,6}RS$'
    
    if re.match(pattern_tn, plaque) or re.match(pattern_rs, plaque):
        return True
    else:
        return False




# Initialize YOLO model
model = YOLO(r"C:\Users\Utilisateur\Desktop\finale\best.pt")

cap = cv2.VideoCapture(r"C:\Users\Utilisateur\Desktop\finale\NVR_ch15_new.mp4")
assert cap.isOpened(), "Error reading video file"
w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

# Define line points
line_points = [(67,230),(342,157)] # sortie 
line_2 = [(574,210),(849,241)]  # air
line_3 = [(423,150),(571,169)] #lavage
region_points = [(602,154),(849,178),(848,242),(575,208)]

# Video writer
video_writer = cv2.VideoWriter(r"C:\Users\Utilisateur\Desktop\finale\video_output_rihab.mp4",
                    cv2.VideoWriter_fourcc(*'mp4v'),
                    fps,
                    (w, h))

# Init Object Counter SORTIE
counter = ObjectCounter()
counter.set_args(view_img=True,
                reg_pts=line_points,
                reg_pts_3=line_3,
                reg_zone=region_points,
                classes_names=model.names,
                draw_tracks=True,
                region_thickness=1,
                track_color=(255, 255, 255), 
                line_dist_thresh=10)



while cap.isOpened():
    success, im0 = cap.read()
    if not success:
        print("Video frame is empty or video processing has been successfully completed.")
        break
    tracks = model.track(im0, persist=True, show=False, conf=0.3, tracker='bytetrack.yaml')
    im0 = counter.start_counting(im0, tracks)
    video_writer.write(im0)



    ################************************PARTIE DETECTION ET LECTURE DU PLAQUES 





    # Créer une liste pour stocker les étiquettes détectées et leurs x_moyennes
    detected_labels = []
    # Effectuer la détection d'objet pour la détection de plaque
    results_detect = model_detect(im0)[0]
    # Vérifier si des plaques sont détectées
    if len(results_detect) > 0:
        print("****plaque detecté deja")
        # Itérer sur les plaques détectées
        for result in results_detect.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = result

            if score > threshold_detect:
                cv2.rectangle(im0, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 4)
                #x6, y6, x7, y7 : Ces variables sont utilisées pour stocker les valeurs des coins de la boîte englobante de la plaque d'immatriculation détectée
                x6 = x1
                x7 = x2
                y6 = y1
                y7 = y2
                # Extraire la région d'intérêt pour la lecture
                frame_2 = im0[int(y1):int(y2), int(x1):int(x2)]

                # Effectuer la détection d'objet pour la lecture
                results_lecture = model_lecture(frame_2)[0]

                # Vérifier si des objets sont détectés
                if len(results_lecture) > 0:
                    # Itérer sur les objets détectés
                    for result in results_lecture.boxes.data.tolist():
                        x1, y1, x2, y2, score, class_id = result

                        if score > threshold_lecture:
                            label = model_lecture.names[int(class_id)].upper()

                            # Calculer la x_moyenne
                            x_moyenne = (x1 + x2) / 2

                            # Ajouter l'étiquette et la x_moyenne à la liste
                            detected_labels.append((x_moyenne, label))

                    # Trier les étiquettes détectées en fonction de x_moyenne de gauche à droite
                    detected_labels.sort(key=lambda x: x[0])

                    # Concaténer les étiquettes dans l'ordre trié
                    detection_string = "".join([label for x_moyenne, label in detected_labels])

                    # Afficher les informations de détection
                    print("num plaque", detection_string)

                    # Afficher l'image avec les boîtes englobantes
                    for x_moyenne, label in detected_labels:
                        # Trouver la boîte correspondante
                        for result in results_lecture.boxes.data.tolist():
                            x1, y1, x2, y2, score, class_id = result
                            if model_lecture.names[int(class_id)].upper() == label:
                                label = detection_string
                                cv2.putText(im0, label, (int(x6), int(y6 - 10)),
                                            cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 0), 3, cv2.LINE_AA)

    cv2.namedWindow("Image avec les boîtes englobantes", cv2.WINDOW_NORMAL)
    cv2.imshow("Image avec les boîtes englobantes", im0)

    # Attendre 1 milliseconde (ou une valeur désirée) et vérifier si 'q' est pressé pour quitter
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break



cap.release()
video_writer.release()
cv2.destroyAllWindows()

