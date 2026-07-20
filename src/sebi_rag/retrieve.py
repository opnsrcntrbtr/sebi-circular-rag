"""Stage-1 hybrid retrieval: dense (FAISS) + sparse (BM25) fused by RRF.

Mandatory architecture per docs/project_context.md D1/D3.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

import bm25s
import faiss
import numpy as np

from .embeddings import Embedder
from .expand import expand_query
from .segment import Chunk
from .splade import SpladeIndex


def _doc_checksum(texts: list[str]) -> str:
    """Deterministic per-document checksum over its (enriched) chunk texts —
    captures corpus edits AND segmentation/enrichment changes (F3, ADR-001)."""
    h = hashlib.sha256()
    for t in texts:
        h.update(t.encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()


class DenseIndex:
    """FAISS IndexFlatIP over L2-normalized vectors (cosine)."""

    def __init__(self, embedder: Embedder) -> None:
        self.embedder = embedder
        self.index = faiss.IndexFlatIP(embedder.dim)

    def build(self, texts: list[str]) -> np.ndarray:
        vecs = self.embedder.encode(texts).astype("float32")
        self.index.add(vecs)
        return vecs

    def build_from_vecs(self, vecs: np.ndarray) -> None:
        self.index.add(vecs.astype("float32"))

    def search(self, query: str, k: int) -> list[tuple[int, float]]:
        q = self.embedder.encode([query]).astype("float32")
        k = min(k, self.index.ntotal)
        scores, idx = self.index.search(q, k)
        return [(int(i), float(s)) for i, s in zip(idx[0], scores[0]) if i != -1]


class SparseIndex:
    """BM25 lexical index (bm25s)."""

    def __init__(self) -> None:
        self._bm25 = bm25s.BM25()
        self._n = 0

    def build(self, texts: list[str]) -> None:
        tokens = bm25s.tokenize(texts, stopwords="en", show_progress=False)
        self._bm25.index(tokens, show_progress=False)
        self._n = len(texts)

    def search(self, query: str, k: int) -> list[tuple[int, float]]:
        qt = bm25s.tokenize(query, stopwords="en", show_progress=False)
        k = min(k, self._n)
        res, scores = self._bm25.retrieve(qt, k=k, show_progress=False)
        return [(int(i), float(s)) for i, s in zip(res[0], scores[0])]


def rrf_fuse(
    rankings: list[list[tuple[int, float]]],
    k_const: int = 60,
    top_n: int = 50,
) -> list[tuple[int, float]]:
    """Reciprocal Rank Fusion. Rank-only — sidesteps score-scale mismatch."""
    fused: dict[int, float] = {}
    for ranking in rankings:
        for rank, (doc_id, _score) in enumerate(ranking):
            fused[doc_id] = fused.get(doc_id, 0.0) + 1.0 / (k_const + rank + 1)
    ordered = sorted(fused.items(), key=lambda kv: -kv[1])
    return ordered[:top_n]


@dataclass
class HybridRetriever:
    chunks: list[Chunk]
    dense: DenseIndex
    sparse: SparseIndex
    vecs: np.ndarray | None = field(default=None, repr=False)  # cached embeddings (F3)
    splade: SpladeIndex | None = field(default=None, repr=False)  # iv11 opt-in leg

    @classmethod
    def build(cls, chunks: list[Chunk], embedder: Embedder) -> "HybridRetriever":
        texts = [c.text for c in chunks]
        d = DenseIndex(embedder)
        vecs = d.build(texts)
        s = SparseIndex()
        s.build(texts)
        return cls(chunks=chunks, dense=d, sparse=s, vecs=vecs)

    @classmethod
    def build_incremental(
        cls, chunks: list[Chunk], embedder: Embedder, path: str | Path
    ) -> "tuple[HybridRetriever, dict]":
        """F3 (ADR-001): encode only new/changed documents; reuse cached
        embedding rows for unchanged ones (per-doc checksum manifest). Deleted
        or changed docs are handled implicitly — their old rows are dropped.
        FAISS Flat + BM25 are rebuilt from the assembled matrix (cheap; the
        bge-m3 encode is ~99% of a full build). Falls back to a full build when
        no embeddings cache exists yet."""
        d = Path(path)
        emb_f, man_f = d / "embeddings.npy", d / "manifest.json"
        if not (emb_f.exists() and man_f.exists()):
            r = cls.build(chunks, embedder)
            stats = {"mode": "full", "docs_total": len({c.doc_id for c in chunks}),
                     "docs_reused": 0, "chunks_encoded": len(chunks)}
            return r, stats

        old_vecs = np.load(emb_f)
        manifest = json.loads(man_f.read_text(encoding="utf-8"))["docs"]

        # group new chunks by doc, preserving corpus order (contiguous per doc)
        doc_order: list[str] = []
        by_doc: dict[str, list[str]] = {}
        for c in chunks:
            if c.doc_id not in by_doc:
                by_doc[c.doc_id] = []
                doc_order.append(c.doc_id)
            by_doc[c.doc_id].append(c.text)

        segments: list[np.ndarray | None] = []
        to_encode: list[int] = []  # segment positions needing encode
        enc_texts: list[str] = []
        reused = 0
        for i, doc in enumerate(doc_order):
            texts = by_doc[doc]
            old = manifest.get(doc)
            if old and old["checksum"] == _doc_checksum(texts) \
                    and old["count"] == len(texts):
                segments.append(old_vecs[old["start"]: old["start"] + old["count"]])
                reused += 1
            else:
                segments.append(None)
                to_encode.append(i)
                enc_texts.extend(texts)
        if enc_texts:
            new_vecs = embedder.encode(enc_texts).astype("float32")
            off = 0
            for i in to_encode:
                n = len(by_doc[doc_order[i]])
                segments[i] = new_vecs[off: off + n]
                off += n
        vecs = (np.vstack(segments) if segments
                else np.zeros((0, embedder.dim), dtype="float32"))

        dense = DenseIndex(embedder)
        dense.build_from_vecs(vecs)
        sparse = SparseIndex()
        sparse.build([c.text for c in chunks])
        stats = {"mode": "incremental", "docs_total": len(doc_order),
                 "docs_reused": reused, "chunks_encoded": len(enc_texts)}
        return cls(chunks=chunks, dense=dense, sparse=sparse, vecs=vecs), stats

    def retrieve(
        self,
        query: str,
        k_dense: int = 50,
        k_sparse: int = 50,
        top_n: int = 50,
        hyde_text: str | None = None,
        use_splade: bool = False,
        k_splade: int = 50,
    ) -> list[tuple[Chunk, float]]:
        dense = self.dense.search(query, k_dense)
        # intervention #2: statutory-synonym expansion, sparse leg only —
        # BM25 misses lay vocabulary; dense keeps the raw query.
        sparse = self.sparse.search(expand_query(query), k_sparse)
        legs = [dense, sparse]
        if hyde_text:
            # intervention #5 (HyDE, Part B): hypothetical statutory passage
            # as an additive third dense leg; raw legs stay untouched.
            legs.append(self.dense.search(hyde_text, k_dense))
        if use_splade:
            # intervention iv11 (SPLADE): learned-sparse third leg on the RAW
            # query (SPLADE does its own expansion; glossary stays BM25-only).
            if self.splade is None:
                raise RuntimeError("use_splade=True but no SPLADE index attached")
            legs.append(self.splade.search(query, k_splade))
        fused = rrf_fuse(legs, top_n=top_n)
        return [(self.chunks[i], score) for i, score in fused]

    # ---- persistence: build the 20k-chunk index once, reload in <1s ----

    def save(self, path: str | Path) -> None:
        d = Path(path)
        d.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.dense.index, str(d / "dense.faiss"))
        self.sparse._bm25.save(str(d / "bm25"))
        with (d / "chunks.jsonl").open("w", encoding="utf-8") as f:
            for c in self.chunks:
                f.write(json.dumps(asdict(c), ensure_ascii=False) + "\n")
        (d / "meta.json").write_text(
            json.dumps({"n": len(self.chunks), "dim": self.dense.embedder.dim}),
            encoding="utf-8",
        )
        if self.vecs is not None:  # F3: embeddings cache + per-doc manifest
            np.save(d / "embeddings.npy", self.vecs.astype("float32"))
            docs: dict[str, dict] = {}
            start = 0
            cur, texts = None, []
            for i, c in enumerate(self.chunks):
                if c.doc_id != cur:
                    if cur is not None:
                        docs[cur] = {"checksum": _doc_checksum(texts),
                                     "start": start, "count": len(texts)}
                    cur, start, texts = c.doc_id, i, []
                texts.append(c.text)
            if cur is not None:
                docs[cur] = {"checksum": _doc_checksum(texts),
                             "start": start, "count": len(texts)}
            (d / "manifest.json").write_text(
                json.dumps({"docs": docs}), encoding="utf-8"
            )

    @classmethod
    def load(cls, path: str | Path, embedder: Embedder) -> "HybridRetriever":
        d = Path(path)
        chunks = [
            Chunk(**json.loads(line))
            for line in (d / "chunks.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        dense = DenseIndex(embedder)
        dense.index = faiss.read_index(str(d / "dense.faiss"))
        sparse = SparseIndex()
        sparse._bm25 = bm25s.BM25.load(str(d / "bm25"))
        sparse._n = len(chunks)
        return cls(chunks=chunks, dense=dense, sparse=sparse)

    @staticmethod
    def index_exists(path: str | Path) -> bool:
        d = Path(path)
        return (d / "dense.faiss").exists() and (d / "meta.json").exists()
