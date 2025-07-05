from src.indexation import *

if __name__ == "__main__":
    data_dir = "data"
    extracted_dir = os.path.join(data_dir, "extraits")
    cleaned_dir = os.path.join(data_dir, "nettoyes")
    whoosh_index_dir = os.path.join(data_dir, "index_whoosh")

    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(extracted_dir, exist_ok=True)
    os.makedirs(cleaned_dir, exist_ok=True)

    # --- PROCESSUS DE RECHERCHE DE DOCUMENTS ---

    # 1. Extraction des PDF bruts
    print("\n--- ÉTAPE 1 : EXTRACTION DES PDF BRUTS ---")
    process_pdfs_in_directory(data_dir)

    # 2. Nettoyage des fichiers extraits
    print("\n--- ÉTAPE 2 : NETTOYAGE DES FICHIERS EXTRAITS ---")
    nettoyer_fichiers_extraits(input_directory=extracted_dir, output_directory=cleaned_dir)

    # 3. Indexation avec Whoosh (maintenant avec lemmatisation et NER)
    print("\n--- ÉTAPE 3 : INDEXATION AVEC WHOOSH (incluant SpaCy Lemmatisation + NER) ---")
    whoosh_index = creer_index_whoosh(cleaned_files_directory=cleaned_dir, index_dir=whoosh_index_dir)

    # 4. Recherche dans l'index Whoosh
    if whoosh_index:
        print("\n--- ÉTAPE 4 : RECHERCHE DANS L'INDEX WHOOSH ---")
        
        rechercher_avec_whoosh(whoosh_index, "série temporelle") 

        rechercher_avec_whoosh(whoosh_index, "Valéry MONTHE")

        rechercher_avec_whoosh(whoosh_index, "Yaoundé")

        rechercher_avec_whoosh(whoosh_index, "20232024")
    

    else:
        print("\nImpossible d'effectuer des recherches car l'index Whoosh n'a pas été créé.")

    print("\nProcessus de recherche de documents avec NER terminé.")