import fitz 
import os

def extract_text_from_pdf(pdf_path):
    pdf_name = os.path.basename(pdf_path).replace(".pdf", "")
    
    # Définit le chemin du dossier de sortie pour les extraits
    output_directory = os.path.join("data", "extraits")
    
    # Définit le chemin complet du fichier de sortie pour le texte extrait
    output_file_path = os.path.join(output_directory, f"{pdf_name}.txt")

    try:
        # Ouvre le document PDF
        doc = fitz.open(pdf_path)
        text = ""
        # Extrait le texte de chaque page
        for page in doc:
            text += page.get_text()
        
        # Crée le dossier de sortie s'il n'existe pas
        os.makedirs(output_directory, exist_ok=True)
        
        # Écrit le texte extrait dans le fichier de sortie
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(text)
        
        print(f"PDF '{os.path.basename(pdf_path)}' extrait avec succès !")
        print(f"Contenu sauvegardé dans : {output_file_path}")
    except FileNotFoundError:
        print(f"Erreur : Le fichier PDF '{pdf_path}' n'a pas été trouvé. Assurez-vous que le chemin est correct.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de l'extraction du PDF '{os.path.basename(pdf_path)}' : {e}")


def process_pdfs_in_directory(directory_path="data"):
    """
    Parcourt un dossier donné, trouve tous les fichiers PDF et en extrait le texte.
    Le texte est sauvegardé dans un sous-dossier 'extraits' à l'intérieur de 'data',
    avec le nom du fichier original.
    """
    print(f"Début du traitement des PDF dans le dossier : {directory_path}\n")
    
    if not os.path.exists(directory_path):
        print(f"Le dossier '{directory_path}' n'existe pas. Veuillez le créer et y placer vos PDF.")
        return

    pdf_found = False
    # os.listdir() liste les fichiers et dossiers à la racine du chemin spécifié
    for filename in os.listdir(directory_path):
        # Construit le chemin complet du fichier
        file_path = os.path.join(directory_path, filename)
        
        # Vérifie si c'est un fichier et si son extension est .pdf
        if os.path.isfile(file_path) and filename.lower().endswith(".pdf"):
            pdf_found = True
            print(f"Fichier PDF trouvé : {filename}")
            extract_text_from_pdf(file_path)
            print("-" * 50) # Séparateur pour une meilleure lisibilité

    if not pdf_found:
        print(f"Aucun fichier PDF trouvé dans le dossier '{directory_path}'.")
    else:
        print("\nTraitement de tous les PDF terminé.")

# # Exemple d'utilisation
# if __name__ == "__main__":
#     # Assure-toi que le dossier 'data' existe pour les tests
#     if not os.path.exists("data"):
#         os.makedirs("data")
#         print("Dossier 'data' créé.")
    
#     process_pdfs_in_directory("data")

 