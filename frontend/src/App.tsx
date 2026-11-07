import { useEffect, useMemo, useRef, useState } from "react";

const API_BASE =
  (import.meta as any).env?.VITE_API_BASE ||
  (typeof window !== "undefined" && window.location.origin.includes("5173")
    ? "http://127.0.0.1:8000/api"
    : "/api");

type IconProps = { className?: string };

const Icon = {
  Database: ({ className = "" }: IconProps) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
      <ellipse cx="12" cy="5" rx="7.5" ry="3" />
      <path d="M4.5 5v7c0 1.7 3.4 3 7.5 3s7.5-1.3 7.5-3V5M4.5 12v7c0 1.7 3.4 3 7.5 3s7.5-1.3 7.5-3v-7" />
    </svg>
  ),
  Download: ({ className = "" }: IconProps) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
      <path d="M12 3v12m0 0 4-4m-4 4-4-4M5 20h14" />
    </svg>
  ),
  Folder: ({ className = "" }: IconProps) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
      <path d="M3.5 6.5h6l2-2h9v15h-17z" />
    </svg>
  ),
  Search: ({ className = "" }: IconProps) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
      <circle cx="10.5" cy="10.5" r="6.5" />
      <path d="m16 16 4.5 4.5" />
    </svg>
  ),
  Grip: ({ className = "" }: IconProps) => (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <circle cx="8" cy="7" r="1.2" />
      <circle cx="16" cy="7" r="1.2" />
      <circle cx="8" cy="12" r="1.2" />
      <circle cx="16" cy="12" r="1.2" />
      <circle cx="8" cy="17" r="1.2" />
      <circle cx="16" cy="17" r="1.2" />
    </svg>
  ),
  ChevronUp: ({ className = "" }: IconProps) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
      <path d="m7 14 5-5 5 5" />
    </svg>
  ),
  ChevronDown: ({ className = "" }: IconProps) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
      <path d="m7 10 5 5 5-5" />
    </svg>
  ),
  ArrowRight: ({ className = "" }: IconProps) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
      <path d="M5 12h14m-4-4 4 4-4 4" />
    </svg>
  ),
  Play: ({ className = "" }: IconProps) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
      <path d="m9 7 8 5-8 5z" />
      <circle cx="12" cy="12" r="9.5" />
    </svg>
  ),
  Check: ({ className = "" }: IconProps) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.3" aria-hidden="true">
      <path d="m6 12 4 4 8-9" />
    </svg>
  ),
  Eye: ({ className = "" }: IconProps) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  ),
  X: ({ className = "" }: IconProps) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M18 6 6 18M6 6l12 12" />
    </svg>
  ),
  Upload: ({ className = "" }: IconProps) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="17 8 12 3 7 8" />
      <line x1="12" y1="3" x2="12" y2="15" />
    </svg>
  ),
  FileText: ({ className = "" }: IconProps) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="16" y1="13" x2="8" y2="13" />
      <line x1="16" y1="17" x2="8" y2="17" />
    </svg>
  ),
};

type PipelineStep = {
  id: string;
  title: string;
  description: string;
  enabled: boolean;
};

const initialSteps: PipelineStep[] = [
  {
    id: "tag_cleaning",
    title: "Tag Cleaning",
    description: "Removes SGML/XML tags & entities",
    enabled: true,
  },
  {
    id: "normalization",
    title: "Normalization",
    description: "Lowercase, strip punctuation, tokenization",
    enabled: true,
  },
  {
    id: "stopwords",
    title: "Stopwords Removal",
    description: "English & Reuters domain stoplist",
    enabled: true,
  },
  {
    id: "stemming",
    title: "Stemming",
    description: "Porter-style suffix stripping",
    enabled: true,
  },
  { id: "lemmatization", title: "Lemmatization", description: "Dictionary lookup", enabled: false },
];

const PRESETS = [
  { name: "Standard Porter (Recommended)", steps: ["tag_cleaning", "normalization", "stopwords", "stemming"] },
  { name: "Lemmatization Focus", steps: ["tag_cleaning", "normalization", "stopwords", "lemmatization"] },
  { name: "Full Chain (All 5)", steps: ["tag_cleaning", "normalization", "stopwords", "stemming", "lemmatization"] },
  { name: "Minimal (No Reduction)", steps: ["tag_cleaning", "normalization", "stopwords"] },
];

const models = ["BoW (Binary)", "F (Frequency)", "TF Normalized", "TF-IDF"];
const structures = [
  "Document-Term Matrix",
  "Term-Document Matrix",
  "Inverted Index (Posting Lists)",
];

const MODEL_MAP: Record<string, string> = {
  "BoW (Binary)": "binary",
  "F (Frequency)": "raw_freq",
  "TF Normalized": "tf_norm",
  "TF-IDF": "tfidf",
};

interface IndexMetrics {
  num_documents: number;
  vocabulary_size: number;
  total_tokens: number;
  avg_tokens_per_doc: number;
  memory: {
    ram_inverted_index_kb: number;
    ram_inverted_index_mb: number;
    ram_matrices_kb: number;
    ram_matrices_mb: number;
    ram_total_kb: number;
    ram_total_mb: number;
  };
}

interface MatrixViewData {
  type: string;
  columns: string[];
  rows: Record<string, any>[];
  total_rows?: number;
  page?: number;
  total_pages?: number;
}

interface InvertedIndexItem {
  terme: string;
  df: number;
  postings: string;
}

interface DocumentItem {
  doc_id: string;
  title: string;
  date: string;
  body: string;
}

function Checkbox({
  checked,
  onChange,
  label,
}: {
  checked: boolean;
  onChange: () => void;
  label: string;
}) {
  return (
    <button
      type="button"
      role="checkbox"
      aria-checked={checked}
      aria-label={label}
      onClick={onChange}
      className={`checkbox ${checked ? "checkbox-checked" : ""}`}
    >
      {checked && <Icon.Check className="h-3.5 w-3.5" />}
    </button>
  );
}

function App() {
  const [steps, setSteps] = useState(initialSteps);
  const [model, setModel] = useState("TF-IDF");
  const [structure, setStructure] = useState("Document-Term Matrix");
  const [filter, setFilter] = useState("");
  const [allDocuments, setAllDocuments] = useState(false);
  const [maxDocuments, setMaxDocuments] = useState("50");
  const [jsonExport, setJsonExport] = useState(true);
  const [binaryExport, setBinaryExport] = useState(true);
  const [datasetPath, setDatasetPath] = useState(
    "c:\\Users\\benzm\\OneDrive\\Bureau\\RI\\archive (2)",
  );

  // File Upload State (Local Disk Explorer)
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [ingestMode, setIngestMode] = useState<"upload" | "path">("upload");

  // Backend state
  const [isBackendConnected, setIsBackendConnected] = useState<boolean>(false);
  const [loadState, setLoadState] = useState<"idle" | "loading" | "loaded">("idle");
  const [loadedCount, setLoadedCount] = useState<number>(0);
  const [indexState, setIndexState] = useState<"idle" | "running" | "done">("idle");
  const [metrics, setMetrics] = useState<IndexMetrics | null>(null);

  // Notifications
  const [toast, setToast] = useState<{ type: "success" | "error" | "info"; msg: string } | null>(null);

  // Table pagination & data
  const [matrixData, setMatrixData] = useState<MatrixViewData | null>(null);
  const [invertedData, setInvertedData] = useState<InvertedIndexItem[]>([]);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [isLoadingTable, setIsLoadingTable] = useState<boolean>(false);

  // Document modal
  const [isDocModalOpen, setIsDocModalOpen] = useState<boolean>(false);
  const [docsList, setDocsList] = useState<DocumentItem[]>([]);
  const [docPage, setDocPage] = useState<number>(1);
  const [docTotal, setDocTotal] = useState<number>(0);
  const [selectedDoc, setSelectedDoc] = useState<DocumentItem | null>(null);

  const [draggedStep, setDraggedStep] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const activeSteps = useMemo(() => steps.filter((step) => step.enabled), [steps]);

  const showToast = (type: "success" | "error" | "info", msg: string) => {
    setToast({ type, msg });
    setTimeout(() => setToast(null), 4000);
  };

  // Check backend health on mount
  useEffect(() => {
    fetch(`${API_BASE}/status`)
      .then((res) => res.json())
      .then((data) => {
        setIsBackendConnected(true);
        if (data.documents_loaded > 0) {
          setLoadedCount(data.documents_loaded);
          setLoadState("loaded");
        }
        if (data.indexes_generated) {
          setIndexState("done");
          fetchMetrics();
        }
      })
      .catch(() => {
        setIsBackendConnected(false);
      });
  }, []);

  const fetchMetrics = async () => {
    try {
      const res = await fetch(`${API_BASE}/indexes/metrics`);
      if (res.ok) {
        const data = await res.json();
        setMetrics(data);
      }
    } catch (e) {
      console.error(e);
    }
  };

  // Fetch matrix / index data
  useEffect(() => {
    if (indexState !== "done") return;

    const modelKey = MODEL_MAP[model] || "tfidf";
    setIsLoadingTable(true);

    if (structure === "Inverted Index (Posting Lists)") {
      const url = filter
        ? `${API_BASE}/indexes/inverted?model=${modelKey}&search_term=${encodeURIComponent(filter)}&page=${currentPage}&page_size=25`
        : `${API_BASE}/indexes/inverted?model=${modelKey}&page=${currentPage}&page_size=25`;

      fetch(url)
        .then((res) => res.json())
        .then((data) => {
          if (data.sample_terms) {
            setInvertedData(data.sample_terms);
            setTotalPages(data.total_pages || 1);
          } else {
            setInvertedData([]);
            setTotalPages(1);
          }
        })
        .catch((err) => console.error(err))
        .finally(() => setIsLoadingTable(false));
    } else {
      const matrixType = structure === "Term-Document Matrix" ? "term_doc" : "doc_term";
      const filterParam = filter ? `&filter=${encodeURIComponent(filter)}` : "";
      fetch(
        `${API_BASE}/indexes/matrix?model=${modelKey}&matrix_type=${matrixType}&page=${currentPage}&page_size=16&max_cols=8${filterParam}`,
      )
        .then((res) => res.json())
        .then((data) => {
          if (data.columns && data.rows) {
            setMatrixData(data);
            setTotalPages(data.total_pages || 1);
          }
        })
        .catch((err) => console.error(err))
        .finally(() => setIsLoadingTable(false));
    }
  }, [model, structure, indexState, currentPage, filter]);

  // Load Document Previews for Modal
  const loadDocumentsList = async (page = 1) => {
    try {
      const res = await fetch(`${API_BASE}/dataset/documents?page=${page}&page_size=8`);
      if (res.ok) {
        const data = await res.json();
        setDocsList(data.documents);
        setDocTotal(data.total);
        setDocPage(data.page);
        if (data.documents.length > 0 && !selectedDoc) {
          setSelectedDoc(data.documents[0]);
        }
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleOpenDocModal = () => {
    setIsDocModalOpen(true);
    loadDocumentsList(1);
  };

  const moveStep = (index: number, direction: -1 | 1) => {
    const destination = index + direction;
    if (destination < 0 || destination >= steps.length) return;
    const next = [...steps];
    [next[index], next[destination]] = [next[destination], next[index]];
    setSteps(next);
  };

  const moveDraggedStep = (targetId: string) => {
    if (!draggedStep || draggedStep === targetId) return;
    const from = steps.findIndex((step) => step.id === draggedStep);
    const to = steps.findIndex((step) => step.id === targetId);
    const next = [...steps];
    const [item] = next.splice(from, 1);
    next.splice(to, 0, item);
    setSteps(next);
  };

  const applyPreset = (presetSteps: string[]) => {
    const newSteps = initialSteps.map((s) => ({
      ...s,
      enabled: presetSteps.includes(s.id),
    }));
    newSteps.sort((a, b) => {
      const idxA = presetSteps.indexOf(a.id);
      const idxB = presetSteps.indexOf(b.id);
      if (idxA === -1 && idxB === -1) return 0;
      if (idxA === -1) return 1;
      if (idxB === -1) return -1;
      return idxA - idxB;
    });
    setSteps(newSteps);
    showToast("info", "Preset configuration applied.");
  };

  // Real backend call: Load Dataset (Direct Upload from Local Disk or Path)
  const handleLoadDataset = async () => {
    setLoadState("loading");
    try {
      if (ingestMode === "upload") {
        if (!selectedFile) {
          throw new Error("Please select a file (.csv or .sgm) from your local disk.");
        }
        const formData = new FormData();
        formData.append("file", selectedFile);
        if (!allDocuments && maxDocuments) {
          formData.append("max_docs", maxDocuments);
        }
        const res = await fetch(`${API_BASE}/dataset/upload`, {
          method: "POST",
          body: formData,
        });
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.detail || "Error uploading dataset");
        }
        setLoadedCount(data.count);
        setLoadState("loaded");
        setIsBackendConnected(true);
        showToast("success", `Loaded ${data.count} documents from '${selectedFile.name}' (${data.size_mb} MB).`);
      } else {
        const res = await fetch(`${API_BASE}/dataset/load`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            path: datasetPath,
            max_docs: allDocuments ? null : Number(maxDocuments),
          }),
        });
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.detail || "Error loading dataset");
        }
        setLoadedCount(data.count);
        setLoadState("loaded");
        setIsBackendConnected(true);
        showToast("success", `Loaded ${data.count} documents from disk path.`);
      }
    } catch (err: any) {
      showToast("error", err.message || "Failed to load dataset.");
      setLoadState("idle");
    }
  };

  // Real backend call: Configure Pipeline + Generate Indexes
  const handleGenerateIndexes = async () => {
    if (loadState !== "loaded" && loadedCount === 0) {
      showToast("error", "Please load a dataset before generating indexes.");
      return;
    }

    setIndexState("running");

    try {
      // 1. Configure pipeline
      const configRes = await fetch(`${API_BASE}/pipeline/configure`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          steps: activeSteps.map((s) => s.id),
        }),
      });
      const configData = await configRes.json();
      if (!configRes.ok) {
        throw new Error(configData.detail || "Pipeline configuration error");
      }

      // 2. Generate indexes
      const genRes = await fetch(`${API_BASE}/indexes/generate`, {
        method: "POST",
      });
      const genData = await genRes.json();
      if (!genRes.ok) {
        throw new Error(genData.detail || "Indexing error");
      }

      setMetrics(genData.metrics);
      setIndexState("done");
      setCurrentPage(1);
      showToast("success", `Generated all 4 models across ${genData.metrics.num_documents} docs.`);
    } catch (err: any) {
      showToast("error", err.message || "An error occurred during index generation.");
      setIndexState("idle");
    }
  };

  // Real backend call: Save to disk
  const handleSaveToDisk = async () => {
    try {
      const res = await fetch(`${API_BASE}/indexes/save`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          export_json: jsonExport,
          export_binary: binaryExport,
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Failed to save indexes");
      }
      showToast("success", `Saved 13 files to: ${data.output_directory}`);
    } catch (err: any) {
      showToast("error", err.message || "Save error");
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      {/* Toast Notification */}
      {toast && (
        <div className="fixed top-5 right-8 z-50 transition-all">
          <div
            className={`flex items-center gap-2.5 rounded-xl border px-4 py-3 shadow-lg backdrop-blur-md text-xs font-semibold ${
              toast.type === "success"
                ? "border-emerald-200 bg-emerald-50/95 text-emerald-800"
                : toast.type === "error"
                ? "border-rose-200 bg-rose-50/95 text-rose-800"
                : "border-blue-200 bg-blue-50/95 text-blue-800"
            }`}
          >
            <span
              className={`h-2 w-2 rounded-full ${
                toast.type === "success" ? "bg-emerald-500" : toast.type === "error" ? "bg-rose-500" : "bg-blue-500"
              }`}
            />
            <span>{toast.msg}</span>
            <button onClick={() => setToast(null)} className="ml-2 text-slate-400 hover:text-slate-700">
              <Icon.X className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      )}

      {/* Header */}
      <header className="sticky top-0 z-20 h-16 border-b border-white/60 bg-white/70 backdrop-blur-xl">
        <div className="mx-auto flex h-full max-w-[1440px] items-center justify-between px-8">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center logo-mark rounded-lg text-white">
              <Icon.Database className="h-[18px] w-[18px]" />
            </div>
            <h1 className="text-[15px] font-semibold tracking-[-0.01em] text-slate-950">
              Reuters IR Admin
            </h1>
            <span className="rounded-full border border-slate-200 bg-slate-50 px-2.5 py-1 text-[12px] font-semibold text-slate-600">
              Part 1 · Dynamic Indexer
            </span>
          </div>

          <div className="flex items-center gap-3">
            <div
              className={`flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-medium ${
                isBackendConnected
                  ? "border-emerald-200 bg-emerald-50 text-emerald-700"
                  : "border-amber-200 bg-amber-50 text-amber-700"
              }`}
            >
              <span className="live-dot" />
              {isBackendConnected ? "Backend: Connected (FastAPI)" : "Connecting to API..."}
            </div>

            {loadedCount > 0 && (
              <button
                type="button"
                onClick={handleOpenDocModal}
                className="secondary-button"
                title="Inspect loaded Reuters articles"
              >
                <Icon.Eye className="h-4 w-4 text-blue-600" />
                Inspect Articles ({loadedCount})
              </button>
            )}

            <button type="button" onClick={handleSaveToDisk} disabled={indexState !== "done"} className="secondary-button disabled:opacity-50">
              <Icon.Download className="h-4 w-4" />
              Export / Save
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto grid max-w-[1440px] grid-cols-[400px_minmax(0,1fr)] gap-8 px-8 py-8">
        {/* Left Column */}
        <aside className="space-y-5">
          {/* Section 1: Ingestion - Bouton/Explorateur Disque Local */}
          <section className="card p-6">
            <div className="section-heading justify-between">
              <div className="flex items-start gap-2.5">
                <span className="step-badge">1</span>
                <div>
                  <h2>Sélection des Données</h2>
                  <p>Charger les documents depuis le disque local</p>
                </div>
              </div>
              <div className="flex gap-1 text-[11px] font-semibold bg-slate-100 p-0.5 rounded-lg border border-slate-200">
                <button
                  type="button"
                  onClick={() => setIngestMode("upload")}
                  className={`px-2 py-0.5 rounded transition ${
                    ingestMode === "upload" ? "bg-white text-blue-700 shadow-2xs font-bold" : "text-slate-500 hover:text-slate-700"
                  }`}
                >
                  Fichier
                </button>
                <button
                  type="button"
                  onClick={() => setIngestMode("path")}
                  className={`px-2 py-0.5 rounded transition ${
                    ingestMode === "path" ? "bg-white text-blue-700 shadow-2xs font-bold" : "text-slate-500 hover:text-slate-700"
                  }`}
                >
                  Chemin
                </button>
              </div>
            </div>

            <div className="mt-4 space-y-4">
              {ingestMode === "upload" ? (
                <div>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".csv,.sgm,.txt"
                    className="hidden"
                    onChange={(event) => {
                      const file = event.target.files?.[0];
                      if (file) setSelectedFile(file);
                    }}
                  />
                  {!selectedFile ? (
                    <div
                      onClick={() => fileInputRef.current?.click()}
                      onDragOver={(e) => {
                        e.preventDefault();
                        setIsDragging(true);
                      }}
                      onDragLeave={() => setIsDragging(false)}
                      onDrop={(e) => {
                        e.preventDefault();
                        setIsDragging(false);
                        const file = e.dataTransfer.files?.[0];
                        if (file) setSelectedFile(file);
                      }}
                      className={`cursor-pointer border-2 border-dashed rounded-xl p-5 text-center transition-all ${
                        isDragging
                          ? "border-blue-500 bg-blue-50/70"
                          : "border-slate-300 hover:border-blue-400 bg-slate-50/40 hover:bg-blue-50/20"
                      }`}
                    >
                      <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-full bg-blue-50 text-blue-600 mb-2">
                        <Icon.Upload className="h-5 w-5" />
                      </div>
                      <p className="text-xs font-semibold text-slate-800">
                        Cliquer pour explorer le disque local
                      </p>
                      <p className="text-[11px] text-slate-500 mt-0.5">
                        ou glisser-déposer le fichier Reuters-21578 (.csv ou .sgm)
                      </p>
                    </div>
                  ) : (
                    <div className="flex items-center justify-between p-3 rounded-lg border border-blue-200 bg-blue-50/50">
                      <div className="flex items-center gap-2.5 min-w-0">
                        <div className="h-8 w-8 rounded-lg bg-blue-100 flex items-center justify-center text-blue-700 shrink-0">
                          <Icon.FileText className="h-4 w-4" />
                        </div>
                        <div className="min-w-0">
                          <p className="text-xs font-bold text-slate-900 truncate">{selectedFile.name}</p>
                          <p className="text-[10.5px] text-slate-500">
                            {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB · Prêt au chargement
                          </p>
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={() => {
                          setSelectedFile(null);
                          if (fileInputRef.current) fileInputRef.current.value = "";
                        }}
                        className="text-slate-400 hover:text-slate-700 p-1 rounded-md hover:bg-slate-200"
                        title="Changer de fichier"
                      >
                        <Icon.X className="h-4 w-4" />
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                <label className="field-label">
                  Chemin du dossier / fichier local
                  <div className="mt-1.5 flex">
                    <input
                      value={datasetPath}
                      onChange={(event) => setDatasetPath(event.target.value)}
                      className="input rounded-r-none font-mono text-[12px]"
                      aria-label="Dataset path"
                    />
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".csv,.sgm"
                      className="hidden"
                      onChange={(event) => {
                        const file = event.target.files?.[0];
                        if (file) setDatasetPath((file as any).path || file.name);
                      }}
                    />
                    <button
                      type="button"
                      onClick={() => fileInputRef.current?.click()}
                      className="browse-button"
                    >
                      <Icon.Folder className="h-3.5 w-3.5" />
                      Parcourir…
                    </button>
                  </div>
                </label>
              )}

              <div className="grid grid-cols-[1fr_auto] items-end gap-4">
                <label className="field-label">
                  Max Documents
                  <input
                    type="number"
                    value={maxDocuments}
                    disabled={allDocuments}
                    onChange={(event) => setMaxDocuments(event.target.value)}
                    className="input mt-1.5 disabled:bg-slate-50 disabled:text-slate-400 font-mono text-xs"
                    placeholder="50"
                  />
                </label>
                <label className="mb-2 flex cursor-pointer items-center gap-2 text-xs font-medium text-slate-600 select-none">
                  <button
                    type="button"
                    role="switch"
                    aria-checked={allDocuments}
                    onClick={() => setAllDocuments(!allDocuments)}
                    className={`switch ${allDocuments ? "switch-on" : ""}`}
                  >
                    <span />
                  </button>
                  Tous ({allDocuments ? "Illimité" : "Limité"})
                </label>
              </div>

              <div className="flex items-center gap-3 pt-1">
                <button
                  type="button"
                  onClick={handleLoadDataset}
                  disabled={loadState === "loading" || (ingestMode === "upload" && !selectedFile)}
                  className="secondary-button flex-1 justify-center disabled:opacity-50"
                >
                  <Icon.Upload className="h-4 w-4 text-blue-600" />
                  {loadState === "loading" ? "Chargement en cours…" : "Charger les documents"}
                </button>
                <span className="status-pill">
                  <span
                    className={`h-1.5 w-1.5 rounded-full ${
                      loadState === "loading"
                        ? "animate-pulse bg-amber-500"
                        : loadState === "loaded"
                        ? "bg-emerald-500"
                        : "bg-slate-300"
                    }`}
                  />
                  {loadState === "loading"
                    ? "Lecture en cours..."
                    : loadState === "loaded"
                    ? `${loadedCount} docs chargés`
                    : "Non chargé"}
                </span>
              </div>
            </div>
          </section>

          {/* Section 2: Pipeline */}
          <section className="card p-6">
            <div className="section-heading">
              <span className="step-badge">2</span>
              <div>
                <h2>Dynamic NLP Pipeline</h2>
                <p>Select steps and drag or use arrows to define execution order</p>
              </div>
            </div>

            {/* Presets */}
            <div className="mt-3 flex flex-wrap gap-1.5">
              {PRESETS.map((p) => (
                <button
                  key={p.name}
                  type="button"
                  onClick={() => applyPreset(p.steps)}
                  className="rounded-full border border-slate-200 bg-slate-50 px-2.5 py-0.5 text-[11px] font-medium text-slate-600 hover:border-blue-300 hover:bg-blue-50 hover:text-blue-700 transition"
                >
                  {p.name}
                </button>
              ))}
            </div>

            <div className="mt-3.5 space-y-2">
              {steps.map((step, index) => (
                <div
                  key={step.id}
                  draggable
                  onDragStart={() => setDraggedStep(step.id)}
                  onDragOver={(event) => event.preventDefault()}
                  onDrop={() => moveDraggedStep(step.id)}
                  onDragEnd={() => setDraggedStep(null)}
                  className={`pipeline-item ${draggedStep === step.id ? "opacity-45" : ""}`}
                >
                  <Icon.Grip className="h-5 w-5 shrink-0 cursor-grab text-slate-300 active:cursor-grabbing" />
                  <span className="order-number">{index + 1}</span>
                  <Checkbox
                    checked={step.enabled}
                    label={`Enable ${step.title}`}
                    onChange={() =>
                      setSteps(
                        steps.map((item) =>
                          item.id === step.id ? { ...item, enabled: !item.enabled } : item,
                        ),
                      )
                    }
                  />
                  <div className="min-w-0 flex-1">
                    <h3
                      className={`text-xs font-semibold ${
                        step.enabled ? "text-slate-800" : "text-slate-500"
                      }`}
                    >
                      {step.title}
                    </h3>
                    <p className="mt-0.5 truncate text-[11.5px] text-slate-500">
                      {step.description}
                    </p>
                  </div>
                  <div className="flex flex-col border-l border-slate-100 pl-1">
                    <button
                      type="button"
                      disabled={index === 0}
                      title="Move up"
                      onClick={() => moveStep(index, -1)}
                      className="icon-button"
                    >
                      <Icon.ChevronUp className="h-3.5 w-3.5" />
                    </button>
                    <button
                      type="button"
                      disabled={index === steps.length - 1}
                      title="Move down"
                      onClick={() => moveStep(index, 1)}
                      className="icon-button"
                    >
                      <Icon.ChevronDown className="h-3.5 w-3.5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-4 rounded-md border border-slate-200 bg-slate-50 px-3 py-2.5">
              <p className="mb-2 text-[10.5px] font-bold uppercase tracking-[0.12em] text-slate-400">
                Execution flow
              </p>
              <div className="flex flex-wrap items-center gap-1.5 font-mono text-[10.5px] font-medium text-slate-600">
                {activeSteps.map((step, index) => (
                  <div key={step.id} className="flex items-center gap-1.5">
                    <span>{step.id}</span>
                    {index < activeSteps.length - 1 && (
                      <Icon.ArrowRight className="h-3 w-3 text-slate-400" />
                    )}
                  </div>
                ))}
              </div>
            </div>
          </section>

          {/* Section 3: Action */}
          <section className="card p-6">
            <button
              type="button"
              onClick={handleGenerateIndexes}
              disabled={indexState === "running" || loadState !== "loaded"}
              className="primary-button w-full justify-center disabled:opacity-50"
            >
              {indexState === "done" ? (
                <Icon.Check className="h-4 w-4" />
              ) : (
                <Icon.Play className="h-4 w-4" />
              )}
              {indexState === "running"
                ? "Generating Indexes…"
                : indexState === "done"
                ? "Re-Generate Indexes"
                : "Generate Indexes"}
            </button>

            <div className="my-4 border-t border-slate-100" />
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-700">Save to Disk</span>
              <span className="font-mono text-[10.5px] text-slate-400">./saved_indexes/</span>
            </div>
            <div className="mt-3 flex items-center gap-5">
              <label className="check-label">
                <Checkbox
                  checked={jsonExport}
                  label="JSON export"
                  onChange={() => setJsonExport(!jsonExport)}
                />
                JSON export
              </label>
              <label className="check-label">
                <Checkbox
                  checked={binaryExport}
                  label="Binary bundle"
                  onChange={() => setBinaryExport(!binaryExport)}
                />
                Binary bundle <span className="font-mono text-[11.5px] text-slate-400">(.pkl)</span>
              </label>
            </div>
          </section>
        </aside>

        {/* Right Column: Dashboard & Table */}
        <div className="min-w-0 space-y-6">
          {/* Monitoring Cards */}
          <section>
            <div className="mb-3 flex items-end justify-between">
              <div>
                <h2 className="text-sm font-semibold text-slate-900">Post-Indexing Monitoring</h2>
                <p className="mt-0.5 text-xs text-slate-500">
                  Live summary of the current in-memory index
                </p>
              </div>
              <span className="flex items-center gap-1.5 text-[12px] text-slate-400">
                <span className="live-dot" />
                {indexState === "done" ? "Indexes in memory" : "Waiting for index generation"}
              </span>
            </div>
            <div className="grid grid-cols-4 gap-3">
              <MetricCard
                label="Indexed Documents"
                value={metrics ? String(metrics.num_documents) : String(loadedCount || 0)}
                unit="docs"
              />
              <MetricCard
                label="Vocabulary Size"
                value={metrics ? metrics.vocabulary_size.toLocaleString() : "—"}
                unit="unique terms"
              />
              <MetricCard
                label="Total Tokens"
                value={metrics ? metrics.total_tokens.toLocaleString() : "—"}
                unit="tokens"
                subtext={metrics ? `${metrics.avg_tokens_per_doc} avg / doc` : "—"}
              />
              {/* KPI 4: RAM Memory Usage with Dual-Color Progress Bar */}
              <div className="card metric-card px-5 py-5 hover:border-blue-300 transition-all">
                <div className="flex items-start justify-between">
                  <p className="text-[11.5px] font-semibold uppercase tracking-[0.08em] text-slate-500">
                    RAM Memory Usage
                  </p>
                  <svg viewBox="0 0 72 28" className="spark h-7 w-[60px]" fill="none" aria-hidden="true">
                    <path
                      d="M0 14 L12 16 L24 12 L36 15 L48 9 L60 11 L72 7"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </div>
                <div className="mt-3 flex items-baseline gap-1.5">
                  <span className="text-[30px] font-semibold leading-none tracking-[-0.035em] text-slate-950">
                    {metrics ? String(metrics.memory.ram_total_mb) : "—"}
                  </span>
                  <span className="text-[12px] font-medium text-slate-500">MB Total</span>
                </div>

                {/* Dual-Color Comparison Bar: Matrix vs Inverted Index */}
                {metrics ? (
                  <div className="mt-3 space-y-1">
                    <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden flex shadow-inner">
                      <div
                        className="bg-blue-600 h-full transition-all duration-500"
                        style={{
                          width: `${(metrics.memory.ram_matrices_mb / metrics.memory.ram_total_mb) * 100}%`,
                        }}
                        title={`Matrices: ${metrics.memory.ram_matrices_mb} MB`}
                      />
                      <div
                        className="bg-emerald-500 h-full transition-all duration-500"
                        style={{
                          width: `${(metrics.memory.ram_inverted_index_mb / metrics.memory.ram_total_mb) * 100}%`,
                        }}
                        title={`Inverted Index: ${metrics.memory.ram_inverted_index_mb} MB`}
                      />
                    </div>
                    <div className="flex justify-between text-[10.5px] font-mono text-slate-600 pt-0.5">
                      <span className="text-blue-700 font-semibold">🟦 Mat: {metrics.memory.ram_matrices_mb}MB</span>
                      <span className="text-emerald-700 font-semibold">🟩 Inv: {metrics.memory.ram_inverted_index_mb}MB</span>
                    </div>
                  </div>
                ) : (
                  <p className="mt-2 h-4 truncate text-[11.5px] text-slate-500">
                    RAM Matrice vs Inverted
                  </p>
                )}
              </div>
            </div>
          </section>

          {/* Data Explorer */}
          <section className="card overflow-hidden">
            <div className="border-b border-slate-200 px-5 pt-5">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-sm font-semibold text-slate-900">
                    Multi-Model Data Explorer
                  </h2>
                  <p className="mt-0.5 text-xs text-slate-500">
                    Inspect generated matrix weights and posting lists
                  </p>
                </div>
                <span className="rounded-md border border-slate-200 bg-slate-50 px-2 py-1 font-mono text-[11.5px] text-slate-500">
                  float64 · sparse
                </span>
              </div>
              <nav className="mt-5 flex gap-6" aria-label="Index model">
                {models.map((item) => (
                  <button
                    type="button"
                    key={item}
                    onClick={() => {
                      setModel(item);
                      setCurrentPage(1);
                    }}
                    className={`model-tab ${model === item ? "model-tab-active" : ""}`}
                  >
                    {item}
                  </button>
                ))}
              </nav>
            </div>

            <div className="flex items-center justify-between border-b border-slate-200 bg-slate-50/70 px-5 py-3">
              <div className="segmented-control">
                {structures.map((item) => (
                  <button
                    type="button"
                    key={item}
                    onClick={() => {
                      setStructure(item);
                      setCurrentPage(1);
                    }}
                    className={structure === item ? "segment-active" : ""}
                  >
                    {item}
                  </button>
                ))}
              </div>
              <div className="relative">
                <Icon.Search className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
                <input
                  value={filter}
                  onChange={(event) => {
                    setFilter(event.target.value);
                    setCurrentPage(1);
                  }}
                  placeholder="Filter terms…"
                  className="h-9 w-[240px] rounded-lg border border-slate-200 bg-white pl-8 pr-8 text-xs text-slate-700 outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
                />
                {filter && (
                  <button
                    onClick={() => {
                      setFilter("");
                      setCurrentPage(1);
                    }}
                    className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-700"
                    title="Clear filter"
                  >
                    <Icon.X className="h-3.5 w-3.5" />
                  </button>
                )}
              </div>
            </div>

            <div className="overflow-x-auto min-h-[300px]">
              {isLoadingTable ? (
                <div className="py-16 text-center text-xs text-slate-400">Loading data...</div>
              ) : indexState !== "done" ? (
                <div className="py-16 text-center text-xs text-slate-400">
                  Click "Generate Indexes" to build matrices and inverted index.
                </div>
              ) : structure === "Inverted Index (Posting Lists)" ? (
                <table className="data-table">
                  <thead>
                    <tr>
                      <th className="w-48">TERME</th>
                      <th className="w-28">DOC FREQ.</th>
                      <th>POSTING LIST (DOC ID : WEIGHT)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {invertedData.length > 0 ? (
                      invertedData.map((item, idx) => (
                        <tr key={item.terme + idx}>
                          <td>
                            <span className="font-mono font-medium text-slate-800">
                              {item.terme}
                            </span>
                          </td>
                          <td className="font-mono text-slate-600">{item.df}</td>
                          <td className="font-mono text-[12px] text-slate-600">{item.postings}</td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={3} className="py-14 text-center text-xs text-slate-400">
                          No matching terms found.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              ) : matrixData && matrixData.columns ? (
                <table className="data-table">
                  <thead>
                    <tr>
                      {matrixData.columns.map((col) => (
                        <th key={col} className="font-mono">
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {matrixData.rows.length > 0 ? (
                      matrixData.rows.map((row, rowIdx) => (
                        <tr key={rowIdx}>
                          {matrixData.columns.map((col, cIdx) => {
                            const val = row[col];
                            const isZero = val === 0 || val === 0.0 || val === "0.0000" || val === "0";
                            return (
                              <td key={col} className="font-mono text-[12px]">
                                {cIdx === 0 ? (
                                  <span className="font-bold text-slate-800">{val}</span>
                                ) : isZero ? (
                                  <span className="text-slate-300">—</span>
                                ) : (
                                  <span className="inline-block rounded px-1.5 py-0.5 text-[11.5px] font-semibold text-blue-700 bg-blue-50 border border-blue-100 shadow-2xs">
                                    {typeof val === "number" ? val.toFixed(4) : val}
                                  </span>
                                )}
                              </td>
                            );
                          })}
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={matrixData.columns.length} className="py-14 text-center text-xs text-slate-400">
                          No matching records.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              ) : null}
            </div>

            <div className="flex items-center justify-between border-t border-slate-200 px-5 py-3">
              <p className="text-[12px] text-slate-500">
                Page {currentPage} of {totalPages}
              </p>
              <div className="flex items-center gap-1">
                <button
                  type="button"
                  disabled={currentPage <= 1 || indexState !== "done"}
                  onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                  className="pagination-button"
                >
                  Previous
                </button>
                <button
                  type="button"
                  disabled={currentPage >= totalPages || indexState !== "done"}
                  onClick={() => setCurrentPage((p) => p + 1)}
                  className="pagination-button"
                >
                  Next
                </button>
              </div>
            </div>
          </section>
        </div>
      </main>

      {/* Raw Document Inspector Modal */}
      {isDocModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-xs p-6">
          <div className="card w-full max-w-4xl max-h-[85vh] flex flex-col overflow-hidden shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4 bg-slate-50">
              <div className="flex items-center gap-2.5">
                <Icon.Folder className="h-5 w-5 text-blue-600" />
                <div>
                  <h3 className="text-sm font-bold text-slate-900">
                    Reuters-21578 Document Inspector
                  </h3>
                  <p className="text-xs text-slate-500">
                    {docTotal} total articles ingested from collection
                  </p>
                </div>
              </div>
              <button
                onClick={() => setIsDocModalOpen(false)}
                className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-200 hover:text-slate-800"
              >
                <Icon.X className="h-5 w-5" />
              </button>
            </div>

            <div className="grid grid-cols-[300px_1fr] flex-1 overflow-hidden divide-x divide-slate-200">
              {/* Document List */}
              <div className="overflow-y-auto p-3 space-y-2 bg-slate-50/50">
                {docsList.map((doc) => (
                  <div
                    key={doc.doc_id}
                    onClick={() => setSelectedDoc(doc)}
                    className={`cursor-pointer rounded-lg p-2.5 border transition ${
                      selectedDoc?.doc_id === doc.doc_id
                        ? "border-blue-400 bg-blue-50 shadow-xs"
                        : "border-slate-200 bg-white hover:border-slate-300"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-[11px] font-bold text-blue-700">
                        DOC_{doc.doc_id}
                      </span>
                      <span className="text-[10px] text-slate-400">{doc.date || "Reuters"}</span>
                    </div>
                    <p className="mt-1 text-xs font-semibold text-slate-800 line-clamp-1">
                      {doc.title}
                    </p>
                  </div>
                ))}

                <div className="flex items-center justify-between pt-2 px-1">
                  <button
                    disabled={docPage <= 1}
                    onClick={() => loadDocumentsList(docPage - 1)}
                    className="pagination-button text-xs py-1 px-2 h-7 disabled:opacity-40"
                  >
                    Prev
                  </button>
                  <span className="text-xs font-mono text-slate-500">Page {docPage}</span>
                  <button
                    disabled={docPage * 8 >= docTotal}
                    onClick={() => loadDocumentsList(docPage + 1)}
                    className="pagination-button text-xs py-1 px-2 h-7 disabled:opacity-40"
                  >
                    Next
                  </button>
                </div>
              </div>

              {/* Full Article Content */}
              <div className="overflow-y-auto p-6 bg-white">
                {selectedDoc ? (
                  <article className="space-y-4">
                    <div className="border-b border-slate-100 pb-3">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="rounded bg-blue-100 px-2 py-0.5 font-mono text-xs font-bold text-blue-800">
                          DOCUMENT #{selectedDoc.doc_id}
                        </span>
                        <span className="text-xs text-slate-400">{selectedDoc.date}</span>
                      </div>
                      <h2 className="text-lg font-bold text-slate-900">{selectedDoc.title}</h2>
                    </div>
                    <div>
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
                        Raw Article Text
                      </h4>
                      <p className="whitespace-pre-line text-xs font-mono leading-relaxed text-slate-700 bg-slate-50 p-4 rounded-xl border border-slate-200">
                        {selectedDoc.body || "(No body text content)"}
                      </p>
                    </div>
                  </article>
                ) : (
                  <div className="py-20 text-center text-xs text-slate-400">
                    Select a document to read its content.
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

const sparkPaths = [
  "M0 22 L12 18 L24 20 L36 12 L48 14 L60 6 L72 8",
  "M0 20 L12 22 L24 14 L36 16 L48 8 L60 10 L72 4",
  "M0 18 L12 20 L24 12 L36 14 L48 10 L60 12 L72 5",
  "M0 14 L12 16 L24 12 L36 15 L48 9 L60 11 L72 7",
];
let sparkIndex = 0;

function MetricCard({
  label,
  value,
  unit,
  subtext,
}: {
  label: string;
  value: string;
  unit: string;
  subtext?: string;
}) {
  const path = sparkPaths[sparkIndex++ % sparkPaths.length];
  return (
    <div className="card metric-card px-5 py-5">
      <div className="flex items-start justify-between">
        <p className="text-[11.5px] font-semibold uppercase tracking-[0.08em] text-slate-500">
          {label}
        </p>
        <svg viewBox="0 0 72 28" className="spark h-7 w-[60px]" fill="none" aria-hidden="true">
          <path
            d={path}
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </div>
      <div className="mt-3 flex items-baseline gap-1.5">
        <span className="text-[30px] font-semibold leading-none tracking-[-0.035em] text-slate-950">
          {value}
        </span>
        <span className="text-[12px] font-medium text-slate-500">{unit}</span>
      </div>
      <p className="mt-2 h-4 truncate text-[11.5px] text-slate-500">{subtext || " "}</p>
    </div>
  );
}

export default App;
