# Human Packet Handoff — Step-by-Step Instructions

**Purpose:** Manually label 30 SEBI circular rows to promote them to `adjudicated` status, contributing to the CI gate that flips when `adjudicated_n >= 100`.

**Current state:** 65 adjudicated (35 short of gate). This packet covers 30 rows from the external-100 sample. ~20 of these are expected to promote if the human's labels agree with claude/qwen at the provision level.

---

## Prerequisites

- Work in the `golden-v7` worktree:
  ```bash
  cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG/.worktrees/golden-v7"
  ```

- Ensure these files exist in `eval/golden/v7_annotations/packet_human/`:
  - `packet.html` — the blind review interface (500 KB, opens in browser)
  - `labels_template.csv` — the fillable answer sheet (30 rows)
  - `manifest.json` — internal letter→chunk_id mapping (do NOT edit)

---

## Step 1: Open the Packet HTML

Open `eval/golden/v7_annotations/packet_human/packet.html` in your browser.

You will see 30 collapsible entries, each showing:
- **Row ID** (e.g., `swagat`, `v7-bp-026`) — in the summary line
- **Query** — the question the row was designed to answer
- **Prompt** — either:
  - `"Which excerpt(s) contain the governing provision, or none?"` (non-abstain rows)
  - `"Is this answerable from SEBI circulars? (yes = flag, no = confirm abstain)"` (abstain rows)

For each non-abstain row, expand `<details>` to see:
- A shuffled list of excerpt options labeled **A, B, C, …** (up to 20)
- Each excerpt shows the circular reference and a text snippet

**Key: The excerpts are shuffled per row. You see only letters — never the original ordering.**

---

## Step 2: Fill `labels_template.csv`

Open `eval/golden/v7_annotations/packet_human/labels_template.csv` in a spreadsheet editor (Excel, Sheets, etc.).

The CSV has 3 columns:

| Column | What it means |
|---|---|
| `id` | Row identifier (do NOT edit) |
| `choices` | Letter(s) of the governing excerpt(s) — **fill this for non-abstain rows** |
| `expected_literal` | The key provision text — **fill this for ALL rows** |

### For non-abstain rows (22 rows):

1. **Read the query** at the top of each `<details>` block.
2. **Expand the `<details>`** to see the shuffled excerpt options (A, B, C, …).
3. **Read each excerpt** carefully. Identify which excerpt(s) contain the **governing provision** — the specific rule, threshold, or requirement that answers the query.
4. **Enter the letter(s)** in the `choices` column:
   - Single answer: `P`
   - Multiple answers: `A;C;E` (semicolon-separated, no spaces required)
   - If NO excerpt contains the governing provision: type `none`
5. **Enter the expected_literal** — paste the key provision text from the excerpt you selected. This should be a distinctive phrase (≥ 40 chars after whitespace normalization) that uniquely identifies the provision.

**Example for row `swagat`:**
- Query: "Single Window Automatic and Generalised Access for Trusted Foreign Investors (SWAGAT-FI) framework for FPIs and FVCIs"
- The governing provision is in excerpt **P**
- `choices` = `P`
- `expected_literal` = `Single Window Automatic and Generalised Access for Trusted Foreign Investors (SWAGAT-FI) framework for FPIs and FVCIs`

### For abstain rows (8 rows):

These rows were pre-set with `choices = "none"` because they have no pooled excerpts to choose from. For these:

1. **Read the abstain prompt:** `"Is this answerable from SEBI circulars? (yes = flag, no = confirm abstain)"`
2. **If you believe the answer IS flaggable** (the circular contains the answer): enter `yes` in `expected_literal`
3. **If you agree it should abstain** (no answerable content): leave `expected_literal` blank (this confirms the abstain)

**Abstain row ids:** `v7-bp-002`, `v7-bp-014`, `v7-bp-019`, `hn-egr`, `v7-hn-022`, `v7-hn-004`, `v7-hn-030`, `v7-fn-009`

### Rules for choices:
- Letters must match what you see in the HTML (A through Z)
- Multiple letters: semicolon-separated, e.g., `A;C;E`
- `none` (lowercase) means "no excerpt contains the governing provision"
- Do NOT leave `choices` blank for non-abstain rows — this is a validation error

### Rules for expected_literal:
- Must be a verbatim substring from one of the excerpts
- Should be distinctive enough to uniquely identify the provision (≥ 40 chars after whitespace normalization)
- For abstain rows: blank confirms abstain; any text disputes it

---

## Step 3: Save the CSV

Save `labels_template.csv` after filling all 30 rows. Ensure:
- No rows are skipped
- No extra columns are added
- The header row (`id,choices,expected_literal`) is preserved

---

## Step 4: Ingest the Filled CSV

Run from the worktree root:

```bash
cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG/.worktrees/golden-v7"
make golden-v7-packet-ingest
```

This runs:
```bash
$(ENV) $(PY) scripts/golden_v7/make_packet.py --ingest eval/golden/v7_annotations/packet_human/labels_template.csv
```

Expected output:
```
ingested 30 human votes -> eval/golden/v7_annotations/votes.jsonl
```

**What this does:**
- Reads your filled `labels_template.csv`
- Maps letters back to chunk IDs using `manifest.json`
- Rewrites `votes.jsonl` with 30 new `annotator: "human"` vote records
- Existing claude and qwen votes are preserved

---

## Step 5: Run the Agreement Protocol

```bash
make golden-v7-agree
```

This runs `scripts/golden_v7/agreement.py` which:
1. Reads all votes (claude: 207, qwen: 100, human: 30)
2. For each of the 100 external rows, applies the promotion rules:
   - **Promote** if the human's label agrees with claude at the **provision level** (exact set match, containment, or any picked chunk's text contains the row's span quote)
   - **Flip-promote** if human + qwen agree on a different alternative than claude
   - **Queue** for arbitration otherwise (including all dated `as_of` rows)
3. Updates `golden_v7.jsonl` — promoted rows get `review_status: "adjudicated"`
4. Writes `arbitration_queue.jsonl` — queued rows with all votes for later review
5. Writes `reports/golden_v7_agreement.md` — kappa statistics per annotator pair per stratum

Expected output:
```
promoted=XX flipped=YY queued=ZZ -> eval/golden/golden_v7.jsonl
```

---

## Step 6: Validate and Commit

```bash
# Run full test suite
make test

# Check the updated state
python3 -c "
import json
from collections import Counter
rows = [json.loads(l) for l in open('eval/golden/golden_v7.jsonl') if l.strip()]
print(f'Adjudicated: {sum(1 for r in rows if r.get(\"review_status\") == \"adjudicated\")}')
"

# Commit if 603 tests pass
git add eval/golden/golden_v7.jsonl eval/golden/v7_annotations/votes.jsonl \
       eval/golden/v7_annotations/arbitration_queue.jsonl reports/golden_v7_agreement.md
git commit -m "data(golden-v7): human packet handoff — XX promoted, YY queued

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Understanding the Gate

The CI gate flips when **both** conditions are met:
1. `eval/golden/gate_v7.json` exists (produced by `make golden-v7-gate`)
2. `adjudicated_n >= 100` in that gate file

**Current status:** 65 adjudicated, 35 short of the gate.

This packet (30 rows) can contribute up to ~20 promotions (some will queue if the human disagrees with claude/qwen at the provision level). You may need additional packets or additional qwen adjudication on queued rows to reach 100.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `make golden-v7-packet-ingest` says "unknown letter" | Check that letters match the HTML exactly (case-sensitive, A-Z only) |
| `make golden-v7-agree` says "no pool record" | The row was escalated during Task 8 and has no pooled excerpts — skip it |
| Tests fail after ingest | Verify `labels_template.csv` has exactly 30 data rows with the header preserved |
| Gate doesn't flip after 100 adjudicated | Run `make golden-v7-gate` first to produce `gate_v7.json`, then rerun `agreement.py` |

---

## Reference: What the Manifest Maps

`manifest.json` maps each row-id to a dictionary of `{letter: chunk_id}`. This is used internally by `ingest_packet()` to convert your letters back to chunk IDs. **Do not edit this file.**

Example entry for row `swagat`:
```json
{
  "A": "HO/19/34/14(5)2025-AFD-POD2/I/2703/2026#6. This Circular is issued...",
  "B": "HO/19/34/14(5)2025-AFD-POD2/I/199/2025#1. Foreign Venture Capital...",
  ...
  "P": "HO/19/34/14(5)2025-AFD-POD2/I/2703/2026#4. The Stock Exchanges..."
}
```

When you enter `choices = "P"`, the ingest script looks up `manifest["swagat"]["P"]` to get the chunk ID for the vote record.
