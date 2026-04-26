"""
AUTHOR: Rohan Joseph
PURPOSE: Shared repository settings, schema definitions, and filtering vocabularies.
DATE CREATED: 2026-04-25
DATE MODIFIED: 2026-04-25
MODIFIED BY: Rohan Joseph
"""



"""
Settings
"""

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

MISSING_SENTINELS = ["None", -999, "-999"]
EMPLOYER_RELEVANCE_THRESHOLD_DEFAULT = 0.0
EMPLOYER_MATCH_THRESHOLD_DEFAULT = 0.92
SUMMARY_TOP_N = 10


"""
Negative Filtering Settings
"""

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
        "Customer Service Representatives Sales Representatives, Wholesale and Manufacturing, Except Technical and Scientific Products",
        "Office Clerks, General",
        "Receptionists and Information Clerks",
        "Cashiers",
        "Insurance Sales Agents",
        "Real Estate Sales Agents",
        "Telemarketers",
        "Sales Representatives, Wholesale and Manufacturing, Except Technical and Scientific Products",
        "Sales Representatives, Wholesale and Manufacturing, Technical and Scientific Products",
    ],
    "lot_occupation_group_name": [],
    "lot_specialized_occupation_name": [],
}



"""
Finance Filtering Settings
"""

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



"""
Employer Matching Settings
"""

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

SUMMARY_CATEGORY_COLUMNS = [
    "company_name",
    "naics2_name",
    "soc_2_name",
    "lot_career_area_name",
    "title_clean",
]
