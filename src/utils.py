import re

# Charger le modèle de langue française de SpaCy
# 'disable' permet de désactiver les composants du pipeline dont vous n'avez pas besoin
# pour accélérer le traitement si vous ne faites que de la lemmatisation.
# Pour la NER, vous auriez besoin de 'ner', 'textcat', etc.


def nettoyer_texte(texte):
    texte = re.sub(r'<[^>]+>', '', texte)
    texte = texte.replace('&amp;', '&')
    texte = texte.replace('&lt;', '<')
    texte = texte.replace('&gt;', '>')
    texte = texte.replace('&quot;', '"')
    texte = texte.replace('&#x27;', "'") 
    texte = texte.replace('&#x2F;', '/')
    texte = re.sub(r'[^a-zA-Z0-9\s.,!?-ÀàÂâÄäÈèÉéÊêËëÎîÏïÔôŒœÙùÛûÜüŸÿÇç\']', '', texte)
    texte = re.sub(r'\s+', ' ', texte) 
    texte = re.sub(r'^\s*\d+\s*$', '', texte, flags=re.MULTILINE) 
    texte = re.sub(r'\b\d{1,4}\b', '', texte)
    
    # Pas de lemmatisation ici car elle sera appliquée pendant l'extraction des entités et pour le contenu principal.
    # On veut que le NER s'exécute sur un texte propre mais pas encore lemmatisé globalement.
    
    texte = re.sub(r'\n\s*\n', '\n', texte)
    texte = "\n".join([line.strip() for line in texte.split('\n')])
    texte = texte.strip()
    return texte

# --- Nouvelle fonction pour nettoyer les fichiers existants ---
def nettoyer_fichiers_extraits(input_directory="data/extraits", output_directory="data/nettoyes"):
    print(f"Début du nettoyage des fichiers dans : {input_directory}\n")
    if not os.path.exists(input_directory):
        print(f"Erreur : Le dossier d'entrée '{input_directory}' n'existe pas.")
        return
    os.makedirs(output_directory, exist_ok=True)
    files_found = False
    for filename in os.listdir(input_directory):
        if filename.lower().endswith(".txt"):
            files_found = True
            input_file_path = os.path.join(input_directory, filename)
            output_file_path = os.path.join(output_directory, filename)
            try:
                with open(input_file_path, "r", encoding="utf-8") as f:
                    texte_brut = f.read()
                print(f"Nettoyage de : {filename}")
                texte_nettoye = nettoyer_texte(texte_brut) # On nettoie mais on ne lemmatise pas encore tout le texte ici
                with open(output_file_path, "w", encoding="utf-8") as f:
                    f.write(texte_nettoye)
                print(f"Version nettoyée sauvegardée dans : {output_file_path}")
            except Exception as e:
                print(f"Erreur lors du nettoyage du fichier '{filename}' : {e}")
    if not files_found:
        print(f"Aucun fichier .txt trouvé dans le dossier '{input_directory}'.")
    else:
        print("\nNettoyage de tous les fichiers extraits terminé.")

from .pdf_extractor import *

# --- Exemple d'utilisation du processus en deux étapes ---
if __name__ == "__main__":
    # 1. Préparation des dossiers et fichiers de test
    data_dir = "data"

    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print("Dossier 'data' créé.")

    extracted_dir = os.path.join(data_dir, "extraits")
    cleaned_dir = os.path.join(data_dir, "nettoyes")

    # --- PROCESSUS EN DEUX ÉTAPES ---

    print("\n--- ÉTAPE 1 : EXTRACTION DES PDF BRUTS ---")
    process_pdfs_in_directory(data_dir) # Extrait les PDF dans data/extraits

    print("\n--- ÉTAPE 2 : NETTOYAGE DES FICHIERS EXTRAITS ---")
    # Nettoie les fichiers de data/extraits et les sauvegarde dans data/nettoyes
    nettoyer_fichiers_extraits(input_directory=extracted_dir, output_directory=cleaned_dir)

    print("\nProcessus terminé : Les fichiers PDF ont été extraits et leurs versions nettoyées sont disponibles.")
    print(f"Fichiers bruts : {extracted_dir}")
    print(f"Fichiers nettoyés : {cleaned_dir}")

