"""
test_xray_importer.py
SQAI-14 — Unit tests for Xray importer pre/post validation logic
"""
import csv
import os
import pytest
import tempfile
from unittest.mock import patch, MagicMock
from xray_importer import validate_csv, REQUIRED_HEADERS

# ── Fixtures ──────────────────────────────────────────────────────────────────

def make_csv(rows: list, path: str):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for row in rows:
            writer.writerow(row)

VALID_HEADER = [
    "Test ID", "Issue Type", "Test Summary", "Test Priority",
    "Test Type", "Assignee", "Labels", "Test Repo Path",
    "Action", "Data", "Expected Result"
]

VALID_TC_ROW = [
    "TC-001", "Test", "Verify login", "High", "Functional",
    "sergio.juarez", "Sprint-1", "/SergioQE/Epic1",
    "Navigate to login page", "URL: /login", ""
]

VALID_STEP_ROW = [
    "", "", "", "", "", "", "", "",
    "Enter credentials", "user@test.com", "Login page shown"
]

VALID_LAST_STEP = [
    "", "", "", "", "", "", "", "",
    "Verify dashboard", "", "Dashboard is displayed"
]

# ── Required header tests ─────────────────────────────────────────────────────

def test_all_required_headers_present():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        path = f.name
    try:
        make_csv([VALID_HEADER, VALID_TC_ROW, VALID_LAST_STEP], path)
        rows = validate_csv(path)
        assert rows[0] == VALID_HEADER
    finally:
        os.unlink(path)

def test_missing_required_header_raises():
    bad_header = [h for h in VALID_HEADER if h != "Test ID"]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        path = f.name
    try:
        make_csv([bad_header, VALID_TC_ROW], path)
        with pytest.raises(ValueError, match="Missing required columns"):
            validate_csv(path)
    finally:
        os.unlink(path)

def test_empty_csv_raises():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        path = f.name
    try:
        make_csv([], path)
        with pytest.raises(ValueError, match="empty"):
            validate_csv(path)
    finally:
        os.unlink(path)

# ── SQAI-31: Test ID validation ───────────────────────────────────────────────

def test_sqai31_test_id_present_on_tc_row():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        path = f.name
    try:
        make_csv([VALID_HEADER, VALID_TC_ROW, VALID_LAST_STEP], path)
        rows = validate_csv(path)
        assert rows[1][0] == "TC-001"
    finally:
        os.unlink(path)

def test_sqai31_missing_test_id_raises():
    bad_tc = [""] + VALID_TC_ROW[1:]  # blank Test ID
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        path = f.name
    try:
        make_csv([VALID_HEADER, bad_tc], path)
        with pytest.raises(ValueError, match="validation failed"):
            validate_csv(path)
    finally:
        os.unlink(path)

# ── SQAI-30: Step row column alignment ───────────────────────────────────────

def test_sqai30_step_row_has_8_empty_leading_cols():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        path = f.name
    try:
        make_csv([VALID_HEADER, VALID_TC_ROW, VALID_STEP_ROW, VALID_LAST_STEP], path)
        rows = validate_csv(path)
        step = rows[2]
        empty = sum(1 for c in step[:8] if c.strip() == "")
        assert empty == 8
    finally:
        os.unlink(path)

def test_sqai30_step_row_wrong_col_count_raises():
    bad_step = ["", "", "", "", "", "", "",  # only 7 empty — missing one
                "Enter credentials", "user@test.com", "Login page shown"]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        path = f.name
    try:
        make_csv([VALID_HEADER, VALID_TC_ROW, bad_step], path)
        with pytest.raises(ValueError, match="validation failed"):
            validate_csv(path)
    finally:
        os.unlink(path)

# ── Multi-TC validation ───────────────────────────────────────────────────────

def test_multiple_test_cases_all_valid():
    tc2 = ["TC-002", "Test", "Verify logout", "High", "Functional",
            "sergio.juarez", "Sprint-1", "/SergioQE/Epic1",
            "Click logout", "", ""]
    tc2_last = ["", "", "", "", "", "", "", "",
                "Verify redirect", "", "Login page shown"]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        path = f.name
    try:
        make_csv([
            VALID_HEADER,
            VALID_TC_ROW, VALID_STEP_ROW, VALID_LAST_STEP,
            tc2, tc2_last
        ], path)
        rows = validate_csv(path)
        tc_rows = [r for r in rows[1:] if r[0].strip()]
        assert len(tc_rows) == 2
    finally:
        os.unlink(path)

def test_correct_test_case_and_step_counts():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        path = f.name
    try:
        make_csv([
            VALID_HEADER,
            VALID_TC_ROW,
            VALID_STEP_ROW,
            VALID_LAST_STEP,
        ], path)
        rows = validate_csv(path)
        tc_rows   = [r for r in rows[1:] if r[0].strip()]
        step_rows = [r for r in rows[1:] if not r[0].strip()]
        assert len(tc_rows)   == 1
        assert len(step_rows) == 2
    finally:
        os.unlink(path)

# ── Auth & import (mocked) ────────────────────────────────────────────────────

def test_get_xray_token_success():
    from xray_importer import get_xray_token
    with patch("xray_importer.requests.post") as mock_post:
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: "mock-bearer-token-abc123"
        )
        token = get_xray_token()
        assert token == "mock-bearer-token-abc123"

def test_get_xray_token_failure_raises():
    from xray_importer import get_xray_token
    with patch("xray_importer.requests.post") as mock_post:
        mock_post.return_value = MagicMock(
            status_code=401,
            text="Unauthorized"
        )
        with pytest.raises(RuntimeError, match="Auth failed"):
            get_xray_token()

def test_import_csv_success():
    from xray_importer import import_csv_to_xray
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("Test ID,Issue Type\nTC-001,Test\n")
        path = f.name
    try:
        with patch("xray_importer.requests.post") as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200,
                json=lambda: {"testIssues": {"success": ["TC-001"]}}
            )
            result = import_csv_to_xray(path, "mock-token")
            assert "testIssues" in result
    finally:
        os.unlink(path)

def test_import_csv_failure_raises():
    from xray_importer import import_csv_to_xray
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("Test ID\nTC-001\n")
        path = f.name
    try:
        with patch("xray_importer.requests.post") as mock_post:
            mock_post.return_value = MagicMock(
                status_code=400,
                text="Bad Request"
            )
            with pytest.raises(RuntimeError, match="Import failed"):
                import_csv_to_xray(path, "mock-token")
    finally:
        os.unlink(path)

# ── Repo validation (mocked) ──────────────────────────────────────────────────

def test_validate_repository_returns_correct_count():
    from xray_importer import validate_repository
    mock_response = {
        "total": 15,
        "issues": [
            {"fields": {"summary": f"Test case {i}"}} for i in range(15)
        ]
    }
    with patch("xray_importer.JIRA_EMAIL", "test@test.com"), \
         patch("xray_importer.JIRA_API_TOKEN", "mock-token"), \
         patch("xray_importer.requests.get") as mock_get:
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_response
        )
        result = validate_repository(expected_count=15)
        assert result["total"] == 15
        assert len(result["summaries"]) == 15

def test_validate_repository_skips_without_credentials():
    from xray_importer import validate_repository
    with patch("xray_importer.JIRA_EMAIL", ""), \
         patch("xray_importer.JIRA_API_TOKEN", ""):
        result = validate_repository()
        assert result == {}
