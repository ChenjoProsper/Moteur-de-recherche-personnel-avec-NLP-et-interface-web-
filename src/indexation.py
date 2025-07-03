from utils import *

# --- Fonction d'Indexation ---
def creer_index_inverse(cleaned_files_directory="data/nettoyes"):
    """
    Crée un index inversé à partir des fichiers texte nettoyés.
    L'index stocke pour chaque mot, les noms des fichiers où il apparaît.
    """
    index_inverse = {} # Dictionnaire: {mot: [liste_de_fichiers_ou_le_mot_apparait]}
    
    print(f"Début de l'indexation des fichiers dans : {cleaned_files_directory}\n")

    if not os.path.exists(cleaned_files_directory):
        print(f"Erreur : Le dossier des fichiers nettoyés '{cleaned_files_directory}' n'existe pas.")
        print("Assurez-vous d'avoir exécuté les étapes d'extraction et de nettoyage auparavant.")
        return None

    files_indexed_count = 0
    # Parcourir tous les fichiers dans le dossier des fichiers nettoyés
    for filename in os.listdir(cleaned_files_directory):
        if filename.lower().endswith(".txt"):
            file_path = os.path.join(cleaned_files_directory, filename)
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Tokenisation simple: diviser le texte en mots
                # Convertir en minuscules pour une recherche insensible à la casse
                words = re.findall(r'\b\w+\b', content.lower()) 
                
                # Ajouter les mots à l'index inversé
                for word in set(words): # Utilise un set pour ne pas ajouter le même fichier plusieurs fois pour le même mot
                    if word not in index_inverse:
                        index_inverse[word] = []
                    index_inverse[word].append(filename)
                
                print(f"Fichier '{filename}' indexé.")
                files_indexed_count += 1

            except Exception as e:
                print(f"Erreur lors de l'indexation du fichier '{filename}' : {e}")

    if files_indexed_count == 0:
        print(f"Aucun fichier .txt à indexer trouvé dans '{cleaned_files_directory}'.")
        return None
    else:
        print(f"\nIndexation terminée. {files_indexed_count} fichiers indexés.")
        print(f"Taille de l'index (nombre de mots uniques) : {len(index_inverse)}")
        return index_inverse

# --- Fonction de Recherche (pour tester l'index) ---
def rechercher_dans_index(index_inverse, requete):
    """
    Recherche une requête dans l'index inversé et retourne les fichiers pertinents.
    """
    if not index_inverse:
        print("L'index n'a pas été créé ou est vide.")
        return []

    # Nettoyer la requête de recherche de la même manière que le texte a été nettoyé
    requete_nettoyee = nettoyer_texte(requete).lower()
    mots_requete = re.findall(r'\b\w+\b', requete_nettoyee)

    if not mots_requete:
        print("Veuillez entrer des mots valides pour la recherche.")
        return []

    # Initialiser l'ensemble des résultats avec les documents du premier mot
    # Si le mot n'est pas dans l'index, les résultats sont vides.
    resultats = set(index_inverse.get(mots_requete[0], [])) 

    # Pour les recherches multi-mots (ET logique)
    for i in range(1, len(mots_requete)):
        word = mots_requete[i]
        if word in index_inverse:
            resultats = resultats.intersection(set(index_inverse[word])) # Intersection pour trouver les docs qui contiennent TOUS les mots
        else:
            # Si un mot de la requête n'est pas dans l'index, aucun document ne peut contenir tous les mots.
            return [] 
    
    # Retourner la liste des noms de fichiers triés (optionnel)
    return sorted(list(resultats))

# --- Exemple d'utilisation dans le script principal ---
if __name__ == "__main__":
    # Assure-toi que les dossiers existent et contiennent des fichiers nettoyés pour le test
    data_dir = "data"
    extracted_dir = os.path.join(data_dir, "extraits")
    cleaned_dir = os.path.join(data_dir, "nettoyes")

    # Crée des fichiers nettoyés factices si non existants
    os.makedirs(cleaned_dir, exist_ok=True)
    sample_cleaned_files = {
        "doc1.txt": "Le chat noir dort sur le canapé.",
        "doc2.txt": "Le chien et le chat jouent dans le jardin.",
        "doc3.txt": "Les animaux domestiques incluent les chats et les chiens.",
        "doc4.txt": "Un oiseau vole dans le ciel bleu."
    }
    for filename, content in sample_cleaned_files.items():
        file_path = os.path.join(cleaned_dir, filename)
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Fichier nettoyé factice '{filename}' créé pour le test.")

    # Étape d'Indexation
    mon_index = creer_index_inverse(cleaned_files_directory=cleaned_dir)

    # Étape de Recherche (si l'index a été créé)
    if mon_index:
        print("\n--- TEST DE RECHERCHE ---")
        requete1 = "chat noir"
        resultats1 = rechercher_dans_index(mon_index, requete1)
        print(f"Recherche pour '{requete1}' : {resultats1}") # Attendu: ['doc1.txt']

        requete2 = "chat chien"
        resultats2 = rechercher_dans_index(mon_index, requete2)
        print(f"Recherche pour '{requete2}' : {resultats2}") # Attendu: ['doc2.txt', 'doc3.txt']

        requete3 = "oiseau"
        resultats3 = rechercher_dans_index(mon_index, requete3)
        print(f"Recherche pour '{requete3}' : {resultats3}") # Attendu: ['doc4.txt']

        requete4 = "python"
        resultats4 = rechercher_dans_index(mon_index, requete4)
        print(f"Recherche pour '{requete4}' : {resultats4}") # Attendu: [] (car pas dans les fichiers d'exemple)

        requete5 = "nombre temps"
        resultats5 = rechercher_dans_index(mon_index, requete5)
        print(f"Recherche pour '{requete5}' : {resultats5}") # Attendu: ['doc1.txt', 'doc2.txt', 'doc3.txt', 'doc4.txt']
    else:
        print("\nIndexation échouée, impossible de lancer la recherche.")