# Finance Job Postings Pipeline

Standalone pipeline that builds a finance-focused job-postings sample from raw Lightcast-style
monthly exports, links postings to a reference employer list, and summarizes the result.

## Why this matters

Raw job-posting exports are huge and noisy: most postings are not finance, employer names are
written inconsistently, and the useful signal is spread across several taxonomy fields. This
pipeline cleans each month's postings, keeps finance jobs that agree across at least two signals,
resolves employer names to a reference dictionary, and produces an analysis-ready sample — all in
pure pandas, chunked so large monthly files stay within memory.

## Quickstart

```bash
python setup_env.py                 # create .venv, install deps, write .env from .env.example
source .venv/bin/activate
python run_all.py                   # run the data/ then analysis/ stages in order
pytest                              # run the tests
```

The repo ships small **synthetic** sample inputs under `input/` and defaults to
`RUNTIME_MODE=sample`, so everything above runs fully offline. Point `.env` at your own Lightcast
folder and employer dictionary to run on real data.

## Stages

Run in order by `run_all.py`; each writes a Markdown log to `logs/`. Stages 1, 2, and 5 write one
file per month; stages 3, 4, and the summary aggregate across all months.

| Script | Does | Writes to |
|--------|------|-----------|
| `data/d001_initial_data_filtering.py` | Clean each monthly file in chunks; drop uncategorized rows and denylisted sectors/occupations | `output/data-output/` |
| `data/d002_finance_related_jobs.py` | Keep jobs appearing in ≥2 of four finance signals (industry, education, skills, title) | `output/data-output/` |
| `data/d003_employer_name_standardization.py` | Standardize finance-sample and reference employer names into employer-level tables | `output/data-output/` |
| `data/d004_employer_name_matching.py` | Match standardized finance employers to the reference list (exact then fuzzy) | `output/data-output/` |
| `data/d005_employer_filtered_finance_jobs.py` | Keep finance jobs whose employer matched the reference list | `output/data-output/` |
| `analysis/a001_summary_statistics.py` | Summarize the finance and employer-filtered samples and compare them | `output/analysis-output/` |

The shared employer standardization and matching logic lives in `src/matching.py` and is used by
stages 3, 4, and 5.

## Layout

```text
src/          shared code: settings (config + paths + vocabularies), io, logger, utils, validation, matching
data/         d001–d005 data-processing scripts
analysis/     a001 summary script
input/        committed synthetic sample postings + employer dictionary (real data gitignored)
output/       data-output/ and analysis-output/ (gitignored)
logs/         one <script>.md per run
tests/        pytest (t001–t007)
```

## How finance selection works

A posting is kept when it matches at least two of four inclusion signals: the industry is Finance
and Insurance (`naics2_name`), the education field is a finance/quantitative CIP, the skills text
contains a finance keyword, or the cleaned title contains a finance-or-role keyword. Requiring two
independent signals keeps any single noisy taxonomy field from deciding inclusion on its own.

## How employer resolution works

Employer names are standardized by folding case, punctuation, legal suffixes (`inc`, `llc`, `co`,
…), a leading "the", and generic trailing words (`group`, `holdings`, `partners`, …). Standardized
finance employers are matched to the standardized reference dictionary — exact standardized-name
match first, then a token-aware `difflib` fuzzy fallback at or above `EMPLOYER_MATCH_THRESHOLD`
(default 0.92). Stage 5 keeps only postings whose employer matched.

## Data & reproducibility

- Inputs: a folder of monthly posting CSVs (`LIGHTCAST_MAIN_DATA_COLUMNS`) and a reference employer
  dictionary (`REFERENCE_EMPLOYER_COLUMNS`), both declared in `src/settings.py`.
- The committed samples are synthetic and internally consistent — they exercise negative
  filtering, the two-signal finance rule, exact employer matches, and an unmatched employer that is
  filtered out; real inputs are gitignored.

## Testing

```bash
pytest
```

Tests cover cleaning and negative filtering, the finance two-signal rule, employer standardization
and matching, the employer filter, the summary builders, and the validation guards.

## License

Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
