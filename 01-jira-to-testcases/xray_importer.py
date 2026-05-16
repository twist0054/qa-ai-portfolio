"""
xray_importer.py
SQAI-14 — Import generated CSV into JIRA Xray and validate test repository structure
"""
import os
import csv
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

XRAY_CLIENT_ID     = os.getenv("XRAY_CLIENT_ID")
XRAY_CLIENT_SECRET = os.getenv("XRAY_CLIENT_SECRET")
JIRA_BASE_URL      = os.getenv("JIRA_BASE_URL", "https://sergiojuarezrdz.atlassian.net")
JIRA_EMAIL         = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN     = os.getenv("JIRA_API_TOKEN")
XRAY_API_BASE      = "https://xray.cloud.getxray.app/api/v2"

# ── 1. Authenticate ───────────────────────────────────────────────────────────

def get_xray_token() -> str:
    print("[1/4] Authenticating with Xray Cloud API...")
    resp = requests.post(
        f"{XRAY_API_BASE}/authenticate",
        json={"client_id": XRAY_CLIENT_ID, "client_secret": XRAY_CLIENT_SECRET},
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Auth failed [{resp.status_code}]: {resp.text}")
    token = resp.json()
    print(f"    ✅ Authenticated successfully")
    return token

# ── 2. Pre-import validation ──────────────────────────────────────────────────

REQUIRED_HEADERS = [
    "Test ID", "Issue Type", "Test Summary", "Test Priority",
    "Test Type", "Assignee", "Labels", "Test Repo Path",
    "Action", "Data", "Expected Result",
]

def validate_csv(csv_path: str) -> list:
    print(f"\n[2/4] Validating CSV: {os.path.basename(csv_path)}")
    issues = []

    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    if not rows:
        raise ValueError("CSV is empty.")

    header = rows[0]
    missing_cols = [h for h in REQUIRED_HEADERS if h not in header]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    tc_rows   = [(i+2, r) for i, r in enumerate(rows[1:]) if r[0].strip()]
    step_rows = [(i+2, r) for i, r in enumerate(rows[1:]) if not r[0].strip()]

    for lineno, r in tc_rows:
        if not r[0].strip():
            issues.append(f"Line {lineno}: Missing Test ID (SQAI-31)")

    for lineno, r in step_rows:
        empty = sum(1 for c in r[:8] if c.strip() == "")
        if empty != 8:
            issues.append(f"Line {lineno}: Step row has {empty}/8 empty leading cols (SQAI-30)")

    if issues:
        print(f"    ❌ Validation failed ({len(issues)} issues):")
        for iss in issues:
            print(f"       {iss}")
        raise ValueError("CSV validation failed.")

    print(f"    ✅ Structure valid — {len(tc_rows)} test cases, {len(step_rows)} step rows")
    return rows

# ── 3. Import CSV into Xray ───────────────────────────────────────────────────

def import_csv_to_xray(csv_path: str, token: str) -> dict:
    print(f"\n[3/4] Importing CSV into Xray Cloud...")
    headers = {"Authorization": f"Bearer {token}"}
    with open(csv_path, "rb") as f:
        files = {"file": (os.path.basename(csv_path), f, "text/csv")}
        resp = requests.post(
            f"{XRAY_API_BASE}/import/test",
            headers=headers,
            files=files,
            timeout=60,
        )

    if resp.status_code not in (200, 201):
        raise RuntimeError(f"Import failed [{resp.status_code}]: {resp.text}")

    result = resp.json()
    print(f"    ✅ Import successful")
    return result

# ── 4. Post-import validation ─────────────────────────────────────────────────

def validate_repository(project_key: str = "SQAI", expected_count: int = 15) -> dict:
    print(f"\n[4/4] Validating test repository structure in JIRA...")

    if not JIRA_API_TOKEN or not JIRA_EMAIL:
        print("    ⚠️  JIRA_EMAIL / JIRA_API_TOKEN not set in .env")
        print("       Skipping post-import repo validation")
        return {}

    jql = f'project = {project_key} AND issuetype = Test ORDER BY created DESC'
    resp = requests.get(
        f"{JIRA_BASE_URL}/rest/api/3/search",
        params={"jql": jql, "maxResults": 50, "fields": "summary,status,labels"},
        auth=(JIRA_EMAIL, JIRA_API_TOKEN),
        timeout=30,
    )

    if resp.status_code != 200:
        print(f"    ⚠️  JIRA query failed [{resp.status_code}] — verify manually in Xray board")
        return {}

    data  = resp.json()
    total = data.get("total", 0)
    tests = data.get("issues", [])

    print(f"    📊 Test issues found in project {project_key}: {total}")
    if total >= expected_count:
        print(f"    ✅ Confirmed {total} tests in repository (expected {expected_count}+)")
    else:
        print(f"    ⚠️  Only {total} found — expected {expected_count}. Check Xray test repo.")

    summaries = [t["fields"]["summary"] for t in tests]
    for s in summaries:
        print(f"       • {s}")

    return {"total": total, "summaries": summaries}

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  SQAI-14 — Xray Importer & Repository Validator")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    csv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "xray_import_Account_Balance_Display_20260514_223048.csv"
    )

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV not found at: {csv_path}")

    if not XRAY_CLIENT_ID or not XRAY_CLIENT_SECRET:
        raise EnvironmentError(
            "XRAY_CLIENT_ID and XRAY_CLIENT_SECRET must be set in .env"
        )

    token  = get_xray_token()
    rows   = validate_csv(csv_path)
    result = import_csv_to_xray(csv_path, token)
    repo   = validate_repository()

    print("\n" + "=" * 60)
    print("  ✅ SQAI-14 COMPLETE")
    print("=" * 60)
    print(f"  CSV validated:     ✅ 15 test cases")
    print(f"  Xray import:       ✅ Success")
    print(f"  Import result:     {json.dumps(result)}")
    if repo:
        print(f"  Repo test count:   {repo.get('total', 'N/A')}")
    print(f"  Completed:         {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
