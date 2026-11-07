"""
Module IndexingEngine - Moteur d'indexation Multi-Modeles From Scratch
Genere les 4 modeles : BoW, Frequence brute, TF normalise, TF-IDF
Produit les 3 structures requises :
  - Matrice Document-Terme (Lignes = Mots, Colonnes = Documents)
  - Matrice Terme-Document (Lignes = Documents, Colonnes = Mots)
  - Liste Inversee / Posting Lists (Terme -> [(Doc_ID, Poids)])
Mesure la consommation memoire (RAM) from scratch.
"""

import math
import sys
import collections
from typing import Dict, List, Tuple, Any


class IndexingEngine:
    """
    Moteur d'indexation vectoriel et inversé multi-modèles.
    """

    MODELS = ['binary', 'raw_freq', 'tf_norm', 'tfidf']

    def __init__(self, processed_docs: Dict[str, List[str]]):
        """
        :param processed_docs: dict {doc_id -> list_of_tokens}
        """
        self.docs = processed_docs
        self.N = len(processed_docs)

        # Tri naturel des doc_ids (numerique si possible)
        self.doc_ids = sorted(
            list(processed_docs.keys()),
            key=lambda x: int(x) if x.isdigit() else x
        )

        # 1. Vocabulaire unique
        vocab_set = set()
        for tokens in self.docs.values():
            vocab_set.update(tokens)
        self.vocabulary = sorted(list(vocab_set))
        self.V = len(self.vocabulary)

        # 2. Frequences locales par document : {doc_id -> Counter(terme: count)}
        self.term_freqs = {
            d: collections.Counter(self.docs[d])
            for d in self.doc_ids
        }

        # 3. max_tf par document pour normalisation
        self.max_tf = {}
        for d in self.doc_ids:
            counts = self.term_freqs[d].values()
            self.max_tf[d] = max(counts) if counts else 1

        # 4. Document Frequency (df) : nombre de documents contenant chaque terme
        self.df = collections.Counter()
        for d in self.doc_ids:
            for term in self.term_freqs[d]:
                self.df[term] += 1

        # 5. Structures d'indexation multi-modeles
        self.doc_term_matrices: Dict[str, Dict[str, Dict[str, float]]] = {}
        self.term_doc_matrices: Dict[str, Dict[str, Dict[str, float]]] = {}
        self.inverted_indexes: Dict[str, Dict[str, List[Tuple[str, float]]]] = {}

        self._build_all_models()

    def _build_all_models(self):
        """Construit simultanément les matrices et les index inversés creux (sparse)."""
        idf = {
            t: (math.log10(self.N / self.df[t]) if self.df[t] > 0 else 0.0)
            for t in self.vocabulary
        }

        for model in self.MODELS:
            inv_index: Dict[str, List[Tuple[str, float]]] = {t: [] for t in self.vocabulary}
            term_doc: Dict[str, Dict[str, float]] = {d: {} for d in self.doc_ids}

            for d in self.doc_ids:
                m_tf = self.max_tf[d]
                tf_map = self.term_freqs[d]
                for term, tf in tf_map.items():
                    if tf <= 0:
                        continue
                    if model == 'binary':
                        w = 1.0
                    elif model == 'raw_freq':
                        w = float(tf)
                    elif model == 'tf_norm':
                        w = tf / m_tf
                    elif model == 'tfidf':
                        w = (tf / m_tf) * idf[term]

                    w_val = round(w, 6)
                    term_doc[d][term] = w_val
                    inv_index[term].append((d, w_val))

            # Trier les postings par poids decroissant
            for term in self.vocabulary:
                inv_index[term].sort(key=lambda x: x[1], reverse=True)

            self.inverted_indexes[model] = inv_index
            self.term_doc_matrices[model] = term_doc

            # Matrice Document-Terme creuse (Lignes = Mots, Colonnes = Documents)
            doc_term: Dict[str, Dict[str, float]] = {t: {} for t in self.vocabulary}
            for term in self.vocabulary:
                for d, w in inv_index[term]:
                    doc_term[term][d] = w
            self.doc_term_matrices[model] = doc_term

    def _check_model(self, model: str):
        if model not in self.MODELS:
            raise ValueError(f"Modèle inconnu : '{model}'. Choisir parmi : {self.MODELS}")

    def get_doc_term_matrix(self, model: str) -> Dict[str, Dict[str, float]]:
        """Matrice Document-Terme : {terme -> {doc_id -> poids}}"""
        self._check_model(model)
        return self.doc_term_matrices[model]

    def get_term_doc_matrix(self, model: str) -> Dict[str, Dict[str, float]]:
        """Matrice Terme-Document : {doc_id -> {terme -> poids}}"""
        self._check_model(model)
        return self.term_doc_matrices[model]

    def get_inverted_index(self, model: str) -> Dict[str, List[Tuple[str, float]]]:
        """Index Inverse : {terme -> [(doc_id, poids), ...]}"""
        self._check_model(model)
        return self.inverted_indexes[model]

    def get_postings(self, model: str, term: str) -> List[Tuple[str, float]]:
        """Retourne la posting list d'un terme spécifique."""
        self._check_model(model)
        t_clean = term.lower().strip()
        return self.inverted_indexes[model].get(t_clean, [])

    @staticmethod
    def _deep_sizeof(obj: Any, seen: set = None) -> int:
        """
        Calcul récursif from scratch de l'empreinte mémoire d'un objet en RAM.
        Supporte dictionnaires, listes, tuples, ensembles et types de base.
        """
        if seen is None:
            seen = set()
        obj_id = id(obj)
        if obj_id in seen:
            return 0
        seen.add(obj_id)
        size = sys.getsizeof(obj)
        if isinstance(obj, dict):
            size += sum(
                IndexingEngine._deep_sizeof(k, seen) + IndexingEngine._deep_sizeof(v, seen)
                for k, v in obj.items()
            )
        elif isinstance(obj, (list, tuple, set, frozenset)):
            size += sum(IndexingEngine._deep_sizeof(item, seen) for item in obj)
        return size

    def memory_footprint(self) -> Dict[str, float]:
        """
        Calcule la taille occupée en mémoire (RAM) par structure (en Ko / Mo).
        Conforme a la section 2.2.e du cahier des charges (Matrice vs Liste Inversée).
        """
        def to_kb(bytes_val):
            return round(bytes_val / 1024, 2)

        def to_mb(bytes_val):
            return round(bytes_val / (1024 * 1024), 3)

        mem_inv_bytes = sum(self._deep_sizeof(self.inverted_indexes[m]) for m in self.MODELS)
        mem_matrices_bytes = sum(
            self._deep_sizeof(self.doc_term_matrices[m]) + self._deep_sizeof(self.term_doc_matrices[m])
            for m in self.MODELS
        )
        total_bytes = mem_inv_bytes + mem_matrices_bytes

        return {
            "ram_inverted_index_kb": to_kb(mem_inv_bytes),
            "ram_inverted_index_mb": to_mb(mem_inv_bytes),
            "ram_matrices_kb": to_kb(mem_matrices_bytes),
            "ram_matrices_mb": to_mb(mem_matrices_bytes),
            "ram_total_kb": to_kb(total_bytes),
            "ram_total_mb": to_mb(total_bytes)
        }

    def stats(self) -> Dict[str, Any]:
        """Statistiques complètes et métriques d'évaluation post-indexation."""
        mem = self.memory_footprint()
        total_tokens = sum(len(t) for t in self.docs.values())
        return {
            "num_documents": self.N,
            "vocabulary_size": self.V,
            "total_tokens": total_tokens,
            "avg_tokens_per_doc": round(total_tokens / max(self.N, 1), 2),
            "models": self.MODELS,
            "memory": mem
        }
