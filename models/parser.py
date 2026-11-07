"""
Module Parser (Reuters-21578) - Implementation From Scratch
Sans bibliothèques XML ni module regex (re).
"""

import os
import csv
from typing import List, Dict, Optional


class ReutersParser:
    """
    Parseur pour le corpus Reuters-21578.
    Supporte les formats .sgm (SGML brut) et .csv.
    """

    @staticmethod
    def _extract_tag_content(text: str, tag_name: str) -> str:
        """
        Extrait le contenu textuel entre <TAG> et </TAG> (insensible a la casse).
        """
        open_tag = f"<{tag_name}>".lower()
        close_tag = f"</{tag_name}>".lower()
        lower = text.lower()
        start = lower.find(open_tag)
        if start == -1:
            return ""
        content_start = start + len(open_tag)
        end = lower.find(close_tag, content_start)
        if end == -1:
            return text[content_start:].strip()
        return text[content_start:end].strip()

    @staticmethod
    def _extract_attr(header: str, attr_name: str) -> str:
        """
        Extrait la valeur d'un attribut SGML (ex: NEWID="123") sans regex.
        """
        key = f"{attr_name.lower()}="
        lower = header.lower()
        pos = lower.find(key)
        if pos == -1:
            return ""
        pos += len(key)
        if pos < len(header) and header[pos] in ('"', "'"):
            quote = header[pos]
            end = header.find(quote, pos + 1)
            if end != -1:
                return header[pos + 1:end].strip()
        else:
            end = pos
            while end < len(header) and header[end] not in (' ', '>', '\t', '\n'):
                end += 1
            return header[pos:end].strip()
        return ""

    @classmethod
    def parse_sgml_text(cls, text: str) -> List[Dict[str, str]]:
        """
        Parse une chaine de texte SGML Reuters et retourne la liste des documents.
        """
        documents = []
        lower = text.lower()
        idx = 0
        auto_id = 1

        while True:
            start_reuters = lower.find("<reuters", idx)
            if start_reuters == -1:
                break
            header_end = lower.find(">", start_reuters)
            if header_end == -1:
                break
            end_reuters = lower.find("</reuters>", header_end)
            if end_reuters == -1:
                block_content = text[header_end + 1:]
                idx = len(text)
            else:
                block_content = text[header_end + 1:end_reuters]
                idx = end_reuters + len("</reuters>")

            header = text[start_reuters:header_end + 1]
            newid = cls._extract_attr(header, "newid")
            doc_id = newid if newid else str(auto_id)
            auto_id += 1

            title = cls._extract_tag_content(block_content, "title")
            body = cls._extract_tag_content(block_content, "body")
            date = cls._extract_tag_content(block_content, "date")

            parts = [p for p in [title, body] if p]
            full_text = "\n".join(parts).strip()

            documents.append({
                "doc_id": str(doc_id),
                "title": title,
                "body": body,
                "date": date,
                "raw_text": full_text
            })

        return documents

    @classmethod
    def parse_sgml_file(cls, filepath: str) -> List[Dict[str, str]]:
        """Charge un fichier .sgm en testant plusieurs encodages courants."""
        for enc in ("latin-1", "utf-8", "cp1252"):
            try:
                with open(filepath, "r", encoding=enc, errors="replace") as f:
                    content = f.read()
                return cls.parse_sgml_text(content)
            except Exception:
                continue
        raise IOError(f"Impossible de lire le fichier : {filepath}")

    @classmethod
    def parse_csv_file(cls, filepath: str, max_docs: Optional[int] = None) -> List[Dict[str, str]]:
        """Charge un fichier CSV Reuters (ex: reuters21578_news.csv)."""
        documents = []
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                body = (row.get("topic_body") or row.get("body") or "").strip()
                title = (row.get("title") or "").strip()
                if not body and not title:
                    continue
                doc_id = row.get("newID") or row.get("doc_id") or str(count + 1)
                date = row.get("document_date") or row.get("date") or ""
                parts = [p for p in [title, body] if p]
                full_text = "\n".join(parts).strip()
                documents.append({
                    "doc_id": str(doc_id),
                    "title": title,
                    "body": body,
                    "date": date,
                    "raw_text": full_text
                })
                count += 1
                if max_docs is not None and count >= max_docs:
                    break
        return documents

    @classmethod
    def load_corpus(cls, path: str, max_docs: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Point d'entree unifie : charge les documents depuis un fichier (.sgm / .csv)
        ou un dossier complet.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Chemin introuvable : {path}")

        if os.path.isfile(path):
            if path.lower().endswith(".csv"):
                return cls.parse_csv_file(path, max_docs=max_docs)
            else:
                docs = cls.parse_sgml_file(path)
                return docs[:max_docs] if max_docs else docs

        elif os.path.isdir(path):
            # Priorite aux fichiers .sgm si presents
            sgm_files = [f for f in os.listdir(path) if f.lower().endswith(".sgm")]
            if sgm_files:
                all_docs = []
                for fname in sorted(sgm_files):
                    fpath = os.path.join(path, fname)
                    docs = cls.parse_sgml_file(fpath)
                    all_docs.extend(docs)
                    if max_docs and len(all_docs) >= max_docs:
                        return all_docs[:max_docs]
                return all_docs

            # Sinon recherche de fichiers .csv
            csv_candidates = [f for f in os.listdir(path) if f.lower().endswith(".csv")]
            if csv_candidates:
                target_csv = "reuters21578_news.csv" if "reuters21578_news.csv" in csv_candidates else csv_candidates[0]
                return cls.parse_csv_file(os.path.join(path, target_csv), max_docs=max_docs)

        return []
