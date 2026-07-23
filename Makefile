VENV := .venv
PY   := $(VENV)/bin/python
ENV  := HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 PYTORCH_ENABLE_MPS_FALLBACK=1 PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0 PYTHONPATH=src
PORT ?= 8000
MAX  ?= 25
MAX_MASTER ?= 200

.PHONY: help test annotate index reindex calibrate bench-rerank bench-retrieval rescore benchmark-export export-datasets eval-asof serve scrape ops scrape-master verify-master scrape-regs reg-edges audit-regs

help:
	@echo "test       run offline test suite"
	@echo "reindex    annotate lineage + rebuild persisted index (after corpus change)"
	@echo "index      build + persist FAISS/BM25 index and lineage.json"
	@echo "annotate   recompute supersession status in the corpus"
	@echo "calibrate  run the retrieval calibration sweep"
	@echo "bench-retrieval run retrieval-only benchmark + TREC runfile"
	@echo "rescore    re-score archived runs with bootstrap CIs + paired significance"
	@echo "benchmark-export export BEIR/TREC + RAG benchmark artifacts"
	@echo "export-datasets  export publishable dataset configs to dist/datasets"
	@echo "eval-asof  run the as-of-date golden eval (selector + pipeline cases)"
	@echo "serve      run the API (PORT=$(PORT)); set SEBI_RAG_API_KEY in env"
	@echo "ui         run the Gradio UI dashboard"
	@echo "ops        run the local ops HTTP server for n8n (port 8765)"
	@echo "scrape     fetch circulars (MAX=$(MAX)); runs on this machine"
	@echo "scrape-master  fetch master circulars (MAX_MASTER=$(MAX_MASTER))"
	@echo "verify-master  coverage report vs live SEBI master-circular listing (OFFLINE=1 to skip fetch)"
	@echo "scrape-regs    fetch SEBI regulations (Updated List, sid=1&ssid=3)"
	@echo "reg-edges      build circular->regulation edges + annotate corpus (offline)"
	@echo "audit-regs     precision audit of regulation edges (sample + CI)"

test:
	$(PY) -m pytest -q -m "not integration"

annotate:
	$(ENV) $(PY) -c "from sebi_rag.lineage import annotate_corpus; print(annotate_corpus('data/corpus/circulars.jsonl'))"

index:
	$(ENV) $(PY) scripts/build_index.py

reindex: annotate index

calibrate:
	$(ENV) $(PY) scripts/calibrate.py

bench-rerank:
	$(ENV) $(PY) scripts/bench_rerankers.py --models bge,qwen0.6b

eval-asof:
	$(ENV) $(PY) scripts/eval_asof.py

bench-retrieval:
	$(ENV) $(PY) scripts/bench_retrieval.py

rescore:
	$(ENV) $(PY) scripts/rescore_runs.py

benchmark-export:
	$(ENV) $(PY) scripts/build_golden_v6.py
	$(ENV) $(PY) scripts/export_benchmark.py

export-datasets:
	$(PY) scripts/export_datasets.py

serve:
	$(ENV) $(VENV)/bin/uvicorn sebi_rag.api:app --host 127.0.0.1 --port $(PORT) --workers 1

ui:
	$(ENV) $(PY) src/sebi_rag/ui.py

ops:
	$(ENV) $(PY) scripts/ops_server.py

scrape:
	$(ENV) $(PY) scripts/scrape_sebi.py --max $(MAX) --rate 3

scrape-master:
	$(ENV) $(PY) scripts/scrape_sebi.py --section master-circulars --max $(MAX_MASTER) --rate 3

verify-master:
	$(ENV) $(PY) scripts/verify_master.py $(if $(OFFLINE),--offline,)

scrape-regs:
	$(ENV) $(PY) scripts/scrape_regulations.py --rate 3

reg-edges:
	$(ENV) $(PY) scripts/build_reg_edges.py

audit-regs:
	$(ENV) $(PY) scripts/audit_reg_edges.py
