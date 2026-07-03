# SEBI Circular Scraping & Ingestion Plan

Last updated: 2026-06-29. Goal: grow `data/corpus/circulars.jsonl` with real SEBI
circulars from the official source, legally and reproducibly.

## 1. Legality & compliance

- **robots.txt (verified 2026-06-29):** `User-agent: *` with only `/js`, `/css`
  (and Hindi variants) disallowed. `/legal/circulars/*` and the PDF store
  `/sebi_data/attachdocs/*` are **not** disallowed → crawlable. No `Crawl-delay`
  is specified, so we self-impose ≥ 3 s between requests.
- **Nature of content:** SEBI circulars are public regulatory instruments issued
  by a statutory regulator. We use them for retrieval/reference, store the
  official `source_url`, fetch date, and a SHA-256 checksum as provenance, and
  attribute SEBI. Review SEBI's "Terms of Use" page before any redistribution.
- **No circumvention:** the public circulars listing needs no login. We never
  bypass logins, captchas, or any access control. A descriptive `User-Agent`
  (purpose + contact) is sent.
- **Politeness:** rate limiting, exponential backoff on 429/5xx, resume/cache to
  avoid re-downloading, run off-peak, bounded `--max` per run.

## 2. Execution model (important)

The scraper **runs on your machine** (`scripts/scrape_sebi.py`). Claude's sandboxed
web tools are restricted from bulk web fetching, so Claude authored the script and
verified the site structure, but **you execute the downloads**. Claude then helps
parse, validate, and calibrate the ingested results.

## 3. Pipeline

```
discover (listing: Legal > Circulars, paginated, date-filtered)
   -> detail page URLs + (date, title)
for each circular:
   fetch detail page -> extract PDF url under /sebi_data/attachdocs/
   download PDF -> data/raw/<id>.pdf   (skip if checksum already seen)
   ingest_pdf.ingest(pdf, corpus, source_url)   # existing, deterministic
annotate lineage (lineage.annotate_corpus)       # supersession graph
re-run scripts/calibrate.py + extend eval/golden  # recalibrate top_k / threshold
```

Reuses already-built, tested components: `ingest_pdf.py` (header-aware metadata,
dedupe, provenance), `lineage.py` (supersession), `calibrate.py`.

## 4. Scope (configurable CLI args)

- `--from / --to` issue-date range (default: last 12 months)
- `--max` cap on circulars per run (default 25 — start small, verify, scale)
- `--department` optional filter (e.g. "Corporation Finance Department")
- `--rate` seconds between requests (default 3.0)

## 5. Commands

Sections (sid=1 Legal): **ssid=7 Circulars** (~2.8k records, confirmed),
ssid=6 Master Circulars (~135). Pagination is a POST; the scraper has a no-advance
guard that stops safely if the POST params need tuning (verify on a >1-page run).

```
# 1. discover + download (run on your Mac)
PYTHONPATH=src .venv/bin/python scripts/scrape_sebi.py \
    --section circulars --from 2025-01-01 --to 2026-06-30 --max 50 --rate 3 [--ocr]

# 2. lineage + recalibration (Claude can run / assist)
PYTHONPATH=src .venv/bin/python -c "from sebi_rag.lineage import annotate_corpus; print(annotate_corpus('data/corpus/circulars.jsonl'))"
HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 \
PYTORCH_ENABLE_MPS_FALLBACK=1 PYTHONPATH=src .venv/bin/python scripts/calibrate.py
```

## 6. Risks & mitigations

- **Pagination (SOLVED):** POST `/sebiweb/ajax/home/getnewslistinfo.jsp` with
  `doDirect=<0-based page>` and sid/ssid/smid/ssidhidden/next=n/nextValue/intmid=-1
  (+ empty search/date/text fields). Page-0 GET first to seed the JSESSIONID cookie
  (carried by the scraper's cookie jar). Response = `listHTML #@# breadcrumb`; the
  list fragment has the usual date+href rows. Discovery dedupes the 1-row page
  overlap and degrades gracefully on any fetch error.
- **Scanned/image PDFs:** `ingest_pdf` yields no text → OCR fallback (ocrmypdf /
  pytesseract) needed; flagged, not silently ingested.
- **Bilingual (Hindi/English) PDFs:** body text still ingests; subject line may be
  garbled (known, acceptable — see ITD/AI circular in corpus).
- **Format variety:** header circular-number/date parser already handles 2026 and
  legacy formats; unknown formats raise `ValueError` rather than mis-tagging.
- **Duplicates / master circulars:** dedupe by circular number + checksum;
  `--replace` to upgrade an excerpt to full text.

## 7. Verification after each batch

- `wc -l data/corpus/circulars.jsonl`; spot-check 3 records' number/date/subject.
- `pytest -m "not integration"` stays green.
- Re-run calibration; confirm citation precision and abstention hold.
