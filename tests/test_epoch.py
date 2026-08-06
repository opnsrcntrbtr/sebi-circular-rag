"""Epoch/frame identity and the comparability guard (spec A §6)."""
import pytest

from sebi_rag.autoresearch.epoch import (
    Frame,
    IncomparableFramesError,
    assert_comparable,
    frame_of,
)

EPOCHS = {"4083518f": "E1", "913e762c": "E2"}


def _results(corpus: str, golden: str) -> dict:
    return {"metadata": {"corpus_sha256": corpus, "golden_sha256": golden}}


def test_frame_pairs_epoch_with_eval_set():
    f = frame_of(_results("913e762c", "f01d8779"), EPOCHS)
    assert f == Frame(epoch="E2", eval_set="f01d8779")


def test_same_corpus_different_instruments_share_an_epoch():
    golden = frame_of(_results("913e762c", "f01d8779"), EPOCHS)
    probes = frame_of(_results("913e762c", "99a9da66"), EPOCHS)
    assert golden.epoch == probes.epoch == "E2"
    assert golden != probes


def test_unknown_corpus_yields_no_frame():
    assert frame_of(_results("deadbeef", "f01d8779"), EPOCHS) is None


def test_missing_corpus_sha_yields_no_frame():
    assert frame_of({"metadata": {"golden_sha256": "f01d8779"}}, EPOCHS) is None


def test_identical_frames_are_comparable():
    f = Frame(epoch="E2", eval_set="f01d8779")
    assert_comparable(f, f, label_a="iv7", label_b="iv8")


def test_different_epochs_raise():
    a = Frame(epoch="E1", eval_set="f01d8779")
    b = Frame(epoch="E2", eval_set="f01d8779")
    with pytest.raises(IncomparableFramesError, match="E1.*E2"):
        assert_comparable(a, b, label_a="ft", label_b="iv8")


def test_different_eval_sets_raise():
    a = Frame(epoch="E2", eval_set="f01d8779")
    b = Frame(epoch="E2", eval_set="99a9da66")
    with pytest.raises(IncomparableFramesError, match="f01d8779.*99a9da66"):
        assert_comparable(a, b, label_a="iv7-golden", label_b="iv7-probes")


def test_unframed_run_raises():
    a = Frame(epoch="E2", eval_set="f01d8779")
    with pytest.raises(IncomparableFramesError, match="no frame"):
        assert_comparable(a, None, label_a="iv7", label_b="pool-sweep")
