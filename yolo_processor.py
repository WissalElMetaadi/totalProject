from ultralytics import YOLO
import cv2
from code_1_ligne import ObjectCounter
from code_1_ligne import combine_dicts


# Initialiser le modèle YOLO et l'ObjectCounter en dehors de la fonction pour éviter la réinitialisation à chaque appel
model = YOLO(r"C:\Users\Utilisateur\Desktop\finale\best.pt")
counter = ObjectCounter()
roi_coords = {
    'Pompe 6': [(776, 453), (1314, 656)],
    'Pompe 7': [(460, 478), (813, 708)],
    'Pompe 8': [(100, 518), (357, 744)],
    'Pompe 4': [(1521, 333), (1840, 576)],
    'Pompe 5': [(1316, 400), (1517, 612)]
}
line_points = [(8, 785), (1946, 568)]
counter.set_args(view_img=True, reg_pts=line_points, classes_names=model.names, draw_tracks=True, roi=roi_coords)

def process_frame(frame):
    if frame is None or frame.size == 0:
        return None


    
    #counter.set_args(view_img=True,reg_pts=line_points,classes_names=model.names,draw_tracks=True, roi=roi_coords)



    tracks = model.track(frame, persist=True, show=False)
    annotated_frame = counter.start_counting(frame, tracks, roi_coords)
    #video_writer.write(frame)
   
    #video_writer.release()
    #print(counter.infos_vehicules)
    #print(counter.LP_info_dict)
    #combined_dict = combine_dicts(counter.LP_info_dict, counter.infos_vehicules)
    #print(combined_dict)
    return annotated_frame,counter.combined_dict

