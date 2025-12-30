"""
Curriculum loader and validator for the Phonics Anki deck generator.

Loads curriculum.json and validates its structure, providing clear error messages
for missing or malformed fields.
"""

import json
from pathlib import Path
from typing import Any


class CurriculumError(Exception):
    """Raised when curriculum validation fails."""

    pass


def _validate_meta(meta: Any, path: str = "meta") -> None:
    """Validate the meta section of the curriculum."""
    if not isinstance(meta, dict):
        raise CurriculumError(f"{path}: expected object, got {type(meta).__name__}")

    required_fields = ["dialect", "version"]
    for field in required_fields:
        if field not in meta:
            raise CurriculumError(f"{path}: missing required field '{field}'")


def _validate_letter(letter: Any, index: int, path: str) -> None:
    """Validate a single letter entry in the alphabet section."""
    if not isinstance(letter, dict):
        raise CurriculumError(f"{path}[{index}]: expected object, got {type(letter).__name__}")

    required_fields = ["id", "upper", "lower", "order"]
    for field in required_fields:
        if field not in letter:
            raise CurriculumError(f"{path}[{index}]: missing required field '{field}'")

    if not isinstance(letter["id"], str) or not letter["id"]:
        raise CurriculumError(f"{path}[{index}].id: must be a non-empty string")

    if not isinstance(letter["order"], int):
        raise CurriculumError(f"{path}[{index}].order: must be an integer")


def _validate_confusable(confusable: Any, index: int, path: str) -> None:
    """Validate a single confusable entry in the alphabet section."""
    if not isinstance(confusable, dict):
        raise CurriculumError(f"{path}[{index}]: expected object, got {type(confusable).__name__}")

    required_fields = ["id", "left", "right"]
    for field in required_fields:
        if field not in confusable:
            raise CurriculumError(f"{path}[{index}]: missing required field '{field}'")

    if not isinstance(confusable["id"], str) or not confusable["id"]:
        raise CurriculumError(f"{path}[{index}].id: must be a non-empty string")


def _validate_alphabet(alphabet: Any, path: str = "alphabet") -> None:
    """Validate the alphabet section of the curriculum."""
    if not isinstance(alphabet, dict):
        raise CurriculumError(f"{path}: expected object, got {type(alphabet).__name__}")

    # letters is required (even if empty)
    if "letters" not in alphabet:
        raise CurriculumError(f"{path}: missing required field 'letters'")

    if not isinstance(alphabet["letters"], list):
        raise CurriculumError(f"{path}.letters: expected array, got {type(alphabet['letters']).__name__}")

    for i, letter in enumerate(alphabet["letters"]):
        _validate_letter(letter, i, f"{path}.letters")

    # confusables is optional
    if "confusables" in alphabet:
        if not isinstance(alphabet["confusables"], list):
            raise CurriculumError(
                f"{path}.confusables: expected array, got {type(alphabet['confusables']).__name__}"
            )
        for i, confusable in enumerate(alphabet["confusables"]):
            _validate_confusable(confusable, i, f"{path}.confusables")


def _validate_example(example: Any, index: int, path: str) -> None:
    """Validate a single example in an item's examples list."""
    if not isinstance(example, dict):
        raise CurriculumError(f"{path}[{index}]: expected object, got {type(example).__name__}")

    if "word" not in example:
        raise CurriculumError(f"{path}[{index}]: missing required field 'word'")

    if not isinstance(example["word"], str) or not example["word"]:
        raise CurriculumError(f"{path}[{index}].word: must be a non-empty string")


def _validate_item(item: Any, index: int, path: str) -> None:
    """Validate a single curriculum item (sound, pattern, or minimal_pair_sound)."""
    if not isinstance(item, dict):
        raise CurriculumError(f"{path}[{index}]: expected object, got {type(item).__name__}")

    # Required fields for all items
    if "id" not in item:
        raise CurriculumError(f"{path}[{index}]: missing required field 'id'")

    if not isinstance(item["id"], str) or not item["id"]:
        raise CurriculumError(f"{path}[{index}].id: must be a non-empty string")

    if "type" not in item:
        raise CurriculumError(f"{path}[{index}] (id={item['id']}): missing required field 'type'")

    item_type = item["type"]
    valid_types = ["sound", "pattern", "minimal_pair_sound"]
    if item_type not in valid_types:
        raise CurriculumError(
            f"{path}[{index}] (id={item['id']}): invalid type '{item_type}'. "
            f"Must be one of: {', '.join(valid_types)}"
        )

    # Type-specific validation
    if item_type in ("sound", "pattern"):
        # These types require examples
        if "examples" not in item:
            raise CurriculumError(f"{path}[{index}] (id={item['id']}): missing required field 'examples'")

        if not isinstance(item["examples"], list):
            raise CurriculumError(
                f"{path}[{index}] (id={item['id']}).examples: expected array, "
                f"got {type(item['examples']).__name__}"
            )

        if len(item["examples"]) == 0:
            raise CurriculumError(f"{path}[{index}] (id={item['id']}): examples list cannot be empty")

        for i, example in enumerate(item["examples"]):
            _validate_example(example, i, f"{path}[{index}].examples")

    elif item_type == "minimal_pair_sound":
        # Minimal pairs require left and right
        for field in ("left", "right"):
            if field not in item:
                raise CurriculumError(f"{path}[{index}] (id={item['id']}): missing required field '{field}'")
            if not isinstance(item[field], dict):
                raise CurriculumError(
                    f"{path}[{index}] (id={item['id']}).{field}: expected object, "
                    f"got {type(item[field]).__name__}"
                )
            if "word" not in item[field]:
                raise CurriculumError(f"{path}[{index}] (id={item['id']}).{field}: missing required field 'word'")


def _validate_items(items: Any, path: str = "items") -> None:
    """Validate the items array of the curriculum."""
    if not isinstance(items, list):
        raise CurriculumError(f"{path}: expected array, got {type(items).__name__}")

    seen_ids: set[str] = set()
    for i, item in enumerate(items):
        _validate_item(item, i, path)

        # Check for duplicate IDs
        item_id = item["id"]
        if item_id in seen_ids:
            raise CurriculumError(f"{path}[{i}]: duplicate id '{item_id}'")
        seen_ids.add(item_id)


def _normalize_item(item: dict) -> dict:
    """Normalize an item by ensuring all expected fields exist with defaults."""
    normalized = dict(item)

    # Ensure graphemes is a list
    if "graphemes" not in normalized:
        normalized["graphemes"] = []
    elif isinstance(normalized["graphemes"], str):
        normalized["graphemes"] = [normalized["graphemes"]]

    # Ensure notes exists
    if "notes" not in normalized:
        normalized["notes"] = ""

    return normalized


def _normalize_curriculum(data: dict) -> dict:
    """Normalize the curriculum data, adding defaults where needed."""
    normalized = dict(data)

    # Normalize items
    normalized["items"] = [_normalize_item(item) for item in data.get("items", [])]

    # Ensure alphabet.confusables exists
    if "alphabet" in normalized:
        if "confusables" not in normalized["alphabet"]:
            normalized["alphabet"]["confusables"] = []

    return normalized


def load_curriculum(path: Path | str) -> dict:
    """
    Load and validate the curriculum from a JSON file.

    Args:
        path: Path to the curriculum.json file.

    Returns:
        The validated and normalized curriculum data.

    Raises:
        CurriculumError: If the file is missing, malformed, or fails validation.
        FileNotFoundError: If the file does not exist.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Curriculum file not found: {path}")

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise CurriculumError(f"Invalid JSON in {path}: {e}") from e

    if not isinstance(data, dict):
        raise CurriculumError(f"Curriculum root must be an object, got {type(data).__name__}")

    # Validate required top-level sections
    required_sections = ["meta", "alphabet", "items"]
    for section in required_sections:
        if section not in data:
            raise CurriculumError(f"Missing required section: '{section}'")

    # Validate each section
    _validate_meta(data["meta"])
    _validate_alphabet(data["alphabet"])
    _validate_items(data["items"])

    # Normalize and return
    return _normalize_curriculum(data)


def get_items_by_type(curriculum: dict, item_type: str) -> list[dict]:
    """
    Get all items of a specific type from the curriculum.

    Args:
        curriculum: The loaded curriculum data.
        item_type: The type to filter by (e.g., "sound", "pattern").

    Returns:
        List of items matching the specified type.
    """
    return [item for item in curriculum.get("items", []) if item.get("type") == item_type]
