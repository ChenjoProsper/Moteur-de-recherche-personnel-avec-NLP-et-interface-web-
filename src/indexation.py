import os
import shutil
import spacy
import numpy as np
import fasttext

from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser

from .utils import * # Assurez-vous que le . est bien là pour l'import relatif

# --- Chargement du modèle SpaCy ---
try:
    nlp = spacy.load("fr_core_news_sm", disable=['parser', 'textcat'])
    print("Modèle SpaCy 'fr_core_news_sm' chargé avec succès (incluant NER).")
except OSError:
    print("Le modèle SpaCy 'fr_core_news_sm' n'est pas trouvé. Veuillez l'installer en exécutant :")
    print("python -m spacy download fr_core_news_sm")
    exit()

# --- Chargement du modèle fastText ---
# Utilisez le modèle quantifié (.ftz) si le .bin est trop gourmand en RAM
FASTTEXT_MODEL_PATH = "data/cc.fr.300.bin" # <-- Assurez-vous d'utiliser .ftz si nécessaire
# FASTTEXT_MODEL_PATH = "data/cc.fr.300.ftz" # <-- Décommentez ceci si .bin pose problème

ft_model = None
try:
    print(f"Chargement du modèle fastText depuis : {FASTTEXT_MODEL_PATH}...")
    ft_model = fasttext.load_model(FASTTEXT_MODEL_PATH)
    print("Modèle fastText chargé avec succès.")
except ValueError:
    print(f"Erreur : Impossible de charger le modèle fastText depuis '{FASTTEXT_MODEL_PATH}'.")
    print("Veuillez vous assurer que le fichier '.bin'/.ftz est bien un modèle fastText valide et qu'il est téléchargé.")
    exit()
except Exception as e:
    print(f"Une erreur inattendue est survenue lors du chargement de fastText : {e}")
    print("Vérifiez que 'fasttext' est installé (pip install fasttext) et que le chemin du modèle est correct.")
    exit()


# --- Schéma Whoosh (inchangé) ---
schema = Schema(
    filepath=ID(stored=True), 
    content=TEXT(stored=True), 
    PERSON=TEXT(stored=True),    
    ORG=TEXT(stored=True),       
    LOC=TEXT(stored=True),       
    DATE=TEXT(stored=True),      
    GPE=TEXT(stored=True),       
)

# --- Chemin pour sauvegarder les embeddings ---
EMBEDDINGS_DIR = "data/document_embeddings"

# --- Fonction pour obtenir l'intégration (embedding) d'un texte (MODIFIÉE) ---
def get_text_embedding(text, max_tokens=500): # Ajout de max_tokens
    """
    Calcule l'intégration d'un texte en moyennant les intégrations de ses mots.
    Utilise le modèle fastText chargé.
    max_tokens: Limite le nombre de tokens traités pour l'embedding afin de réduire la consommation mémoire.
    """
    if not ft_model:
        print("Erreur : Le modèle fastText n'est pas chargé.")
        return None

    doc = nlp(text.lower())
    # Limitez le nombre de tokens pour l'embedding si le document est très long
    tokens = [
        token.lemma_ for token in doc 
        if not token.is_space and not token.is_punct and not token.is_stop
    ][:max_tokens] # <-- Troncation ici

    # Si aucun token valide n'est trouvé, retourne un vecteur de zéros
    if not tokens:
        # Assurez-vous d'avoir une dimension valide, même si le modèle n'a pas encore de mots
        # Une façon est d'interroger un mot commun ou de fixer la dimension (ici 300 pour cc.fr.300)
        embedding_dim = ft_model.get_word_vector('test').shape[0] if ft_model else 300
        return np.zeros(embedding_dim) 
    
    word_vectors = []
    for word in tokens:
        # Vérifiez que le mot existe dans le vocabulaire du modèle avant de tenter de récupérer son vecteur
        if word in ft_model: # fastText permet de vérifier si un mot est dans le vocabulaire
            word_vectors.append(ft_model.get_word_vector(word))
    
    # Si aucun mot dans le texte n'a de vecteur dans le modèle, retourne un vecteur de zéros
    if not word_vectors:
        embedding_dim = ft_model.get_word_vector('test').shape[0] if ft_model else 300
        return np.zeros(embedding_dim)
        
    return np.mean(word_vectors, axis=0)


# --- Fonction creer_index_whoosh (MODIFIÉE pour passer max_tokens) ---
def creer_index_whoosh(cleaned_files_directory="data/nettoyes", index_dir="data/index_whoosh"):
    # ... (code inchangé pour la suppression des dossiers et la création de l'index) ...

    print(f"Début de la création/mise à jour de l'index Whoosh dans : {index_dir}\n")

    if os.path.exists(index_dir):
        shutil.rmtree(index_dir)
        print(f"Dossier d'index existant '{index_dir}' supprimé.")
    
    os.makedirs(index_dir)

    if os.path.exists(EMBEDDINGS_DIR):
        shutil.rmtree(EMBEDDINGS_DIR)
        print(f"Dossier d'embeddings existant '{EMBEDDINGS_DIR}' supprimé.")
    os.makedirs(EMBEDDINGS_DIR)
    print(f"Dossier d'embeddings créé : {EMBEDDINGS_DIR}")

    ix = create_in(index_dir, schema)
    writer = ix.writer()

    files_indexed_count = 0
    if not os.path.exists(cleaned_files_directory):
        print(f"Erreur : Le dossier des fichiers nettoyés '{cleaned_files_directory}' n'existe pas.")
        return None

    for filename in os.listdir(cleaned_files_directory):
        if filename.lower().endswith(".txt"):
            file_path = os.path.join(cleaned_files_directory, filename)
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content_brut_nettoye = f.read()

                # --- Traitement SpaCy : Lemmatisation et NER ---
                doc = nlp(content_brut_nettoye) 

                lemmas = [
                    token.lemma_ for token in doc 
                    if not token.is_space and not token.is_punct and not token.is_stop
                ]
                content_lemmatise = " ".join(lemmas)

                entities = {
                    "PERSON": [], "ORG": [], "LOC": [], "DATE": [], "GPE": []
                }
                for ent in doc.ents:
                    if ent.label_ in entities:
                        ent_lemmatized = " ".join([token.lemma_ for token in nlp(ent.text) if not token.is_space])
                        entities[ent.label_].append(ent_lemmatized)
                
                person_ents = " ".join(sorted(list(set(entities["PERSON"]))))
                org_ents = " ".join(sorted(list(set(entities["ORG"]))))
                loc_ents = " ".join(sorted(list(set(entities["LOC"]))))
                date_ents = " ".join(sorted(list(set(entities["DATE"]))))
                gpe_ents = " ".join(sorted(list(set(entities["GPE"]))))

                # --- Calcul de l'embedding du document et sauvegarde sur disque (MODIFIÉ) ---
                # Passe le paramètre max_tokens pour éviter les erreurs d'allocation
                doc_embedding = get_text_embedding(content_lemmatise, max_tokens=1000) # Essayez 1000 tokens, ajustez si nécessaire
                
                if doc_embedding is not None and np.linalg.norm(doc_embedding) > 0: # S'assurer que l'embedding n'est pas nul
                    embedding_filename = os.path.splitext(filename)[0] + ".npy"
                    embedding_path = os.path.join(EMBEDDINGS_DIR, embedding_filename)
                    np.save(embedding_path, doc_embedding)
                    # print(f"Embedding pour '{filename}' sauvegardé dans '{embedding_path}'.")
                else:
                    print(f"Avertissement : Embedding non généré ou nul pour '{filename}'.")


                # --- Ajout du document à l'index Whoosh ---
                writer.add_document(
                    filepath=filename, 
                    content=content_lemmatise,
                    PERSON=person_ents,
                    ORG=org_ents,
                    LOC=loc_ents,
                    DATE=date_ents,
                    GPE=gpe_ents
                )
                
                print(f"Fichier '{filename}' indexé avec lemmatisation, NER et embedding.")
                files_indexed_count += 1

            except Exception as e:
                print(f"Erreur lors de l'ajout du fichier '{filename}' à l'index Whoosh : {e}")
                # Si l'erreur est liée à l'allocation, l'embedding n'a pas été créé/sauvegardé.
                # Le document sera tout de même dans Whoosh pour la recherche par mots-clés.

    writer.commit()
    
    if files_indexed_count == 0:
        print(f"Aucun fichier .txt à indexer trouvé dans '{cleaned_files_directory}'.")
        return None
    else:
        print(f"\nIndexation Whoosh avec TLN terminée. {files_indexed_count} documents indexés.")
        print(f"Embeddings de documents sauvegardés dans : {EMBEDDINGS_DIR}")
        return ix

# --- Fonction de calcul de similarité cosinus (MODIFIÉE) ---
def cosine_similarity(vec1, vec2):
    """Calcule la similarité cosinus entre deux vecteurs, gère les vecteurs nuls."""
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    
    # Si l'un des vecteurs est nul, la similarité est 0
    if norm_vec1 == 0 or norm_vec2 == 0:
        return 0.0
    
    return np.dot(vec1, vec2) / (norm_vec1 * norm_vec2)


# --- Variables et fonctions de chargement des embeddings (inchangées) ---
loaded_document_embeddings = {}

def charger_embeddings_depuis_disque():
    global loaded_document_embeddings
    loaded_document_embeddings = {} # Réinitialise avant de charger

    if not os.path.exists(EMBEDDINGS_DIR):
        print(f"Avertissement : Le dossier d'embeddings '{EMBEDDINGS_DIR}' n'existe pas. Impossible de charger les embeddings.")
        return

    print(f"Chargement des embeddings depuis : {EMBEDDINGS_DIR}...")
    for filename in os.listdir(EMBEDDINGS_DIR):
        if filename.lower().endswith(".npy"):
            # Reconstitue le nom du fichier texte original (e.g., 'doc.npy' -> 'doc.txt')
            filepath_without_ext = os.path.splitext(filename)[0] + ".txt" 
            embedding_path = os.path.join(EMBEDDINGS_DIR, filename)
            try:
                embedding = np.load(embedding_path)
                loaded_document_embeddings[filepath_without_ext] = embedding
            except Exception as e:
                print(f"Erreur lors du chargement de l'embedding '{filename}' : {e}")
    print(f"{len(loaded_document_embeddings)} embeddings chargés en mémoire pour la recherche.")


# --- Fonction rechercher_avec_whoosh (MODIFIÉE pour meilleure robustesse) ---
def rechercher_avec_whoosh(index, requete, top_n=5, search_field="content", semantic_search_weight=0.5):
    """
    Recherche une requête dans l'index Whoosh, combinant recherche par mots-clés et recherche sémantique.
    """
    if index is None:
        print("L'index Whoosh n'a pas été créé ou est vide.")
        return []

    # Charge les embeddings si ce n'est pas déjà fait
    if not loaded_document_embeddings:
        charger_embeddings_depuis_disque()
        if not loaded_document_embeddings:
            print("Aucun embedding de document disponible pour la recherche sémantique. Désactivation de la recherche sémantique.")
            semantic_search_weight = 0.0 

    print(f"\n--- Recherche pour '{requete}' (Combinée mots-clés + sémantique) ---")
    
    # --- 1. Recherche par mots-clés avec Whoosh ---
    keyword_results = {} 
    with index.searcher() as searcher:
        query_parser = QueryParser(search_field, index.schema)
        try:
            query = query_parser.parse(requete)
            results = searcher.search(query, limit=top_n*5) 
            for hit in results:
                keyword_results[hit['filepath']] = hit.score
            print(f"Recherche mots-clés Whoosh a trouvé {len(keyword_results)} résultats.")
        except Exception as e:
            print(f"Avertissement : Erreur lors de la recherche Whoosh par mots-clés pour la requête '{requete}' sur le champ '{search_field}' : {e}")
            print("Poursuite avec la recherche sémantique uniquement si possible.")
            semantic_search_weight = 1.0 # Si mots-clés échoue, on se base sur la sémantique

    # --- 2. Recherche sémantique avec fastText ---
    semantic_results = {} 
    if ft_model and loaded_document_embeddings and semantic_search_weight > 0:
        # Assurez-vous que la requête a un embedding non nul
        query_embedding = get_text_embedding(requete, max_tokens=100) # Limiter la requête aussi
        if query_embedding is not None and np.linalg.norm(query_embedding) > 0:
            for filepath, doc_emb in loaded_document_embeddings.items():
                try:
                    # Ne calcule la similarité que si l'embedding du document n'est pas nul
                    if np.linalg.norm(doc_emb) > 0:
                        sim = cosine_similarity(query_embedding, doc_emb)
                        semantic_results[filepath] = sim
                except Exception as e:
                    print(f"Avertissement : Erreur de calcul de similarité pour '{filepath}' : {e}")
            print(f"Recherche sémantique a calculé des scores pour {len(semantic_results)} documents.")
        else:
            print("Avertissement : L'embedding de la requête est nul ou vide. Désactivation de la recherche sémantique.")
            semantic_search_weight = 0.0 
    else:
        print("Avertissement : Modèle fastText ou embeddings de documents non disponibles/désactivés pour la recherche sémantique.")
        semantic_search_weight = 0.0 

    # --- 3. Fusion des résultats (pondération simple) ---
    final_scores = {}
    all_filepaths = set(keyword_results.keys()) | set(semantic_results.keys())

    if not all_filepaths:
        print("Aucun résultat combiné trouvé.")
        return []

    # Normalisation des scores
    # Utiliser 1e-6 (un très petit nombre) au lieu de 0 pour éviter la division par zéro
    max_keyword_score = max(keyword_results.values()) if keyword_results else 1e-6
    max_semantic_score = max(semantic_results.values()) if semantic_results else 1e-6
    
    if semantic_search_weight < 0: semantic_search_weight = 0
    if semantic_search_weight > 1: semantic_search_weight = 1

    for fp in all_filepaths:
        # Les scores sont mis à 0 si le document n'était pas présent dans cette recherche spécifique
        norm_kw_score = (keyword_results.get(fp, 0) / max_keyword_score) 
        norm_sem_score = (semantic_results.get(fp, 0) / max_semantic_score) 
        
        final_score = (norm_kw_score * (1 - semantic_search_weight)) + \
                      (norm_sem_score * semantic_search_weight)
        final_scores[fp] = final_score

    sorted_results = sorted(final_scores.items(), key=lambda item: item[1], reverse=True)
    
    results_list = []
    print(f"Trouvé {len(sorted_results)} résultat(s) potentiels (top {top_n} affichés) :")
    for fp, score in sorted_results[:top_n]:
        with index.searcher() as searcher: 
            doc_data = searcher.document(filepath=fp) 

            ents_info = []
            if doc_data: 
                for ent_type in ["PERSON", "ORG", "LOC", "DATE", "GPE"]:
                    if doc_data[ent_type]:
                        ents_info.append(f"{ent_type}: {doc_data[ent_type]}")
            
            results_list.append((fp, score))
            print(f"- {fp} (Score combiné: {score:.4f})")
            if ents_info:
                print(f"  Entités : {'; '.join(ents_info)}")
        
    if not results_list:
        print("Aucun résultat trouvé.")

    return results_list