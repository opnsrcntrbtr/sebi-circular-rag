# Label provenance audit

Rows: 260. Artifacts scanned: votes.jsonl (227 ids), arbitration_queue.jsonl (0 ids), packet_human (30 ids), gemini (21 ids), qwen (150 ids)

| label_source | n | accounted by |
|---|---|---|
| `claude (draft adjudication)` | 95 | gemini=2, packet_human=7, qwen=27, votes.jsonl=95 |
| `v7-draft-2026-07` | 82 | gemini=8, packet_human=17, qwen=82, votes.jsonl=82 |
| `claude (abstain validation)` | 26 | qwen=1, votes.jsonl=1 |
| `golden_v5` | 20 | gemini=5, packet_human=3, qwen=20, votes.jsonl=20 |
| `golden_v5 (promoted golden_v5)` | 13 | votes.jsonl=9 |
| `claude (arbitration resolved: title_direct)` | 12 | gemini=6, packet_human=2, qwen=12, votes.jsonl=12 |
| `external-flip` | 2 | qwen=2, votes.jsonl=2 |
| `claude (arbitration resolved: body_paraphrase)` | 2 | qwen=2, votes.jsonl=2 |
| `corrected: actually SEBI SAST topic` | 2 | qwen=1, votes.jsonl=1 |
| `corrected: actually SEBI topic` | 2 | packet_human=1, qwen=1, votes.jsonl=1 |
| `claude (qwen failed to find governing)` | 1 | qwen=1, votes.jsonl=1 |
| `corrected: actually SEBI LODR topic` | 1 | — |
| `corrected: actually SEBI FVCI topic` | 1 | qwen=1, votes.jsonl=1 |
| `corrected: actually SEBI IPEF topic` | 1 | — |

**Unaccounted rows: 33**

```
[
 "abstain",
 "hn-buyback",
 "hn-delist",
 "hn-esop",
 "hn-muni",
 "hn-settle",
 "hn-steward",
 "hn-ipef",
 "v7-ls-038",
 "v7-ls-040",
 "v7-hn-002",
 "v7-hn-003",
 "v7-hn-005",
 "v7-hn-007",
 "v7-hn-008",
 "v7-hn-011",
 "v7-hn-012",
 "v7-hn-013",
 "v7-hn-014",
 "v7-hn-016",
 "v7-hn-018",
 "v7-hn-020",
 "v7-hn-023",
 "v7-hn-024",
 "v7-hn-025",
 "v7-hn-026",
 "v7-hn-027",
 "v7-hn-028",
 "v7-fn-001",
 "v7-fn-003",
 "v7-fn-005",
 "v7-fn-007",
 "v7-fn-008"
]
```
