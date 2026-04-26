# Finance Job Postings Pipeline

Standalone research pipeline for constructing, matching, and analyzing finance-related job posting samples from Lightcast-style raw posting exports.

## Overview

This repository builds a finance-focused job-postings dataset from raw Lightcast-style monthly exports. It is designed as a reproducible empirical data pipeline rather than a notebook collection: raw postings are cleaned, finance-related jobs are identified, employer names are standardized and matched to a reference employer dataset, and summary statistics are generated from the final outputs.

The repo is organized as a staged pipeline so each major transformation is explicit and inspectable. Each stage writes CSV outputs and a Markdown run log, which makes it easier to validate intermediate results and trace how the final analytical sample was constructed.

## Purpose

The repository does six things:

1. Clean raw monthly job-posting files and remove clearly irrelevant sectors or occupations.
2. Construct a finance-related jobs sample using multiple inclusion signals.
3. Standardize employer names from the finance sample and the reference employer file.
4. Match finance-sample employers to the reference employer list.
5. Build an employer-filtered finance jobs sample.
6. Generate summary statistics for the main and employer-filtered samples.

The main outputs are stage-level CSVs, employer matching tables, and summary-statistics tables that can be used for downstream labor-market analysis.

## Key Definitions

- `Lightcast`: a labor-market data source that provides structured job-posting exports and related employer metadata.
- `NAICS`: the North American Industry Classification System used to label industries such as `Finance and Insurance`.
- `CIP`: the Classification of Instructional Programs used to label education fields and degree areas.
- `SOC` / `O*NET`: occupational classification systems used to label job families and occupations.
- `Entity Resolution`: the process of standardizing and matching employer names across datasets when the raw names are inconsistent.

## Data Access Notes

The raw input data is not tracked in this repository. If you'd like to discuss the sample data structure, expected schema, or reproduction details, feel free to contact me.

## Pipeline Stages

### Stage 1: Initial Data Filtering

This stage reads raw monthly posting files, standardizes missing values, drops rows with no usable classification information, and removes postings that fall into clearly irrelevant sectors or occupations.

Primary output:

- Output file: `output/exports/001_initial_data_filtering/<month>_initial_data_filtering.csv`

### Stage 2: Finance-Related Jobs

This stage reads the Stage 1 outputs and identifies finance-related jobs using multiple signals:

- Industry (`naics2_name`)
- Education field (`cip6_name`)
- Skills (`skills_name`)
- Title (`title_clean`)

Jobs are retained when they satisfy at least two inclusion signals.

Primary output:

- Output file: `output/exports/002_finance_related_jobs/<month>_finance_related_jobs.csv`

### Stage 3: Employer Name Standardization

This stage constructs employer-level tables from the Stage 2 finance sample and the external employer reference dataset, then standardizes employer names so they can be compared consistently.

Primary outputs:

- Output file: `output/exports/003_employer_name_standardization/finance_job_employers_standardized.csv`
- Output file: `output/exports/003_employer_name_standardization/reference_employers_standardized.csv`

### Stage 4: Employer Name Matching

This stage matches standardized finance-sample employer names to the standardized reference employer list using exact standardized-name matches and a fuzzy fallback.

Primary outputs:

- Output file: `output/exports/004_employer_name_matching/employer_name_matches.csv`
- Output file: `output/exports/004_employer_name_matching/unmatched_finance_job_employers.csv`

### Stage 5: Employer Filtered Finance Jobs

This stage filters the Stage 2 finance-related jobs sample to employers that matched the external employer reference dataset and appends the matched employer metadata.

Primary output:

- Output file: `output/exports/005_employer_filtered_finance_jobs/<month>_employer_filtered_finance_jobs.csv`

### Stage 6: Summary Statistics

This stage generates dataset-level summary statistics for the finance-related jobs sample, the employer-filtered finance jobs sample, and a comparison between the two.

Primary outputs:

- Output file: `output/exports/006_summary_statistics/finance_related_jobs_summary_statistics.csv`
- Output file: `output/exports/006_summary_statistics/employer_filtered_finance_jobs_summary_statistics.csv`
- Output file: `output/exports/006_summary_statistics/cross_dataset_summary_statistics.csv`

## Repository Structure

```text
finance-job-postings-pipeline/
├── .env.example
├── .gitignore
├── README.md
├── pyproject.toml
├── requirements.txt
├── scripts/
│   ├── 001_initial_data_filtering.py
│   ├── 002_finance_related_jobs.py
│   ├── 003_employer_name_standardization.py
│   ├── 004_employer_name_matching.py
│   ├── 005_employer_filtered_finance_jobs.py
│   ├── 006_summary_statistics.py
│   ├── 00A_run_all.py
│   ├── check_env.py
│   ├── run_pipeline.py
│   └── setup_env.py
├── src/
│   └── project/
│       ├── __init__.py
│       ├── config.py
│       ├── env.py
│       ├── io.py
│       ├── logger.py
│       ├── paths.py
│       ├── settings.py
│       ├── utils.py
│       ├── validation.py
│       ├── analysis/
│       │   ├── __init__.py
│       │   └── summary_statistics.py
│       ├── matching/
│       │   ├── __init__.py
│       │   └── employer_names.py
│       └── pipelines/
│           ├── __init__.py
│           ├── employer_filter.py
│           ├── employer_matching.py
│           ├── employer_standardization.py
│           ├── finance_related.py
│           ├── initial_filtering.py
│           └── summary_statistics.py
├── tests/
│   ├── conftest.py
│   ├── test_employer_matching.py
│   ├── test_finance_related.py
│   ├── test_initial_filtering.py
│   ├── test_setup_env.py
│   ├── test_summary_statistics.py
│   └── test_validation.py
├── input/
└── output/
    ├── exports/
    ├── figures/
    ├── logs/
    └── tables/
```

## Required Inputs

- Raw Lightcast-style monthly posting files under `RAW_LIGHTCAST_DIR`
- Employer reference file at `EMPLOYER_JOB_POSTINGS_PATH`

Raw data is not stored in the git history for this repo. The repository expects you to place the input files in the local `input/` directory or point the `.env` paths to an external location on your machine.

The expected raw layout under `RAW_LIGHTCAST_DIR` is:

```text
RAW_LIGHTCAST_DIR/
├── 2021/
│   ├── all_for_2021-03-01/
│   │   ├── file_a.csv
│   │   ├── file_a.csv.gz
│   │   └── file_b.csv.gz
│   └── all_for_2021-04-01/
└── 2022/
```

The raw posting files should contain, at minimum, the columns used by the pipeline:

- Field: `id`
- Field: `company`
- Field: `company_name`
- Field: `posted`
- Field: `expired`
- Field: `cip6_name`
- Field: `naics2_name`
- Field: `soc_2_name`
- Field: `lot_career_area_name`
- Field: `onet_name`
- Field: `lot_occupation_group_name`
- Field: `lot_specialized_occupation_name`
- Field: `title_clean`
- Field: `skills_name`

The employer reference file should contain, at minimum:

- Field: `company`
- Field: `company_name`
- Field: `count_of_relevant_jobs`
- Field: `total_count_of_jobs`
- Field: `percentage_relevant_jobs`

## Input Data Examples

### Example Raw Posting Layout

If you keep the inputs inside the repository, the expected local structure is:

```text
input/
├── lightcast_sample/
│   ├── 2021/
│   │   ├── all_for_2021-03-01/
│   │   │   ├── 2021_main_data_0_0_0.csv
│   │   │   └── 2021_main_data_0_0_1.csv.gz
│   │   └── all_for_2021-04-01/
│   └── 2022/
└── reference/
    └── employer_job_postings_dictionary.csv
```

### Example Raw Posting Rows

Below is a fake example showing the full raw input schema across continuation tables. The values are shortened so the structure stays readable, but the column names match the actual Lightcast sample file used in the repo.

#### Raw Posting Example Part 1

| id | city | city_name | company | company_name | company_raw | company_is_staffing | duplicates | education_levels | education_levels_name | min_edulevels | min_edulevels_name | max_edulevels | max_edulevels_name | employment_type | employment_type_name | min_years_experience | max_years_experience | expired | is_internship | location | county |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `job_0001` | `enc_sd` | `San Diego, CA` | `1001` | `Example Capital Partners` | `Example Capital Partners LLC` | `false` | `1` | `2` | `Bachelor's degree` | `2` | `Bachelor's degree` | `` | `` | `1` | `Full-time` | `2` | `5` | `2021-04-11` | `false` | `{"lat":32.7,"lon":-117.1}` | `6073` |

#### Raw Posting Example Part 2

| county_name | msa | msa_name | state | state_name | naics2 | naics2_name | naics3 | naics3_name | naics4 | naics4_name | naics5 | naics5_name | naics6 | naics6_name | duration | posted | title | title_name | title_raw | title_clean | body |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `San Diego, CA` | `41740` | `San Diego Metro` | `6` | `California` | `52` | `Finance and Insurance` | `523` | `Securities, Commodity Contracts` | `5231` | `Investment Banking` | `52311` | `Investment Banking and Securities` | `523110` | `Investment Banking and Securities Dealing` | `30` | `2021-03-12` | `ttl_001` | `Financial Analyst` | `Junior Financial Analyst` | `financial analyst` | `Short example job text.` |

#### Raw Posting Example Part 3

| salary | skills | skills_name | specialized_skills | specialized_skills_name | certifications | certifications_name | common_skills | common_skills_name | remote_type | remote_type_name | onet | onet_name | onet_2019 | onet_2019_name | sources | url | active_urls | salary_to | salary_from | software_skills | software_skills_name |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `` | `sk1\\|sk2\\|sk3` | `financial modeling\\|valuation\\|excel` | `ssk1\\|ssk2` | `valuation\\|forecasting` | `c1` | `CFA Level I` | `ck1\\|ck2` | `communication\\|analysis` | `0` | `On-site` | `13-2051.00` | `Financial and Investment Analysts` | `13-2051.00` | `Financial and Investment Analysts` | `jobboard.example` | `https://example.com/job/1` | `https://example.com/job/1` | `95000` | `75000` | `sw1\\|sw2` | `excel\\|sql` |

#### Raw Posting Example Part 4

| cip6 | cip6_name | cip4 | cip4_name | cip2 | cip2_name | original_pay_period | soc_2021_2 | soc_2021_2_name | soc_2021_3 | soc_2021_3_name | soc_2021_4 | soc_2021_4_name | soc_2021_5 | soc_2021_5_name | lot_career_area | lot_career_area_name | lot_occupation | lot_occupation_name | lot_specialized_occupation | lot_specialized_occupation_name | lot_occupation_group |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `52.0801` | `Finance, General` | `52.08` | `Finance and Financial Management Services` | `52` | `Business, Management, Marketing` | `YEAR` | `13-0000` | `Business and Financial Operations Occupations` | `13-2000` | `Financial Specialists` | `13-2050` | `Financial Specialists, All Other` | `13-2051` | `Financial Analysts` | `12` | `Finance` | `1201` | `Analyst` | `120101` | `Financial Analyst` | `1200` |

#### Raw Posting Example Part 5

| lot_occupation_group_name | lot_v6_specialized_occupation | lot_v6_specialized_occupation_name | lot_v6_occupation | lot_v6_occupation_name | lot_v6_occupation_group | lot_v6_occupation_group_name | lot_v6_career_area | lot_v6_career_area_name | soc_2 | soc_2_name | soc_3 | soc_3_name | soc_4 | soc_4_name | soc_5 | soc_5_name | last_updated_date | source_types | lightcast_sectors | lightcast_sectors_name | naics_2017_2 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Financial Analysts` | `120101` | `Financial Analyst` | `1201` | `Analyst` | `1200` | `Financial Analysts` | `12` | `Finance` | `13-0000` | `Business and Financial Operations Occupations` | `13-2000` | `Financial Specialists` | `13-2050` | `Financial Specialists, All Other` | `13-2051` | `Financial Analysts` | `2023-12-14` | `Job Board` | `` | `` | `52` |

#### Raw Posting Example Part 6

| naics_2017_2_name | naics_2017_3 | naics_2017_3_name | naics_2017_4 | naics_2017_4_name | naics_2017_5 | naics_2017_5_name | naics_2017_6 | naics_2017_6_name | naics_2022_2 | naics_2022_2_name | naics_2022_3 | naics_2022_3_name | naics_2022_4 | naics_2022_4_name | naics_2022_5 | naics_2022_5_name | naics_2022_6 | naics_2022_6_name | modeled_expired | modeled_duration |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Finance and Insurance` | `523` | `Securities, Commodity Contracts` | `5231` | `Investment Banking` | `52311` | `Investment Banking and Securities` | `523110` | `Investment Banking and Securities Dealing` | `52` | `Finance and Insurance` | `523` | `Securities, Commodity Contracts` | `5231` | `Investment Banking` | `52311` | `Investment Banking and Securities` | `523110` | `Investment Banking and Securities Dealing` | `2021-04-11` | `30` |

### Example Employer Reference Rows

Below is a fake example of the reference file used in Stages 3 through 5. The percentage field is stored as a percentage-point value in the actual file, not as a `0` to `1` share.

| company | company_name | count_of_relevant_jobs | total_count_of_jobs | percentage_relevant_jobs | naics2_distribution |
| --- | --- | --- | --- | --- | --- |
| `2001` | `Example Capital Partners` | `87` | `100` | `87.0` | `Finance and Insurance: 87` |
| `2002` | `Demo Savings Bank` | `92` | `100` | `92.0` | `Finance and Insurance: 92` |
| `2003` | `Sample Retail Group` | `4` | `100` | `4.0` | `Retail Trade: 4` |

## Setup

`setup_env.py` creates the expected local directories, creates `.env` from the tracked `.env.example` template when `.env` does not already exist, and installs the packages listed in `requirements.txt` into the current interpreter or the local `.venv` if one exists.

```bash
python3 scripts/setup_env.py
python3 scripts/check_env.py
```

This repository expects a repo-local `.env` file at the project root. On first run, `setup_env.py` seeds that file from `.env.example`, after which you can edit `.env` for your local machine. The tracked sample template contains:

```bash
RAW_LIGHTCAST_DIR=input/lightcast_sample
EMPLOYER_JOB_POSTINGS_PATH=input/reference/Sample Set - Lightcast Employer-Job Postings Dictionary.csv
EMPLOYER_RELEVANCE_THRESHOLD=0.0
EMPLOYER_MATCH_THRESHOLD=0.92
CHUNK_SIZE=50000
RUNTIME_MODE=local
```

## Run

Run all stages:

```bash
python3 scripts/run_pipeline.py --all
```

Run one stage:

```bash
python3 scripts/run_pipeline.py --stage 003_employer_name_standardization
```

## Outputs

The repository writes two kinds of outputs:

- Stage logs in `output/logs/`
- Stage exports in `output/exports/`

The expected output structure is:

```text
output/
├── exports/
│   ├── 001_initial_data_filtering/
│   │   └── 2021-03_initial_data_filtering.csv
│   ├── 002_finance_related_jobs/
│   │   └── 2021-03_finance_related_jobs.csv
│   ├── 003_employer_name_standardization/
│   │   ├── finance_job_employers_standardized.csv
│   │   └── reference_employers_standardized.csv
│   ├── 004_employer_name_matching/
│   │   ├── employer_name_matches.csv
│   │   └── unmatched_finance_job_employers.csv
│   ├── 005_employer_filtered_finance_jobs/
│   │   └── 2021-03_employer_filtered_finance_jobs.csv
│   └── 006_summary_statistics/
│       ├── cross_dataset_summary_statistics.csv
│       ├── employer_filtered_finance_jobs_summary_statistics.csv
│       └── finance_related_jobs_summary_statistics.csv
└── logs/
    ├── 001_initial_data_filtering.md
    ├── 002_finance_related_jobs.md
    ├── 003_employer_name_standardization.md
    ├── 004_employer_name_matching.md
    ├── 005_employer_filtered_finance_jobs.md
    └── 006_summary_statistics.md
```

### Example Output Rows

The examples below are fake but aligned to the actual output schemas written by the pipeline.

Stage 2 finance-related jobs output should look like this:

| id | company | company_name | posted | expired | title_clean | naics2_name | soc_2_name | lot_career_area_name | onet_name | lot_occupation_group_name | lot_specialized_occupation_name | cip6_name | skills_name |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `job_0001` | `1001` | `Example Capital Partners LLC` | `2021-03-12` | `2021-04-11` | `financial analyst` | `Finance and Insurance` | `Business and Financial Operations Occupations` | `Finance` | `Financial and Investment Analysts` | `Financial Analysts` | `Financial Analyst` | `Finance, General` | `financial modeling\\|valuation\\|excel` |

Stage 3 finance-employer standardization output should look like this:

| company | company_name | company_name_standardized | job_posting_count |
| --- | --- | --- | --- |
| `1001` | `Example Capital Partners LLC` | `example capital partners` | `12` |
| `1002` | `Demo Savings Bank Inc` | `demo savings bank` | `9` |

Stage 3 reference-employer standardization output should look like this:

| company | company_name | company_name_standardized | job_posting_count | percentage_relevant_jobs | count_of_relevant_jobs | total_count_of_jobs |
| --- | --- | --- | --- | --- | --- | --- |
| `2001` | `Example Capital Partners` | `example capital partners` | `1` | `87.0` | `87` | `100` |
| `2002` | `Demo Savings Bank` | `demo savings bank` | `1` | `92.0` | `92` | `100` |

Stage 4 employer matching output should look like this:

| source_company | source_company_name | source_company_name_standardized | source_job_posting_count | reference_company | reference_company_name | reference_company_name_standardized | reference_job_posting_count | percentage_relevant_jobs | match_method | match_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `1001` | `Example Capital Partners LLC` | `example capital partners` | `12` | `2001` | `Example Capital Partners` | `example capital partners` | `87` | `87.0` | `exact_standardized_name` | `1.0` |

Stage 5 employer-filtered finance jobs output should look like a job-level finance dataset with the matched employer metadata appended. The actual Stage 5 file retains the Stage 2 job-level columns and adds the employer-match columns shown below.

| id | company | company_name | posted | expired | title_clean | naics2_name | soc_2_name | lot_career_area_name | onet_name | lot_occupation_group_name | lot_specialized_occupation_name | cip6_name | skills_name | source_company_name_standardized | reference_company | reference_company_name | reference_company_name_standardized | reference_job_posting_count | percentage_relevant_jobs | match_method | match_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `job_0001` | `1001` | `Example Capital Partners LLC` | `2021-03-12` | `2021-04-11` | `financial analyst` | `Finance and Insurance` | `Business and Financial Operations Occupations` | `Finance` | `Financial and Investment Analysts` | `Financial Analysts` | `Financial Analyst` | `Finance, General` | `financial modeling\\|valuation\\|excel` | `example capital partners` | `2001` | `Example Capital Partners` | `example capital partners` | `87` | `87.0` | `exact_standardized_name` | `1.0` |

Stage 6 summary-statistics output should look like this:

| section | metric | value | notes |
| --- | --- | --- | --- |
| `dataset_info` | `row_count` | `298` | `Total number of rows in finance_related_jobs.` |
| `dataset_info` | `unique_companies` | `169` | `Count of unique company identifiers.` |

## Data Management

- Everything under `input/` and `output/` is gitignored.
- You should place the raw input data for this repo inside `input/` or point the `.env` paths to an external data location on your machine.
- At minimum, `input/` needs:
  - A Lightcast-style directory tree for monthly posting files
  - An employer reference CSV for the matching stages
- The repository code, tests, and configuration are meant to be versioned; the raw inputs and generated outputs are not.

## Limitations

- The repository is path-configured through `.env`, so reproducibility still depends on the local input layout being restored correctly.
- The included tests cover core filtering, employer matching, validation, and summary-statistics helpers.
- The current test suite is unit-level rather than fully end-to-end: it checks core transformation logic in isolation, but it does not yet serve as a full integration test of the entire pipeline and all written outputs.
