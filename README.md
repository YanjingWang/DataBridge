# DataBridge: Customer Records Normalizer

## Overview

BridgeCo receives raw customer export files from partner CRMs and must clean and load them into a central SQLite analytics database before downstream reporting runs. The ETL skeleton is partially built — you will complete the transform and load steps to normalize customer records, then write a SQL query to report active customers grouped by country.

## File Structure

```text
./
├── README.md                                  (PROVIDED)
├── pipeline.py                                (EDIT THIS)
├── queries/
│   └── active_customers_by_country.sql        (EDIT THIS)
├── data/
│   └── customers.csv                          (PROVIDED)
├── customers.db                               (PROVIDED)
├── seed.sql                                   (PROVIDED)
├── requirements.txt                           (PROVIDED)
├── conftest.py                                (PROVIDED)
└── tests/
    └── test_pipeline.py                       (PROVIDED)
```
