# Ultralytics YOLO 🚀, AGPL-3.0 license

from collections import defaultdict
import json
import cv2
from ultralytics import YOLO
from ultralytics.utils.checks import check_imshow, check_requirements
from ultralytics.utils.plotting import Annotator, colors
import re
import easyocr
import datetime
import time
import os
check_requirements("shapely>=2.0.0")

from shapely.geometry import LineString, Point, Polygon
import matplotlib.pyplot as plt


# Créer un objet EasyOCR
reader = easyocr.Reader(['en'])

first_date = None
first_time = None

output2_folder = r'C:\Users\Utilisateur\Desktop\finale\output_license_plates'
output1_folder = r'C:\Users\Utilisateur\Desktop\finale\output_cars'

classe_id_to_nom = {
    0.0: 'CM1',
    1.0: 'Big Truck',
    2.0: 'Car',
    3.0: 'Motorcycle',
    4.0: 'Person',
    5.0:'Small Truck',
    6.0:'Taxi',
    7.0:'Worker'
    
}



###################################################FONCTION POUR LIRE LA DATE DANS UNE IMAGE AVEC EASYOCR
def extract_date_and_time(image_region):
    # Lire le texte de l'image
    result = reader.readtext(image_region)

    # Extraire la date et l'heure du résultat OCR
    if result:
        print(result)
        text_with_date_and_time = result[0][1]  # Récupérer le texte contenant la date et l'heure
        try:
            date_and_time = datetime.datetime.strptime(text_with_date_and_time, "%Y-%m-%d %H.%M.%S")
            combined_info = date_and_time.strftime("%Y-%m-%d %H:%M:%S")
            return combined_info
        except ValueError:
            return None
    else:
        return None





def valider_plaque(plaque):
    pattern_tn = r'^\d{2,3}(TN|TU)\d{3,4}$'
    pattern_rs = r'^\d{1,6}RS$'

    if re.match(pattern_tn, plaque) or re.match(pattern_rs, plaque):
        return True
    else:
        return False

date1_list = []


def get_car(license_plate, vehicle_track_ids):
    """
    Retrieve the vehicle coordinates and ID based on the license plate coordinates.

    Args:
        license_plate (tuple): Tuple containing the coordinates of the license plate (x1, y1, x2, y2, score, class_id).
        vehicle_track_ids (list): List of vehicle track IDs and their corresponding coordinates.

    Returns:
        tuple: Tuple containing the vehicle coordinates (x1, y1, x2, y2) and ID.
    """
    x1, y1, x2, y2, score, class_id = license_plate

    foundIt = False
    for vehicle_info in vehicle_track_ids:
        vehicle_coords, car_id ,clls= vehicle_info
        xcar1, ycar1, xcar2, ycar2 = vehicle_coords

        if x1 > xcar1 and y1 > ycar1 and x2 < xcar2 and y2 < ycar2:
            foundIt = True
            break

    if foundIt:
        return xcar1, ycar1, xcar2, ycar2, car_id,clls

    return -1, -1, -1, -1, -1,-1


def read_license_plate(license_plate_image):
        # Charger le modèle YOLOv8n pré-entraîné
        model = YOLO(r'C:\Users\Utilisateur\Desktop\finale\best7.pt')


        # Exécuter l'inférence sur l'image
        results = model(license_plate_image, conf=0.3)

        # Récupérer les résultats de l'image
        boites_resultats = results[0].boxes

        # Récupérer les noms de classes utilisés par le modèle
        noms_classes = results[0].names

        # Afficher les classes prédites par leurs noms
        classes = [noms_classes[int(cls)] for cls in boites_resultats.cls.tolist()]

        # Récupérer les coordonnées x des boîtes englobantes
        coordonnees_x = [boite[0] for boite in boites_resultats.xyxy.tolist()]

        # Regrouper les classes avec les coordonnées x correspondantes, en excluant la classe spécifique
        classes_et_coordonnees_x = [(classe, coord_x) for classe, coord_x in zip(classes, coordonnees_x) if classe != 'matricule']

        # Trier les paires en fonction des coordonnées x
        classes_triees_x = sorted(classes_et_coordonnees_x, key=lambda x: x[1])

        # Extraire les classes triées
        classes_triees = [classe for classe, _ in classes_triees_x]

        # Joindre les classes triées dans une seule ligne sans virgule
        classes_jointes = ''.join(classes_triees)
        # Récupérer les confiances de chaque boîte englobante
        confiances_boites = results[0].boxes.conf.tolist()

        # Calculer la confiance moyenne pour toutes les classes prédites
        confiance_globale = sum(confiances_boites) / len(confiances_boites) if confiances_boites else 0
    # Retourner la lecture et la confiance
        return classes_jointes, confiance_globale




def combine_dicts(LP_info_dict, pompes_dict):
    # Créer un dictionnaire combiné
    combined_dict = {}

    # Parcourir LP_info_dict pour combiner les informations
    for id_, lp_info in LP_info_dict.items():
        combined_dict[id_] = {
            'track_id': id_,
            'class': lp_info.get('class', None),
            'license_plate_text': lp_info.get('license_plate_text', None),
            'score LP': lp_info.get('score LP', None),
            'pompes_info': None,
            "date d'entrée": None,
            'date de sortie': None,
            'wait_time': None
        }

        # Rechercher les informations de la pompe correspondant à cet ID
        for pompe, infos in pompes_dict.items():
            for i in infos:
                if isinstance(i, dict) and 'track_id' in i and i['track_id'] == id_:
                    combined_dict[id_]['pompes_info'] = pompe
                    combined_dict[id_]["date d'entrée"] = i.get("date d'entrée", None)
                    combined_dict[id_]['date de sortie'] = i.get('date de sortie', None)
                    combined_dict[id_]['wait_time'] = i.get('wait_time', None)
                    break  # Sortir de la boucle dès qu'on trouve l'information de la pompe pour cet ID

    # Ajouter les éléments restants de pompes_dict
    for pompe, infos in pompes_dict.items():
        for i in infos:
            id_ = i['track_id']
            if id_ not in combined_dict:
                combined_dict[id_] = {
                    'track_id': id_,
                    'class': i.get('class', None),
                    'license_plate_text': None,
                    'score LP': None,
                    'pompes_info': pompe,
                    "date d'entrée": i.get("date d'entrée", None),
                    'date de sortie': i.get('date de sortie', None),
                    'wait_time': i.get('wait_time', None)
                }

    return combined_dict


class ObjectCounter:
    """A class to manage the counting of objects in a real-time video stream based on their tracks."""

    def __init__(self):
        """Initializes the Counter with default values for various tracking and counting parameters."""

        # Mouse events
        self.is_drawing = False
        self.selected_point = None

        # Region & Line Information
        self.reg_pts = [(20, 400), (1260, 400)]
        self.line_dist_thresh = 15
        self.counting_region = None
        self.region_color = (255, 255, 255)
        self.region_thickness = 1
        self.roi = None
        self.roi_entry_times = {}
        self.pompe_entry_times = {}
        self.temps_attente_pompe = {'Pompe 6': [], "Pompe 7": [], "Pompe 8":[],"Pompe 4":[],"Pompe 5":[]}
        self.infos_vehicules={'Pompe 6': [], "Pompe 7": [], "Pompe 8":[],"Pompe 4":[],"Pompe 5":[]}
        self.LP_info_dict={}
        self.date1 = None






        # Image and annotation Information
        self.im0 = None
        self.tf = None
        self.view_img = False
        self.view_in_counts = True
        self.view_out_counts = True

        self.names = None  # Classes names
        self.annotator = None  # Annotator

        # Object counting Information
        #Déclaration pour sortie de kiosque
        self.car_out = 0
        self.CM1_out = 0
        self.bigTruck_out = 0
        self.motorcycle_out =0
        self.small_truck_out = 0
        self.taxi_out = 0
        self.in_counts = 0
        self.out_counts= 0
        self.counting_list = []


        self.count_txt_thickness = 0
        self.count_txt_color = (0, 0, 0)
        self.count_color = (255, 255, 255)

        # Tracks info
        self.track_history = defaultdict(list)
        self.track_thickness = 1
        self.draw_tracks = False
        self.track_color = (0, 255, 0)

        # Check if environment support imshow
        self.env_check = check_imshow(warn=True)

    def set_args(
        self,
        classes_names,
        reg_pts,
        roi ,
        count_reg_color=(255, 255, 255),
        line_thickness=2,
        track_thickness=2,
        view_img=False,
        view_in_counts=True,
        view_out_counts=True,
        draw_tracks=False,
        count_txt_thickness=2,
        count_txt_color=(0, 0, 0),
        count_color=(255, 255, 255),
        track_color=(0, 255, 0),
        region_thickness=2,
        line_dist_thresh=15,
    ):
        """
        Configures the Counter's image, bounding box line thickness, and counting region points.

        Args:
            line_thickness (int): Line thickness for bounding boxes.
            view_img (bool): Flag to control whether to display the video stream.
            view_in_counts (bool): Flag to control whether to display the incounts on video stream.
            view_out_counts (bool): Flag to control whether to display the outcounts on video stream.
            reg_pts (list): Initial list of points defining the counting region.
            classes_names (dict): Classes names
            track_thickness (int): Track thickness
            draw_tracks (Bool): draw tracks
            count_txt_thickness (int): Text thickness for object counting display
            count_txt_color (RGB color): count text color value
            count_color (RGB color): count text background color value
            count_reg_color (RGB color): Color of object counting region
            track_color (RGB color): color for tracks
            region_thickness (int): Object counting Region thickness
            line_dist_thresh (int): Euclidean Distance threshold for line counter
        """
        self.tf = line_thickness
        self.view_img = view_img
        self.view_in_counts = view_in_counts
        self.view_out_counts = view_out_counts
        self.track_thickness = track_thickness
        self.draw_tracks = draw_tracks

        # Region and line selection
        if len(reg_pts) == 2:
            print("Line Counter Initiated.")
            self.reg_pts = reg_pts
            self.counting_region = LineString(self.reg_pts)
        elif len(reg_pts) == 4:
            print("Region Counter Initiated.")
            self.reg_pts = reg_pts
            self.counting_region = Polygon(self.reg_pts)
        else:
            print("Invalid Region points provided, region_points can be 2 or 4")
            print("Using Line Counter Now")
            self.counting_region = LineString(self.reg_pts)




        self.names = classes_names
        self.track_color = track_color
        self.count_txt_thickness = count_txt_thickness
        self.count_txt_color = count_txt_color
        self.count_color = count_color
        self.region_color = count_reg_color
        self.region_thickness = region_thickness
        self.line_dist_thresh = line_dist_thresh


    def extract_and_process_tracks(self, tracks,roi_coords):
        """Extracts and processes tracks for object counting in a video stream."""
        boxes = tracks[0].boxes.xyxy.cpu()
        clss = tracks[0].boxes.cls.cpu().tolist()
        track_ids = tracks[0].boxes.id.int().cpu().tolist()
        scores = tracks[0].boxes.conf.cpu().tolist()


        xdate1, ydate1, xdate2, ydate2 = 1315, 39, 1930, 111
        date_time_region = self.im0[ydate1:ydate2, xdate1:xdate2]

        self.date1 = extract_date_and_time(date_time_region)
        last_valid_date = None
        # Si la nouvelle date est None, récupérer la dernière valeur non-None de la liste
        if self.date1 is None:
            for date in reversed(date1_list):
                if date is not None:
                    last_valid_date = date
                    break
        else:
            last_valid_date = self.date1

        # Afficher la date et l'heure
        if last_valid_date:
            print("Date:", last_valid_date)
        else:
            print("Impossible d'extraire la date et l'heure de la région capturée.","Date:",last_valid_date)

        # Ajouter la nouvelle valeur de date1 à la liste
        date1_list.append(self.date1)

        #print("ROI", roi_coords)
        # Initialize results dictionary
        results = {}
        object_coordinates = []
        license_plate_coordinates = []
        # MODELE DE DETECTION DE PLAQUE
        model_detect_path =  r"C:\Users\Utilisateur\Desktop\finale\license_plate_detector.pt"
        model_detect = YOLO(model_detect_path)

        # PARTIE TEMPS D'ATTENTE AUX POMPES
        if roi_coords is None:
            print("Les coordonnées de la zone ROI ne sont pas définies.")
            return

        # Utilisez les coordonnées des pompes pour extraire et traiter les pistes
        for pompe_name, pompe_coord in roi_coords.items():
            #print(pompe_name)
            #print(self.temps_attente_pompe)
            # Récupérez les coordonnées de la pompe actuelle
            pompe_x1, pompe_y1 = pompe_coord[0]
            pompe_x2, pompe_y2 = pompe_coord[1]


            #print(f"Coordonnées de la pompe {pompe_name} : x1={pompe_x1}, y1={pompe_y1}, x2={pompe_x2}, y2={pompe_y2}")

            for box, cls, track_id, score in zip(boxes, clss, track_ids, scores):
                x1, y1, x2, y2 = box
                # */*partie de telechargement des images de vehicules */*
                if cls == 2:
                  roi = self.im0[int(y1):int(y2), int(x1):int(x2)]
                  # Créer le dossier s'il n'existe pas déjà
                  if not os.path.exists(output1_folder):
                      os.makedirs(output1_folder)

                  # Récupérer le chemin complet du fichier d'image à enregistrer
                  output_file_path = os.path.join(output1_folder, f"car_{track_id}.jpg")

                  # Enregistrer l'image de la voiture détectée
                  cv2.imwrite(output_file_path, roi)
                object_coordinates.append((x1, y1, x2, y2, track_id, score))

                # Calculer le centre de la boîte englobante
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2

                if pompe_x1 <= center_x <= pompe_x2 and pompe_y1 <= center_y <= pompe_y2:
                    if not any(track_id == vehicle["track_id"] for vehicle in self.temps_attente_pompe.get(pompe_name, [])) and not any(track_id == vehicle["track_id"] for vehicle in self.infos_vehicules.get(pompe_name, [])):

                        # Enregistrez l'ID du véhicule, la classe et le temps d'entrée
                        entry = {"track_id": track_id, "class": classe_id_to_nom.get(cls, 'Inconnu'), "entry_time": time.time(), "date d'entrée" :last_valid_date}
                        self.temps_attente_pompe[pompe_name].append(entry)
                        self.infos_vehicules[pompe_name].append(entry)

                else:
                    # Si le véhicule quitte la zone de la pompe, calculez et imprimez le temps d'attente
                    for vehicle in self.temps_attente_pompe[pompe_name]:
                        if vehicle["track_id"] == track_id:
                            print("Date2:", last_valid_date)
                            exit_time = time.time()
                            entry_time = vehicle["entry_time"]
                            wait_time = exit_time - entry_time
                            print("**********************")
                            print(f"Temps d'attente pour le véhicule d'id {track_id} à la pompe {pompe_name} ({vehicle['class']}): {wait_time}")
                            # Ajouter les informations supplémentaires au dictionnaire infos_vehicules
                            for info_vehicle in self.infos_vehicules[pompe_name]:
                                if info_vehicle["track_id"] == track_id:

                                    info_vehicle["wait_time"] = wait_time
                                    info_vehicle["date de sortie"] = last_valid_date
                                    break  # Sortir de la boucle une fois que les informations ont été ajoutées
                            # Retirez le véhicule de la liste des temps d'entrée pour cette pompe
                            self.temps_attente_pompe[pompe_name].remove(vehicle)
                            break  # Sortir de la boucle une fois que le véhicule est trouvé

        #print("### TEMPORAIRE  ###",self.temps_attente_pompe)
        #print("### PERMANENT ###",self.infos_vehicules)









# """ ##############PARTIE LECTURE LICENSE PLATES

        vehicle_track_ids = []
        for box, track_id, clls in zip(boxes, track_ids, clss):
             vehicle_track_ids.append((box, track_id, clls))
        license_plates = model_detect(self.im0)[0]
        for license_plate in license_plates.boxes.data.tolist():

             # print("license_plate",license_plate)
              x1, y1, x2, y2, score, class_id = license_plate

             # Assign license plate to car
              xcar1, ycar1, xcar2, ycar2, car_id ,clls= get_car(license_plate, vehicle_track_ids)
              # Check if a corresponding car is found
              if car_id != -1:
                  #print("Car found for license plate!")
                  #print("Car ID:", car_id)
                  #print("Car bbox:", xcar1, ycar1, xcar2, ycar2)

                  # Crop the license plate area from the original image
                  license_plate_crop = self.im0[int(y1):int(y2), int(x1):int(x2)]
                  license_plate_text, license_plate_text_score = read_license_plate(license_plate_crop)

                  # */*partie de téléchargement des images des plaques*/*
                  if not os.path.exists(output2_folder):
                      os.makedirs(output2_folder)
                  if valider_plaque(license_plate_text):
                      # Récupérer le chemin complet du fichier d'image à enregistrer
                      output_file_path = os.path.join(output2_folder, f"{license_plate_text}.jpg")

                      # Enregistrer l'image de la plaque détectée
                      cv2.imwrite(output_file_path, license_plate_crop)
                  #print("License plate text:", license_plate_text)
                  #print("Confidence score:", license_plate_text_score)
                  if license_plate_text is not None:
                     if valider_plaque(license_plate_text):

                          # Draw bounding box around license plate
                          cv2.rectangle(self.im0, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                          cv2.putText(self.im0, license_plate_text, (int(x1), int(y2) + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                          self.LP_info_dict[car_id] = {'track_id': car_id, 'class': classe_id_to_nom.get(clls, 'Inconnu'), 'license_plate_text': license_plate_text,'score LP':license_plate_text_score}
        #print(self.LP_info_dict)

################# PARTIE EXTRACTION DU TEMPS D'aPRES L'IMAGE

        """  #print("Dimensions de l'image complète:", self.im0.shape)
        x1, y1, x2, y2 = 1487, 20, 1943, 108
        date_time_region = self.im0[y1:y2, x1:x2]
        # Afficher la région extraite
        #cv2.imshow("Date and Time Region", date_time_region)
        #cv2.waitKey(1)

        #cv2.destroyAllWindows()
        # Extraire la date et l'heure de la région capturée
        date1 = None
        time1= None
        date, time = extract_date_and_time(date_time_region)
        if date1 and time1:
            print("Date:", date1)
            print("Time:", time1)
        else:
            print("Impossible d'extraire la date et l'heure de la région capturée.")  """


##########  PARTIE COMPTAGE


        # Annotator Init and region drawing
        self.annotator = Annotator(self.im0, self.tf, self.names)
        self.annotator.draw_region(reg_pts=self.reg_pts, color=self.region_color, thickness=self.region_thickness)


        # Extract tracks
        for box, track_id, cls in zip(boxes, track_ids, clss):
            # Draw bounding box
            self.annotator.box_label(box, label=f"{track_id}:{self.names[cls]}", color=colors(int(cls), True))

            # Draw Tracks
            track_line = self.track_history[track_id]
            track_line.append((float((box[0] + box[2]) / 2), float((box[1] + box[3]) / 2)))
            if len(track_line) > 30:
                track_line.pop(0)

            # Draw track trails
            if self.draw_tracks:
                self.annotator.draw_centroid_and_tracks(
                    track_line, color=self.track_color, track_thickness=self.track_thickness
                )

            prev_position = self.track_history[track_id][-2] if len(self.track_history[track_id]) > 1 else None

            # Count objects

            if len(self.reg_pts) == 2:
                if prev_position is not None:
                    distance = Point(track_line[-1]).distance(self.counting_region)
                    if distance < self.line_dist_thresh and track_id not in self.counting_list:
                        self.counting_list.append(track_id)
                        if (box[0] - prev_position[0]) * (self.counting_region.centroid.x - prev_position[0]) > 0:
                            if self.names[cls] == "car":
                                self.car_out += 1
                            if self.names[cls] == "CM1":
                                self.CM1_out += 1
                            if self.names[cls] == "bigTruck":
                                 self.bigTruck_out +=1
                            if self.names[cls] == "motorcycle":
                                 self.motorcycle_out +=1
                            if self.names[cls] == "small truck":
                                 self.small_truck_out +=1
                            if self.names[cls] == "taxi":
                                self.taxi_out += 1

                            self.out_counts += 1




        #return self.infos_vehicules, self.LP_info_dict

    def display_frames(self):
        """Display frame."""
        if self.env_check:
            cv2.namedWindow("Ultralytics YOLOv8 Object Counter")
            if len(self.reg_pts) == 4:  # only add mouse event If user drawn region
                cv2.setMouseCallback(
                    "Ultralytics YOLOv8 Object Counter", self.mouse_event_for_region, {"region_points": self.reg_pts}
                )
            cv2.imshow("Ultralytics YOLOv8 Object Counter", self.im0)
            # Break Window
            if cv2.waitKey(1) & 0xFF == ord("q"):
                return

    def start_counting(self, im0, tracks,roi_coords):
        """
        Main function to start the object counting process.

        Args:
            im0 (ndarray): Current frame from the video stream.
            tracks (list): List of tracks obtained from the object tracking process.
        """
        self.im0 = im0  # store image
        self.roi_coords=roi_coords
        font_size = 2  # Vous pouvez ajuster cette valeur en fonction de vos besoins


        cv2.putText(im0, str(self.car_out),(70, 1405), cv2.FONT_HERSHEY_SIMPLEX, font_size, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(im0, str(self.small_truck_out),(384, 1405), cv2.FONT_HERSHEY_SIMPLEX, font_size, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(im0, str(self.bigTruck_out), (736, 1405), cv2.FONT_HERSHEY_SIMPLEX, font_size, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(im0, str(self.taxi_out), (1037, 1405), cv2.FONT_HERSHEY_SIMPLEX, font_size, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(im0, str(self.motorcycle_out ), (1349, 1405), cv2.FONT_HERSHEY_SIMPLEX, font_size, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(im0, str(self.CM1_out), (1688, 1405), cv2.FONT_HERSHEY_SIMPLEX, font_size, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(im0, str(self.out_counts), (1921, 1405), cv2.FONT_HERSHEY_SIMPLEX, font_size, (0, 0, 0), 3, cv2.LINE_AA)




        


        if tracks[0].boxes.id is None:
            if self.view_img:
                self.display_frames()
            return im0
        self.extract_and_process_tracks(tracks,roi_coords)

        if self.view_img:
            self.display_frames()
        return self.im0



if __name__ == "__main__":

    ObjectCounter()

