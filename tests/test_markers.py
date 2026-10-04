from doc_sync.approval import build_diff, prepare_approval
from doc_sync.markers import replace_marked_section


def test_replace_marked_section_keeps_content_outside_markers() -> None:
    original = "before\n<!-- doc-sync:start -->\nold\n<!-- doc-sync:end -->\nafter"
    updated = replace_marked_section(original, "new")

    assert "before" in updated
    assert "new" in updated
    assert "after" in updated
    assert "old" not in updated


def test_replace_marked_section_refuses_duplicate_markers() -> None:
    original = "<!-- doc-sync:start -->\none\n<!-- doc-sync:start -->\nother\n<!-- doc-sync:end -->"

    try:
        replace_marked_section(original, "new")
        raise AssertionError("duplicate markers should fail")
    except ValueError:
        pass


def test_prepare_approval_rechecks_target_fingerprint() -> None:
    original = "one\ntwo"
    approved = prepare_approval(original, "one\nthree", approved=True)
    assert approved["approved"] is True
    assert approved["diff"]

    current_target = "one\nthree"
    try:
        prepare_approval(current_target, "one\nfour", approved=True, fingerprint=approved["fingerprint"])
        raise AssertionError("changed target should require fresh approval")
    except ValueError:
        pass


def test_build_diff_has_unified_format() -> None:
    diff = build_diff("one\n", "two\n")
    assert diff.startswith("---") or "@@" in diff
