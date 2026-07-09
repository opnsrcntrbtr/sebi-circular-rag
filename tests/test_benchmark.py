from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from sebi_rag.benchmark import (
    export_beir,
    run_metadata,
    validate_golden,
    write_judge_results,
    write_trec_run,
)
from sebi_rag.segment import Chunk

ROOT = Path(__file__).resolve().parents[1]


def _golden():
    return [
        {
            "id": "q1",
            "query": "nomination rules",
            "relevant_circulars": ["SEBI/HO/X/1"],
            "relevant_chunks": [],
            "answer_contains": "nomination",
            "must_contain": ["nomination"],
            "must_not_contain": [],
            "abstain": False,
            "task_type": "body_paraphrase",
            "difficulty": "medium",
            "expected_citation_level": "circular",
            "rationale": "fixture",
            "label_source": "test",
            "review_status": "reviewed",
        },
        {
            "id": "hn",
            "query": "cookie recipe",
            "relevant_circulars": [],
            "relevant_chunks": [],
            "answer_contains": "",
            "must_contain": [],
            "must_not_contain": [],
            "abstain": True,
            "task_type": "far_negative",
            "difficulty": "easy",
            "expected_citation_level": "none",
            "rationale": "fixture",
            "label_source": "test",
            "review_status": "reviewed",
        },
    ]


def _chunks():
    return [
        Chunk(
            id="SEBI/HO/X/1#preamble#0",
            doc_id="SEBI/HO/X/1",
            section="SEBI/HO/X/1/preamble/p0",
            text="SEBI/HO/X/1 | nomination rules\nNomination text.",
            meta={
                "subject": "nomination rules",
                "issue_date": "2026-01-01",
                "issuing_department": "OIAE",
                "supersession_status": "in_force",
            },
        ),
        Chunk(
            id="SEBI/HO/Y/2#preamble#0",
            doc_id="SEBI/HO/Y/2",
            section="SEBI/HO/Y/2/preamble/p0",
            text="SEBI/HO/Y/2 | unrelated\nOther text.",
            meta={"subject": "unrelated"},
        ),
    ]


def test_golden_v6_schema_guardrails():
    rows = _golden()
    assert validate_golden(rows) == []
    bad = [dict(rows[0], id="bad", abstain=True)]
    issues = validate_golden(bad)
    assert any("abstain item has relevant_circulars" in i.message for i in issues)


def test_beir_export_and_qrels_shape(tmp_path):
    counts = export_beir(chunks=_chunks(), golden=_golden(), out_dir=tmp_path)
    assert counts == {"corpus": 2, "queries": 2, "qrels": 1}
    corpus = [json.loads(line) for line in (tmp_path / "corpus.jsonl").read_text().splitlines()]
    queries = [json.loads(line) for line in (tmp_path / "queries.jsonl").read_text().splitlines()]
    qrels = (tmp_path / "qrels" / "test.tsv").read_text().splitlines()
    assert corpus[0]["_id"] == "SEBI/HO/X/1#preamble#0"
    assert queries[0] == {"_id": "q1", "text": "nomination rules"}
    assert qrels[0] == "query-id\tcorpus-id\tscore"
    assert qrels[1].endswith("\t1")


def test_trec_run_and_research_judges_are_sidecar_only(tmp_path):
    run = tmp_path / "run.trec"
    write_trec_run(run, "fixture", {"q1": [("c1", 1.0), ("c2", 0.5)]})
    assert run.read_text().splitlines()[0] == "q1 Q0 c1 1 1.00000000 fixture"
    judges = tmp_path / "judge.jsonl"
    write_judge_results(judges, [{"id": "q1", "faithfulness": 1.0}])
    row = json.loads(judges.read_text())
    assert row["research_only"] is True


def test_run_metadata_has_reproducibility_fields(tmp_path):
    corpus = tmp_path / "corpus.jsonl"
    corpus.write_text("{}\n", encoding="utf-8")
    index = tmp_path / "index"
    index.mkdir()
    (index / "meta.json").write_text('{"n": 0}', encoding="utf-8")
    golden = tmp_path / "golden.jsonl"
    golden.write_text("{}\n", encoding="utf-8")
    meta = run_metadata(
        root=ROOT,
        corpus_path=corpus,
        index_dir=index,
        golden_path=golden,
        run_name="test",
        models={"embedder": "hash"},
        params={"top_n": 5},
    )
    for key in ("corpus_sha256", "index_fingerprint", "golden_sha256", "git_commit"):
        assert key in meta and meta[key]


def test_bench_retrieval_smoke_runner(tmp_path):
    out = tmp_path / "run"
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "bench_retrieval.py"),
            "--smoke",
            "--out",
            str(out),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert (out / "run.trec").exists()
    result = json.loads((out / "results.json").read_text())
    assert result["metrics"]["n"] == 1
    assert result["metadata"]["params"]["smoke"] is True
