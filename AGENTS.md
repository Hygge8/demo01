# Repository guidance

## Project

This repository contains nine Olist CSV datasets and standard-library Python utilities. Use Python 3.11 or later. The default data directory is `data/raw/`; locate it relative to the repository, not the caller's working directory.

## Data

- Treat `data/raw/` as source data. Keep its original bytes unless the task explicitly changes the dataset.
- `data/manifest.json` records the checked-in CSV schema, record counts, sizes and SHA-256 hashes. Explain any deliberate changes to the data and manifest together.
- Read CSV with `csv.reader` and `newline=""`. Review text can include quoted line breaks; line counts are not record counts.
- Keep outputs in `reports/` or `output/`. Commit code and useful documentation separately from generated outputs.

## Development

- Linux initialization: `bash scripts/setup.sh`.
- No third-party packages are needed for the current scripts. Document and pin dependencies if introducing them.
- Keep scripts usable from Linux and Windows. Shell scripts use LF; CSV files have Git text conversion disabled.
- Keep `README.md`, `data/README.md` and `docs/cloud-environment.md` consistent with changed paths and commands.

## Verification

Run these from the repository root after modifying validation code or data:

```bash
python -m unittest discover -s tests -v
python scripts/validate_data.py
```

`python scripts/validate_data.py --quick` checks existence, size and headers only. Use full validation for integrity claims. After changing environment configuration, also run `bash -n scripts/setup.sh` and test initialization in Linux when available.

## Cloud setup

The repository script is an installation entry point. The user's Codex Cloud environment must be created and published through the account's environment settings. Report these states separately; repository files alone do not prove that a cloud environment is active.
