# Reuters-21578 Information Retrieval (IR) System - Part 1

> **Module :** Recherche d'Information (RI) - S9 Ingénierie IA  
> **Phase 1 :** Interface Administrateur d'Indexation Dynamique  
> **Implementation :** 100% From Scratch (Standard Python Library only, no external NLP/XML/regex libraries)

---

## 🏛️ Project Architecture (MVC)

```
ri part1/
│
├── models/                           # 🧠 [M]ODEL (Business Logic & Algorithms From Scratch)
│   ├── parser.py                     # SGML/XML and CSV Reuters-21578 parser (no XML/regex)
│   ├── nlp.py                        # Dynamic 5-step NLP pipeline (cleaning, norm, stopwords, stemming, lemma)
│   ├── indexer.py                    # Multi-model indexing (BoW, Frequency, TF norm, TF-IDF) + Matrices & Postings
│   └── storage.py                    # Disk serialization (JSON exports & binary bundle .pkl)
│
├── controllers/                      # 🎮 [C]ONTROLLER (Orchestration Layer)
│   └── admin_controller.py           # Coordinates ingestion, pipeline validation, indexing, and memory monitoring
│
├── backend/                          # 🌐 REST API Backend (FastAPI)
│   └── app.py                        # Exposes the controller to the web frontend (CORS enabled)
│
├── frontend/                         # ⚛️ [V]IEW (Figma UI in React 19 + Vite + Tailwind CSS)
│   ├── src/
│   │   ├── App.tsx                   # Interactive admin dashboard wired to the FastAPI backend
│   │   └── index.css                 # Clean engineering aesthetic
│   └── package.json
│
├── run_app.py                        # Single command to launch Backend + Frontend together
├── run_backend.py                    # Launches the FastAPI server standalone
└── tests/
    └── test_mvc.py                   # Automated end-to-end verification test suite
```

---

## 🚀 Quick Start

### 1. Launch Everything (Backend + Frontend)
From the root directory (`ri part1`):
```bash
py run_app.py
```
- **Web App (UI) :** [http://localhost:5173](http://localhost:5173)
- **Backend API Docs (Swagger) :** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📋 Features Checklist (Part 1 Requirements)

- [x] **Dataset Selection :** Loads Reuters-21578 collections (.csv or .sgm) from local disk.
- [x] **Dynamic NLP Pipeline :**
  - Tag Cleaning (SGML/XML tags & entities)
  - Normalization (lowercase, strip punctuation, tokenization)
  - Stopwords Removal (English + Reuters noise words)
  - Stemming (Porter-style suffix stripping from scratch)
  - Lemmatization (Custom dictionary lookup)
  - Re-orderable execution sequence with order validation rules.
- [x] **Indexing Trigger :** "Generate Indexes" button executes the whole workflow in the background.
- [x] **Multi-Model Generation :**
  - BoW (Binary 0/1)
  - F (Raw frequency counts)
  - TF (Normalized term frequency: $tf / \max\_tf$)
  - TF-IDF ($TF \times IDF$ with $\log_{10}(N / df)$)
- [x] **Three Output Data Formats per Model :**
  - Document-Term Matrix (Rows = Words, Columns = Documents)
  - Term-Document Matrix (Rows = Documents, Columns = Words)
  - Inverted Index / Posting Lists (`term -> [(doc_id, weight), ...]`)
- [x] **Monitoring Dashboard :**
  - Vocabulary dimension ($V$)
  - Indexed document count ($N$)
  - Total and average tokens per document
  - Real RAM footprint measurement (Matrices vs Inverted Index in KB / MB)
- [x] **Serialization / Save to Disk :** Exports 12 JSON index files + 1 metadata file + 1 unified binary bundle (`.pkl`) ready for Phase 2.
- [x] **Strict "From Scratch" Compliance :** 0 external NLP libraries (No NLTK, spaCy, scikit-learn, gensim, or `re` regex).
