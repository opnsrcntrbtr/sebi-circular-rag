"""Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped
to in-force circular(s) by a distinctive subject substring, resolved to exact
circular numbers from the corpus (so labels stay correct as numbers vary). Prints
a match report; 0 or surprising counts are flagged for review.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from sebi_rag.lineage import build_lineage, load_records  # noqa: E402

CORPUS = Path(__file__).resolve().parents[1] / "data" / "corpus" / "circulars.jsonl"
OUT = Path(__file__).resolve().parents[1] / "eval" / "golden" / "golden_v4.jsonl"

# (id, query, subject_substring, answer_contains)
Q = [
    ("surv", "Master circular on surveillance of the securities market", "surveillance of securities market", "surveillance"),
    ("icdr", "Master circular for Issue of Capital and Disclosure Requirements (ICDR)", "master circular for sebi (issue of capital", "capital"),
    ("depo", "Master circular for depositories", "master circular for depositories", "depositor"),
    ("secc", "Master circular for stock exchanges and clearing corporations", "master circular for stock exchanges and clearing corporations", "clearing"),
    ("broker", "Master circular for stock brokers", "master circular for stock brokers", "broker"),
    ("esg", "Master circular for ESG rating providers", "esg rating providers", "esg"),
    ("cra", "Master circular for credit rating agencies", "master circular for credit rating agencies", "credit rating"),
    ("reit", "Master circular for Real Estate Investment Trusts (REITs)", "master circular for real estate investment trusts", "real estate"),
    ("invit", "Master circular for Infrastructure Investment Trusts (InvITs)", "master circular for infrastructure investment trusts", "infrastructure"),
    ("pms", "Master circular for portfolio managers", "master circular for portfolio managers", "portfolio"),
    ("dt", "Master circular for debenture trustees", "master circular for debenture trustees", "debenture"),
    ("sse", "Master circular on the framework for the Social Stock Exchange", "framework on social stock exchange", "social stock"),
    ("ia", "Master circular for investment advisers", "master circular for investment advisers", "investment adviser"),
    ("ra", "Master circular for research analysts", "master circular for research analysts", "research analyst"),
    ("rta", "Master circular for registrars to an issue and share transfer agents", "master circular for registrars", "registrar"),
    ("matevents", "Disclosure of material events including buy back of securities by listed entities", "disclosure of material events", "buyback"),
    ("blockdeal", "Review of the block deal framework", "review of block deal framework", "block deal"),
    ("cas", "Introduction of a closing auction session in the equity cash segment", "closing auction session", "closing auction"),
    ("otr", "Revision of the order-to-trade ratio framework", "order-to-trade ratio", "order-to-trade"),
    ("calspread", "Calendar spread margin benefit for single stock derivatives on expiry day", "calendar spread margin", "calendar spread"),
    ("intraday", "Framework for intraday position limits monitoring for equity index derivatives", "intraday position limits monitoring", "intraday"),
    ("disc_doc", "Format of the disclosure document for portfolio managers", "disclosure document", "disclosure document"),
    ("pms_transfer", "Transfer of portfolios of clients in the PMS business by portfolio managers", "transfer of portfolios of clients", "transfer of portfolios"),
    ("reit_reclass", "Reclassification of REITs as equity related instruments", "reclassification of real estate investment trusts", "reclassification"),
    ("sif", "Compliance reporting formats for Specialized Investment Funds (SIF)", "specialized investment funds (sif)", "specialized investment"),
    ("pledge", "Creation and invocation of pledge of securities through the depository system", "invocation of pledge", "pledge"),
    ("swagat", "Single Window Automatic and Generalised Access for Trusted Foreign Investors (SWAGAT)", "single window automatic and generalised access", "single window"),
    ("aif_co", "Certification requirement for compliance officers of managers of AIFs", "certification requirement for compliance officers", "compliance officer"),
    ("nomination", "Modified norms for nomination in demat accounts and mutual fund folios", "nomination in demat accounts", "nomination"),
    ("pricedata", "Norms for sharing and usage of stock exchange price data for educational purposes", "price data for educational purposes", "price data"),
]

recs = load_records(CORPUS)
lin = build_lineage(recs)
inforce = [r for r in recs if lin.status(r["circular_number"]) == "in_force"]

lines, warnings = [], []
for qid, query, sub, ac in Q:
    # master-circular queries: match only circulars whose subject STARTS with the
    # phrase (a "modification of the master circular" must not count as the master).
    start = sub.startswith("master circular for")
    hits = []
    for r in inforce:
        s = (r.get("subject") or "").lower().lstrip()
        if (s.startswith(sub) if start else sub in s):
            hits.append(r["circular_number"])
    if len(hits) != 1:
        warnings.append(f"{qid}: {len(hits)} matches for '{sub}' -> {hits}")
    lines.append({"id": qid, "query": query, "relevant_circulars": hits,
                  "answer_contains": ac, "abstain": False})
lines.append({"id": "abstain", "query": "What is the best recipe for chocolate chip cookies?",
              "relevant_circulars": [], "answer_contains": "", "abstain": True})

OUT.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in lines) + "\n",
               encoding="utf-8")
print(f"wrote {len(lines)} items -> {OUT}")
for w in warnings:
    print("  WARN", w)
