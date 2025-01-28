Windows automator for Mixed In Key. Known works for MIK versions 10 and 11.

# Installation

Can install using pip:

`pip install git+https://github.com/bvandrc/mixed-in-key-automator@main`

Or add this line to your `requirements.txt`:

`git+https://github.com/bvandrc/mixed-in-key-automator@main`

# Development

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -e ".[dev]"
```

Lint with `pylint $(git ls-files '*.py')` and `pyright`, and format with `black .`. CI runs all three on pull requests.
