# philiprehberger-dict-merge

[![Tests](https://github.com/philiprehberger/py-dict-merge/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-dict-merge/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-dict-merge.svg)](https://pypi.org/project/philiprehberger-dict-merge/)
[![License](https://img.shields.io/github/license/philiprehberger/py-dict-merge)](LICENSE)

Deep merge dictionaries safely with conflict resolution.

## Installation

```bash
pip install philiprehberger-dict-merge
```

## Usage

```python
from philiprehberger_dict_merge import merge, Strategy

base = {"db": {"host": "localhost", "port": 5432}, "debug": False}
override = {"db": {"port": 3306, "name": "mydb"}, "debug": True}

merge(base, override)
# {"db": {"host": "localhost", "port": 3306, "name": "mydb"}, "debug": True}

# Multiple dicts
merge(defaults, config_file, env_overrides)

# Keep first value on conflict
merge(a, b, strategy=Strategy.KEEP_FIRST)

# Append lists instead of replacing
merge(a, b, list_strategy="append")
```

## API

- `merge(*dicts, strategy=Strategy.REPLACE, list_strategy="replace")` — Deep merge
- `Strategy.REPLACE` — Later values win (default)
- `Strategy.KEEP_FIRST` — Earlier values win
- `Strategy.ERROR` — Raise on conflict
- List strategies: `"replace"`, `"append"`, `"unique"`, `"concat"`


## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## License

MIT
