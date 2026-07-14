from sebi_rag.master_meta import annotate_master_fields, master_series


def _master(n, subj, date):
    return {"circular_number": n, "subject": subj, "issue_date": date,
            "circular_type": "MASTER_CIRCULAR"}


def test_master_series_rule_table():
    assert master_series("Master Circular for Mutual Funds") == "Mutual Funds"
    assert master_series("Master Circular for Depositories") == "Depositories"
    assert master_series("Master Circular for Stock Brokers") == "Stock Brokers"
    assert master_series(
        "Master Circular for Alternative Investment Funds (AIFs)") == "AIFs"
    assert master_series("Master Circular on something novel") is None
    assert master_series(None) is None


def test_annotate_sets_identity_and_chains_editions():
    recs = [
        _master("MF/2023/1", "Master Circular for Mutual Funds", "2023-05-19"),
        _master("MF/2024/2", "Master Circular for Mutual Funds", "2024-06-27"),
        _master("DEP/2024/3", "Master Circular for Depositories", "2024-10-06"),
        {"circular_number": "C/1", "subject": "Nomination", "issue_date":
         "2025-01-10", "circular_type": "CIRCULAR"},
    ]
    changed = annotate_master_fields(recs)
    assert changed == 4
    assert recs[0]["is_master"] and recs[0]["master_edition"] == 2023
    assert recs[0]["previous_edition"] is None
    assert recs[1]["previous_edition"] == "MF/2023/1"     # chained by series+date
    assert recs[2]["previous_edition"] is None            # different series
    assert recs[3] == {**recs[3], "is_master": False, "master_series": None,
                       "master_edition": None, "previous_edition": None}


def test_annotate_idempotent():
    recs = [_master("MF/2023/1", "Master Circular for Mutual Funds", "2023-05-19")]
    annotate_master_fields(recs)
    assert annotate_master_fields(recs) == 0
