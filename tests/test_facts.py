from doc_sync.facts import FactModel, NotFound


def test_fact_model_resolves_missing_and_conflict_values() -> None:
    facts = FactModel()
    facts.add("project_name", "demo")
    facts.add("project_name", "demo-2")
    facts.add("description", None)

    resolved = facts.resolve()

    assert resolved["project_name"] == "demo"
    assert resolved["description"] == NotFound
    assert "project_name" in resolved["conflicts"]


def test_fact_model_rejects_sensitive_values() -> None:
    facts = FactModel()

    facts.add("api_key", "secret-token-value")

    assert facts.resolve()["api_key"] == NotFound
