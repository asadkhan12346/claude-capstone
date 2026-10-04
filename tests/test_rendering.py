from doc_sync.rendering import render_api_docs, render_empty_repository_readme, render_readme


def test_render_readme_includes_required_sections() -> None:
    rendered = render_readme(
        {
            "project_name": "demo-app",
            "description": "A demo app",
            "dependencies": ["requests>=2.0"],
            "entry_points": {"doc-sync": "demo.cli:main"},
            "config_variables": ["API_URL"],
            "overview": "This project syncs docs.",
            "usage": "Run the tool locally.",
            "installation": "pip install demo-app",
        }
    )

    assert "# demo-app" in rendered
    assert "## Overview" in rendered
    assert "This project syncs docs." in rendered
    assert "## Usage" in rendered
    assert "Run the tool locally." in rendered


def test_render_empty_repository_readme_uses_required_notice() -> None:
    rendered = render_empty_repository_readme()

    assert "Repository is empty or contains no supported files" in rendered
    assert "## Overview" in rendered


def test_render_api_docs_escapes_markdown() -> None:
    rendered = render_api_docs({"modules": [{"name": "demo.module", "functions": [{"name": "run*", "signature": "run(arg: str)"}]}]})

    assert "demo.module" in rendered
    assert "run*" in rendered
