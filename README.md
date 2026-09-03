# Release Notes Generator

## Overview

The **Release Notes Generator** is a Python project that automatically collects merged pull requests from a GitHub repository, categorizes them, and generates clean, Markdown‑formatted release notes. It leverages the **LangChain GitHub Toolkit** and **LangGraph** to orchestrate the workflow.

---

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/<your‑org>/release-notes-generator.git
   cd release-notes-generator
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # On Windows use `.venv\Scripts\activate`
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   - `GITHUB_TOKEN`: A personal access token with `repo` scope.
   - `GITHUB_REPO`: The target repository in the form `owner/name` (e.g., `myorg/myrepo`).
   - You can place these in a `.env` file and load them with `python-dotenv` (optional).

---

## Usage

The project provides a simple CLI entry‑point. After the setup steps above, run:

```bash
python -m src.release_notes_agent.main
```

The script will:
1. Authenticate with GitHub using the provided token.
2. Fetch all merged pull requests for the configured repository.
3. Categorize the PRs (Features, Fixes, Docs, Refactors, etc.).
4. Output a formatted Markdown release note to `stdout` (or to a file if you redirect the output).

### Example
```bash
python -m src.release_notes_agent.main > RELEASE_NOTES_2024_09_03.md
```

---

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes and ensure tests (if any) pass.
4. Push and open a PR against the `main` branch.

---

## License

This project is licensed under the MIT License.

---

## Existing Features (for reference)
- Fetches merged PRs from a GitHub repository
- Categorizes changes (Features, Fixes, Docs, Refactors, etc.)
- Generates Markdown release notes in a clean format
- Runs as a simple Python script (CLI planned)

---

## Tech Stack
- **Python 3.10+**
- [LangChain GitHub Toolkit](https://python.langchain.com/)
- [LangGraph](https://www.langchain.com/langgraph)

---

## Dummy Feature
Just testing Pull Requests for the Release Notes Generator project.
