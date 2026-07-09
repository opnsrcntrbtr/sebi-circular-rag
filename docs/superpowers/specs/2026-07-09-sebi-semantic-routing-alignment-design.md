# SEBI Semantic-Routing Alignment — Scraper Hardening & Missing-PDF Recovery Design

**Date:** 2026-07-09
**Status:** Draft — pending user review
**Owner:** ianpinto
**Supersedes:** the BLOCKED status of Task 11 in `docs/superpowers/plans/2026-07-08-regai-inspired-enhancements.md`

## Background: what SEBI changed (verified live, 2026-07-09)

SEBI migrated PDF hosting as part of a site modernisation:

- **Detail pages unchanged:** circulars remain at `sebi.gov.in/legal/circulars/[month-year]/[slug]_[id].html` (semantic routing); listings remain at `sebiweb/home/HomeAction.do?doListing` with AJAX pagination.
- **PDF hosting moved:** flat `/sebi_data/attachdocs/{stem}.pdf` → month-year subfolders `/sebi_data/attachdocs/{mon-yyyy}/{stem}.pdf`. Old flat URLs are hard 404s (static error page, no redirect). **Numeric stems are preserved** (verified: 2023 circular `1689245602256.pdf` now at `attachdocs/jul-2023/1689245602256.pdf`).
- **Viewer wrapper:** detail pages embed the PDF via `<iframe src='../../../web/?file=https://www.sebi.gov.in/sebi_data/attachdocs/{mon-yyyy}/{stem}.pdf'>`. Direct GET of the inner URL returns `200 application/pdf`.
- **Blind reconstruction is unreliable:** `attachdocs/{epoch-month}/{stem}.pdf` 404'd for a missing stem (`jan-2024/1705319176210.pdf`); authoritative resolution requires extracting the URL from the circular's detail page.

## Alignment assessment of the current system

| Component | Status | Evidence |
|---|---|---|
| `discover()` listing + AJAX pagination (`scripts/scrape_sebi.py`) | **Aligned** — already targets the dynamic entry points | Listing pages return 200; pagination logic unchanged by migration |
| `pdf_url_for()` regex extraction from detail pages | **Working but brittle** | `PDF_HREF` matched live 2026 and 2023 pages (absolute URL inside iframe src). Breaks silently if SEBI switches to relative/encoded `file=` params; first-match-only loses multi-annexure PDFs; zero test coverage |
| PDF download + stem filename derivation | **Aligned** | Extracted new-format URL downloads fine; `rsplit("/",1)[-1]` still yields `{stem}.pdf` |
| `scripts/acquire_missing_pdfs.py` | **Broken** | Predicts flat static URLs from hardcoded stems — the exact anti-pattern the migration killed. Root cause of Task 11's "blocked" status; **the block is now resolvable** |
| Corpus `source_url` fields | **Aligned** | Detail-page URLs, all still live |
| `tests/test_scrape_sebi.py` | **Gap** | Covers listing parsing/pagination only; nothing on PDF-URL extraction |

**Conclusion:** no wholesale shift of the parsing base is required — the scraper already enters via `/legal/` + `/sebiweb/home/` and extracts PDF URLs dynamically. Required work is (1) hardening the extractor to be viewer-structure-aware instead of pattern-lucky, and (2) reworking the missing-PDF recovery script to resolve detail pages instead of predicting static names.

## Design

### Component 1: `extract_pdf_urls(html: str, base_url: str) -> list[str]`

New pure function in `scripts/scrape_sebi.py`; `pdf_url_for()` becomes a thin wrapper returning the first result (no change to `main()`).

Extraction order (deduped, page order preserved; first hit = primary document):
1. **Viewer-aware:** parse `iframe`/`embed`/`object` `src` attributes; when the src is a `web/?file=<target>` wrapper, URL-decode the `file` parameter; resolve relative srcs/targets against `base_url` via `urllib.parse.urljoin`.
2. **Anchors:** `href` values ending `.pdf` (absolute or relative, resolved against `base_url`).
3. **Fallback:** existing `PDF_HREF` absolute-URL regex scan (kept as safety net).

Only URLs on `www.sebi.gov.in` are returned (same-origin guard, preserves the existing SSRF posture). Multi-annexure pages: `main()` ingests the primary PDF only (corpus model is one record per circular); additional URLs are logged as skipped attachments. Multi-annexure ingestion is explicitly out of scope.

### Component 2: recovery of the 14 missing PDFs (`scripts/acquire_missing_pdfs.py` v2)

Stems (epoch-ms) span Jan 2024 – Jan 2025. Per unique month across all stems, with ±1 month tolerance:
1. Derive date window from stem epoch; run existing `discover("circulars", ...)` (and `master-circulars` if unresolved) over that window to collect detail URLs.
2. Fetch each detail page once (cached in-run), extract PDF URLs via `extract_pdf_urls`, index by trailing stem.
3. For each matched stem: download, verify PDF magic bytes, write `{stem}.pdf` + `.sha256`, ingest with `source_url=<detail page URL>` (provenance improvement over v1's direct-PDF URL).
4. Report per-stem outcome; exit non-zero if any stem stays unresolved. Unresolved stems are documented as possibly withdrawn documents.

Politeness: reuse `fetch()` with the 3 s rate limit; estimated ≲300 requests total for the one-time recovery.

### Component 3: hardening & compliance

- **PDF magic-byte check** (`%PDF` prefix) before writing any downloaded file, in both scripts — prevents persisting HTML error pages as `.pdf`.
- **robots.txt re-verification step** in the recovery run (log-only): confirm `/legal/` and `/sebi_data/attachdocs/` subpaths remain allowed; update the scraper docstring's legality note to describe the month-year structure and viewer wrapper.

### Error handling

- No PDF URL extractable → log detail URL and count as failed (existing behavior, now far less likely).
- Non-PDF payload → failure, file not written.
- `discover()` pagination stall / WAF block → existing guarded stop; recovery reports affected stems as unresolved rather than crashing.

### Testing (offline, no network)

New fixtures + tests in `tests/test_scrape_sebi.py` (or `tests/test_pdf_extract.py` if it grows):
1. Live-shape fixture: single-quoted iframe with `../../../web/?file=<absolute new-format URL>` → extracted.
2. Relative viewer target: `web/?file=/sebi_data/attachdocs/jul-2026/x.pdf` → resolved absolute.
3. URL-encoded `file` param → decoded.
4. Direct `<a href>` (absolute and relative) → resolved.
5. Multi-PDF page → all returned, order preserved, `pdf_url_for` returns first.
6. No PDF → empty list / `None`.
7. Off-origin PDF URL → excluded.
8. Recovery: stem→month-window mapping; stem matching against stubbed detail pages; magic-byte rejection of HTML payloads.

Regression: full offline suite stays green; existing `parse_rows`/pagination tests unchanged.

### Success criteria

1. All new and existing offline tests pass.
2. Live smoke test: `scrape_sebi.py --max 2` ingests current circulars end-to-end.
3. Recovery run resolves and ingests the missing circulars (target: all 14; any misses individually explained), `validate_corpus.py` passes on the grown corpus, then `make reindex`.
4. Enhancement plan Task 11 flipped from BLOCKED to done/unblocked, referencing this spec.

## Out of scope

- Multi-annexure ingestion into the corpus schema.
- Any change to ingest/segmentation/lineage logic.
- Bulk re-download of already-held PDFs (all 603 corpus records keep their local files; only the 14 gaps are acquired).
