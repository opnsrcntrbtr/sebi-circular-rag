# HF Hub Dataset Push Runbook (dist/datasets → opnsrcntrbtrian/sebi-circulars)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> **Harness-agnostic:** This plan is executable by ANY agent (Claude Code with any model, a local model, or another agent harness) or by a human. It uses only `bash`, `git`, `curl`, and the project's `.venv` Python. No MCP tools, no editor-specific features. Every step has an explicit command and its expected output; every gate has an abort rule.

**Goal:** Publish the regenerated `dist/datasets/` (which adds `circular_type`, `validity_status`, `superseded_by_id`, `supersession_edges` from the 2026-07 metadata-layer migration) to the live Hugging Face dataset repo `opnsrcntrbtrian/sebi-circulars`, safely and reversibly.

**Architecture:** Fix the stale hardcoded row counts in the card generator, regenerate `dist/datasets`, snapshot the live repo as a rollback asset, then push via a new committed script (`scripts/push_datasets.py`, modeled on the existing `scripts/upload_spaces_index.py`) that uploads the six config directories + root metadata files + a provenance copy of `export_datasets.py` — exactly matching the live repo's current layout. Verify remotely via the HF tree API and datasets-server rows API.

**Tech Stack:** Python 3.12 (`.venv`), `huggingface_hub` (already a dependency — used by `scripts/upload_spaces_index.py`), `pytest`, `curl`.

## Global Constraints

- Target repo: `opnsrcntrbtrian/sebi-circulars`, `repo_type="dataset"`. Never create a different repo; `exist_ok=True` only.
- **NEVER print, echo, or log the HF token.** Auth is via cached login or the `HF_TOKEN` env var, checked only with `whoami`-style calls.
- Upload EXCLUDES `dist/datasets/AIKOSH_SUBMISSION_PACK/` and `dist/datasets/ZENODO_SUBMISSION_PACK/` (platform packs — not on the live repo).
- Upload INCLUDES (matching the live repo root, verified 2026-07-12): `README.md`, `manifest.json`, `metadata.json`, the six config dirs (`chunks/ citation-normalization/ corpus/ eval/ lineage/ supersession-pairs/`, each with `.jsonl` + `.parquet`), and a copy of `scripts/export_datasets.py` at repo-root path `export_datasets.py` (provenance).
- The actual push (Task 5 Step 3) is **gated on explicit human confirmation** in the harness. Do not pass `--yes` without it.
- Run all commands from the repo root: `/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG` (quote the path — it contains a space).
- Expected corpus state (from the accepted migration milestone): `corpus.jsonl` sha256 `5645fd7942a37a1d98118f627ce4bd7bc0fd06c7a5dde333e88c7c35b08d38c6`, `chunks.jsonl` sha256 `e221f6956152f9bf40542fdf90b9a1983388b37e2806a65adb934f3938e598e3`, row counts `corpus=603, chunks=36683, lineage=1437, eval=56, citation-normalization=2951, supersession-pairs=1281`.
- **Abort rule (all tasks):** if a gate's actual output does not match its expected output, STOP, do not push, and report the mismatch verbatim to the user. Do not improvise fixes beyond this plan.

---

### Task 1: Preflight gates (read-only)

**Files:** none modified.

- [ ] **Step 1: Verify git state**

```bash
cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG"
git branch --show-current
git status --short -- src scripts tests Makefile docs
```

Expected: branch `spaces`; status output empty (untracked/ignored data files are fine; tracked-file modifications are NOT — abort if any appear).

- [ ] **Step 2: Verify local artifacts match the accepted milestone**

```bash
shasum -a 256 data/corpus/circulars.jsonl data/index/chunks.jsonl
```

Expected (abort on mismatch — it means the corpus changed since the accepted milestone; regenerate/re-review first):

```
5645fd7942a37a1d98118f627ce4bd7bc0fd06c7a5dde333e88c7c35b08d38c6  data/corpus/circulars.jsonl
e221f6956152f9bf40542fdf90b9a1983388b37e2806a65adb934f3938e598e3  data/index/chunks.jsonl
```

- [ ] **Step 3: Verify manifest matches those shas and the expected row counts**

```bash
.venv/bin/python -c "
import json
m = json.load(open('dist/datasets/manifest.json'))
c = m['configs']
assert c['corpus']['source_sha256'] == '5645fd7942a37a1d98118f627ce4bd7bc0fd06c7a5dde333e88c7c35b08d38c6', c['corpus']
assert c['chunks']['source_sha256'] == 'e221f6956152f9bf40542fdf90b9a1983388b37e2806a65adb934f3938e598e3', c['chunks']
rows = {k: v['rows'] for k, v in c.items()}
assert rows == {'corpus': 603, 'chunks': 36683, 'lineage': 1437, 'eval': 56,
                'citation-normalization': 2951, 'supersession-pairs': 1281}, rows
print('manifest OK:', rows, '| version', m['version'])
"
```

Expected: `manifest OK: {...} | version v2026.07`

- [ ] **Step 4: Verify HF auth without exposing the token**

```bash
.venv/bin/python -c "
from huggingface_hub import HfApi
u = HfApi().whoami()
print('authenticated as:', u['name'])
"
```

Expected: `authenticated as: opnsrcntrbtrian`. If this raises (401 / no token): STOP and ask the user to either run `hf auth login` in a terminal or export `HF_TOKEN`. Do not ask the user to paste the token into the conversation.

- [ ] **Step 5: Verify offline test suite is green before touching anything**

```bash
make test 2>&1 | tail -1
```

Expected: `199 passed, 2 deselected, 1 warning in ...` (count may be higher if tests were added since; zero failures is the gate).

---

### Task 2: Snapshot the live repo (rollback asset)

**Files:**
- Create: `dist/backups/hf-sebi-circulars-pre-push/` (under `dist/`, which is gitignored — never commit this)

- [ ] **Step 1: Download the current live snapshot (~180 MB)**

```bash
.venv/bin/python -c "
from huggingface_hub import snapshot_download
p = snapshot_download(repo_id='opnsrcntrbtrian/sebi-circulars', repo_type='dataset',
                      local_dir='dist/backups/hf-sebi-circulars-pre-push')
print('backup at:', p)
"
```

Expected: prints the backup path; takes a few minutes.

- [ ] **Step 2: Verify the backup is complete**

```bash
ls dist/backups/hf-sebi-circulars-pre-push
.venv/bin/python -c "
from pathlib import Path
b = Path('dist/backups/hf-sebi-circulars-pre-push')
need = ['README.md', 'manifest.json', 'metadata.json', 'export_datasets.py',
        'chunks', 'citation-normalization', 'corpus', 'eval', 'lineage', 'supersession-pairs']
missing = [n for n in need if not (b / n).exists()]
assert not missing, f'backup incomplete: {missing}'
print('backup complete')
"
```

Expected: `backup complete`. Abort the whole runbook if the backup is incomplete — the rollback path (Task 7) depends on it.

---

### Task 3: Fix stale hardcoded counts in the card generator (TDD via existing suite)

The dataset card table, Kaggle description, and Zenodo date in `scripts/export_datasets.py` are hardcoded to the pre-migration counts (`36,603` chunks / `1,434` lineage / date `2026-07-09`). The manifest already carries the true counts; the card must match. The test fixtures in `tests/test_dataset_cards.py` pin the same stale numbers and must move in lockstep.

**Files:**
- Modify: `scripts/export_datasets.py` (4 exact-string replacements below)
- Modify: `tests/test_dataset_cards.py` (mechanical count updates)

- [ ] **Step 1: Confirm the exact current text** (protects against drift since this plan was written)

```bash
grep -n "36,603\|1,434\|2026-07-09" scripts/export_datasets.py
```

Expected — exactly these four content sites (line numbers approximate):

```
430:**Date:** 2026-07-09
439:| **chunks** | 36,603 | Section-aware retrieval chunks | RAG, dense retrieval, section-level analysis |
440:| **lineage** | 1,434 | Regulatory supersession edges | Citation graph, link prediction, lineage reasoning |
563:- **Extraction date:** 2026-07-09
588:            "Six configurations: corpus (603 circulars), chunks (36,603 retrieval chunks), "
589:            "lineage (1,434 supersession/amendment edges), eval (56-query benchmark), "
627:            "publication_date": "2026-07-09",
```

(Line 563 `Extraction date` is the true PDF-extraction date — leave it unchanged. Line 6 / 49 comment mentions of 2026-07-09 are docs — leave unchanged.)

- [ ] **Step 2: Apply the six replacements** (exact old → new, one at a time)

In `scripts/export_datasets.py`:

1. `**Date:** 2026-07-09` → `**Date:** 2026-07-12`
2. `| **chunks** | 36,603 | Section-aware retrieval chunks | RAG, dense retrieval, section-level analysis |` → `| **chunks** | 36,683 | Section-aware retrieval chunks | RAG, dense retrieval, section-level analysis |`
3. `| **lineage** | 1,434 | Regulatory supersession edges | Citation graph, link prediction, lineage reasoning |` → `| **lineage** | 1,437 | Regulatory supersession edges | Citation graph, link prediction, lineage reasoning |`
4. `"Six configurations: corpus (603 circulars), chunks (36,603 retrieval chunks), "` → `"Six configurations: corpus (603 circulars), chunks (36,683 retrieval chunks), "`
5. `"lineage (1,434 supersession/amendment edges), eval (56-query benchmark), "` → `"lineage (1,437 supersession/amendment edges), eval (56-query benchmark), "`
6. `"publication_date": "2026-07-09",` → `"publication_date": "2026-07-12",`

In `tests/test_dataset_cards.py`, replace **every** occurrence (they are fixture dicts and assertions, ~9 sites found by the grep in Step 3):

- `36603` → `36683`
- `36,603` → `36,683`
- `1434` → `1437` (only where it is the lineage `"rows"` value; check each match)

- [ ] **Step 3: Verify no stale numbers remain**

```bash
grep -n "36,603\|36603\|1,434" scripts/export_datasets.py tests/test_dataset_cards.py; echo "grep-done rc=$?"
```

Expected: no matches printed, `grep-done rc=1`.

- [ ] **Step 4: Run the affected tests**

```bash
.venv/bin/python -m pytest tests/test_dataset_cards.py tests/test_export_datasets.py tests/test_export_integration.py -q
```

Expected: all pass, zero failures.

- [ ] **Step 5: Commit**

```bash
git add scripts/export_datasets.py tests/test_dataset_cards.py
git commit -m "fix: update dataset card counts to post-migration actuals (36683 chunks, 1437 lineage)"
```

---

### Task 4: Regenerate the export and gate it

**Files:**
- Regenerates: `dist/datasets/` (gitignored)

- [ ] **Step 1: Regenerate**

```bash
make export-datasets 2>&1 | tail -45
```

Expected: JSON manifest printed with `"version": "v2026.07"` and the six configs at the expected row counts (`603 / 36683 / 1437 / 56 / 2951 / 1281`), no traceback.

- [ ] **Step 2: Gate — card, manifest, and data agree; new fields present**

```bash
.venv/bin/python -c "
import json
card = open('dist/datasets/README.md').read()
assert '36,683' in card and '1,437' in card and '**Date:** 2026-07-12' in card, 'card stale'
for col in ('circular_type', 'validity_status', 'superseded_by_id', 'supersession_edges'):
    assert col in card, f'card missing column {col}'
row = json.loads(open('dist/datasets/corpus/corpus.jsonl').readline())
for col in ('circular_type', 'validity_status', 'superseded_by_id', 'supersession_edges'):
    assert col in row, f'corpus row missing {col}'
crow = json.loads(open('dist/datasets/chunks/chunks.jsonl').readline())
for col in ('circular_type', 'validity_status', 'superseded_by_id'):
    assert col in crow, f'chunk row missing {col}'
print('export gate OK')
"
```

Expected: `export gate OK`

- [ ] **Step 3: Full suite still green**

```bash
make test 2>&1 | tail -1
```

Expected: zero failures.

---

### Task 5: Push script + the push itself

**Files:**
- Create: `scripts/push_datasets.py`
- Test: `tests/test_push_datasets.py`

**Interfaces:**
- Produces: `upload_plan(dist: Path) -> list[tuple[Path, str]]` — pure function returning `(local_path, path_in_repo)` pairs; and a CLI `python scripts/push_datasets.py --repo opnsrcntrbtrian/sebi-circulars [--yes]`.

- [ ] **Step 1: Write the failing test** — create `tests/test_push_datasets.py`:

```python
"""Offline tests for the HF dataset push script (no network)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import push_datasets as P  # noqa: E402


def _fake_dist(tmp_path: Path) -> Path:
    dist = tmp_path / "datasets"
    for d in P.CONFIG_DIRS:
        (dist / d).mkdir(parents=True)
        (dist / d / f"{d}.jsonl").write_text("{}\n")
        (dist / d / f"{d}.parquet").write_bytes(b"PAR1")
    for f in P.ROOT_FILES:
        (dist / f).write_text("x")
    # platform packs that must be excluded
    (dist / "AIKOSH_SUBMISSION_PACK").mkdir()
    (dist / "AIKOSH_SUBMISSION_PACK" / "manifest.csv").write_text("x")
    (dist / "ZENODO_SUBMISSION_PACK").mkdir()
    (dist / "ZENODO_SUBMISSION_PACK" / "metadata.json").write_text("x")
    return dist


def test_upload_plan_includes_configs_and_root_files(tmp_path):
    plan = P.upload_plan(_fake_dist(tmp_path))
    repo_paths = {rp for _, rp in plan}
    assert "README.md" in repo_paths
    assert "manifest.json" in repo_paths
    assert "metadata.json" in repo_paths
    assert "corpus/corpus.jsonl" in repo_paths
    assert "corpus/corpus.parquet" in repo_paths
    assert "chunks/chunks.parquet" in repo_paths
    assert "export_datasets.py" in repo_paths  # provenance copy


def test_upload_plan_excludes_platform_packs(tmp_path):
    plan = P.upload_plan(_fake_dist(tmp_path))
    for _, rp in plan:
        assert "AIKOSH" not in rp and "ZENODO" not in rp


def test_upload_plan_fails_on_missing_config(tmp_path):
    dist = _fake_dist(tmp_path)
    (dist / "eval" / "eval.jsonl").unlink()
    import pytest
    with pytest.raises(SystemExit):
        P.upload_plan(dist)
```

- [ ] **Step 2: Run to verify failure**

```bash
.venv/bin/python -m pytest tests/test_push_datasets.py -q
```

Expected: collection error `ModuleNotFoundError: No module named 'push_datasets'`.

- [ ] **Step 3: Create `scripts/push_datasets.py`:**

```python
"""Push dist/datasets to the live HF Hub dataset repo (default:
opnsrcntrbtrian/sebi-circulars), matching the live repo layout exactly:
six config dirs + README.md + manifest.json + metadata.json + a provenance
copy of scripts/export_datasets.py at repo root. Platform submission packs
(AIKOSH/ZENODO) are never uploaded.

Runbook: docs/superpowers/plans/2026-07-12-hf-dataset-push-runbook.md
Regenerate first:  make export-datasets
Dry-run (default): .venv/bin/python scripts/push_datasets.py
Real push:         .venv/bin/python scripts/push_datasets.py --yes
"""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist" / "datasets"
CONFIG_DIRS = ["chunks", "citation-normalization", "corpus", "eval",
               "lineage", "supersession-pairs"]
ROOT_FILES = ["README.md", "manifest.json", "metadata.json"]


def upload_plan(dist: Path) -> list[tuple[Path, str]]:
    """(local_path, path_in_repo) pairs; SystemExit if anything is missing."""
    pairs: list[tuple[Path, str]] = []
    missing: list[str] = []
    for name in ROOT_FILES:
        p = dist / name
        pairs.append((p, name)) if p.exists() else missing.append(name)
    for d in CONFIG_DIRS:
        cfg = dist / d
        expected = [cfg / f"{d}.jsonl", cfg / f"{d}.parquet"]
        for p in expected:
            if p.exists():
                pairs.append((p, f"{d}/{p.name}"))
            else:
                missing.append(str(p.relative_to(dist)))
    exporter = ROOT / "scripts" / "export_datasets.py"
    if exporter.exists():
        pairs.append((exporter, "export_datasets.py"))
    else:
        missing.append("scripts/export_datasets.py")
    if missing:
        raise SystemExit(f"refusing to push, missing artifacts: {missing} "
                         f"(run `make export-datasets` first)")
    return pairs


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", default="opnsrcntrbtrian/sebi-circulars")
    ap.add_argument("--dist", default=str(DIST))
    ap.add_argument("--yes", action="store_true",
                    help="actually upload; without it, print the plan and exit")
    args = ap.parse_args()

    pairs = upload_plan(Path(args.dist))
    total = sum(p.stat().st_size for p, _ in pairs)
    print(f"upload plan -> {args.repo} ({len(pairs)} files, "
          f"{total / 1e6:.1f} MB):")
    for p, rp in pairs:
        print(f"  {rp:45s} {p.stat().st_size / 1e6:8.1f} MB")
    if not args.yes:
        print("\nDRY RUN ONLY. Re-run with --yes to push.")
        return

    from huggingface_hub import HfApi
    api = HfApi()
    api.create_repo(args.repo, repo_type="dataset", exist_ok=True)
    for p, rp in pairs:
        api.upload_file(path_or_fileobj=str(p), path_in_repo=rp,
                        repo_id=args.repo, repo_type="dataset",
                        commit_message=f"Metadata layer migration v2026.07: {rp}")
    print(f"pushed {len(pairs)} files -> "
          f"https://huggingface.co/datasets/{args.repo}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Tests pass; dry run looks right**

```bash
.venv/bin/python -m pytest tests/test_push_datasets.py -q
.venv/bin/python scripts/push_datasets.py
```

Expected: `3 passed`; then a printed plan of **16 files** (3 root + 6×2 config files + 1 exporter, ~165 MB total) ending with `DRY RUN ONLY. Re-run with --yes to push.`

- [ ] **Step 5: Commit the script (before pushing — the push must be reproducible)**

```bash
git add scripts/push_datasets.py tests/test_push_datasets.py
git commit -m "feat: add gated push script for the sebi-circulars HF dataset repo"
```

- [ ] **Step 6: 🛑 HUMAN GATE — ask the user, in so many words:** "Dry run above shows N files / M MB going to `opnsrcntrbtrian/sebi-circulars`. Confirm push?" Only on an explicit yes:

```bash
.venv/bin/python scripts/push_datasets.py --yes 2>&1 | tail -5
```

Expected: ends with `pushed 16 files -> https://huggingface.co/datasets/opnsrcntrbtrian/sebi-circulars`. (Upload of ~165 MB takes several minutes.)

---

### Task 6: Post-push verification (read-only, remote)

- [ ] **Step 1: Repo tree contains all configs + root files**

```bash
curl -sL "https://huggingface.co/api/datasets/opnsrcntrbtrian/sebi-circulars/tree/main" | .venv/bin/python -c "
import json, sys
paths = {x['path'] for x in json.load(sys.stdin)}
need = {'README.md', 'manifest.json', 'metadata.json', 'export_datasets.py',
        'chunks', 'citation-normalization', 'corpus', 'eval', 'lineage', 'supersession-pairs'}
assert need <= paths, f'missing on hub: {need - paths}'
print('tree OK:', sorted(paths))
"
```

Expected: `tree OK: [...]` with no assertion error.

- [ ] **Step 2: Live README shows the new counts and columns**

```bash
curl -sL "https://huggingface.co/datasets/opnsrcntrbtrian/sebi-circulars/raw/main/README.md" | .venv/bin/python -c "
import sys
card = sys.stdin.read()
for s in ('36,683', '1,437', 'circular_type', 'validity_status', 'superseded_by_id', 'supersession_edges'):
    assert s in card, f'live card missing: {s}'
print('live card OK')
"
```

Expected: `live card OK`

- [ ] **Step 3: datasets-server exposes the new columns** (the viewer reprocesses asynchronously — retry every ~5 min, up to 30 min, before treating as failure)

```bash
curl -sL "https://datasets-server.huggingface.co/rows?dataset=opnsrcntrbtrian%2Fsebi-circulars&config=corpus&split=train&offset=0&length=1" | .venv/bin/python -c "
import json, sys
d = json.load(sys.stdin)
cols = {f['name'] for f in d.get('features', [])}
need = {'circular_type', 'validity_status', 'superseded_by_id'}
assert need <= cols, f'viewer missing {need - cols} (may still be reprocessing — retry)'
print('viewer OK:', sorted(need))
"
```

Expected (eventually): `viewer OK: [...]`. If still failing after 30 min, check `https://datasets-server.huggingface.co/is-valid?dataset=opnsrcntrbtrian%2Fsebi-circulars` and report the error to the user; the raw files (Steps 1–2) are the authoritative success signal.

- [ ] **Step 4: Spaces demo note (no action unless asked).** The live Space (`opnsrcntrbtrian/sebi-circular-rag-demo`) loads this dataset only at startup and reads columns by name, so the additive columns are backward-compatible. It will pick up new data on its next restart/rebuild. Do not restart it as part of this runbook.

---

### Task 7: Rollback procedure (ONLY if the push corrupted the live repo)

Skip this task entirely on success. If Task 6 reveals broken/missing files:

- [ ] **Step 1: Re-upload the pre-push snapshot taken in Task 2**

```bash
.venv/bin/python -c "
from huggingface_hub import HfApi
api = HfApi()
api.upload_folder(folder_path='dist/backups/hf-sebi-circulars-pre-push',
                  repo_id='opnsrcntrbtrian/sebi-circulars', repo_type='dataset',
                  ignore_patterns=['.cache/**', '.gitattributes'],
                  commit_message='Rollback to pre-migration-push snapshot')
print('rolled back')
"
```

- [ ] **Step 2: Re-run Task 6 Steps 1–2** expecting the OLD values (`36,603`, `1,434`, no `circular_type` requirement). Report the rollback and the original failure to the user.

---

### Task 8: Record completion

- [ ] **Step 1:** Append to `docs/superpowers/plans/2026-07-12-metadata-layer-migration.md`, at the very end:

```markdown

## HF Hub Push (executed <DATE>)

Pushed regenerated dist/datasets (v2026.07, +circular_type/validity_status/
superseded_by_id/supersession_edges) to opnsrcntrbtrian/sebi-circulars per
docs/superpowers/plans/2026-07-12-hf-dataset-push-runbook.md. All Task 6
verification gates passed. Migration fully shipped.
```

(Replace `<DATE>` with the actual push date.)

- [ ] **Step 2: Commit**

```bash
git add docs/superpowers/plans/2026-07-12-metadata-layer-migration.md docs/superpowers/plans/2026-07-12-hf-dataset-push-runbook.md
git commit -m "docs: record HF dataset push completion"
```

- [ ] **Step 3 (optional, housekeeping):** the backup in `dist/backups/` can be deleted after a week of stable operation; it is gitignored either way.
