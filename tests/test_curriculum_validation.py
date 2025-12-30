"""
Tests for curriculum validation.

These tests ensure that:
1. Valid curricula are accepted
2. Invalid curricula produce clear error messages
3. Edge cases are handled gracefully
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from curriculum import load_curriculum, CurriculumError, get_items_by_type


@pytest.fixture
def valid_curriculum():
    """A minimal valid curriculum."""
    return {
        "meta": {"dialect": "General American", "version": "v1"},
        "alphabet": {
            "letters": [
                {"id": "letter_a", "upper": "A", "lower": "a", "order": 1}
            ],
            "confusables": [],
        },
        "items": [
            {
                "id": "sound_ae",
                "type": "sound",
                "ipa": "/æ/",
                "examples": [{"word": "apple"}],
            }
        ],
    }


@pytest.fixture
def temp_curriculum_file(valid_curriculum):
    """Create a temporary curriculum file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(valid_curriculum, f)
        return Path(f.name)


class TestValidCurriculum:
    """Test that valid curricula are accepted."""

    def test_load_valid_curriculum(self, temp_curriculum_file):
        """A valid curriculum should load without errors."""
        curriculum = load_curriculum(temp_curriculum_file)
        assert curriculum is not None
        assert "meta" in curriculum
        assert "alphabet" in curriculum
        assert "items" in curriculum

    def test_items_are_normalized(self, temp_curriculum_file):
        """Items should be normalized with default values."""
        curriculum = load_curriculum(temp_curriculum_file)
        item = curriculum["items"][0]
        assert "graphemes" in item  # Should be added if missing
        assert "notes" in item  # Should be added if missing

    def test_get_items_by_type(self, temp_curriculum_file):
        """get_items_by_type should filter correctly."""
        curriculum = load_curriculum(temp_curriculum_file)
        sounds = get_items_by_type(curriculum, "sound")
        assert len(sounds) == 1
        assert sounds[0]["id"] == "sound_ae"

        patterns = get_items_by_type(curriculum, "pattern")
        assert len(patterns) == 0


class TestMissingFields:
    """Test that missing required fields produce clear errors."""

    def test_missing_meta(self):
        """Missing meta section should raise error."""
        data = {"alphabet": {"letters": []}, "items": []}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            path = Path(f.name)

        with pytest.raises(CurriculumError) as exc_info:
            load_curriculum(path)
        assert "meta" in str(exc_info.value)

    def test_missing_alphabet(self):
        """Missing alphabet section should raise error."""
        data = {"meta": {"dialect": "GA", "version": "v1"}, "items": []}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            path = Path(f.name)

        with pytest.raises(CurriculumError) as exc_info:
            load_curriculum(path)
        assert "alphabet" in str(exc_info.value)

    def test_missing_items(self):
        """Missing items section should raise error."""
        data = {
            "meta": {"dialect": "GA", "version": "v1"},
            "alphabet": {"letters": []},
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            path = Path(f.name)

        with pytest.raises(CurriculumError) as exc_info:
            load_curriculum(path)
        assert "items" in str(exc_info.value)

    def test_item_missing_id(self):
        """Item without id should raise error."""
        data = {
            "meta": {"dialect": "GA", "version": "v1"},
            "alphabet": {"letters": [], "confusables": []},
            "items": [{"type": "sound", "examples": [{"word": "test"}]}],
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            path = Path(f.name)

        with pytest.raises(CurriculumError) as exc_info:
            load_curriculum(path)
        assert "id" in str(exc_info.value)

    def test_item_missing_type(self):
        """Item without type should raise error."""
        data = {
            "meta": {"dialect": "GA", "version": "v1"},
            "alphabet": {"letters": [], "confusables": []},
            "items": [{"id": "test", "examples": [{"word": "test"}]}],
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            path = Path(f.name)

        with pytest.raises(CurriculumError) as exc_info:
            load_curriculum(path)
        assert "type" in str(exc_info.value)

    def test_sound_item_missing_examples(self):
        """Sound item without examples should raise error."""
        data = {
            "meta": {"dialect": "GA", "version": "v1"},
            "alphabet": {"letters": [], "confusables": []},
            "items": [{"id": "test", "type": "sound"}],
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            path = Path(f.name)

        with pytest.raises(CurriculumError) as exc_info:
            load_curriculum(path)
        assert "examples" in str(exc_info.value)


class TestInvalidValues:
    """Test that invalid values produce clear errors."""

    def test_invalid_item_type(self):
        """Invalid item type should raise error."""
        data = {
            "meta": {"dialect": "GA", "version": "v1"},
            "alphabet": {"letters": [], "confusables": []},
            "items": [
                {"id": "test", "type": "invalid_type", "examples": [{"word": "test"}]}
            ],
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            path = Path(f.name)

        with pytest.raises(CurriculumError) as exc_info:
            load_curriculum(path)
        assert "invalid_type" in str(exc_info.value)

    def test_duplicate_ids(self):
        """Duplicate item IDs should raise error."""
        data = {
            "meta": {"dialect": "GA", "version": "v1"},
            "alphabet": {"letters": [], "confusables": []},
            "items": [
                {"id": "same_id", "type": "sound", "examples": [{"word": "one"}]},
                {"id": "same_id", "type": "sound", "examples": [{"word": "two"}]},
            ],
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            path = Path(f.name)

        with pytest.raises(CurriculumError) as exc_info:
            load_curriculum(path)
        assert "duplicate" in str(exc_info.value).lower()

    def test_empty_examples_list(self):
        """Empty examples list should raise error."""
        data = {
            "meta": {"dialect": "GA", "version": "v1"},
            "alphabet": {"letters": [], "confusables": []},
            "items": [{"id": "test", "type": "sound", "examples": []}],
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            path = Path(f.name)

        with pytest.raises(CurriculumError) as exc_info:
            load_curriculum(path)
        assert "empty" in str(exc_info.value).lower()


class TestFileHandling:
    """Test file handling edge cases."""

    def test_file_not_found(self):
        """Missing file should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_curriculum(Path("/nonexistent/curriculum.json"))

    def test_invalid_json(self):
        """Invalid JSON should raise CurriculumError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{ invalid json }")
            path = Path(f.name)

        with pytest.raises(CurriculumError) as exc_info:
            load_curriculum(path)
        assert "JSON" in str(exc_info.value)
