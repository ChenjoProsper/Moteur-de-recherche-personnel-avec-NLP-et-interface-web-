from utils import *
import shutil # Pour nettoyer le dossier d'index Whoosh

# Importations Whoosh
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser


# --- Fonctions d'Indexation et de Recherche avec Whoosh ---

# Définition du schéma de l'index
# 'path' : le chemin unique du fichier (non analysé)
# 'content' : le contenu du fichier (texte analysé pour la recherche)
schema = Schema(filepath=ID(stored=True), content=TEXT(stored=True))

def creer_index_whoosh(cleaned_files_directory="data/nettoyes", index_dir="data/index_whoosh"):
    """
    Crée ou met à jour un index Whoosh à partir des fichiers texte nettoyés.
    """
    print(f"Début de la création/mise à jour de l'index Whoosh dans : {index_dir}\n")

    # Supprime l'index précédent pour s'assurer qu'il est propre (utile en développement)
    if os.path.exists(index_dir):
        shutil.rmtree(index_dir)
        print(f"Dossier d'index existant '{index_dir}' supprimé.")
    
    os.makedirs(index_dir) # Crée le dossier pour le nouvel index

    # Crée un nouvel index Whoosh avec le schéma défini
    ix = create_in(index_dir, schema)
    writer = ix.writer() # Obtient un writer pour ajouter des documents à l'index

    files_indexed_count = 0
    if not os.path.exists(cleaned_files_directory):
        print(f"Erreur : Le dossier des fichiers nettoyés '{cleaned_files_directory}' n'existe pas.")
        print("Veuillez d'abord exécuter les étapes d'extraction et de nettoyage.")
        return None

    # Parcourt les fichiers nettoyés et les ajoute à l'index
    for filename in os.listdir(cleaned_files_directory):
        if filename.lower().endswith(".txt"):
            file_path = os.path.join(cleaned_files_directory, filename)
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Ajoute le document à l'index
                # 'filepath' sera le nom du fichier (identifiant unique)
                # 'content' sera le texte du fichier
                writer.add_document(filepath=filename, content=content)
                
                print(f"Fichier '{filename}' ajouté à l'index.")
                files_indexed_count += 1

            except Exception as e:
                print(f"Erreur lors de l'ajout du fichier '{filename}' à l'index : {e}")

    writer.commit() # Valide toutes les modifications à l'index
    
    if files_indexed_count == 0:
        print(f"Aucun fichier .txt à indexer trouvé dans '{cleaned_files_directory}'.")
        return None
    else:
        print(f"\nIndexation Whoosh terminée. {files_indexed_count} documents indexés.")
        return ix # Retourne l'objet Index pour la recherche

def rechercher_avec_whoosh(index, requete, top_n=5):
    """
    Recherche une requête dans l'index Whoosh et retourne les fichiers pertinents.
    """
    if index is None:
        print("L'index Whoosh n'a pas été créé ou est vide.")
        return []

    print(f"\n--- Recherche pour '{requete}' ---")
    results_list = []
    
    # Ouvre un moteur de recherche sur l'index
    with index.searcher() as searcher:
        # Crée un parser de requête pour le champ 'content' (où se trouve le texte)
        # Whoosh gère automatiquement la tokenisation, le stemming, les stop words ici
        query_parser = QueryParser("content", index.schema)
        
        try:
            # Parse la requête de l'utilisateur
            query = query_parser.parse(requete)
            
            # Exécute la recherche
            results = searcher.search(query, limit=top_n)
            
            print(f"Trouvé {len(results)} résultat(s) (top {top_n} affichés) :")
            for hit in results:
                # 'hit.score' est le score de pertinence
                # 'hit['filepath']' accède au champ 'filepath' du document indexé
                results_list.append((hit['filepath'], hit.score))
                print(f"- {hit['filepath']} (Score: {hit.score:.2f})")
            
            if not results_list:
                print("Aucun résultat trouvé.")

        except Exception as e:
            print(f"Erreur lors de la recherche Whoosh : {e}")
            print("Astuce : Assurez-vous que votre requête est valide (ex: 'mot' ou 'mot AND autre_mot').")

    return results_list


# --- Exécution du workflow complet ---
if __name__ == "__main__":
    data_dir = "data"
    extracted_dir = os.path.join(data_dir, "extraits")
    cleaned_dir = os.path.join(data_dir, "nettoyes")
    whoosh_index_dir = os.path.join(data_dir, "index_whoosh")


    # --- PROCESSUS DE RECHERCHE DE DOCUMENTS ---

    # 1. Extraction des PDF bruts
    print("\n--- ÉTAPE 1 : EXTRACTION DES PDF BRUTS ---")
    process_pdfs_in_directory(data_dir)

    # 2. Nettoyage des fichiers extraits
    print("\n--- ÉTAPE 2 : NETTOYAGE DES FICHIERS EXTRAITS ---")
    nettoyer_fichiers_extraits(input_directory=extracted_dir, output_directory=cleaned_dir)

    # 3. Indexation avec Whoosh
    print("\n--- ÉTAPE 3 : INDEXATION AVEC WHOOSH ---")
    whoosh_index = creer_index_whoosh(cleaned_files_directory=cleaned_dir, index_dir=whoosh_index_dir)

    # 4. Recherche dans l'index Whoosh
    if whoosh_index:
    #     print("\n--- ÉTAPE 4 : RECHERCHE DANS L'INDEX WHOOSH ---")
    #     rechercher_avec_whoosh(whoosh_index, "abstraite")
    #     rechercher_avec_whoosh(whoosh_index, "Modélisation ") # Teste le stemming (garantie vs garantir)
    #     rechercher_avec_whoosh(whoosh_index, "séries temporelle") # Teste les stop words (l' et les apostrophes)
        rechercher_avec_whoosh(whoosh_index, "Valéry MONTHE Base")
    # else:
    #     print("\nImpossible d'effectuer des recherches car l'index Whoosh n'a pas été créé.")

    # print("\nProcessus de recherche de documents terminé.")