# Tests for JIRA Story Parser — SQAI-10
# Validates all acceptance criteria are met
# Author: Sergio Juarez — SergioQE Portfolio

import pytest
import os
from story_parser import parse_story, parse_all_stories


# Path helpers
STORIES_DIR = os.path.join(os.path.dirname(__file__), 'sample_stories')
STORY_01 = os.path.join(STORIES_DIR, 'story_01.txt')
STORY_02 = os.path.join(STORIES_DIR, 'story_02.txt')
STORY_03 = os.path.join(STORIES_DIR, 'story_03.txt')


# ─── AC 1: Agent accepts free-text JIRA story input ───────────────
class TestStoryInput:

    def test_parser_accepts_valid_file_path(self):
        """AC1: Agent accepts a .txt story file as input"""
        result = parse_story(STORY_01)
        assert result is not None

    def test_parser_returns_dictionary(self):
        """AC1: Output is a dictionary"""
        result = parse_story(STORY_01)
        assert isinstance(result, dict)


# ─── AC 2: Identifies and separates all 5 sections ────────────────
class TestSectionExtraction:

    def test_all_5_keys_present(self):
        """AC2: All 5 section keys exist in output"""
        result = parse_story(STORY_01)
        expected_keys = [
            'TITLE', 'USER STORY', 'ACCEPTANCE CRITERIA',
            'TECHNICAL NOTES', 'DEFINITION OF DONE'
        ]
        for key in expected_keys:
            assert key in result, f"Missing key: {key}"

    def test_title_extracted_correctly(self):
        """AC2: Title is extracted as a clean string"""
        result = parse_story(STORY_01)
        assert result['TITLE'] == 'Account Balance Display'

    def test_user_story_extracted_correctly(self):
        """AC2: User story is extracted as a clean string"""
        result = parse_story(STORY_01)
        assert 'bank customer' in result['USER STORY']
        assert isinstance(result['USER STORY'], str)

    def test_acceptance_criteria_is_list(self):
        """AC2: Acceptance criteria returned as a list"""
        result = parse_story(STORY_01)
        assert isinstance(result['ACCEPTANCE CRITERIA'], list)

    def test_acceptance_criteria_count(self):
        """AC2: All AC items extracted — story_01 has 5"""
        result = parse_story(STORY_01)
        assert len(result['ACCEPTANCE CRITERIA']) == 5

    def test_technical_notes_is_list(self):
        """AC2: Technical notes returned as a list"""
        result = parse_story(STORY_01)
        assert isinstance(result['TECHNICAL NOTES'], list)

    def test_definition_of_done_is_list(self):
        """AC2: Definition of done returned as a list"""
        result = parse_story(STORY_01)
        assert isinstance(result['DEFINITION OF DONE'], list)


# ─── AC 3: Output is a structured dictionary ──────────────────────
class TestStructuredOutput:

    def test_ac_items_are_strings(self):
        """AC3: Each AC item is a clean string without dashes"""
        result = parse_story(STORY_01)
        for item in result['ACCEPTANCE CRITERIA']:
            assert isinstance(item, str)
            assert not item.startswith('-'), \
                f"AC item still has dash: {item}"

    def test_title_has_no_colon(self):
        """AC3: Title does not contain the header colon"""
        result = parse_story(STORY_01)
        assert ':' not in result['TITLE'] or \
               result['TITLE'].index(':') > 5


# ─── AC 4: Handles missing sections gracefully ────────────────────
class TestMissingSections:

    def test_missing_section_returns_empty_list(self, tmp_path):
        """AC4: Missing list sections return empty list not error"""
        # Create a minimal story with only TITLE and USER STORY
        minimal_story = tmp_path / "minimal.txt"
        minimal_story.write_text(
            "TITLE: Minimal Story\n\n"
            "USER STORY:\n"
            "As a user I want something so that I benefit.\n"
        )
        result = parse_story(str(minimal_story))
        assert result['ACCEPTANCE CRITERIA'] == []
        assert result['TECHNICAL NOTES'] == []
        assert result['DEFINITION OF DONE'] == []

    def test_missing_title_returns_empty_string(self, tmp_path):
        """AC4: Missing title returns empty string not error"""
        no_title_story = tmp_path / "no_title.txt"
        no_title_story.write_text(
            "ACCEPTANCE CRITERIA:\n"
            "- Item one\n"
            "- Item two\n"
        )
        result = parse_story(str(no_title_story))
        assert result['TITLE'] == ''
        assert len(result['ACCEPTANCE CRITERIA']) == 2


# ─── AC 5: Tested with 3 different story formats ──────────────────
class TestMultipleStories:

    def test_story_02_parsed_correctly(self):
        """AC5: Parser handles story_02 correctly"""
        result = parse_story(STORY_02)
        assert result['TITLE'] == 'User Login Authentication'
        assert len(result['ACCEPTANCE CRITERIA']) == 5

    def test_story_03_parsed_correctly(self):
        """AC5: Parser handles story_03 correctly"""
        result = parse_story(STORY_03)
        assert result['TITLE'] == 'Fund Transfer Between Accounts'
        assert len(result['ACCEPTANCE CRITERIA']) == 6

    def test_parse_all_stories_returns_3_stories(self):
        """AC5: parse_all_stories processes all files in folder"""
        stories = parse_all_stories(STORIES_DIR)
        assert len(stories) == 3

    def test_all_stories_have_titles(self):
        """AC5: All 3 stories have non-empty titles"""
        stories = parse_all_stories(STORIES_DIR)
        for story in stories:
            assert story['TITLE'] != '', \
                f"Empty title in {story.get('filename')}"