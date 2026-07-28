# SEBI Scraping & Ingestion Plan

Last updated: 2026-07-28. Goal: grow `data/corpus/circulars.jsonl` and
`data/corpus/regulations.jsonl` with real SEBI content from the official source,
legally and reproducibly.

## 1. Legality & compliance

- **robots.txt (verified 2026-06-29, re-checked 2026-07-23):** `User-agent: *` with
  only `/js`, `/css` (and Hindi variants) disallowed. `/legal/circulars/*`,
  `/legal/regulations/*`, and the PDF store `/sebi_data/attachdocs/*` are **not**
  disallowed → crawlable. No `Crawl-delay` is specified, so we self-impose ≥ 3 s
  between requests.
- **Nature of content:** SEBI circulars and regulations are public regulatory
  instruments issued by a statutory regulator. We use them for retrieval/reference,
  store the official `source_url`, fetch date, and a SHA-256 checksum as
  provenance, and attribute SEBI. Review SEBI's "Terms of Use" page before any
  redistribution.
- **No circumvention:** the public circulars and regulations listings need no
  login. We never bypass logins, captchas, or any access control. A descriptive
  `User-Agent` (purpose + contact) is sent.
- **Politeness:** rate limiting, exponential backoff on 429/5xx, resume/cache to
  avoid re-downloading, run off-peak, bounded `--max` per run.

## 2. Execution model (important)

Both scrapers **run on your machine**:

| Script | Purpose |
|--------|---------|
| `scripts/scrape_sebi.py` (v0.2) | Circulars + Master Circulars discovery, PDF download, corpus ingestion |
| `scripts/scrape_regulations.py` (v0.1) | In-force regulations listing, PDF download, `regulations.jsonl` output |

Claude's sandboxed web tools are restricted from bulk web fetching, so Claude
authored the scripts and verified the site structure, but **you execute the
downloads**. Claude then helps parse, validate, and calibrate the ingested results.

## 3. Pipeline

### Circulars (existing)

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

### Regulations (new — `scrape_regulations.py`)

```
fetch listing (sid=1, ssid=3, single page, 42 rows)
   -> (year, url, title, short_name, last_amended) per row
for each regulation:
   fetch detail page -> extract PDF url (same viewer iframe mechanism)
   download PDF -> data/raw/regulations/<id>.pdf  (skip if --skip-pdfs)
   write RegulationMeta record -> data/corpus/regulations.jsonl
reg_lineage.synthesise_repealed_stubs()   # derives repealed regs from corpus citations
make reg-edges                           # build regulation edges
```

Reuses already-built, tested components: `ingest_pdf.py`, `lineage.py`,
`calibrate.py`, and `extract_pdf_urls()` (shared from `scrape_sebi.py`).

## 4. Scope (configurable CLI args)

### Circulars (`scrape_sebi.py`)

- `--section` — `circulars` (ssid=7, ~2.8k total) or `master-circulars` (ssid=6, ~135)
- `--from / --to` issue-date range (default: last 12 months)
- `--max` cap on circulars per run (default 25 — start small, verify, scale)
- `--rate` seconds between requests (default 3.0)
- `--out` raw PDF directory (default `data/raw`)
- `--corpus` corpus JSONL path (default `data/corpus/circulars.jsonl`)
- `--ocr` — OCR fallback for scanned PDFs

### Regulations (`scrape_regulations.py`)

- `--rate` seconds between requests (default 3.0)
- `--out` regulations JSONL path (default `data/corpus/regulations.jsonl`)
- `--raw` raw PDF directory (default `data/raw/regulations`)
- `--skip-pdfs` — identity-only; do not download regulation PDFs

## 5. Commands

### Circulars

Sections (sid=1 Legal): **ssid=7 Circulars** (~2.8k records),
**ssid=6 Master Circulars** (~135). Pagination is a POST; the scraper has a
no-advance guard that stops safely if the POST params need tuning (verify on a
>1-page run).

Current corpus: **705 circular records** in `circulars.jsonl` (as of 2026-07-25).

```bash
# 1. discover + download (run on your Mac)
PYTHONPATH=src .venv/bin/python scripts/scrape_sebi.py \
    --section circulars --from 2025-01-01 --to 2026-06-30 --max 50 --rate 3 [--ocr]

# 2. lineage + recalibration (Claude can run / assist)
PYTHONPATH=src .venv/bin/python -c "from sebi_rag.lineage import annotate_corpus; print(annotate_corpus('data/corpus/circulars.jsonl'))"
HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 \
PYTORCH_ENABLE_MPS_FALLBACK=1 PYTHONPATH=src .venv/bin/python scripts/calibrate.py
```

### Regulations

Section sid=1 ssid=3: "List of All SEBI Regulations (Updated)" — 42 in-force
regulations on a **single page** with no pagination. Repealed regulations sit
behind a `showHistory()` control defined in external JS under `/js`, which
robots.txt disallows. They are therefore **NOT scraped**; `reg_lineage.synthesise_repealed_stubs()`
derives them from corpus citations.

Current corpus: **90 regulation records** in `regulations.jsonl` (as of 2026-07-23).

```bash
# 1. fetch listing + download PDFs
PYTHONPATH=src .venv/bin/python scripts/scrape_regulations.py --rate 3

# Identity-only (no PDF downloads):
PYTHONPATH=src .venv/bin/python scripts/scrape_regulations.py --rate 3 --skip-pdfs

# 2. build regulation edges
make reg-edges
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
- **Repealed regulations (SOLVED):** Not scraped (JS behind `/js` disallowed).
  `reg_lineage.synthesise_repealed_stubs()` derives stub records from circular
  citations in the corpus.
- **2026 site migration (SOLVED):** Detail pages embed PDFs via a viewer iframe
  (`src='../../../web/?file=<pdf-url>'`). PDFs live under
  `/sebi_data/attachdocs/<mon-yyyy>/<stem>.pdf` (flat legacy paths 404).
  `extract_pdf_urls()` resolves the current URL from the detail page — never
  predicts static PDF names. Handles absolute, relative, and URL-encoded targets.

## 7. Verification after each batch

### Circulars
- `wc -l data/corpus/circulars.jsonl` (currently 705); spot-check 3 records' number/date/subject.
- `pytest -m "not integration"` stays green.
- Re-run calibration; confirm citation precision and abstention hold.

### Regulations
- `wc -l data/corpus/regulations.jsonl` (currently 90); spot-check 3 records' reg_id/short_name/year.
- `pytest -m "not integration"` stays green (includes 18 regulation-specific tests).
- `make reg-edges` completes without errors.

## 8. Test coverage

- `tests/test_scrape_sebi.py` — 15 tests: circular href matching, row parsing,
  date filtering, pagination error handling, no-advance guard, PDF URL extraction
  (viewer iframe absolute/relative/URL-encoded, anchor fallback, multi-PDF order,
  off-origin exclusion, magic-byte validation).
- `tests/test_scrape_regulations.py` — 18 tests: listing parses 42 rows, year/url/title
  extraction, short name extraction (nested parens, curly braces, no SEBI prefix),
  last-amended date parsing (including SEBI's own typos), unique reg_id generation,
  fixture captured 2026-07-22.
