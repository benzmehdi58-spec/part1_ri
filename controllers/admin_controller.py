"""
Module AdminController (Contrôleur MVC)
Coordonne le flux de travail de l'administrateur :
  1. Chargement des donnees
  2. Configuration dynamique du pipeline NLP
  3. Generation et construction des index multi-modeles
  4. Calcul et exposition des métriques (Monitoring)
  5. Sauvegarde / Sérialisation sur le disque
"""

from typing import List, Dict, Optional, Any, Callable
from models.parser import ReutersParser
from models.nlp import NLPPipeline
from models.indexer import IndexingEngine
from models.storage import IndexStorage


class AdminController:
    """
    Contrôleur central pour l'interface Administrateur.
    Permet à n'importe quelle vue (GUI Desktop, Web App, CLI) d'interagir
    avec la couche métier sans couplage fort.
    """

    def __init__(self):
        self.raw_documents: List[Dict[str, str]] = []
        self.pipeline: Optional[NLPPipeline] = None
        self.processed_corpus: Optional[Dict[str, List[str]]] = None
        self.engine: Optional[IndexingEngine] = None
        self.last_stats: Optional[Dict[str, Any]] = None

    def load_dataset(self, path: str, max_docs: Optional[int] = None) -> int:
        """
        Charge les documents depuis un fichier ou un dossier.
        :return: Nombre de documents chargés.
        """
        self.raw_documents = ReutersParser.load_corpus(path, max_docs=max_docs)
        self.processed_corpus = None
        self.engine = None
        self.last_stats = None
        return len(self.raw_documents)

    def set_nlp_pipeline(self, steps: List[str]) -> str:
        """
        Configure les étapes du pipeline NLP dans l'ordre spécifié.
        Lève une ValueError si l'ordre ou les étapes sont incohérentes.
        :return: Description lisible de la chaîne (ex: 'tag_cleaning -> normalization -> ...')
        """
        self.pipeline = NLPPipeline(steps=steps)
        return self.pipeline.describe()

    def generate_indexes(self, progress_callback: Optional[Callable[[str, float], None]] = None) -> Dict[str, Any]:
        """
        Lance la chaîne complète : Prétraitement NLP + Indexation multi-modèles.
        :param progress_callback: Fonction callback(status_msg, progress_ratio) pour les barres de progression de la vue.
        :return: Dictionnaire des métriques post-indexation.
        """
        if not self.raw_documents:
            raise ValueError("Aucun document chargé. Veuillez charger un dataset au préalable.")

        if self.pipeline is None:
            # Pipeline par défaut si non spécifié
            self.pipeline = NLPPipeline()

        if progress_callback:
            progress_callback("Prétraitement NLP en cours...", 0.2)

        # 1. Prétraitement
        corpus_dict = {doc["doc_id"]: doc["raw_text"] for doc in self.raw_documents}
        self.processed_corpus = self.pipeline.fit_transform(corpus_dict)

        if progress_callback:
            progress_callback("Génération des index multi-modèles...", 0.6)

        # 2. Indexation
        self.engine = IndexingEngine(self.processed_corpus)

        if progress_callback:
            progress_callback("Calcul des métriques de monitoring...", 0.9)

        # 3. Statistiques & Mémoire
        self.last_stats = self.engine.stats()

        if progress_callback:
            progress_callback("Indexation terminée avec succès.", 1.0)

        return self.last_stats

    def get_metrics(self) -> Dict[str, Any]:
        """Retourne les métriques calculées pour affichage dans la vue."""
        if self.engine is None or self.last_stats is None:
            raise ValueError("Les index n'ont pas encore été générés.")
        return self.last_stats

    def get_matrix_view(self, model: str, matrix_type: str = "doc_term",
                        page: int = 1, page_size: int = 20, max_cols: int = 10,
                        filter_query: Optional[str] = None) -> Dict[str, Any]:
        """
        Prépare une vue paginée d'une matrice pour affichage tabulaire dans l'UI.
        :param matrix_type: 'doc_term' (mots en lignes, docs en colonnes) ou 'term_doc' (docs en lignes, mots en colonnes)
        """
        if self.engine is None:
            raise ValueError("Les index n'ont pas encore été générés.")

        if matrix_type == "doc_term":
            mat = self.engine.get_doc_term_matrix(model)
            all_terms = self.engine.vocabulary
            if filter_query:
                q = filter_query.lower()
                all_terms = [t for t in all_terms if q in t.lower()]

            total_rows = len(all_terms)
            total_pages = max(1, (total_rows + page_size - 1) // page_size)
            start = (page - 1) * page_size
            end = start + page_size

            row_keys = all_terms[start:end]
            col_keys = self.engine.doc_ids[:max_cols]
            rows = []
            for term in row_keys:
                row_data = {"Terme": term}
                for doc_id in col_keys:
                    row_data[f"Doc {doc_id}"] = mat[term].get(doc_id, 0.0)
                rows.append(row_data)
            return {
                "type": "Matrice Document-Terme (Lignes=Mots, Colonnes=Docs)",
                "columns": ["Terme"] + [f"Doc {d}" for d in col_keys],
                "rows": rows,
                "total_rows": total_rows,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }
        elif matrix_type == "term_doc":
            mat = self.engine.get_term_doc_matrix(model)
            all_docs = self.engine.doc_ids
            total_rows = len(all_docs)
            total_pages = max(1, (total_rows + page_size - 1) // page_size)
            start = (page - 1) * page_size
            end = start + page_size

            row_keys = all_docs[start:end]
            col_keys = [t for t in self.engine.vocabulary if self.engine.df[t] < self.engine.N]
            if filter_query:
                q = filter_query.lower()
                col_keys = [t for t in col_keys if q in t.lower()]
            col_keys = (col_keys or self.engine.vocabulary)[:max_cols]

            rows = []
            for doc_id in row_keys:
                row_data = {"Doc ID": f"Doc {doc_id}"}
                for term in col_keys:
                    row_data[term] = mat[doc_id].get(term, 0.0)
                rows.append(row_data)
            return {
                "type": "Matrice Terme-Document (Lignes=Docs, Colonnes=Mots)",
                "columns": ["Doc ID"] + col_keys,
                "rows": rows,
                "total_rows": total_rows,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }
        else:
            raise ValueError(f"Type de matrice inconnu : '{matrix_type}'")

    def get_inverted_index_view(self, model: str, page: int = 1, page_size: int = 25,
                                filter_query: Optional[str] = None) -> Dict[str, Any]:
        """Prépare un extrait paginé de l'index inversé pour affichage dans l'UI."""
        if self.engine is None:
            raise ValueError("Les index n'ont pas encore été générés.")

        inv = self.engine.get_inverted_index(model)
        all_terms = self.engine.vocabulary
        if filter_query:
            q = filter_query.lower()
            all_terms = [t for t in all_terms if q in t.lower()]

        total_rows = len(all_terms)
        total_pages = max(1, (total_rows + page_size - 1) // page_size)
        start = (page - 1) * page_size
        end = start + page_size

        terms_subset = all_terms[start:end]
        result = []
        for term in terms_subset:
            postings = inv.get(term, [])
            postings_str = ", ".join([f"(Doc {d}: {w})" for d, w in postings[:8]])
            if len(postings) > 8:
                postings_str += f", ... (+{len(postings) - 8})"
            result.append({
                "terme": term,
                "df": len(postings),
                "postings": postings_str
            })
        return {
            "model": model,
            "total_terms": total_rows,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "sample_terms": result
        }

    def save_indexes(self, output_dir: str, export_json: bool = True, export_binary: bool = True) -> Dict[str, Any]:
        """
        Sauvegarde les structures générées sur le disque local.
        """
        if self.engine is None:
            raise ValueError("Aucun index généré à sauvegarder.")

        results = {}
        metadata = {
            "pipeline_steps": self.pipeline.steps if self.pipeline else [],
            "stats": self.last_stats
        }

        if export_json:
            saved_json = IndexStorage.save_to_json(self.engine, output_dir, metadata=metadata)
            results["json_files"] = saved_json

        if export_binary:
            bin_path = f"{output_dir}/reuters_index_bundle.pkl"
            saved_bin = IndexStorage.save_to_binary(self.engine, bin_path, metadata=metadata)
            results["binary_file"] = saved_bin

        return results
