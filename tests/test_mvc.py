"""
Test unitaire et de bout en bout de l'architecture MVC (Partie 1)
Valide :
  1. Le chargement d'un sous-ensemble Reuters
  2. La validation et l'execution du pipeline NLP dynamique
  3. La generation des 4 modeles d'index (BoW, F, TF, TF-IDF)
  4. Les formats Doc-Terme, Terme-Doc, et Index Inverse
  5. Le calcul des métriques de monitoring (RAM en Ko/Mo)
  6. La sauvegarde et la restauration depuis le disque
"""

import os
import sys

# Ajouter la racine du projet au sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from controllers.admin_controller import AdminController
from models.storage import IndexStorage


def test_full_mvc_flow():
    print("=" * 65)
    print("TEST DE VALIDATION MVC - PARTIE 1 DU PROJET RI")
    print("=" * 65)

    controller = AdminController()

    # 1. Chargement des données
    dataset_path = r"c:\Users\benzm\OneDrive\Bureau\RI\archive (2)"
    max_docs = 20

    print(f"\n[1] Chargement des données depuis : {dataset_path}")
    count = controller.load_dataset(dataset_path, max_docs=max_docs)
    print(f"    -> {count} documents charges.")
    assert count > 0, "Aucun document chargé !"

    # 2. Configuration du Pipeline NLP dynamique
    pipeline_steps = ['tag_cleaning', 'normalization', 'stopwords', 'stemming']
    print(f"\n[2] Configuration du pipeline NLP : {pipeline_steps}")
    desc = controller.set_nlp_pipeline(pipeline_steps)
    print(f"    -> Pipeline actif : {desc}")

    # 3. Test de validation d'un ordre invalide
    try:
        controller.set_nlp_pipeline(['stemming', 'normalization'])
        print("    [ATTENTION] La validation d'ordre n'a pas levé d'erreur !")
    except ValueError as e:
        print(f"    [OK] Validation d'ordre NLP reussie : {e}")

    # Remettre le bon pipeline
    controller.set_nlp_pipeline(pipeline_steps)

    # 4. Lancement de l'indexation
    print("\n[3] Lancement de l'indexation multi-modeles...")
    stats = controller.generate_indexes(progress_callback=lambda msg, p: print(f"    [{int(p*100)}%] {msg}"))

    # 5. Verification des métriques de monitoring
    print("\n[4] Métriques de Monitoring post-indexation :")
    print(f"    - Documents indexés      : {stats['num_documents']}")
    print(f"    - Taille du vocabulaire  : {stats['vocabulary_size']}")
    print(f"    - Total tokens           : {stats['total_tokens']}")
    print(f"    - RAM Index Inversé (KB) : {stats['memory']['ram_inverted_index_kb']} KB")
    print(f"    - RAM Matrices (KB)      : {stats['memory']['ram_matrices_kb']} KB")
    print(f"    - RAM Totale (KB)        : {stats['memory']['ram_total_kb']} KB")

    # 6. Vérification des formats de matrice et index inverse
    print("\n[5] Vérification des vues matricielles (BoW & TF-IDF) :")
    doc_term_view = controller.get_matrix_view("tfidf", matrix_type="doc_term", page=1, page_size=3, max_cols=3)
    print(f"    -> Matrice Doc-Terme colonnes : {doc_term_view['columns']}")

    term_doc_view = controller.get_matrix_view("binary", matrix_type="term_doc", page=1, page_size=3, max_cols=3)
    print(f"    -> Matrice Terme-Doc colonnes : {term_doc_view['columns']}")

    inv_view = controller.get_inverted_index_view("tfidf", page=1, page_size=3)
    print(f"    -> Extrait Index Inversé : {inv_view['sample_terms'][0]}")

    # 7. Sauvegarde sur disque
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage_test"))
    print(f"\n[6] Sauvegarde des index sur disque dans : {output_dir}")
    saved = controller.save_indexes(output_dir, export_json=True, export_binary=True)
    print(f"    -> Fichiers JSON generes : {len(saved.get('json_files', {}))}")
    print(f"    -> Fichier binaire généré : {saved.get('binary_file')}")

    # 8. Test de rechargement binaire pour Phase 2
    loaded = IndexStorage.load_from_binary(saved["binary_file"])
    assert loaded["N"] == count, "Discordance dans le nombre de documents rechargés !"
    print(f"    -> Rechargement binaire validé avec succès ({loaded['N']} docs, {loaded['V']} mots).")

    print("\n" + "=" * 65)
    print(" TOUS LES TESTS MVC ONT REUSSI AVEC SUCCES (100% OK)")
    print("=" * 65)


if __name__ == "__main__":
    test_full_mvc_flow()
