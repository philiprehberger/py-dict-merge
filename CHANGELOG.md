# Changelog

## 0.3.0 (2026-04-28)

- Add `flatten(d, sep=".")` and `unflatten(d, sep=".")` helpers for converting between nested and dot-notation flat dicts
- `unflatten` raises `ValueError` on path conflicts (e.g. mixing `"a"` and `"a.b"`)
- Fix `pyproject.toml` description to end with a period (matches README one-liner)

## 0.2.0 (2026-04-27)

- Add `Strategy.CALLBACK` and `on_conflict` callable parameter to `merge()` for custom per-key conflict resolution
- Callback receives the dotted full key path (e.g. `"db.host"`) along with the conflicting left/right values

## 0.1.9 (2026-03-31)

- Standardize README to 3-badge format with emoji Support section
- Update CI checkout action to v5 for Node.js 24 compatibility
- Add GitHub issue templates, dependabot config, and PR template

## 0.1.8 (2026-03-22)

- Add pytest and mypy configuration to pyproject.toml

## 0.1.7

- Export and document MergeConflictError in API table
- Add Strategy.ERROR usage example to README
- Convert API section to table format

## 0.1.4

- Add Development section to README

## 0.1.1

- Add project URLs to pyproject.toml

## 0.1.0 (2026-03-10)

- Initial release
