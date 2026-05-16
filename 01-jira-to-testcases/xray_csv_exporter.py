# Xray CSV Exporter — SQAI-12 (Bug Fix SQAI-30)
# Purpose: Map AI-generated test cases to Xray Manual Test CSV format
# Fix:     Each test step exported as individual CSV row
# Author:  Sergio Juarez — SergioQE Portfolio

import csv
import os
import json
from datetime import datetime


DEFAULT_CONFIG = {
    "application":          "SergioQE Portfolio",
    "project_name":         "SergioQE",
    "project_id":           "SQAI",
    "assignee":             "sergio.juarez",
    "label_release":        "Sprint-1",
    "automated_control":    "Manual",
    "test_design_status":   "Draft",
    "crew":                 "QA-Team-Alpha",
    "test_repository_path": "/SergioQE/Epic1-Xray-Agent"
}

XRAY_HEADERS = [
    "Test ID",
    "Issue Type",
    "Test Summary",
    "Test Priority",
    "Test Type",
    "Assignee",
    "Labels",
    "Test Repo Path",
    "Action",
    "Data",
    "Expected Result"
]


def get_steps(test_case):
    """
    Extracts steps from a test case.
    Handles both new format (steps array) and
    old format (action string).
    """
    # New format — steps is an array of objects
    if "steps" in test_case and isinstance(
            test_case["steps"], list):
        return test_case["steps"]

    # Old format fallback — action is a string
    action_text = test_case.get("action", "")
    data_text = test_case.get("data_steps", "")
    expected_text = test_case.get("expected_results", "")

    # Try to split numbered steps from string
    steps = []
    if "1." in action_text:
        lines = action_text.split("\n")
        for i, line in enumerate(lines):
            if line.strip():
                clean = line.strip().lstrip(
                    "0123456789.- ")
                steps.append({
                    "step_number": i + 1,
                    "action": clean,
                    "test_data": data_text if i == 0 else "",
                    "expected": expected_text if i == len(
                        lines) - 1 else ""
                })
    else:
        steps = [{
            "step_number": 1,
            "action": action_text,
            "test_data": data_text,
            "expected": expected_text
        }]

    return steps


def export_to_xray_csv(test_cases, story_title,
                        config=None, output_dir=None):
    """
    Exports test cases to Xray Manual Test CSV format.
    Each step becomes a separate row in the CSV.
    """
    if config is None:
        config = DEFAULT_CONFIG

    if output_dir is None:
        output_dir = os.path.dirname(__file__)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = story_title.replace(" ", "_").replace(
        "/", "-")
    filename = f"xray_import_{safe_title}_{timestamp}.csv"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w', newline='',
               encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(XRAY_HEADERS)

        for tc in test_cases:
            steps = get_steps(tc)

            if not steps:
                steps = [{"step_number": 1,
                           "action": "Execute test",
                           "test_data": "",
                           "expected": "Test passes"}]

            # First step row — includes test case metadata
            writer.writerow([
                tc.get("tcid", ""),
                "Test",
                tc.get("summary", ""),
                tc.get("priority", "Medium"),
                tc.get("test_type", "Functional"),
                config["assignee"],
                config["label_release"],
                config["test_repository_path"],
                steps[0].get("action", ""),
                steps[0].get("test_data", ""),
                steps[0].get("expected", "")
            ])

            # Remaining step rows — metadata columns empty
            for step in steps[1:]:
                writer.writerow([
                    "",  # Test ID
                    "",  # Issue Type
                    "",  # Test Summary
                    "",  # Test Priority
                    "",  # Test Type
                    "",  # Assignee
                    "",  # Labels
                    "",  # Test Repo Path
                    step.get("action", ""),
                    step.get("test_data", ""),
                    step.get("expected", "")
                ])

    return filepath


def display_preview(filepath, max_tests=3):
    """Shows preview of generated CSV with steps"""
    print("\n📋 CSV Preview — Manual Test Format:")
    print("-" * 70)

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        current_test = 0
        step_count = 0

        for i, row in enumerate(reader):
            if i == 0:
                continue

            if row[0] == "Test":
                current_test += 1
                step_count = 1
                if current_test > max_tests:
                    print("\n  ... more test cases in file")
                    break
                print(f"\n  📝 TC {current_test}: "
                      f"{row[1][:50]}")
                print(f"     Priority: {row[2]} | "
                      f"Type: {row[3]}")
                print(f"     Steps:")
                print(f"       {step_count}. "
                      f"{row[7][:55]}")
            elif row[7] and current_test <= max_tests:
                step_count += 1
                print(f"       {step_count}. "
                      f"{row[7][:55]}")

    print("-" * 70)


def run_full_export(story_title,
                    test_cases_file=None):
    """Full pipeline: load → export → preview"""
    print("=" * 60)
    print("SQAI-12 — Xray CSV Exporter")
    print("Bug Fix SQAI-30 — Manual Test Step Format")
    print("=" * 60)

    if test_cases_file is None:
        test_cases_file = os.path.join(
            os.path.dirname(__file__),
            'generated_test_cases.json'
        )

    with open(test_cases_file, 'r') as f:
        test_cases = json.load(f)

    print(f"\n✅ Loaded {len(test_cases)} test cases")

    filepath = export_to_xray_csv(
        test_cases=test_cases,
        story_title=story_title
    )

    print(f"✅ CSV: {os.path.basename(filepath)}")
    display_preview(filepath)

    print(f"\n{'=' * 60}")
    print(f"✅ Bug SQAI-30 Fixed!")
    print(f"   Steps now exported as individual rows")
    print(f"   Ready for Xray Manual Test import")
    print(f"{'=' * 60}")

    return filepath


if __name__ == '__main__':
    run_full_export("Account_Balance_Display")