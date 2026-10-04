from pathlib import Path
import tomllib


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def load_project_metadata() -> dict[str, object]:
    pyproject_path = REPOSITORY_ROOT / "pyproject.toml"
    project_file = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    return project_file["project"]


def test_project_metadata_has_required_fields() -> None:
    project = load_project_metadata()

    assert {"name", "version", "description", "requires-python", "dependencies"} <= project.keys()


def test_project_supports_python_311_and_newer() -> None:
    project = load_project_metadata()

    assert project["requires-python"] == ">=3.11"


def test_runtime_dependencies_use_requested_minimum_versions() -> None:
    project = load_project_metadata()

    assert set(project["dependencies"]) == {"PyYAML>=6.0", "packaging>=23.0"}
    assert all("<" not in dependency for dependency in project["dependencies"])


def test_pytest_is_a_development_dependency() -> None:
    project = load_project_metadata()

    assert project["optional-dependencies"]["dev"] == ["pytest>=8.0"]


def test_requirements_record_the_final_runtime_and_dependency_policy() -> None:
    requirements = (REPOSITORY_ROOT / "docs" / "requirements.md").read_text(encoding="utf-8")

    assert 'The tool supports Python 3.11 and later (`requires-python = ">=3.11"`).' in requirements
    assert "PyYAML `>=6.0` and packaging `>=23.0`" in requirements
    assert "pytest `>=8.0`" in requirements
    assert "Exact supported Python runtime versions for the tool itself: `Not Found`." not in requirements