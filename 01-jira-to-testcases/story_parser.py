# JIRA Story Parser — SQAI-10
# Purpose: Read a JIRA story text file and extract structured data
# Input: Path to a .txt story file
# Output: Dictionary with keys: TITLE, USER STORY,
#         ACCEPTANCE CRITERIA, TECHNICAL NOTES, DEFINITION OF DONE
# Author: Sergio Juarez — SergioQE Portfolio
#
# Handles story formats with or without colons after headers
# Acceptance Criteria, Technical Notes and DoD returned as lists
# Title and User Story returned as clean strings

import json
import os


def parse_story(story_file):
    """
    Reads a JIRA story .txt file and extracts structured data.
    Returns a dictionary with all story sections parsed cleanly.
    """
    with open(story_file, 'r') as file:
        content = file.read()

    # Define the sections we want to extract
    section_keys = [
        'TITLE',
        'USER STORY',
        'ACCEPTANCE CRITERIA',
        'TECHNICAL NOTES',
        'DEFINITION OF DONE'
    ]

    # Initialize empty sections
    sections = {key: [] for key in section_keys}
    current_section = None

    for line in content.splitlines():
        stripped = line.strip()
        if not stripped:
            continue  # skip blank lines

        # Check if this line is a section header
        # Handles both "TITLE" and "TITLE:" formats
        matched_header = None
        for key in section_keys:
            if stripped.upper() == key or stripped.upper() == key + ':':
                matched_header = key
                break
            # Handle "TITLE: Some value" on same line
            if stripped.upper().startswith(key + ':'):
                matched_header = key
                inline = stripped[len(key) + 1:].strip()
                if inline:
                    sections[key].append(inline)
                break

        if matched_header:
            current_section = matched_header
            continue

        # Add line to current section
        if current_section:
            clean = stripped.lstrip('- ').strip()
            if clean:
                sections[current_section].append(clean)

    # Convert TITLE and USER STORY from list to single string
    string_sections = ['TITLE', 'USER STORY']
    for key in string_sections:
        sections[key] = ' '.join(sections[key]).strip()

    return sections


def parse_story_to_json(story_file):
    """
    Parses a story file and returns formatted JSON string.
    Useful for debugging and feeding into test case generator.
    """
    result = parse_story(story_file)
    return json.dumps(result, indent=2)


def parse_all_stories(stories_folder):
    """
    Reads all .txt files in a folder and parses each one.
    Returns a list of parsed story dictionaries.
    """
    stories = []
    for filename in sorted(os.listdir(stories_folder)):
        if filename.endswith('.txt'):
            file_path = os.path.join(stories_folder, filename)
            story = parse_story(file_path)
            story['filename'] = filename
            stories.append(story)
    return stories


# Quick test — run this file directly to see parser in action
if __name__ == '__main__':
    sample_path = os.path.join(
        os.path.dirname(__file__),
        'sample_stories',
        'story_01.txt'
    )
    print("=" * 60)
    print("JIRA Story Parser — SQAI-10")
    print("=" * 60)
    result = parse_story_to_json(sample_path)
    print(result)
    print()
    print("=" * 60)
    print("Testing all 3 stories...")
    print("=" * 60)
    all_stories = parse_all_stories(
        os.path.join(os.path.dirname(__file__), 'sample_stories')
    )
    for story in all_stories:
        print(f"\nFile: {story['filename']}")
        print(f"Title: {story['TITLE']}")
        print(f"AC items: {len(story['ACCEPTANCE CRITERIA'])}")