import pandas as pd

# Tentative de relecture et conversion du fichier Excel en raison d'une erreur interne
excel_file_path = r'C:\Users\Utilisateur\Desktop\projet_flask\nouveau_excel2.xlsx'
csv_output_file_path = r'C:\Users\Utilisateur\Desktop\projet_flask\nouveau_excel2_converted.csv'

# Réessayer de lire le fichier Excel
try:
    df_from_excel = pd.read_excel(excel_file_path)
    # Sauvegarder en tant que fichier CSV
    df_from_excel.to_csv(csv_output_file_path, index=False)
    success = True
except Exception as e:
    success = False
    print(e)

csv_output_file_path if success else "Échec de la conversion."
