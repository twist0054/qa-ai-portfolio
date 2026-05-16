# Test Case Generator — SQAI-11
# Purpose: Use Claude AI to generate structured test cases
# Input:   Parsed story dictionary from story_parser.py
# Output:  List of test case dictionaries ready for CSV export
# Author:  Sergio Juarez — SergioQE Portfolio

import os
import json
import re
import anthropic
from dotenv import load_dotenv
from story_parser import parse_story

load_dotenv()


def generate_test_cases(parsed_story):
    """
    Sends parsed story to Claude AI and gets back
    structured test cases. Uses simple flat JSON format
    for reliability then processes steps in Python.
    """
    client = anthropic.Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )

    ac_items = "\n".join([
        f"{i+1}. {ac}"
        for i, ac in enumerate(
            parsed_story["ACCEPTANCE CRITERIA"])
    ])

    tech_notes = "\n".join([
        f"- {note}"
        for note in parsed_story.get(
            "TECHNICAL NOTES", [])
    ])

    prompt = f"""You are a senior QA Engineer specializing 
in banking and fintech applications.

Analyze this JIRA story and generate comprehensive 
test cases:

STORY TITLE: {parsed_story["TITLE"]}
USER STORY: {parsed_story["USER STORY"]}

ACCEPTANCE CRITERIA:
{ac_items}

TECHNICAL NOTES:
{tech_notes}

Return ONLY a JSON array. No explanations. No markdown.
Each test case must have these exact fields:
- tcid: string (TC-001, TC-002, etc.)
- summary: string (concise test case title)
- description: string (what this test validates)
- action: string (steps separated by | like this:
  "Navigate to login page|Enter valid credentials|Click Sign In|Verify dashboard loads")
- test_data: string (all test data needed)
- expected_results: string (overall expected result)
- complexity: string (Low, Medium, or High)
- priority: string (Low, Medium, High, or Critical)
- test_type: string (Functional, Negative, Edge Case,
  Security, or Regression)

IMPORTANT: Use | to separate steps in the action field.
Do NOT use newlines inside field values.
Generate minimum 10 maximum 15 test cases.
Cover ALL acceptance criteria items.
Include positive, negative, edge case and security tests."""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    response_text = message.content[0].text

    # Extract JSON array from response
    clean = response_text.strip()

    # Remove markdown if present
    if "```json" in clean:
        clean = clean.split("```json")[1].split(
            "```")[0].strip()
    elif "```" in clean:
        clean = clean.split("```")[1].split(
            "```")[0].strip()

    # Find array boundaries
    start = clean.find("[")
    end = clean.rfind("]") + 1
    if start != -1 and end > 0:
        clean = clean[start:end]

    # Remove control characters
    clean = re.sub(
        r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]',
        ' ', clean)

    test_cases = json.loads(clean)

    # Convert pipe-separated action into steps list
    for tc in test_cases:
        action_text = tc.get("action", "")
        if "|" in action_text:
            step_list = [s.strip() for s in
                         action_text.split("|")
                         if s.strip()]
        elif "\n" in action_text:
            step_list = [s.strip().lstrip(
                "0123456789.- ")
                for s in action_text.split("\n")
                if s.strip()]
        else:
            step_list = [action_text]

        # Build structured steps
        steps = []
        for i, step_text in enumerate(step_list):
            steps.append({
                "step_number": i + 1,
                "action": step_text,
                "test_data": tc.get(
                    "test_data", "") if i == 0 else "",
                "expected": tc.get(
                    "expected_results", "")
                if i == len(step_list) - 1 else ""
            })

        tc["steps"] = steps

    return test_cases


def generate_and_display(story_file):
    """Full pipeline: parse → generate → display"""
    print("=" * 60)
    print("SQAI-11 — AI Test Case Generator")
    print("=" * 60)

    print("\n📖 Parsing story...")
    parsed = parse_story(story_file)
    print(f"   Title: {parsed['TITLE']}")
    print(f"   AC items found: "
          f"{len(parsed['ACCEPTANCE CRITERIA'])}")

    print("\n🤖 Calling Claude AI to generate test cases...")
    print("   This takes 10-20 seconds...")
    test_cases = generate_test_cases(parsed)

    print(f"\n✅ Generated {len(test_cases)} test cases!\n")
    print("=" * 60)

    for tc in test_cases:
        steps = tc.get("steps", [])
        print(f"\n{tc['tcid']} — {tc['summary']}")
        print(f"   Type:       {tc['test_type']}")
        print(f"   Priority:   {tc['priority']}")
        print(f"   Steps:      {len(steps)}")
        if steps:
            print(f"   Step 1:     "
                  f"{steps[0]['action'][:55]}")

    print("\n" + "=" * 60)
    print(f"Total: {len(test_cases)} test cases")
    total_steps = sum(
        len(tc.get("steps", [])) for tc in test_cases)
    print(f"Total steps: {total_steps}")
    print("Ready for Xray CSV export (SQAI-12)")

    return test_cases


if __name__ == '__main__':
    story_path = os.path.join(
        os.path.dirname(__file__),
        'sample_stories',
        'story_01.txt'
    )
    results = generate_and_display(story_path)

    output_path = os.path.join(
        os.path.dirname(__file__),
        'generated_test_cases.json'
    )
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Saved to: {output_path}")