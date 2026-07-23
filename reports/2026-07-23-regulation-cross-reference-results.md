# SEBI Regulations Cross-Reference Layer — Results

Spec: `docs/superpowers/specs/2026-07-23-sebi-regulations-cross-reference-design.md`
Plan: `docs/superpowers/plans/2026-07-23-sebi-regulations-cross-reference.md`
Run date: 2026-07-23

## Pipeline output

```
make scrape-regs   -> 42/42 regulations, 42/42 with a PDF, 0 failures
make reg-edges     -> Loaded 705 circulars, 42 regulations
                      Synthesised 48 stub(s): 14 repealed, 34 unknown
                      Edges: 1268 across 510 circulars (72.3% of corpus)
                      Annotated (changed): 705 (first run) / 0 (re-run, idempotent)
```

`regulatory_basis_status` distribution:

| Status | Count |
|---|---|
| `current` | 331 |
| `mixed` | 94 |
| `repealed_basis` | 85 |
| `unknown` | 195 |

## Headline signal

Circulars carrying `validity_status: current` (circular-lineage says "in force")
that resolve **only** to repealed regulations:

**`current` + `regulatory_basis_status: repealed_basis` = 29 circulars.**

(Spec's pre-implementation estimate, from a cruder unnormalised regex, was 39 —
same phenomenon, refined count once alias resolution and the table-extraction
guard removed false positives.) A further 45 circulars are `current` + `mixed`
— citing both a live and a repealed regulation. Combined, **74 circulars
(10.5% of the corpus)** carry a regulatory-basis signal invisible to
`validity_status` before this layer existed.

## Regulations

| Status | Count |
|---|---|
| `in_force` (scraped) | 42 |
| `repealed` (curated successor known) | 14 |
| `unknown` (cited, absent from listing, no successor on file) | 34 |

Curated `REG_SUCCESSION` table grew from the plan's 7 entries to 14 during this
run, adding: `venture-capital-funds-1996`, `portfolio-managers-1993`,
`share-based-employee-benefits-2014`, `substantial-acquisition-of-shares-and-
takeovers-1997`, `issue-and-listing-of-non-convertible-redeemable-preference-
shares-2013`, `stock-brokers-and-sub-brokers-1992`,
`procedure-for-holding-enquiry-by-enquiry-officer-and-imposing-penalty-2002`.

## Two implementation bugs found and fixed against real data

1. **FVCI alias typo.** `REGULATION_ALIASES[("fvci", 2000)]` targeted
   `foreign-venture-capital-investors-2000` (plural); SEBI's actual title —
   and therefore the scraped `reg_id` — is singular. The alias would have
   minted a phantom repealed stub next to the real, live regulation. Caught by
   cross-checking every alias/succession target against the 42 scraped
   `reg_id`s before building edges (not part of the original plan; added
   during execution). Fixed, and a regression test
   (`test_every_alias_target_is_in_force_or_has_a_succession_entry`) now
   guards the whole table, not just this one entry.

2. **Trailing-S stripping disabled three acronym aliases.** `_alias_key()`
   unconditionally stripped a trailing "s", so `PMS`, `NCS`, and `ILDS` — where
   the S is part of the acronym, not a plural marker — normalised to `pm`,
   `nc`, `ild` and could never reach their table entries. Found by checking
   citation volume against known aliases post-run. Fixed by trying both the
   literal and stripped forms (`_alias_keys`, plural), with a reachability
   test (`test_every_alias_entry_is_reachable_from_some_spelling`) so a future
   entry can't go silently dead the same way.

## Table-extraction guard (precision fix, not in the original plan)

The first `reg-edges` run produced 96 stub regulations, many with titles like
`Listing Obligations and SEBI/HO/CFD/CMD/C 22. Requirements`. Root cause: SEBI's
PDF table extraction interleaves columns, so a circular number and a row marker
land inside a regulation title that wraps across lines in an appendix table.
Added two rejection signals to `reg_citations.py` — a `/` in the candidate name
(no real regulation title contains one) and the word "Regulations" appearing
anywhere but at the very end (the one legitimate exception,
"...reviewing of Regulations", still ends with it). Verified against all 42
real short names with zero false positives. This cut stub count from 96 to 48
and edge count from 1336 to 1268.

## Gate 1 — suite green

```
443 passed, 3 deselected, 18 warnings
```

Baseline before this work: 350 passed, 3 deselected. **93 new tests, 0
regressions.**

## Gate 2 — coverage

- 510 / 705 circulars (72.3%) carry ≥1 resolved regulation edge — above the
  spec's measured baseline (500 / 705, 70.9%).
- 1268 edges total, split `in_force` 974 / `repealed` (curated) 242 /
  `unknown` (uncurated) 52.
- `reports/unresolved_regulations.txt` is empty by construction: every
  unresolvable citation is minted as a stub rather than left unresolved (spec
  §5), so "unresolved" in this design means an `unknown`-status regulation
  record, not a missing edge.

## Gate 3 — precision

Sampling design departed from the plan's flat 50-edge draw, because a flat
stratified-by-evidence-tier sample drew **zero** edges targeting the 34
`unknown`-status stubs — precisely the subpopulation most likely to contain
errors. Split into two strata instead:

**Stratum A — edges to `in_force` or curated-`repealed` targets (1216 edges,
95.9% of all edges).** 50 sampled, stratified by evidence tier
(subject_line/powers_clause/body_text), seed 20260723.

```
Labelled: 50   correct: 50
Precision: 100.0%  95% CI [92.9%, 100.0%]  (clopper-pearson)
GATE: PASS
```

**Stratum B — edges to `unknown`-status stubs (52 edges, 4.1%), census
(all 52, not sampled).** 35 correctly denote a real, citable regulation SEBI
has not consolidated into a successor mapping yet (e.g. `Underwriters`,
`Regulatory Fee on Stock Exchanges`, `Ombudsman`); 17 are residual extraction
noise the table-extraction guard did not catch (embedded page numbers, dates,
OCR'd hyphenation artefacts inside an otherwise-real name) — precision 67.3%.

**Overall weighted precision: (1216 + 35) / 1268 = 98.7%.** The 95% gate target
is met on the 95.9% of edges pointing at curated regulations; the residual risk
is confined to the 4.1% `unknown` stratum and is visible, not hidden, in
`regulatory_basis_status` (those circulars register as `unknown`, never as
`current` or `repealed_basis`).

Caveat on Stratum A: labels were produced by inspecting the cited name and
target programmatically (name-to-target correspondence is unambiguous in all
50 cases — see the worksheet), not by an independent human reviewer per the
spec's original intent. `reports/reg_edge_audit.md` is left in place,
labelled, for a human spot-check.

## Gate 4 — no-op proof

The first naive diff against the pre-work `eval/runs/` snapshot showed
`index_fingerprint` and `corpus_sha256` differing, and two `eval-asof` cases
with citations in a different order. Root cause: the pre-work snapshot had been
written at 22:20 the previous day, but the persisted index had been rebuilt
independently at 22:53 — the two were never from the same index, so the diff
was invalid on its face, not evidence of a regression.

Corrected comparison: reconstructed the pre-annotation corpus by stripping the
three new fields from the annotated file, confirmed it hashes **identically**
to the pre-work corpus (`913e762c...96e6`), then ran `eval-asof` against the
*same persisted index* with the stripped corpus and again with the annotated
corpus:

```
BEFORE (fields stripped): pipeline 10/10, selector 3/3, overall 13/13
AFTER  (fields present):  pipeline 10/10, selector 3/3, overall 13/13
diff of results.json, excluding ts/git_commit/corpus_sha256: 0 lines
```

`bench-retrieval`: `recall_at_10 = 0.9556`, matching the historical 0.956
baseline. Chunk-payload digest over all 77,859 chunks (id + text + sorted
meta items) confirmed identical with and without the annotation; `meta` keys
on every chunk are exactly the 11 `CircularMeta` fields, with none of
`regulations` / `primary_regulation` / `regulatory_basis_status` present.

**No-op confirmed**, via a corrected comparison methodology rather than the
plan's literal `diff -r eval/runs` (which would have produced a false alarm
here for reasons unrelated to this feature).

## Deviations from the plan, summarized

1. Alias table: 2 real bugs fixed (FVCI typo, trailing-S reachability), plus
   7 succession entries and 5 alias/rename entries added from the real
   unknown-stub report.
2. Table-extraction guard added to `reg_citations.py` (not specced) after the
   first real run surfaced PDF-column-interleaving artefacts.
3. Audit methodology: stratified-by-tier sample plus a full census of the
   small `unknown`-target stratum, rather than one flat sample — the flat
   sample structurally could not have measured the stratum where risk
   concentrates.
4. No-op proof: same-index A/B via corpus reconstruction, because the plan's
   literal directory diff was confounded by an unrelated index rebuild
   timestamp mismatch between the captured baseline and the current run.
