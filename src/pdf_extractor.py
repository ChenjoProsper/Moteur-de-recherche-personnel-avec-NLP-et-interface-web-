import fitz 
import os
from .utils import nettoyer_texte

def extract_text_from_pdf(pdf_path, apply_cleaning=False):
    pdf_name = os.path.basename(pdf_path).replace(".pdf", "")
    output_directory = os.path.join("data", "extraits")
    output_file_path = os.path.join(output_directory, f"{pdf_name}.txt")
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        if apply_cleaning:
            text = nettoyer_texte(text)
        os.makedirs(output_directory, exist_ok=True)
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(text)
    except FileNotFoundError:
        print(f"Erreur : Le fichier PDF '{pdf_path}' n'a pas été trouvé.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de l'extraction du PDF '{os.path.basename(pdf_path)}' : {e}")


def process_pdfs_in_directory(directory_path="data"):
    print(f"Début de l'extraction des PDF dans le dossier : {directory_path}\n")
    if not os.path.exists(directory_path):
        print(f"Le dossier '{directory_path}' n'existe pas.")
        return
    pdf_found = False
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path) and filename.lower().endswith(".pdf"):
            pdf_found = True
            print(f"\n--- Extraction de : {filename} ---")
            extract_text_from_pdf(file_path, apply_cleaning=False)
            print("-" * 50) 
    if not pdf_found:
        print(f"Aucun fichier PDF trouvé dans le dossier '{directory_path}'.")
    else:
        print("\nExtraction de tous les PDF terminée.")
# # Exemple d'utilisation
# if __name__ == "__main__":
#     # Assure-toi que le dossier 'data' existe pour les tests
#     if not os.path.exists("data"):
#         os.makedirs("data")
#         print("Dossier 'data' créé.")
    
#     process_pdfs_in_directory("data")

 