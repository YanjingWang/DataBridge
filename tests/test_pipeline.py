import os
import sqlite3
import tempfile

import pytest

from pipeline import extract, load, transform


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

RAW_VALID = [
    {
        "name": "Priya Sharma",
        "email": "  Priya@Example.COM  ",
        "country": "India",
        "status": "Active",
        "signup_year": "2021",
    },
    {
        "name": "Tom Baker",
        "email": "tom@baker.co.uk",
        "country": "United Kingdom",
        "status": "INACTIVE",
        "signup_year": "2018",
    },
]

RAW_INVALID_EMAIL = [
    {
        "name": "Bad Email",
        "email": "not-an-email",
        "country": "US",
        "status": "active",
        "signup_year": "2020",
    },
    {
        "name": "Empty Email",
        "email": "",
        "country": "US",
        "status": "active",
        "signup_year": "2020",
    },
]

RAW_INVALID_YEAR = [
    {
        "name": "Bad Year",
        "email": "good@email.com",
        "country": "US",
        "status": "active",
        "signup_year": "N/A",
    },
    {
        "name": "Text Year",
        "email": "another@email.com",
        "country": "US",
        "status": "active",
        "signup_year": "abc",
    },
]


def make_db(records=None):
    """Create a temp SQLite DB with the customers schema, optionally seeded."""
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()

    conn = sqlite3.connect(tmp.name)
    conn.execute(
        """CREATE TABLE customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            country TEXT NOT NULL,
            status TEXT NOT NULL,
            signup_year INTEGER NOT NULL
        )"""
    )

    if records:
        conn.executemany(
            "INSERT INTO customers (name, email, country, status, signup_year) "
            "VALUES (:name, :email, :country, :status, :signup_year)",
            records,
        )

    conn.commit()
    conn.close()

    return tmp.name


# -------------------------------------------------------------------
# transform() tests
# -------------------------------------------------------------------

def test_transform_strips_and_lowercases_email():
    result = transform(RAW_VALID)
    emails = [r["email"] for r in result]
    assert "priya@example.com" in emails


def test_transform_normalizes_status_to_lowercase():
    result = transform(RAW_VALID)
    statuses = {r["status"] for r in result}

    assert all(s == s.lower() for s in statuses)
    assert "active" in statuses
    assert "inactive" in statuses


def test_transform_casts_signup_year_to_int():
    result = transform(RAW_VALID)

    for record in result:
        assert isinstance(record["signup_year"], int)


def test_transform_skips_rows_with_invalid_email():
    result = transform(RAW_INVALID_EMAIL)
    assert result == []


def test_transform_skips_rows_with_invalid_signup_year():
    result = transform(RAW_INVALID_YEAR)
    assert result == []


def test_transform_returns_only_valid_rows_from_mixed_input():
    mixed = RAW_VALID + RAW_INVALID_EMAIL + RAW_INVALID_YEAR
    result = transform(mixed)

    assert len(result) == len(RAW_VALID)


def test_transform_preserves_name_and_country():
    result = transform(RAW_VALID)

    names = [r["name"] for r in result]
    countries = [r["country"] for r in result]

    assert "Priya Sharma" in names
    assert "India" in countries


# -------------------------------------------------------------------
# load() tests
# -------------------------------------------------------------------

def test_load_inserts_all_records():
    records = [
        {
            "name": "Alice",
            "email": "alice@example.com",
            "country": "US",
            "status": "active",
            "signup_year": 2021,
        },
        {
            "name": "Bob",
            "email": "bob@example.com",
            "country": "UK",
            "status": "inactive",
            "signup_year": 2020,
        },
    ]

    db_path = make_db()

    try:
        load(records, db_path)

        conn = sqlite3.connect(db_path)
        count = conn.execute(
            "SELECT COUNT(*) FROM customers"
        ).fetchone()[0]
        conn.close()

        assert count == 2

    finally:
        os.unlink(db_path)


def test_load_replaces_existing_rows():
    existing = [
        {
            "name": "Old Record",
            "email": "old@example.com",
            "country": "US",
            "status": "active",
            "signup_year": 2015,
        }
    ]

    new_records = [
        {
            "name": "New Record",
            "email": "new@example.com",
            "country": "DE",
            "status": "inactive",
            "signup_year": 2023,
        },
        {
            "name": "New Record 2",
            "email": "new2@example.com",
            "country": "FR",
            "status": "active",
            "signup_year": 2022,
        },
    ]

    db_path = make_db(existing)

    try:
        load(new_records, db_path)

        conn = sqlite3.connect(db_path)
        rows = conn.execute(
            "SELECT name FROM customers"
        ).fetchall()
        conn.close()

        names = [r[0] for r in rows]

        assert "Old Record" not in names
        assert len(names) == 2

    finally:
        os.unlink(db_path)


def test_load_stores_correct_field_values():
    records = [
        {
            "name": "Carol",
            "email": "carol@example.com",
            "country": "Germany",
            "status": "active",
            "signup_year": 2019,
        }
    ]

    db_path = make_db()

    try:
        load(records, db_path)

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row

        row = conn.execute(
            "SELECT * FROM customers"
        ).fetchone()

        conn.close()

        assert row["email"] == "carol@example.com"
        assert row["country"] == "Germany"
        assert row["status"] == "active"
        assert row["signup_year"] == 2019

    finally:
        os.unlink(db_path)


# -------------------------------------------------------------------
# SQL query tests (end-to-end)
# -------------------------------------------------------------------

SQL_QUERY_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "queries",
    "active_customers_by_country.sql",
)


def run_query_on_db(db_path, sql):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(sql).fetchall()

    conn.close()

    return [dict(r) for r in rows]


def test_sql_query_file_exists():
    assert os.path.isfile(
        SQL_QUERY_PATH
    ), "queries/active_customers_by_country.sql not found"


def test_sql_query_returns_active_customers_only():
    """The query must count only active-status customers."""

    seed_records = [
        {
            "name": "A",
            "email": "a@x.com",
            "country": "US",
            "status": "active",
            "signup_year": 2020,
        },
        {
            "name": "B",
            "email": "b@x.com",
            "country": "US",
            "status": "inactive",
            "signup_year": 2020,
        },
        {
            "name": "C",
            "email": "c@x.com",
            "country": "DE",
            "status": "active",
            "signup_year": 2021,
        },
    ]

    db_path = make_db(seed_records)

    with open(SQL_QUERY_PATH) as f:
        sql = f.read()

    try:
        results = run_query_on_db(db_path, sql)

        result_map = {
            r["country"]: r["active_count"]
            for r in results
        }

        assert result_map.get("US") == 1
        assert result_map.get("DE") == 1
        assert "inactive" not in str(results)

    finally:
        os.unlink(db_path)


def test_sql_query_ordered_by_count_descending():
    """Rows must be ordered highest count first."""

    seed_records = [
        {
            "name": "A",
            "email": "a@x.com",
            "country": "US",
            "status": "active",
            "signup_year": 2020,
        },
        {
            "name": "B",
            "email": "b@x.com",
            "country": "US",
            "status": "active",
            "signup_year": 2021,
        },
        {
            "name": "C",
            "email": "c@x.com",
            "country": "US",
            "status": "active",
            "signup_year": 2022,
        },
        {
            "name": "D",
            "email": "d@x.com",
            "country": "India",
            "status": "active",
            "signup_year": 2020,
        },
        {
            "name": "E",
            "email": "e@x.com",
            "country": "India",
            "status": "active",
            "signup_year": 2021,
        },
        {
            "name": "F",
            "email": "f@x.com",
            "country": "Germany",
            "status": "active",
            "signup_year": 2022,
        },
    ]

    db_path = make_db(seed_records)

    with open(SQL_QUERY_PATH) as f:
        sql = f.read()

    try:
        results = run_query_on_db(db_path, sql)

        counts = [r["active_count"] for r in results]

        assert counts == sorted(counts, reverse=True)
        assert results[0]["country"] == "US"
        assert results[0]["active_count"] == 3

    finally:
        os.unlink(db_path)


def test_sql_query_groups_by_country():
    """Each country must appear exactly once."""

    seed_records = [
        {
            "name": "A",
            "email": "a@x.com",
            "country": "US",
            "status": "active",
            "signup_year": 2020,
        },
        {
            "name": "B",
            "email": "b@x.com",
            "country": "US",
            "status": "active",
            "signup_year": 2021,
        },
        {
            "name": "C",
            "email": "c@x.com",
            "country": "DE",
            "status": "active",
            "signup_year": 2020,
        },
    ]

    db_path = make_db(seed_records)

    with open(SQL_QUERY_PATH) as f:
        sql = f.read()

    try:
        results = run_query_on_db(db_path, sql)

        countries = [r["country"] for r in results]

        assert len(countries) == len(
            set(countries)
        ), "Duplicate countries in result"

    finally:
        os.unlink(db_path)


# -------------------------------------------------------------------
# Full pipeline integration test
# -------------------------------------------------------------------

def test_full_pipeline_with_csv(tmp_path):
    """extract → transform → load produces the correct row count."""

    csv_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "data",
        "customers.csv",
    )

    rows = extract(csv_path)
    records = transform(rows)

    # The CSV has 26 raw rows; 4 must be filtered out
    # (2 invalid emails, 2 bad years)
    assert len(records) == 22

    db_path = str(tmp_path / "test.db")

    conn = sqlite3.connect(db_path)

    conn.execute(
        """CREATE TABLE customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            country TEXT NOT NULL,
            status TEXT NOT NULL,
            signup_year INTEGER NOT NULL
        )"""
    )

    conn.commit()
    conn.close()

    load(records, db_path)

    conn = sqlite3.connect(db_path)

    count = conn.execute(
        "SELECT COUNT(*) FROM customers"
    ).fetchone()[0]

    conn.close()

    assert count == 22