"""Metadata layer: circular_type taxonomy + validity_status derivation."""
from sebi_rag.metadata import (
    CIRCULAR_TYPES, VALIDITY_STATUSES, classify_circular_type, derive_validity,
)


def edge(source, target, relation="supersedes", confidence="explicit_text"):
    return {"source": source, "target": target, "relation": relation,
            "confidence": confidence, "extractor": "regex:SUPERSEDE_RE", "evidence": ""}


class TestClassifyCircularType:
    def test_master_circular(self):
        assert classify_circular_type("Master Circular for Mutual Funds") == "MASTER_CIRCULAR"

    def test_corrigendum(self):
        assert classify_circular_type("Corrigendum to circular on KYC norms") == "CORRIGENDUM"

    def test_addendum(self):
        assert classify_circular_type("Addendum to SEBI circular dated ...") == "ADDENDUM"

    def test_clarification(self):
        assert classify_circular_type("Clarification on REIT disclosure norms") == "CLARIFICATION"

    def test_clarificatory_stem_matches(self):
        assert classify_circular_type("Clarificatory circular on AIF norms") == "CLARIFICATION"

    def test_amendment(self):
        assert classify_circular_type("Amendment to circular on margin obligations") == "AMENDMENT"

    def test_plain_circular_default(self):
        assert classify_circular_type("Review of margin framework") == "CIRCULAR"

    def test_none_and_empty_default(self):
        assert classify_circular_type(None) == "CIRCULAR"
        assert classify_circular_type("") == "CIRCULAR"

    def test_precedence_master_beats_amendment(self):
        assert classify_circular_type(
            "Master Circular on Amendment procedures") == "MASTER_CIRCULAR"

    def test_precedence_clarification_beats_amendment(self):
        # mirrors the corpus probe ordering used to lock the taxonomy
        assert classify_circular_type(
            "Clarification on amendment to LODR circular") == "CLARIFICATION"

    def test_all_outputs_in_enum(self):
        for s in ("Master Circular on X", "Corrigendum", "Addendum", "Clarification",
                  "Amendment", "anything else", None):
            assert classify_circular_type(s) in CIRCULAR_TYPES


class TestDeriveValidity:
    CN = "SEBI/HO/IMD/DF2/CIR/P/2021/024"
    NEWER = "SEBI/HO/IMD/DF2/CIR/P/2024/031"

    def test_explicit_supersession_wins(self):
        assert derive_validity(self.CN, "2021-03-01",
                               [edge(self.NEWER, self.CN)]) == "superseded"

    def test_explicit_supersession_wins_even_without_date(self):
        assert derive_validity(self.CN, "", [edge(self.NEWER, self.CN)]) == "superseded"

    def test_explicit_amendment_is_partially_superseded(self):
        assert derive_validity(self.CN, "2021-03-01",
                               [edge(self.NEWER, self.CN, relation="amends")]
                               ) == "partially_superseded"

    def test_supersession_beats_amendment(self):
        edges = [edge(self.NEWER, self.CN, relation="amends"),
                 edge(self.NEWER, self.CN, relation="supersedes")]
        assert derive_validity(self.CN, "2021-03-01", edges) == "superseded"

    def test_inferred_supersession_stays_current(self):
        # locked decision: inferred edges are soft metadata only
        assert derive_validity(self.CN, "2021-03-01",
                               [edge(self.NEWER, self.CN, confidence="inferred")]
                               ) == "current"

    def test_missing_date_unknown(self):
        assert derive_validity(self.CN, "", []) == "unknown"
        assert derive_validity(self.CN, None, []) == "unknown"

    def test_malformed_date_unknown(self):
        assert derive_validity(self.CN, "13 July 2023", []) == "unknown"

    def test_no_edges_good_date_current(self):
        assert derive_validity(self.CN, "2021-03-01", []) == "current"

    def test_edges_for_other_circulars_ignored(self):
        assert derive_validity(self.CN, "2021-03-01",
                               [edge(self.NEWER, "SEBI/HO/OTHER/2020/001")]) == "current"

    def test_outgoing_edges_ignored(self):
        # CN superseding someone else does not change CN's own validity
        assert derive_validity(self.CN, "2021-03-01",
                               [edge(self.CN, "SEBI/HO/OTHER/2020/001")]) == "current"

    def test_all_outputs_in_enum(self):
        for args in (("", []), ("2021-03-01", []),
                     ("2021-03-01", [edge(self.NEWER, self.CN)])):
            assert derive_validity(self.CN, *args) in VALIDITY_STATUSES
