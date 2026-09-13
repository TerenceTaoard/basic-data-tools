# Basic Data Tools

This project contains basic command-line tools for transforming, parsing, and summarizing data.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use .venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Test

```bash
python -m pytest
```

## Tool Table

| Tool | What it does | Main input | Main output |
|---|---|---|---|
| textstats | counts words/lines/tokens | text file | text/JSON report |

## Quick Start

After setup, try running textstats on the provided example file:

```bash
python scripts/textstats.py --input examples/textstats/sample.txt
```

Convert to lowercase and show only the top 10 most frequent words:

```bash
python scripts/textstats.py --input examples/textstats/sample.txt --lowercase --top-words 10
```

Output results as JSON:

```bash
python scripts/textstats.py --input examples/textstats/sample.txt --format json
```

Show all available options:

```bash
python scripts/textstats.py --help
```