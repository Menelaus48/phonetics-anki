"""
Tests for deterministic ID and GUID generation.

These tests ensure that:
1. GUIDs are stable across multiple runs
2. The same input always produces the same output
3. Re-importing won't create duplicate notes
"""

import sys
from pathlib import Path

# Add scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from ids import (
    note_guid,
    deck_id_for_subdeck,
    MODEL_ID_SOUND,
    MODEL_ID_PATTERN,
    MODEL_ID_LETTER_CASE,
    MODEL_ID_VISUAL_CONFUSABLE,
    MODEL_ID_ALPHABET_ORDER,
    MODEL_ID_MINIMAL_PAIR,
    DECK_NAME_SOUNDS,
    DECK_NAME_SPELLINGS,
)


class TestNoteGuidStability:
    """Test that note GUIDs are deterministic."""

    def test_same_input_produces_same_guid(self):
        """Same item_id and namespace should always produce the same GUID."""
        guid1 = note_guid("sound", "sound_ae")
        guid2 = note_guid("sound", "sound_ae")
        assert guid1 == guid2

    def test_different_namespaces_produce_different_guids(self):
        """Same item_id with different namespaces should produce different GUIDs."""
        guid_sound = note_guid("sound", "test_item")
        guid_pattern = note_guid("pattern", "test_item")
        assert guid_sound != guid_pattern

    def test_different_ids_produce_different_guids(self):
        """Different item_ids should produce different GUIDs."""
        guid1 = note_guid("sound", "sound_ae")
        guid2 = note_guid("sound", "sound_b")
        assert guid1 != guid2

    def test_guid_is_string(self):
        """GUIDs should be strings."""
        guid = note_guid("sound", "test")
        assert isinstance(guid, str)

    def test_guid_is_not_empty(self):
        """GUIDs should not be empty."""
        guid = note_guid("sound", "test")
        assert len(guid) > 0

    def test_known_guid_values(self):
        """Test specific GUIDs match expected values (regression test)."""
        # These values were recorded from a known-good run
        # If these change, existing Anki schedules will be lost
        assert note_guid("sound", "sound_ae") == "CGeQgyusBST"
        assert note_guid("pattern", "pattern_th_voiceless") == "EmnACxldShN"


class TestDeckIdStability:
    """Test that deck IDs are deterministic."""

    def test_same_subdeck_produces_same_id(self):
        """Same subdeck name should always produce the same ID."""
        id1 = deck_id_for_subdeck(DECK_NAME_SOUNDS)
        id2 = deck_id_for_subdeck(DECK_NAME_SOUNDS)
        assert id1 == id2

    def test_different_subdecks_produce_different_ids(self):
        """Different subdeck names should produce different IDs."""
        id_sounds = deck_id_for_subdeck(DECK_NAME_SOUNDS)
        id_spellings = deck_id_for_subdeck(DECK_NAME_SPELLINGS)
        assert id_sounds != id_spellings

    def test_deck_id_is_positive(self):
        """Deck IDs should be positive integers."""
        deck_id = deck_id_for_subdeck(DECK_NAME_SOUNDS)
        assert isinstance(deck_id, int)
        assert deck_id > 0


class TestModelIdUniqueness:
    """Test that model IDs are unique."""

    def test_all_model_ids_unique(self):
        """All model IDs should be unique."""
        model_ids = [
            MODEL_ID_SOUND,
            MODEL_ID_PATTERN,
            MODEL_ID_LETTER_CASE,
            MODEL_ID_VISUAL_CONFUSABLE,
            MODEL_ID_ALPHABET_ORDER,
            MODEL_ID_MINIMAL_PAIR,
        ]
        assert len(model_ids) == len(set(model_ids))

    def test_model_ids_are_positive(self):
        """Model IDs should be positive integers."""
        model_ids = [
            MODEL_ID_SOUND,
            MODEL_ID_PATTERN,
            MODEL_ID_LETTER_CASE,
            MODEL_ID_VISUAL_CONFUSABLE,
            MODEL_ID_ALPHABET_ORDER,
            MODEL_ID_MINIMAL_PAIR,
        ]
        for model_id in model_ids:
            assert isinstance(model_id, int)
            assert model_id > 0
