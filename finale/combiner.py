LP_info_dict = {
    2: {'track_id': 2, 'class': 'Taxi', 'license_plate_text': '211TU6617', 'score LP': 0.8247178867459297},
    1: {'track_id': 1, 'class': 'Car', 'license_plate_text': '188TN8229', 'score LP': 0.6499083004891872}
}

pompes_dict = {
    'Pompe 6': [{'track_id': 1, 'class': 'Car', 'entry_time': 1711536072.1774518, 'exit_time': 1711536281.4868178, 'wait_time': 209.3093659877777}, {'track_id': 12, 'class': 'Worker', 'entry_time': 1711536094.7980182, 'exit_time': 1711536164.765995, 'wait_time': 69.96797680854797}, {'track_id': 18, 'class': 'Worker', 'entry_time': 1711536244.747503, 'exit_time': 1711536249.2204096, 'wait_time': 4.472906589508057}],
    'Pompe 7': [{'track_id': 2, 'class': 'Taxi', 'entry_time': 1711536072.1774518}, {'track_id': 13, 'class': 'Worker', 'entry_time': 1711536095.8584843}],
    'Pompe 8': []
}

def combine_dicts(LP_info_dict, pompes_dict):
    combined_dict = {}

    # Parcourir LP_info_dict pour combiner les informations
    for id_, lp_info in LP_info_dict.items():
        combined_dict[id_] = lp_info

        # Rechercher les informations de la pompe correspondant à cet ID
        for pompe, infos in pompes_dict.items():
            for i in infos:
                if isinstance(i, dict) and 'track_id' in i and i['track_id'] == id_:
                    combined_dict[id_]['pompes_info'] = pompe
                    combined_dict[id_]['entry_time'] = i['entry_time']
                    combined_dict[id_]['exit_time'] = i.get('exit_time', None)
                    combined_dict[id_]['wait_time'] = i.get('wait_time', None)

    # Parcourir pompes_dict pour ajouter les objets qui n'ont pas de correspondance
    for pompe, infos in pompes_dict.items():
        for i in infos:
          if isinstance(i, dict) and pompe in i:
            id_ = i[pompe]['track_id']
            if id_ not in combined_dict:
                combined_dict[id_] = {
                    'track_id': id_,
                    'class': i['class'],
                    'license_plate_text': None,
                    'score LP': None,
                    'pompes_info': pompe,
                    'entry_time': i['entry_time'],
                    'exit_time': i.get('exit_time', None),
                    'wait_time': i.get('wait_time', None)
                }

    return combined_dict


# Afficher le dictionnaire combiné
print(combine_dicts(LP_info_dict, pompes_dict))






