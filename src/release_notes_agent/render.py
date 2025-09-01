from typing import Dict, List
from .categorizer import CATEGORIES

'''try:
    from .categorizer import CATEGORIES
except ImportError:
    # when run directly: python src/release_notes_agent/render.py
    from categorizer import CATEGORIES'''


#Turn categories into Markdown release notes - readability
def render_markdown(grouped: Dict[str, List[str]], title: str = "Release Notes") -> str:
    lines: List[str] = [f"# {title}", ""]
    for cat in CATEGORIES:
        items = grouped.get(cat, [])
        if not items:
            continue
        lines.append(f"## {cat}")
        lines.extend(f"- {item}" for item in items)
        lines.append("")
    return "\n".join(lines).strip()



