# Release Notes Generator

## Overview
The **Release Notes Generator** is a Python tool that automatically collects merged pull requests from a GitHub repository, categorizes the changes (features, bug fixes, documentation, refactors, etc.), and generates clean, Markdown‑formatted release notes. It leverages the **LangChain GitHub Toolkit** and **LangGraph** to provide a simple, extensible workflow for creating release notes without manual effort.

## Features
- **Automated PR collection** from a target repository.
- **Smart categorisation** of changes (Features, Fixes, Docs, Refactors, Tests, Chores, etc.).
- **Markdown output** ready to paste into GitHub releases.
- **Extensible architecture** – easy to add custom categories or output formats.
- **CLI ready** – can be invoked from the command line (future enhancements).

## Installation
1. **Clone the repository**
   ```bash
   git clone https://github.com/your‑username/release-notes-generator.git
   cd release-notes-generator
   ```
2. **Create a virtual environment** (optional but recommended)
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # On Windows: .venv\Scripts\activate
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Set up a GitHub token** (required for the LangChain GitHub Toolkit). Export it as an environment variable:
   ```bash
   export GITHUB_TOKEN=your_personal_access_token
   ```
   The token needs `repo` scope for private repositories or `public_repo` for public ones.

## Usage Example
Below is a minimal example of how to generate release notes via the provided script.
```python
from release_notes_agent import generate_release_notes

# Define repository details
owner = "your-org"
repo = "your-repo"
base_branch = "main"
prev_tag = "v1.0.0"
new_tag = "v1.1.0"

# Generate notes
notes = generate_release_notes(
    owner=owner,
    repo=repo,
    base_branch=base_branch,
    previous_tag=prev_tag,
    new_tag=new_tag,
)

print(notes)
```
Running the script will output a Markdown block similar to:
```markdown
## Features
- Added user authentication flow.

## Fixes
- Resolved crash on startup when config file is missing.

## Documentation
- Updated API reference for the new endpoints.
```

For a full CLI experience, future versions will include a command like:
```bash
python -m release_notes_generator --owner your-org --repo your-repo --from v1.0.0 --to v1.1.0
```

## Contribution Guidelines
We welcome contributions! Please follow these steps:
1. **Fork the repository**.
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** and ensure the code passes existing tests (if any).
4. **Run linting/formatting** (we use `black` and `flake8`):
   ```bash
   black .
   flake8 .
   ```
5. **Commit your work** with clear messages.
6. **Push to your fork** and open a Pull Request against the `master` branch.
7. **Describe your changes** clearly in the PR description, linking any relevant issues.

### Code Style
- Follow PEP 8 guidelines.
- Use type hints where appropriate.
- Write docstrings for public functions and classes.

### Testing
If you add new functionality, include unit tests under the `tests/` directory and ensure they pass:
```bash
pytest
```

## License
This project is licensed under the MIT License – see the `LICENSE` file for details.
