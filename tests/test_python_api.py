from doc_sync.extractors.python_api import extract_public_api


def test_extract_public_api_includes_module_functions_and_classes() -> None:
    source = '''
"""Example module."""

def alpha(value: int, *, scale: float = 1.0) -> int:
    """Return a number."""
    return value * int(scale)


class Widget:
    """A widget."""

    def __init__(self, name: str, *, active: bool = True) -> None:
        """Create a widget."""
        self.name = name
        self.active = active

    def render(self, count: int = 1) -> str:
        """Render text."""
        return self.name * count
'''

    api = extract_public_api(source)
    names = [item["name"] for item in api]

    assert names == ["alpha", "Widget"]

    alpha_item = next(item for item in api if item["name"] == "alpha")
    widget_item = next(item for item in api if item["name"] == "Widget")

    assert alpha_item["kind"] == "function"
    assert alpha_item["signature"] == "(value: int, *, scale: float = 1.0) -> int"
    assert alpha_item["docstring"] == "Return a number."

    assert widget_item["kind"] == "class"
    assert widget_item["signature"] == "(name: str, *, active: bool = True) -> None"
    assert widget_item["docstring"] == "A widget."


def test_extract_public_api_respects_all_and_static_relative_exports() -> None:
    source = '''
from .helper import exported

__all__ = ["exported", "public_value"]

def _hidden() -> None:
    pass

def public_value() -> str:
    """Visible value."""
    return "value"
'''

    api = extract_public_api(source)
    names = [item["name"] for item in api]

    assert names == ["exported", "public_value"]
    assert "_hidden" not in names
