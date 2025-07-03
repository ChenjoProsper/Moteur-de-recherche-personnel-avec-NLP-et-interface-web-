import re
import os

# --- Fonction de nettoyage du texte (inchangée) ---
def nettoyer_texte(texte):
    """
    Nettoie une chaîne de texte en supprimant les éléments indésirables,
    tout en conservant l'apostrophe (').
    """
    # Supprimer les balises HTML (ex: <p>, <div>, <a>)
    texte = re.sub(r'<[^>]+>', '', texte)

    # Remplacer les entités HTML (ex: &amp;, &lt;, &#x27;) par leur équivalent
    texte = texte.replace('&amp;', '&')
    texte = texte.replace('&lt;', '<')
    texte = texte.replace('&gt;', '>')
    texte = texte.replace('&quot;', '"')
    texte = texte.replace('&#x27;', "'") # Assure que l'entité apostrophe est bien convertie
    texte = texte.replace('&#x2F;', '/')
    # ... ajoutez d'autres entités si nécessaire

    # Garde les caractères accentués français, la ponctuation courante ET L'APOSTROPHE
    texte = re.sub(r'[^a-zA-Z0-9\s.,!?-ÀàÂâÄäÈèÉéÊêËëÎîÏïÔôŒœÙùÛûÜüŸÿÇç\']', '', texte)

    # Supprimer les multiples espaces, tabulations, retours à la ligne
    texte = re.sub(r'\s+', ' ', texte) 
    
    # Supprimer les numéros de page ou en-têtes/pieds de page répétitifs (générique)
    texte = re.sub(r'^\s*\d+\s*$', '', texte, flags=re.MULTILINE) 
    texte = re.sub(r'\b\d{1,4}\b', '', texte) # 1 à 4 chiffres isolés
    
    # Supprimer les lignes vides excessives
    texte = re.sub(r'\n\s*\n', '\n', texte)
    
    # Supprimer les espaces en début et fin de chaque ligne
    texte = "\n".join([line.strip() for line in texte.split('\n')])

    # Supprimer les espaces en début et fin de la chaîne finale
    texte = texte.strip()

    return texte
# --- Nouvelle fonction pour nettoyer les fichiers existants ---
def nettoyer_fichiers_extraits(input_directory="data/extraits", output_directory="data/nettoyes"):
    """
    Lit tous les fichiers .txt d'un dossier d'entrée, les nettoie
    et sauvegarde les versions nettoyées dans un dossier de sortie.
    """
    print(f"Début du nettoyage des fichiers dans : {input_directory}\n")
    
    if not os.path.exists(input_directory):
        print(f"Erreur : Le dossier d'entrée '{input_directory}' n'existe pas. Veuillez d'abord extraire les fichiers.")
        return

    # Crée le dossier de sortie pour les fichiers nettoyés s'il n'existe pas
    os.makedirs(output_directory, exist_ok=True)
    
    files_found = False
    for filename in os.listdir(input_directory):
        if filename.lower().endswith(".txt"):
            files_found = True
            input_file_path = os.path.join(input_directory, filename)
            output_file_path = os.path.join(output_directory, filename) # Le nom de fichier reste le même

            try:
                # 1. Lire le contenu du fichier extrait
                with open(input_file_path, "r", encoding="utf-8") as f:
                    texte_brut = f.read()
                
                print(f"Nettoyage de : {filename}")
                
                # 2. Nettoyer le texte
                texte_nettoye = nettoyer_texte(texte_brut)
                
                # 3. Enregistrer la version nettoyée
                with open(output_file_path, "w", encoding="utf-8") as f:
                    f.write(texte_nettoye)
                
                print(f"Version nettoyée sauvegardée dans : {output_file_path}")
                print("-" * 50)

            except Exception as e:
                print(f"Erreur lors du nettoyage du fichier '{filename}' : {e}")
                print("-" * 50)
    
    if not files_found:
        print(f"Aucun fichier .txt trouvé dans le dossier '{input_directory}'.")
    else:
        print("\nNettoyage de tous les fichiers extraits terminé.")


from pdf_extractor import *

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