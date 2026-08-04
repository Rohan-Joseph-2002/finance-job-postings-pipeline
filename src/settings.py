"""
AUTHOR: Rohan Joseph
PURPOSE: Hold all settings, paths, thresholds, filtering vocabularies, and column schemas for the
         finance job-postings pipeline in one place, so every stage reads its configuration from a
         single source of truth instead of scattered constants.
DATE CREATED: 2026-04-25
DATE MODIFIED: 2026-08-04
MODIFIED BY: Rohan Joseph
"""



# ============================================================
# Importing Libraries and Utilities
# ============================================================

import os

from dotenv import load_dotenv



# ============================================================
# Environment and Paths
# ============================================================

# Load .env if present; values already set in the real environment always win.
load_dotenv()

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INPUT_DIR = os.path.join(ROOT, "input")
OUTPUT_DIR = os.path.join(ROOT, "output")
DATA_OUTPUT_DIR = os.path.join(OUTPUT_DIR, "data-output")
ANALYSIS_OUTPUT_DIR = os.path.join(OUTPUT_DIR, "analysis-output")
LOG_DIR = os.path.join(ROOT, "logs")



# ============================================================
# Runtime Settings
# ============================================================

RUNTIME_MODE = os.getenv("RUNTIME_MODE", "sample")

RAW_LIGHTCAST_DIR = os.path.join(INPUT_DIR, os.getenv("RAW_LIGHTCAST_SUBDIR", "lightcast_sample"))
EMPLOYER_DICTIONARY_PATH = os.path.join(
    INPUT_DIR, os.getenv("EMPLOYER_DICTIONARY_FILE", "lightcast_employer_dictionary_sample.csv")
)

EMPLOYER_RELEVANCE_THRESHOLD = float(os.getenv("EMPLOYER_RELEVANCE_THRESHOLD", "0.0"))
EMPLOYER_MATCH_THRESHOLD = float(os.getenv("EMPLOYER_MATCH_THRESHOLD", "0.92"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "50000"))
SUMMARY_TOP_N = 10



# ============================================================
# Column Schemas
# ============================================================

LIGHTCAST_MAIN_DATA_COLUMNS = [
    "id",
    "company",
    "company_name",
    "posted",
    "expired",
    "cip6_name",
    "naics2_name",
    "soc_2_name",
    "lot_career_area_name",
    "onet_name",
    "lot_occupation_group_name",
    "lot_specialized_occupation_name",
    "title_clean",
    "skills_name",
]

REORDER_COLUMNS = [
    "id",
    "company",
    "company_name",
    "posted",
    "expired",
    "title_clean",
    "naics2_name",
    "soc_2_name",
    "lot_career_area_name",
    "onet_name",
    "lot_occupation_group_name",
    "lot_specialized_occupation_name",
    "cip6_name",
    "skills_name",
]

KEY_CATEGORY_COLUMNS = [
    "naics2_name",
    "soc_2_name",
    "lot_career_area_name",
    "onet_name",
    "lot_occupation_group_name",
    "lot_specialized_occupation_name",
]

REFERENCE_EMPLOYER_COLUMNS = [
    "company",
    "company_name",
    "percentage_relevant_jobs",
    "count_of_relevant_jobs",
    "total_count_of_jobs",
]

SUMMARY_CATEGORY_COLUMNS = [
    "company_name",
    "naics2_name",
    "soc_2_name",
    "lot_career_area_name",
    "title_clean",
]

MISSING_SENTINELS = ["None", -999, "-999"]



# ============================================================
# Negative Filtering Vocabularies
# ============================================================

NEGATIVE_FILTERS = {
    "naics2_name": [
        "Manufacturing",
        "Administrative and Support and Waste Management and Remediation Services",
        "Retail Trade",
        "Accommodation and Food Services",
        "Educational Services",
        "Public Administration",
        "Transportation and Warehousing",
        "Other Services (except Public Administration)",
        "Construction",
        "Real Estate and Rental and Leasing",
        "Wholesale Trade",
        "Utilities",
        "Arts, Entertainment, and Recreation",
        "Agriculture, Forestry, Fishing and Hunting",
        "Mining, Quarrying, and Oil and Gas Extraction",
        "Health Care and Social Assistance",
        "Unclassified Industry",
    ],
    "soc_2_name": [
        "Healthcare Practitioners and Technical Occupations",
        "Architecture and Engineering Occupations",
        "Installation, Maintenance, and Repair Occupations",
        "Arts, Design, Entertainment, Sports, and Media Occupations",
        "Production Occupations",
        "Construction and Extraction Occupations",
        "Food Preparation and Serving Related Occupations",
        "Community and Social Service Occupations",
        "Transportation and Material Moving Occupations",
        "Personal Care and Service Occupations",
        "Life, Physical, and Social Science Occupations",
        "Building and Grounds Cleaning and Maintenance Occupations",
        "Healthcare Support Occupations",
        "Farming, Fishing, and Forestry Occupations",
        "Protective Service Occupations",
        "Military Specific Occupations",
        "Education, Training, and Library Occupations",
        "Unclassified Occupation",
        "Educational Instruction and Library Occupations",
        "Military-only occupations",
    ],
    "lot_career_area_name": [
        "Health Care including Nursing",
        "Construction, Extraction, and Architecture",
        "Hospitality, Food, and Tourism",
        "Education and Training",
        "Manufacturing and Production",
        "Community and Social Services",
        "Transportation",
        "Design, Media, and Writing",
        "Agriculture, Horticulture, & the Outdoors",
        "Maintenance, Repair, and Installation",
        "Performing Arts",
        "Personal Services",
        "Not Employed",
        "Information Technology and Computer Science",
        "Healthcare",
        "Unclassified Career Area",
        "Social Analysis and Planning",
    ],
    "onet_name": [
        "Office Clerks, General",
        "Receptionists and Information Clerks",
        "Cashiers",
        "Insurance Sales Agents",
        "Real Estate Sales Agents",
        "Telemarketers",
        (
            "Sales Representatives, Wholesale and Manufacturing, "
            "Except Technical and Scientific Products"
        ),
        "Sales Representatives, Wholesale and Manufacturing, Technical and Scientific Products",
    ],
    "lot_occupation_group_name": [],
    "lot_specialized_occupation_name": [],
}



# ============================================================
# Finance Inclusion Vocabularies
# ============================================================

CIP_KEEP_KEYWORDS = {
    "business administration and management, general",
    "accounting",
    "finance, general",
    "statistics, general",
    "mathematics, general",
    "applied mathematics",
    "actuarial science",
    "econometrics and quantitative economics",
    "applied mathematics, general",
    "financial mathematics",
    "business/commerce, general",
    "international business, trade, and tax law",
    "banking and financial support services",
    "applied economics",
    "economics, general",
}

FINANCE_KEYWORDS = {
    "finance",
    "financial",
    "bond",
    "equity",
    "banking",
    "bank",
    "trading",
    "stock market",
    "investment",
    "investor",
    "asset management",
    "funds",
    "swaps",
    "mortgage",
    "credit",
    "brokerage",
    "lending",
    "capital markets",
    "mutual fund",
    "hedge fund",
    "hedging",
    "derivatives",
}

TITLE_KEEP_KEYWORDS = FINANCE_KEYWORDS.union({
    "trader",
    "quantitative researcher",
    "analyst",
    "associate",
})



# ============================================================
# Employer Standardization Vocabularies
# ============================================================

EMPLOYER_NAME_SUFFIXES = {
    "inc",
    "incorporated",
    "corp",
    "corporation",
    "co",
    "company",
    "llc",
    "ltd",
    "limited",
    "lp",
    "llp",
    "plc",
}

EMPLOYER_GENERIC_TRAILING_WORDS = {
    "holdings",
    "holding",
    "group",
    "partners",
    "partner",
    "services",
    "service",
}

EMPLOYER_NAME_REPLACEMENTS = {
    "int'l": "international",
    "intl": "international",
    "u s": "us",
    "u s a": "us",
}
