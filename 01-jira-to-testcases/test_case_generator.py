# Test Case Generator — SQAI-11
# Purpose: Use Claude AI to generate structured test cases
#          from a parsed JIRA story
# Input:   Parsed story dictionary from story_parser.py
# Output:  List of test case dictionaries ready for Xray CSV
# Author:  Sergio Juarez — SergioQE Portfolio

import os
import json
import anthropic
from dotenv import load_dotenv
from story_parser import parse_story

# Load API key from .env file
load_dotenv()


def generate_test_cases(parsed_story):
    """
    Sends parsed story to Claude AI and gets back
    structured test cases covering all AC items.
    Returns a list of test case dictionaries.
    """
    # Initialize Claude AI client
    client = anthropic.Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )

    # Build the prompt from parsed story
    ac_items = "\n".join([
        f"{i+1}. {ac}"
        for i, ac in enumerate(parsed_story["ACCEPTANCE CRITERIA"])
    ])

    tech_notes = "\n".join([
        f"- {note}"
        for note in parsed_story.get("TECHNICAL NOTES", [])
    ])

    prompt = f"""You are a senior QA Engineer specializing in 
banking and fintech applications.

Analyze this JIRA story and generate comprehensive test cases:

STORY TITLE: {parsed_story["TITLE"]}

USER STORY: {parsed_story["USER STORY"]}

ACCEPTANCE CRITERIA:
{ac_items}

TECHNICAL NOTES:
{tech_notes}

Generate test cases that cover:
1. Positive scenarios (happy path for each AC item)
2. Negative scenarios (invalid inputs, errors, failures)
3. Edge cases (boundary values, empty fields, special characters)
4. Security scenarios (unauthorized access, injection attempts)

Return ONLY a JSON array. No explanations. No markdown.
Each test case must have these exact fields:
- tcid: string (TC-001, TC-002, etc.)
- summary: string (concise test case title)
- description: string (what this test validates)
- action: string (numbered steps: 1. Do this\\n2. Do that)
- data_steps: string (test data needed)
- expected_results: string (what should happen)
- complexity: string (Low, Medium, or High)
- priority: string (Low, Medium, High, or Critical)
- test_type: string (Functional, Negative, Edge Case, 
  Security, or Regression)

Generate minimum 10 test cases maximum 15.
Cover ALL acceptance criteria items."""

    # Call Claude AI
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    # Parse the JSON response
    response_text = message.content[0].text

    # Clean response in case of any markdown
    clean_response = response_text.strip()
    if clean_response.startswith("```"):
        lines = clean_response.split("\n")
        clean_response = "\n".join(lines[1:-1])

    test_cases = json.loads(clean_response)
    return test_cases


def generate_and_display(story_file):
    """
    Full pipeline: parse story → generate test cases → display
    """
    print("=" * 60)
    print("SQAI-11 — AI Test Case Generator")
    print("=" * 60)

    # Step 1: Parse the story
    print("\n📖 Parsing story...")
    parsed = parse_story(story_file)
    print(f"   Title: {parsed['TITLE']}")
    print(f"   AC items found: {len(parsed['ACCEPTANCE CRITERIA'])}")

    # Step 2: Generate test cases
    print("\n🤖 Calling Claude AI to generate test cases...")
    print("   This takes 10-20 seconds...")
    test_cases = generate_test_cases(parsed)

    # Step 3: Display results
    print(f"\n✅ Generated {len(test_cases)} test cases!\n")
    print("=" * 60)

    for tc in test_cases:
        print(f"\n{tc['tcid']} — {tc['summary']}")
        print(f"   Type:       {tc['test_type']}")
        print(f"   Priority:   {tc['priority']}")
        print(f"   Complexity: {tc['complexity']}")
        print(f"   Expected:   {tc['expected_results'][:80]}...")

    print("\n" + "=" * 60)
    print(f"Total: {len(test_cases)} test cases generated")
    print("Ready for Xray CSV export (SQAI-12)")

    return test_cases


# Run directly to test the generator
if __name__ == '__main__':
    story_path = os.path.join(
        os.path.dirname(__file__),
        'sample_stories',
        'story_01.txt'
    )
    results = generate_and_display(story_path)

    # Save raw output for inspection
    output_path = os.path.join(
        os.path.dirname(__file__),
        'generated_test_cases.json'
    )
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Saved to: {output_path}")