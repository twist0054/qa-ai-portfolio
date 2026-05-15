# Xray CSV Exporter — SQAI-12
# Purpose: Map AI-generated test cases to Xray CSV format
# Input:   List of test case dictionaries from SQAI-11
# Output:  CSV file ready for JIRA Xray Test Case Importer
# Author:  Sergio Juarez — SergioQE Portfolio

import csv
import os
import json
from datetime import datetime


# Default project configuration
# These values populate the Xray fields automatically
DEFAULT_CONFIG = {
    "application":        "SergioQE Portfolio",
    "project_name":       "SergioQE",
    "project_id":         "SQAI",
    "assignee":           "sergio.juarez",
    "label_release":      "Sprint-1",
    "automated_control":  "Manual",
    "test_design_status": "Draft",
    "crew":               "QA-Team-Alpha",
    "test_repository_path": "/SergioQE/Epic1-Xray-Agent"
}

# All 18 Xray CSV column headers
XRAY_HEADERS = [
    "TCID",
    "Application",
    "Project Name",
    "Project ID",
    "Summary",
    "Description",
    "Action",
    "Data Steps",
    "Expected Results",
    "Test Case Complexity",
    "Priority",
    "Assignee",
    "Label Release",
    "Automated Control",
    "Test Repository Path",
    "Crew",
    "Test Type",
    "Test Design Status"
]


def map_to_xray_row(test_case, config=None):
    """
    Maps a single AI-generated test case to a full Xray CSV row.
    Uses DEFAULT_CONFIG for project-level fields.
    """
    if config is None:
        config = DEFAULT_CONFIG

    return [
        test_case.get("tcid", ""),
        config["application"],
        config["project_name"],
        config["project_id"],
        test_case.get("summary", ""),
        test_case.get("description", ""),
        test_case.get("action", ""),
        test_case.get("data_steps", ""),
        test_case.get("expected_results", ""),
        test_case.get("complexity", "Medium"),
        test_case.get("priority", "Medium"),
        config["assignee"],
        config["label_release"],
        config["automated_control"],
        config["test_repository_path"],
        config["crew"],
        test_case.get("test_type", "Functional"),
        config["test_design_status"]
    ]


def export_to_xray_csv(test_cases, story_title, config=None,
                        output_dir=None):
    """
    Exports a list of test cases to an Xray-ready CSV file.
    Returns the path to the generated CSV file.
    """
    if config is None:
        config = DEFAULT_CONFIG

    if output_dir is None:
        output_dir = os.path.dirname(__file__)

    # Generate timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = story_title.replace(" ", "_").replace("/", "-")
    filename = f"xray_import_{safe_title}_{timestamp}.csv"
    filepath = os.path.join(output_dir, filename)

    # Write CSV file
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Write header row
        writer.writerow(XRAY_HEADERS)

        # Write each test case as a row
        for tc in test_cases:
            row = map_to_xray_row(tc, config)
            writer.writerow(row)

    return filepath


def display_csv_preview(filepath, max_rows=5):
    """
    Displays a preview of the generated CSV in the terminal.
    Shows headers and first few rows.
    """
    print("\n📋 CSV Preview (first rows):")
    print("-" * 80)

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i == 0:
                # Header row
                print(f"{'COLUMN':<25} {'VALUE'}")
                print("-" * 80)
            elif i <= max_rows:
                # Data rows — show key fields only
                print(f"\n  Row {i} — {row[0]}: {row[4][:50]}")
                print(f"    Priority:    {row[10]}")
                print(f"    Test Type:   {row[16]}")
                print(f"    Complexity:  {row[9]}")
            else:
                remaining = sum(1 for _ in reader)
                print(f"\n  ... and {remaining + 1} more rows")
                break

    print("-" * 80)


def run_full_export(story_title, test_cases_file=None):
    """
    Full pipeline: load test cases → export to CSV → display preview
    """
    print("=" * 60)
    print("SQAI-12 — Xray CSV Exporter")
    print("=" * 60)

    # Load test cases from JSON file
    if test_cases_file is None:
        test_cases_file = os.path.join(
            os.path.dirname(__file__),
            'generated_test_cases.json'
        )

    print(f"\n📂 Loading test cases from: {test_cases_file}")

    with open(test_cases_file, 'r') as f:
        test_cases = json.load(f)

    print(f"✅ Loaded {len(test_cases)} test cases")

    # Export to CSV
    print(f"\n⚙️  Mapping {len(test_cases)} test cases to 18 Xray fields...")
    filepath = export_to_xray_csv(
        test_cases=test_cases,
        story_title=story_title,
        output_dir=os.path.dirname(__file__)
    )

    print(f"✅ CSV generated: {os.path.basename(filepath)}")
    print(f"📁 Location: {filepath}")

    # Display preview
    display_csv_preview(filepath)

    # Summary
    print(f"\n{'=' * 60}")
    print(f"✅ SQAI-12 Complete!")
    print(f"   Test cases exported: {len(test_cases)}")
    print(f"   Xray fields mapped:  {len(XRAY_HEADERS)}")
    print(f"   File ready to import into JIRA Xray")
    print(f"{'=' * 60}")
    print(f"\n🚀 Next step: Import this CSV into Xray")
    print(f"   Apps → Xray → Test Case Importer → Upload CSV")

    return filepath


# Run directly to generate CSV
if __name__ == '__main__':
    run_full_export(
        story_title="Account_Balance_Display"
    )