"""
Deterministic ID generation for the Phonics Anki deck generator.

This module provides stable deck IDs, model IDs, and note GUIDs to ensure
that re-importing a regenerated deck does not create duplicate notes.

The IDs are derived deterministically from fixed namespaces and item IDs,
using a hash-based approach that produces stable 64-bit integers suitable
for Anki's ID fields.
"""

import hashlib
from typing import Literal


# =============================================================================
# Stable Deck and Model IDs
# =============================================================================
# These are fixed constants that should NEVER change once notes have been
# created, or existing schedules will be lost.
#
# The values are derived from hashing the namespace strings to get unique
# but reproducible 32-bit integers (Anki uses signed 32-bit for some IDs).
# =============================================================================

def _hash_to_id(namespace: str) -> int:
    """
    Convert a namespace string to a stable positive integer ID.

    Uses MD5 hash (for speed and determinism, not security) and takes
    the first 8 bytes as a 63-bit positive integer.
    """
    h = hashlib.md5(namespace.encode("utf-8")).digest()
    # Use first 8 bytes, mask to 63 bits to ensure positive
    return int.from_bytes(h[:8], "big") & 0x7FFFFFFFFFFFFFFF


# Main deck (parent of all subdecks)
DECK_ID_PHONICS_ROOT = _hash_to_id("phonics-anki:deck:root")

# Model (note type) IDs - one per card type
MODEL_ID_SOUND = _hash_to_id("phonics-anki:model:sound")
MODEL_ID_PATTERN = _hash_to_id("phonics-anki:model:pattern")
MODEL_ID_LETTER_CASE = _hash_to_id("phonics-anki:model:letter_case")
MODEL_ID_VISUAL_CONFUSABLE = _hash_to_id("phonics-anki:model:visual_confusable")
MODEL_ID_ALPHABET_ORDER = _hash_to_id("phonics-anki:model:alphabet_order")
MODEL_ID_MINIMAL_PAIR = _hash_to_id("phonics-anki:model:minimal_pair")


# =============================================================================
# Subdeck Names
# =============================================================================
# Anki uses :: as the hierarchy separator

DECK_NAME_SOUNDS = "Phonics::1. Sounds (Core)"
DECK_NAME_SPELLINGS = "Phonics::2. Spellings (Graphemes)"
DECK_NAME_PATTERNS = "Phonics::3. Patterns (Chunks/Rimes)"
DECK_NAME_ALPHABET_CASE = "Alphabet::1. Uppercase + Lowercase"
DECK_NAME_ALPHABET_ORDER = "Alphabet::2. Order (What Comes Next?)"
DECK_NAME_VISUAL_CONFUSABLES = "Advanced::Visual Discrimination (Letters)"
DECK_NAME_MINIMAL_PAIRS = "Advanced::Minimal Pairs (Sound)"


# =============================================================================
# Note GUID Generation
# =============================================================================

# Model namespace prefixes for GUID generation
# These ensure that the same item_id in different models produces different GUIDs
ModelNamespace = Literal[
    "sound",
    "pattern",
    "letter_case",
    "visual_confusable",
    "alphabet_order",
    "minimal_pair",
]


def note_guid(model_namespace: ModelNamespace, item_id: str) -> str:
    """
    Generate a deterministic GUID for an Anki note.

    The GUID is derived from combining the model namespace with the item ID,
    ensuring that:
    1. The same item_id always produces the same GUID for a given model
    2. Different models with the same item_id produce different GUIDs
    3. The GUID is a valid Anki GUID format (base91 encoded, ~10 chars)

    Args:
        model_namespace: The type of note (e.g., "sound", "pattern")
        item_id: The unique ID of the curriculum item

    Returns:
        A deterministic GUID string suitable for genanki.
    """
    # Combine namespace and item_id
    combined = f"phonics-anki:{model_namespace}:{item_id}"

    # Hash to get stable bytes
    h = hashlib.sha256(combined.encode("utf-8")).digest()

    # Convert to base91 (Anki's GUID format uses approximately this)
    # For simplicity, we'll use base64-like encoding but with Anki-safe chars
    # Anki GUIDs are typically 10 chars from a specific character set
    return _bytes_to_guid(h[:8])


def _bytes_to_guid(data: bytes) -> str:
    """
    Convert bytes to an Anki-compatible GUID string.

    Anki uses a base91-ish encoding for GUIDs. For maximum compatibility,
    we'll use a subset of safe alphanumeric characters.
    """
    # Character set for encoding (alphanumeric, no ambiguous chars)
    # This gives us 62 chars, enough for base62 encoding
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    base = len(chars)

    # Convert bytes to a large integer
    num = int.from_bytes(data, "big")

    # Encode as base62
    if num == 0:
        return chars[0]

    result = []
    while num > 0:
        result.append(chars[num % base])
        num //= base

    return "".join(reversed(result))


def deck_id_for_subdeck(subdeck_name: str) -> int:
    """
    Generate a deterministic deck ID for a subdeck.

    While genanki can auto-generate deck IDs, using deterministic IDs
    ensures stability across regenerations.

    Args:
        subdeck_name: The full subdeck name (e.g., "Phonics::1. Sounds (Core)")

    Returns:
        A stable positive integer deck ID.
    """
    return _hash_to_id(f"phonics-anki:deck:{subdeck_name}")
