"""
Module IndexStorage - Sérialisation et Sauvegarde sur disque
Permet a l'administrateur de sauvegarder les index générés sur le disque
(formats JSON et binaire pickle) pour être réutilisés en Phase 2 sans recalcul.
"""

import os
import json
import pickle
from typing import Dict, Any, Optional
from .indexer import IndexingEngine


class IndexStorage:
    """
    Gestionnaire de persistance pour les index de recherche.
    """

    @staticmethod
    def save_to_json(engine: IndexingEngine, output_dir: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        Sauvegarde tous les index et métadonnées en fichiers JSON.
        """
        os.makedirs(output_dir, exist_ok=True)
        saved_files = {}

        # 1. Sauvegarde des métadonnées générales
        meta_payload = {
            "num_documents": engine.N,
            "vocabulary_size": engine.V,
            "doc_ids": engine.doc_ids,
            "vocabulary": engine.vocabulary,
            "models": engine.MODELS,
            "custom_metadata": metadata or {}
        }
        meta_path = os.path.join(output_dir, "metadata.json")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta_payload, f, ensure_ascii=False, indent=2)
        saved_files["metadata"] = meta_path

        # 2. Sauvegarde par modèle
        for model in engine.MODELS:
            # Inverted index
            inv_path = os.path.join(output_dir, f"inverted_index_{model}.json")
            with open(inv_path, "w", encoding="utf-8") as f:
                json.dump(engine.get_inverted_index(model), f, ensure_ascii=False, indent=2)
            saved_files[f"inverted_{model}"] = inv_path

            # Doc-Term matrix
            doc_term_path = os.path.join(output_dir, f"matrix_doc_term_{model}.json")
            with open(doc_term_path, "w", encoding="utf-8") as f:
                json.dump(engine.get_doc_term_matrix(model), f, ensure_ascii=False, indent=2)
            saved_files[f"doc_term_{model}"] = doc_term_path

            # Term-Doc matrix
            term_doc_path = os.path.join(output_dir, f"matrix_term_doc_{model}.json")
            with open(term_doc_path, "w", encoding="utf-8") as f:
                json.dump(engine.get_term_doc_matrix(model), f, ensure_ascii=False, indent=2)
            saved_files[f"term_doc_{model}"] = term_doc_path

        return saved_files

    @staticmethod
    def save_to_binary(engine: IndexingEngine, filepath: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Sauvegarde l'ensemble du moteur d'indexation dans un fichier binaire unique (.pkl).
        """
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        payload = {
            "metadata": metadata or {},
            "doc_ids": engine.doc_ids,
            "vocabulary": engine.vocabulary,
            "N": engine.N,
            "V": engine.V,
            "MODELS": engine.MODELS,
            "inverted_indexes": engine.inverted_indexes,
            "doc_term_matrices": engine.doc_term_matrices,
            "term_doc_matrices": engine.term_doc_matrices,
            "df": dict(engine.df),
            "max_tf": engine.max_tf
        }
        with open(filepath, "wb") as f:
            pickle.dump(payload, f, protocol=pickle.HIGHEST_PROTOCOL)
        return filepath

    @staticmethod
    def load_from_binary(filepath: str) -> Dict[str, Any]:
        """
        Charge un index binaire pour réutilisation immédiate en Phase 2.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Fichier d'index introuvable : {filepath}")
        with open(filepath, "rb") as f:
            return pickle.load(f)
