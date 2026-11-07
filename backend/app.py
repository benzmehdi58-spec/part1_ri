"""
FastAPI Backend Server for Information Retrieval (RI) - Part 1
Exposes the Admin Controller via REST API for React / Web UI.
"""

import os
import sys
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure project root is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from controllers.admin_controller import AdminController

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize FastAPI application
app = FastAPI(
    title="Reuters-21578 IR Admin API",
    description="REST API for Dynamic NLP Pipeline & Multi-Model Indexing Engine",
    version="1.0.0"
)

# Enable CORS for React frontend (Vite defaults to 5173, CRA to 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global controller singleton
controller = AdminController()

# Default dataset path suggestion
DEFAULT_DATASET_PATH = r"c:\Users\benzm\OneDrive\Bureau\RI\archive (2)"


# =============================================================================
# Request / Response Schemas
# =============================================================================

class LoadDatasetRequest(BaseModel):
    path: str = Field(default=DEFAULT_DATASET_PATH, description="Path to .sgm file, .csv file, or directory")
    max_docs: Optional[int] = Field(default=50, description="Max documents to load (None for all)")


class ConfigurePipelineRequest(BaseModel):
    steps: List[str] = Field(
        default=["tag_cleaning", "normalization", "stopwords", "stemming"],
        description="Ordered list of NLP steps to apply"
    )


class SaveIndexesRequest(BaseModel):
    output_dir: Optional[str] = Field(
        default=os.path.join(BASE_DIR, "saved_indexes"),
        description="Target directory to save index files"
    )
    export_json: bool = Field(default=True, description="Save full JSON index files")
    export_binary: bool = Field(default=True, description="Save binary .pkl bundle for Phase 2")


# =============================================================================
# API Endpoints
# =============================================================================

@app.get("/api")
def api_root():
    return {
        "status": "online",
        "service": "Reuters IR Admin API (Part 1)",
        "docs_url": "/docs",
        "default_dataset_path": DEFAULT_DATASET_PATH
    }


@app.get("/api/status")
def get_status():
    """Returns the current state of the backend controller."""
    return {
        "documents_loaded": len(controller.raw_documents),
        "pipeline_configured": controller.pipeline is not None,
        "pipeline_steps": controller.pipeline.steps if controller.pipeline else [],
        "pipeline_description": controller.pipeline.describe() if controller.pipeline else None,
        "indexes_generated": controller.engine is not None,
        "available_models": ["binary", "raw_freq", "tf_norm", "tfidf"],
    }


@app.get("/api/pipeline/available-steps")
def get_available_steps():
    """Lists all available NLP pipeline steps and ordering rules."""
    return {
        "steps": [
            {
                "id": "tag_cleaning",
                "label": "Tag Cleaning",
                "description": "Removes SGML/XML tags and HTML control entities from Reuters text.",
                "type": "text_preprocessor"
            },
            {
                "id": "normalization",
                "label": "Normalization & Tokenization",
                "description": "Converts to lowercase, strips punctuation, and tokens split.",
                "type": "tokenizer"
            },
            {
                "id": "stopwords",
                "label": "Stopwords Removal",
                "description": "Removes frequent English & Reuters-specific noise words.",
                "type": "token_filter"
            },
            {
                "id": "stemming",
                "label": "Stemming (Porter-style)",
                "description": "Suffix-stripping rule-based algorithm coded from scratch.",
                "type": "token_reducer"
            },
            {
                "id": "lemmatization",
                "label": "Lemmatization",
                "description": "Dictionary-based canonical form lookup.",
                "type": "token_reducer"
            }
        ],
        "default_order": ["tag_cleaning", "normalization", "stopwords", "stemming"],
        "rules": [
            "Tag cleaning must run before normalization.",
            "Normalization is required before stopwords, stemming, or lemmatization.",
            "Steps cannot be duplicated."
        ]
    }


@app.post("/api/dataset/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    max_docs: Optional[int] = Form(None)
):
    """
    Uploads a Reuters collection file (.csv or .sgm) directly from local disk.
    Parses documents and stores them in the controller.
    """
    try:
        filename = file.filename or "reuters_collection.csv"
        saved_path = os.path.join(UPLOAD_DIR, filename)

        with open(saved_path, "wb") as f:
            while chunk := await file.read(1024 * 1024):
                f.write(chunk)

        count = controller.load_dataset(saved_path, max_docs=max_docs)
        if count == 0:
            raise HTTPException(status_code=400, detail="No valid documents found in the uploaded file.")

        file_size_mb = round(os.path.getsize(saved_path) / (1024 * 1024), 2)

        return {
            "success": True,
            "message": f"Successfully loaded {count} documents from uploaded file '{filename}'.",
            "count": count,
            "filename": filename,
            "size_mb": file_size_mb
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/dataset/load")
def load_dataset(req: LoadDatasetRequest):
    """Loads Reuters documents from the given path."""
    try:
        count = controller.load_dataset(req.path, max_docs=req.max_docs)
        if count == 0:
            raise HTTPException(status_code=400, detail="No documents found at the specified path.")
        
        # Sample document previews (first 5)
        previews = [
            {
                "doc_id": doc["doc_id"],
                "title": doc["title"] or "(Untitled)",
                "date": doc["date"],
                "body_snippet": (doc["body"][:120] + "...") if doc["body"] else ""
            }
            for doc in controller.raw_documents[:5]
        ]

        return {
            "success": True,
            "message": f"Successfully loaded {count} documents.",
            "count": count,
            "previews": previews
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/dataset/documents")
def get_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50)
):
    """Returns paginated documents loaded in the corpus."""
    total = len(controller.raw_documents)
    start = (page - 1) * page_size
    end = start + page_size
    docs = controller.raw_documents[start:end]
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "documents": [
            {
                "doc_id": d["doc_id"],
                "title": d["title"] or "(Untitled Article)",
                "date": d["date"],
                "body": d["body"]
            }
            for d in docs
        ]
    }


@app.post("/api/pipeline/configure")
def configure_pipeline(req: ConfigurePipelineRequest):
    """Configures and validates the dynamic NLP pipeline."""
    try:
        desc = controller.set_nlp_pipeline(req.steps)
        return {
            "success": True,
            "pipeline": req.steps,
            "description": desc
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Pipeline error: {str(e)}")


@app.post("/api/indexes/generate")
def generate_indexes():
    """
    Executes the NLP pipeline on the corpus and builds all 4 indexing models:
    BoW, Frequency, TF normalized, and TF-IDF in all 3 formats.
    """
    if not controller.raw_documents:
        raise HTTPException(status_code=400, detail="Please load a dataset before generating indexes.")

    try:
        metrics = controller.generate_indexes()
        return {
            "success": True,
            "message": "All indexes and matrices generated successfully.",
            "metrics": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing error: {str(e)}")


@app.get("/api/indexes/metrics")
def get_metrics():
    """Returns memory footprint (RAM) and index metrics post-generation."""
    try:
        return controller.get_metrics()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/indexes/matrix")
def get_matrix(
    model: str = Query("tfidf", description="Model: binary, raw_freq, tf_norm, tfidf"),
    matrix_type: str = Query("doc_term", description="doc_term or term_doc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    max_cols: int = Query(10, ge=1, le=50),
    filter: Optional[str] = Query(None, description="Term filter")
):
    """Returns paginated matrix data suitable for table rendering in the UI."""
    try:
        view = controller.get_matrix_view(
            model=model,
            matrix_type=matrix_type,
            page=page,
            page_size=page_size,
            max_cols=max_cols,
            filter_query=filter
        )
        return view
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/indexes/inverted")
def get_inverted_index(
    model: str = Query("tfidf", description="Model: binary, raw_freq, tf_norm, tfidf"),
    search_term: Optional[str] = Query(None, description="Optional search term to inspect"),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200)
):
    """Returns inverted index posting lists."""
    if controller.engine is None:
        raise HTTPException(status_code=400, detail="Indexes have not been generated yet.")

    try:
        if search_term and search_term.strip():
            term_clean = search_term.strip().lower()
            postings = controller.engine.get_postings(model, term_clean)
            return {
                "model": model,
                "term": term_clean,
                "document_frequency": len(postings),
                "postings": [{"doc_id": d, "weight": w} for d, w in postings],
                "sample_terms": [
                    {
                        "terme": term_clean,
                        "df": len(postings),
                        "postings": ", ".join([f"(Doc {d}: {w})" for d, w in postings[:10]]) or "Not present in corpus"
                    }
                ]
            }
        else:
            return controller.get_inverted_index_view(model, page=page, page_size=page_size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/indexes/save")
def save_indexes(req: SaveIndexesRequest):
    """Saves the generated indexes to local disk (JSON and/or binary)."""
    try:
        saved = controller.save_indexes(
            output_dir=req.output_dir,
            export_json=req.export_json,
            export_binary=req.export_binary
        )
        return {
            "success": True,
            "message": "Indexes saved successfully to disk.",
            "output_directory": req.output_dir,
            "details": saved
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# =============================================================================
# Frontend SPA & Static Assets Serving (Render All-in-One deployment)
# =============================================================================

FRONTEND_DIST = os.path.join(BASE_DIR, "frontend", "dist")

if os.path.isdir(FRONTEND_DIST):
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse

    assets_dir = os.path.join(FRONTEND_DIST, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/")
    def serve_index():
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        if full_path.startswith("api") or full_path.startswith("docs") or full_path == "openapi.json":
            raise HTTPException(status_code=404, detail="API endpoint not found")
        file_path = os.path.join(FRONTEND_DIST, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))
else:
    @app.get("/")
    def root_fallback():
        return {
            "status": "online",
            "service": "Reuters IR Admin API (Part 1)",
            "docs_url": "/docs",
            "frontend": "Frontend build not detected in frontend/dist. Deploying frontend to Cloudflare Pages or run 'npm run build' inside frontend/"
        }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Reuters IR Admin API server on port {port} ...")
    uvicorn.run("backend.app:app", host="0.0.0.0", port=port, reload=False)
