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







pompes_dict ={'Pompe 6 ': [{'track_id': 1, 'class': 'Car', 'entry_time': 1711896660.4945261, "date d'entrée": 'First date not detected yet', 'wait_time': 440.7119708061218, 'date de sortie': '2023-12-04 08:10:10'}, {'track_id': 12, 'class': 'Worker', 'entry_time': 1711896722.7203498, "date d'entrée": '2023-12-04 08:03:52', 'wait_time': 138.7424876689911, 'date de sortie': '2023-12-04 08:06:11'}, {'track_id': 18, 'class': 'Worker', 'entry_time': 1711897022.67002, "date d'entrée": '2023-12-04 08:08:52', 'wait_time': 5.622784852981567, 'date de sortie': '2023-12-04 08:08:57'}], 'Pompe 7': [{'track_id': 2, 'class': 'Taxi', 'entry_time': 1711896660.494979, "date d'entrée": 'First date not detected yet'}, {'track_id': 13, 'class': 'Worker', 'entry_time': 1711896723.4899054, "date d'entrée": '2023-12-04 08:03:53'}], 'Pompe 8': []}

LP_info_dict ={2: {'track_id': 2, 'class': 'Taxi', 'license_plate_text': '211TU6617', 'score LP': 0.806030735373497}, 1: {'track_id': 1, 'class': 'Car', 'license_plate_text': '188TU8229', 'score LP': 0.8152923211455345}, 15: {'track_id': 15, 'class': 'Car', 'license_plate_text': '06TU487', 'score LP': 0.5623502631982168}, 17: {'track_id': 17, 'class': 'Car', 'license_plate_text': '157TU8276', 'score LP': 0.7515913248062134}}

#combined_dict = combine_dicts(LP_info_dict, pompes_dict)

# Afficher le résultat
#print(combined_dict)






data= {2: {'track_id': 2, 'class': 'Taxi', 'license_plate_text': '211TU6617', 'score LP': 0.806030735373497, 'pompes_info': 'Pompe 7', "date d'entrée": None, 'date de sortie': None, 'wait_time': None}, 1: {'track_id': 1, 'class': 'Car', 'license_plate_text': '188TU8229', 'score LP': 0.8152923211455345, 'pompes_info': 'Pompe 6 ', "date d'entrée": None, 'date de sortie': '2023-12-04 08:03:18', 'wait_time': 459.7431151866913}, 15: {'track_id': 15, 'class': 'Car', 'license_plate_text': '06TU487', 'score LP': 0.5623502631982168, 'pompes_info': None, "date d'entrée": None, 'date de sortie': None, 'wait_time': None}, 17: {'track_id': 17, 'class': 'Car', 'license_plate_text': '157TU8276', 'score LP': 0.7515913248062134, 'pompes_info': 'Pompe 5', "date d'entrée": '2023-12-04 08:03:12', 'date de sortie': None, 'wait_time': None}, 12: {'track_id': 12, 'class': 'Worker', 'license_plate_text': None, 'score LP': None, 'pompes_info': 'Pompe 6 ', "date d'entrée": '2023-12-04 08:02:59', 'date de sortie': '2023-12-04 08:03:05', 'wait_time': 145.47826170921326}, 18: {'track_id': 18, 'class': 'Worker', 'license_plate_text': None, 'score LP': None, 'pompes_info': 'Pompe 6 ', "date d'entrée": '2023-12-04 08:03:15', 'date de sortie': '2023-12-04 08:03:15', 'wait_time': 6.65948486328125}, 13: {'track_id': 13, 'class': 'Worker', 'license_plate_text': None, 'score LP': None, 'pompes_info': 'Pompe 7', "date d'entrée": '2023-12-04 08:02:59', 'date de sortie': None, 'wait_time': None}, 6: {'track_id': 6, 'class': 'Taxi', 'license_plate_text': None, 'score LP': None, 'pompes_info': 'Pompe 4', "date d'entrée": None, 'date de sortie': None, 'wait_time': None}, 10: {'track_id': 10, 'class': 'Taxi', 'license_plate_text': None, 'score LP': None, 'pompes_info': 'Pompe 4', "date d'entrée": '2023-12-04 08:02:57', 'date de sortie': '2023-12-04 08:03:05', 'wait_time': 178.4359962940216}}


import csv

def write_dict_to_csv(data, filename):
    # Liste des noms de colonnes dans le même ordre que les clés du dictionnaire
    fieldnames = ['track_id', 'class', 'license_plate_text', 'score LP', 'pompes_info', "date d'entrée", 'date de sortie', 'wait_time']

    # Écriture des données dans le fichier CSV
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()  # Écriture de l'en-tête avec les noms de colonnes

        # Écriture des lignes de données
        for _, info in data.items():
            writer.writerow(info)

write_dict_to_csv(data, 'output3.csv')