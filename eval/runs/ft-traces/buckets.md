# Final Bucket Assignments — Pre-retrieval Failure Taxonomy

Source data: `eval/runs/ft-traces/traces.jsonl` (10 failures: 3 golden_v6, 7 probes_v1).
Ranks below read `d/s/f/r` = dense / sparse / fused / rerank, answer-chunk level
unless noted; `-1` = absent from top-50.

## Summary

| bucket | count | % | golden | probe |
|---|---|---|---|---|
| sparse_vocabulary_miss | 5 | 50% | 1 | 4 |
| embedding_semantic_miss | 3 | 30% | 2 | 1 |
| chunking_defect | 1 | 10% | 0 | 1 |
| fusion_ranking_loss | 1 | 10% | 0 | 1 |
| extraction_loss | 0 | 0% | 0 | 0 |
| metadata_filter_loss | 0 | 0% | 0 | 0 |

Assigned: 10/10 (100% — spec requires ≥90%). Unassigned: 0.

Severity note: in 4 of 10 failures (probe-num-05, probe-sup-01, probe-par-01,
probe-par-02) the cross-encoder reranker rescues the answer chunk into the
top-10 despite the weak candidate ranking, so end-to-end impact is muted; the
remaining 6 are user-visible failures.

## Per-failure decisions

| failure_id | source | class (doc/answer) | final_bucket | evidence |
|---|---|---|---|---|
| para-aifmaster | golden_v6 | ranked_low / ranked_low | embedding_semantic_miss | Heavy paraphrase ("Category II private pooled investment vehicle" for AIF) defeats BOTH retrievers (d=24, s=33) and the reranker only reaches 16; the harness proposed fusion_ranking_loss, but fusion merely reflects two weak inputs — the primary cause is semantic: no component maps the paraphrase to "Alternative Investment Fund". Secondary: rerank shortfall. |
| para-freeze | golden_v6 | candidate_miss / candidate_miss | sparse_vocabulary_miss | Query says "block outgoing transactions from folio"; corpus says "freeze". Sparse never finds it (s=-1); dense finds it weakly (d=43) and RRF then cuts it from the fused top-50 (f=-1). If BM25 had matched, the doc would have survived fusion. Secondary: weak dense + fusion cutoff. |
| para-parrva | golden_v6 | hit / candidate_miss | embedding_semantic_miss | Doc reaches rerank 2 via sibling chunks, but the answer chunk naming Care Ratings is invisible to dense at doc level (d=-1 for the whole doc) and absent from sparse top-50 (ans s=-1). Coherent 448-char chunk; dense simply doesn't relate "recognised to validate performance claims" to it. |
| probe-tbl-05 | probes_v1 | hit / ranked_low | sparse_vocabulary_miss | Answer chunk (model RTI–Issuer agreement, 3.5.1) found by dense at 9 but sparse misses entirely ("template contract" vs corpus "Models of Agreement"); fusion dilutes to 24 and the reranker demotes further to 31. Secondary: reranker demotion. |
| probe-num-05 | probes_v1 | hit / ranked_low | fusion_ranking_loss | Both retrievers find the answer chunk mid-pack (ans d=32, s=22) and RRF lands it at 44; the reranker rescues to 4. Answer text duplicated across 4 chunks of the master circular splits the vote. End-to-end impact: low (rescued). |
| probe-sup-01 | probes_v1 | hit / ranked_low | sparse_vocabulary_miss | "Replaced ... made void" shares no vocabulary with "stand rescinded"; sparse misses the rescission clause (ans s=-1), dense has it at 11, fused 23; reranker rescues to 4. End-to-end impact: low (rescued). |
| probe-sup-04 | probes_v1 | hit / candidate_miss | embedding_semantic_miss | Answer chunk (rescission of Sl.No. 68-74) never retrieved by either retriever (ans d=-1, s=-1) though the doc itself ranks top-10; coherent 1319-char chunk. Query phrasing "serial numbers ... withdrawn" defeats dense; digits "68-74" alone defeat BM25. Secondary: sparse. |
| probe-par-01 | probes_v1 | ranked_low / ranked_low | sparse_vocabulary_miss | "Papers accompanying a broking licence application" vs corpus "documents ... registration of stock brokers": sparse absent (s=-1), dense 9, fused 17; reranker rescues to 2. End-to-end impact: low (rescued). |
| probe-par-02 | probes_v1 | hit / ranked_low | sparse_vocabulary_miss | "Electronic form" vs corpus "dematerialized form": sparse misses the answer chunk (ans s=-1), dense 7, fused 17, rerank 8. End-to-end impact: low-medium (rank 8 borderline). |
| probe-par-03 | probes_v1 | hit / candidate_miss | chunking_defect | OVERRIDE (harness said embedding_semantic_miss): sub-clauses 4.1.1.1–4.1.1.5 of the CRA master are each chunked as bare list items severed from governing clause 4.1.1 that carries the surrender/winding-down context. The 282-char answer chunk "not take any new clients or fresh mandates;" is context-orphaned, so no retriever can connect "winding down its business" to it. Same family as the nominee-count bug (context loss at chunk boundaries). |

## Cross-cutting observations

1. Doc-level retrieval is near-saturated (golden recall@10 = 0.956, probes 0.96);
   every failure mode that matters is at the **answer-chunk level**.
2. BM25 vocabulary mismatch is the most common primary cause (5/10) and a
   secondary factor in 2 more; regulatory synonymy (freeze/block,
   dematerialized/electronic, rescinded/replaced) is systematic.
3. The cross-encoder reranker is the pipeline's strongest component: it rescues
   4 of the 7 failures where the answer chunk made it into the candidate set at
   all. Widening what reaches it matters more than improving it.
4. Context-orphaned list-item chunks (probe-par-03; nominee bug) hide answers
   from both retrievers — a chunking-repair class distinct from degenerate
   heading-only chunks.
5. No extraction losses and no metadata-filter losses were observed in this
   sample; ingestion text fidelity was sufficient for every harvested failure.
