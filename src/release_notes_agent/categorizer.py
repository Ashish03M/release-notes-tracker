import re

# Categories we will use for release notes
CATEGORIES = [
    "Features", "Fixes", "Docs", "Refactors",
    "Perf", "Chore", "Breaking Changes", "Other",
]

# Map conventional commit prefixes (feat:, fix:, etc.) → categories
_CONV_MAP = {
    "feat": "Features",
    "fix": "Fixes",
    "docs": "Docs",
    "refactor": "Refactors",
    "perf": "Perf",
    "chore": "Chore",
    "breaking": "Breaking Changes",
}


def conventional_guess(text: str) -> str | None:
    """Guess category from PR/commit title (e.g., 'feat:' → Features)."""
    m = re.match(r"(feat|fix|docs|refactor|perf|chore|breaking)(\(.+?\))?:", text, re.I)
    if not m:
        return None
    return _CONV_MAP.get(m.group(1).lower())


def label_guess(labels: list[str]) -> str | None:
    """Guess category from GitHub labels (e.g., 'bug' → Fixes)."""
    low = {l.lower() for l in labels}
    pairs = [
        ("feature", "Features"), ("enhancement", "Features"),
        ("bug", "Fixes"), ("fix", "Fixes"),
        ("docs", "Docs"), ("documentation", "Docs"),
        ("refactor", "Refactors"),
        ("perf", "Perf"),
        ("chore", "Chore"),
        ("breaking", "Breaking Changes"),
    ]
    for key, cat in pairs:
        if key in low:
            return cat
    return None
                               # → None
