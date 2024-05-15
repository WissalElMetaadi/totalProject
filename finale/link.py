import pandas as pd
import os
import numpy as np

# Chemins vers les dossiers contenant les images de voiture et de plaque d'immatriculation
output_cars_folder = r'C:\Users\Utilisateur\Desktop\finale\output_cars'
output_license_plates_folder = r'C:\Users\Utilisateur\Desktop\finale\output_license_plates'

# Chemin vers le fichier Excel
excel_file = r'C:\Users\Utilisateur\Desktop\finale\output3.csv'

# Lire le fichier Excel
df = pd.read_csv(excel_file)

# Fonction pour créer un hyperlien vers une image
def create_hyperlink(image_path):
    return f'=HYPERLINK("{image_path}", "Lien vers l\'image")'

# Parcourir chaque ligne du dataframe
for index, row in df.iterrows():
    print(f"Processing row {index+1}...")
    # Récupérer le track ID de la voiture
    car_track_id = row['track_id']
    print(f"Car track ID: {car_track_id}")
    
    # Créer le nom du fichier de l'image de la voiture
    car_image_name = f"car_{car_track_id}.jpg"
    print(f"Car image name: {car_image_name}")
    
    # Créer le chemin complet vers l'image de la voiture
    car_image_path = os.path.join(output_cars_folder, car_image_name)
    print(f"Car image path: {car_image_path}")
    
    # Vérifier si le chemin d'accès à l'image de la voiture existe et que la valeur n'est pas NaN
    if not pd.isna(car_track_id) and os.path.exists(car_image_path):
        # Créer l'hyperlien pour l'image de la voiture
        car_hyperlink = create_hyperlink(car_image_path)
    else:
        car_hyperlink = 0
    
    # Mettre l'hyperlien dans la colonne correspondante du dataframe
    df.at[index, 'Car Image'] = car_hyperlink
    
    # Récupérer le texte de la plaque d'immatriculation
    license_plate_text = row['license_plate_text']
    print(f"License plate text: {license_plate_text}")
    
    # Créer le nom du fichier de l'image de la plaque d'immatriculation
    license_plate_image_name = f"{license_plate_text}.jpg"
    print(f"License plate image name: {license_plate_image_name}")
    
    # Créer le chemin complet vers l'image de la plaque d'immatriculation
    license_plate_image_path = os.path.join(output_license_plates_folder, license_plate_image_name)
    print(f"License plate image path: {license_plate_image_path}")
    
    # Vérifier si le chemin d'accès à l'image de la plaque d'immatriculation existe et que la valeur n'est pas NaN
    if not pd.isna(license_plate_text) and os.path.exists(license_plate_image_path):
        # Créer l'hyperlien pour l'image de la plaque d'immatriculation
        license_plate_hyperlink = create_hyperlink(license_plate_image_path)
    else:
        license_plate_hyperlink = 0
    
    # Mettre l'hyperlien dans la colonne correspondante du dataframe
    df.at[index, 'License Plate Image'] = license_plate_hyperlink

# Sauvegarder le dataframe avec les hyperliens dans un nouveau fichier Excel
output_excel_file = 'nouveau_excel1.xlsx'
df.to_excel(output_excel_file, index=False)
print(f"DataFrame saved to {output_excel_file}")
