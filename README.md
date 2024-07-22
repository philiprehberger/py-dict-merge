# philiprehberger-dict-merge

[![Tests](https://github.com/philiprehberger/py-dict-merge/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-dict-merge/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-dict-merge.svg)](https://pypi.org/project/philiprehberger-dict-merge/)
[![Last updated](https://img.shields.io/github/last-commit/philiprehberger/py-dict-merge)](https://github.com/philiprehberger/py-dict-merge/commits/main)

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

# Raise on conflict
from philiprehberger_dict_merge import MergeConflictError

try:
    merge({"key": 1}, {"key": 2}, strategy=Strategy.ERROR)
except MergeConflictError as e:
    print(e.key)   # "key"
    print(e.left)  # 1
    print(e.right) # 2
```

## API

| Function / Class | Description |
|------------------|-------------|
| `merge(*dicts, strategy=Strategy.REPLACE, list_strategy="replace")` | Deep merge |
| `Strategy.REPLACE` | Later values win (default) |
| `Strategy.KEEP_FIRST` | Earlier values win |
| `Strategy.ERROR` | Raise on conflict |
| `MergeConflictError` | Raised by `Strategy.ERROR` — has `.key`, `.left`, `.right` attributes |
| List strategies: `"replace"`, `"append"`, `"unique"`, `"concat"` | List merge modes |

## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## Support

If you find this project useful:

⭐ [Star the repo](https://github.com/philiprehberger/py-dict-merge)

🐛 [Report issues](https://github.com/philiprehberger/py-dict-merge/issues?q=is%3Aissue+is%3Aopen+label%3Abug)

💡 [Suggest features](https://github.com/philiprehberger/py-dict-merge/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)

❤️ [Sponsor development](https://github.com/sponsors/philiprehberger)

🌐 [All Open Source Projects](https://philiprehberger.com/open-source-packages)

💻 [GitHub Profile](https://github.com/philiprehberger)

🔗 [LinkedIn Profile](https://www.linkedin.com/in/philiprehberger)

## License

[MIT](LICENSE)
