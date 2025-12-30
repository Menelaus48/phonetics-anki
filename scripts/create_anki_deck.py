#!/usr/bin/env python3
"""
Anki deck generator for the Phonics curriculum.

Generates a single .apkg file with multiple subdecks for:
- Phonics::1. Sounds (Core) - phoneme-first cards
- Phonics::2. Spellings (Graphemes) - grapheme-first cards

Usage:
    python scripts/create_anki_deck.py [curriculum.json] [output.apkg]

Defaults:
    curriculum.json -> curriculum.json (in project root)
    output.apkg -> output/phonics_deck.apkg
"""

import sys
from pathlib import Path

import genanki

from curriculum import load_curriculum, get_items_by_type, CurriculumError
from ids import (
    MODEL_ID_SOUND,
    MODEL_ID_PATTERN,
    MODEL_ID_LETTER_CASE,
    MODEL_ID_VISUAL_CONFUSABLE,
    MODEL_ID_ALPHABET_ORDER,
    DECK_NAME_SOUNDS,
    DECK_NAME_SPELLINGS,
    DECK_NAME_ALPHABET_CASE,
    DECK_NAME_ALPHABET_ORDER,
    DECK_NAME_VISUAL_CONFUSABLES,
    deck_id_for_subdeck,
    note_guid,
)
from alphabet_order import generate_alphabet_order_items


# =============================================================================
# Card Templates
# =============================================================================

# SoundNote: phoneme-first card (hear sound -> see examples)
# Fields: IPA, SoundLabel, Graphemes, FrontExample, AllExamples, Notes, Audio (placeholder)
SOUND_MODEL = genanki.Model(
    MODEL_ID_SOUND,
    "Phonics Sound",
    fields=[
        {"name": "IPA"},
        {"name": "SoundLabel"},
        {"name": "Graphemes"},
        {"name": "FrontExample"},
        {"name": "AllExamples"},
        {"name": "Notes"},
        {"name": "FrontExampleAudio"},  # Placeholder for Phase 4
        {"name": "AllExamplesAudio"},   # Placeholder for Phase 4
    ],
    templates=[
        {
            "name": "Sound Recognition",
            "qfmt": """
<div class="front">
    <div class="sound-label">{{SoundLabel}}</div>
    <div class="ipa">{{IPA}}</div>
    <div class="example-word">{{FrontExample}}</div>
</div>
""",
            "afmt": """
{{FrontSide}}
<hr id="answer">
<div class="back">
    <div class="spellings">Spellings: {{Graphemes}}</div>
    <div class="examples">
        <strong>Examples:</strong><br>
        {{AllExamples}}
    </div>
    {{#Notes}}<div class="notes">{{Notes}}</div>{{/Notes}}
</div>
""",
        }
    ],
    css="""
.card {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 24px;
    text-align: center;
    color: #333;
    background-color: #f5f5f5;
    padding: 20px;
}
.front {
    margin-bottom: 20px;
}
.sound-label {
    font-size: 32px;
    font-weight: bold;
    color: #2196F3;
    margin-bottom: 10px;
}
.ipa {
    font-size: 28px;
    font-family: "Lucida Sans Unicode", "DejaVu Sans", sans-serif;
    color: #666;
    margin-bottom: 15px;
}
.example-word {
    font-size: 36px;
    font-weight: bold;
    color: #4CAF50;
    padding: 20px;
    background-color: white;
    border-radius: 10px;
    display: inline-block;
}
.back {
    text-align: left;
    padding: 15px;
    background-color: white;
    border-radius: 10px;
}
.spellings {
    font-size: 20px;
    color: #FF9800;
    margin-bottom: 10px;
}
.examples {
    font-size: 20px;
    margin-bottom: 10px;
}
.notes {
    font-size: 16px;
    color: #888;
    font-style: italic;
    margin-top: 10px;
}
""",
)


# PatternNote: grapheme-first card (see spelling -> hear examples)
# Fields: Grapheme, IPA, FrontExample, AllExamples, Notes, Audio (placeholder)
PATTERN_MODEL = genanki.Model(
    MODEL_ID_PATTERN,
    "Phonics Pattern",
    fields=[
        {"name": "Grapheme"},
        {"name": "IPA"},
        {"name": "FrontExample"},
        {"name": "AllExamples"},
        {"name": "Notes"},
        {"name": "FrontExampleAudio"},  # Placeholder for Phase 4
        {"name": "AllExamplesAudio"},   # Placeholder for Phase 4
    ],
    templates=[
        {
            "name": "Pattern Recognition",
            "qfmt": """
<div class="front">
    <div class="grapheme">{{Grapheme}}</div>
    <div class="prompt">What sound does this make?</div>
</div>
""",
            "afmt": """
{{FrontSide}}
<hr id="answer">
<div class="back">
    <div class="ipa">{{IPA}}</div>
    <div class="example-word">{{FrontExample}}</div>
    <div class="examples">
        <strong>More examples:</strong><br>
        {{AllExamples}}
    </div>
    {{#Notes}}<div class="notes">{{Notes}}</div>{{/Notes}}
</div>
""",
        }
    ],
    css="""
.card {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 24px;
    text-align: center;
    color: #333;
    background-color: #f5f5f5;
    padding: 20px;
}
.front {
    margin-bottom: 20px;
}
.grapheme {
    font-size: 72px;
    font-weight: bold;
    color: #9C27B0;
    padding: 30px;
    background-color: white;
    border-radius: 15px;
    display: inline-block;
    margin-bottom: 20px;
}
.prompt {
    font-size: 20px;
    color: #666;
}
.back {
    text-align: center;
    padding: 15px;
}
.ipa {
    font-size: 32px;
    font-family: "Lucida Sans Unicode", "DejaVu Sans", sans-serif;
    color: #2196F3;
    margin-bottom: 15px;
}
.example-word {
    font-size: 36px;
    font-weight: bold;
    color: #4CAF50;
    padding: 20px;
    background-color: white;
    border-radius: 10px;
    display: inline-block;
    margin-bottom: 15px;
}
.examples {
    font-size: 20px;
    text-align: left;
    background-color: white;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 10px;
}
.notes {
    font-size: 16px;
    color: #888;
    font-style: italic;
}
""",
)


# LetterCaseNote: uppercase/lowercase association
# Fields: Upper, Lower, LetterName, Audio (placeholder)
LETTER_CASE_MODEL = genanki.Model(
    MODEL_ID_LETTER_CASE,
    "Alphabet Letter Case",
    fields=[
        {"name": "Upper"},
        {"name": "Lower"},
        {"name": "LetterName"},
        {"name": "LetterNameAudio"},  # Placeholder for Phase 4
    ],
    templates=[
        {
            "name": "Upper to Lower",
            "qfmt": """
<div class="front">
    <div class="prompt">What is the lowercase of:</div>
    <div class="letter upper">{{Upper}}</div>
</div>
""",
            "afmt": """
{{FrontSide}}
<hr id="answer">
<div class="back">
    <div class="letter lower">{{Lower}}</div>
</div>
""",
        },
        {
            "name": "Lower to Upper",
            "qfmt": """
<div class="front">
    <div class="prompt">What is the uppercase of:</div>
    <div class="letter lower">{{Lower}}</div>
</div>
""",
            "afmt": """
{{FrontSide}}
<hr id="answer">
<div class="back">
    <div class="letter upper">{{Upper}}</div>
</div>
""",
        },
    ],
    css="""
.card {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 24px;
    text-align: center;
    color: #333;
    background-color: #f5f5f5;
    padding: 20px;
}
.front {
    margin-bottom: 20px;
}
.prompt {
    font-size: 20px;
    color: #666;
    margin-bottom: 20px;
}
.letter {
    font-size: 96px;
    font-weight: bold;
    padding: 30px 50px;
    background-color: white;
    border-radius: 15px;
    display: inline-block;
}
.letter.upper {
    color: #E91E63;
}
.letter.lower {
    color: #00BCD4;
}
.back {
    padding: 15px;
}
""",
)


# VisualConfusableNote: letter pairs that look similar
# Fields: Left, Right, Notes, Hint
VISUAL_CONFUSABLE_MODEL = genanki.Model(
    MODEL_ID_VISUAL_CONFUSABLE,
    "Visual Confusable",
    fields=[
        {"name": "Left"},
        {"name": "Right"},
        {"name": "Notes"},
        {"name": "Hint"},
    ],
    templates=[
        {
            "name": "Which is Left",
            "qfmt": """
<div class="front">
    <div class="prompt">Which one is <strong>{{Left}}</strong>?</div>
    <div class="choices">
        <span class="choice">{{Left}}</span>
        <span class="choice">{{Right}}</span>
    </div>
</div>
""",
            "afmt": """
<div class="back">
    <div class="prompt">Which one is <strong>{{Left}}</strong>?</div>
    <div class="choices">
        <span class="choice correct">{{Left}}</span>
        <span class="choice wrong">{{Right}}</span>
    </div>
    {{#Hint}}<div class="hint">Hint: {{Hint}}</div>{{/Hint}}
</div>
""",
        },
        {
            "name": "Which is Right",
            "qfmt": """
<div class="front">
    <div class="prompt">Which one is <strong>{{Right}}</strong>?</div>
    <div class="choices">
        <span class="choice">{{Left}}</span>
        <span class="choice">{{Right}}</span>
    </div>
</div>
""",
            "afmt": """
<div class="back">
    <div class="prompt">Which one is <strong>{{Right}}</strong>?</div>
    <div class="choices">
        <span class="choice wrong">{{Left}}</span>
        <span class="choice correct">{{Right}}</span>
    </div>
    {{#Hint}}<div class="hint">Hint: {{Hint}}</div>{{/Hint}}
</div>
""",
        },
    ],
    css="""
.card {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 24px;
    text-align: center;
    color: #333;
    background-color: #f5f5f5;
    padding: 20px;
}
.front, .back {
    margin-bottom: 20px;
}
.prompt {
    font-size: 24px;
    color: #333;
    margin-bottom: 30px;
}
.choices {
    display: flex;
    justify-content: center;
    gap: 40px;
}
.choice {
    font-size: 72px;
    font-weight: bold;
    padding: 30px 50px;
    background-color: white;
    border-radius: 15px;
    color: #333;
}
.choice.correct {
    background-color: #4CAF50;
    color: white;
}
.choice.wrong {
    background-color: #f5f5f5;
    color: #999;
}
.hint {
    font-size: 18px;
    color: #666;
    font-style: italic;
    margin-top: 20px;
}
""",
)


# AlphabetOrderNote: "What comes next?" sequence cards
# Fields: Prompt, Answer, Position
ALPHABET_ORDER_MODEL = genanki.Model(
    MODEL_ID_ALPHABET_ORDER,
    "Alphabet Order",
    fields=[
        {"name": "Prompt"},
        {"name": "Answer"},
        {"name": "Position"},
    ],
    templates=[
        {
            "name": "What Comes Next",
            "qfmt": """
<div class="front">
    <div class="instruction">What comes next?</div>
    <div class="sequence">{{Prompt}}</div>
</div>
""",
            "afmt": """
{{FrontSide}}
<hr id="answer">
<div class="back">
    <div class="answer">{{Answer}}</div>
</div>
""",
        },
    ],
    css="""
.card {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 24px;
    text-align: center;
    color: #333;
    background-color: #f5f5f5;
    padding: 20px;
}
.front {
    margin-bottom: 20px;
}
.instruction {
    font-size: 20px;
    color: #666;
    margin-bottom: 30px;
}
.sequence {
    font-size: 48px;
    font-weight: bold;
    font-family: "SF Mono", "Monaco", "Menlo", monospace;
    letter-spacing: 8px;
    color: #333;
    padding: 30px;
    background-color: white;
    border-radius: 15px;
    display: inline-block;
}
.back {
    padding: 15px;
}
.answer {
    font-size: 72px;
    font-weight: bold;
    color: #4CAF50;
    padding: 20px 40px;
    background-color: white;
    border-radius: 15px;
    display: inline-block;
}
""",
)


# =============================================================================
# Note Creation
# =============================================================================


class SoundNote(genanki.Note):
    """A note for the Sound Recognition card type."""

    @property
    def guid(self):
        # Use the first field (IPA) combined with item ID for uniqueness
        # But we override this with a stable GUID in the constructor
        return self._guid

    def __init__(self, item_id: str, **kwargs):
        super().__init__(**kwargs)
        self._guid = note_guid("sound", item_id)


class PatternNote(genanki.Note):
    """A note for the Pattern Recognition card type."""

    @property
    def guid(self):
        return self._guid

    def __init__(self, item_id: str, **kwargs):
        super().__init__(**kwargs)
        self._guid = note_guid("pattern", item_id)


class LetterCaseNote(genanki.Note):
    """A note for the Alphabet Letter Case card type."""

    @property
    def guid(self):
        return self._guid

    def __init__(self, item_id: str, **kwargs):
        super().__init__(**kwargs)
        self._guid = note_guid("letter_case", item_id)


class VisualConfusableNote(genanki.Note):
    """A note for the Visual Confusable card type."""

    @property
    def guid(self):
        return self._guid

    def __init__(self, item_id: str, **kwargs):
        super().__init__(**kwargs)
        self._guid = note_guid("visual_confusable", item_id)


class AlphabetOrderNote(genanki.Note):
    """A note for the Alphabet Order (What Comes Next?) card type."""

    @property
    def guid(self):
        return self._guid

    def __init__(self, item_id: str, **kwargs):
        super().__init__(**kwargs)
        self._guid = note_guid("alphabet_order", item_id)


def create_sound_note(item: dict) -> SoundNote:
    """Create a SoundNote from a curriculum item."""
    examples = item.get("examples", [])
    front_example = examples[0]["word"] if examples else ""
    all_examples = ", ".join(ex["word"] for ex in examples)
    graphemes = ", ".join(item.get("graphemes", []))

    return SoundNote(
        item_id=item["id"],
        model=SOUND_MODEL,
        fields=[
            item.get("ipa", ""),
            item.get("sound_label", item.get("ipa", "")),
            graphemes,
            front_example,
            all_examples,
            item.get("notes", ""),
            "",  # FrontExampleAudio placeholder
            "",  # AllExamplesAudio placeholder
        ],
    )


def create_pattern_note(item: dict) -> PatternNote:
    """Create a PatternNote from a curriculum item."""
    examples = item.get("examples", [])
    front_example = examples[0]["word"] if examples else ""
    all_examples = ", ".join(ex["word"] for ex in examples)
    graphemes = item.get("graphemes", [])
    # Use the first grapheme as the main display
    grapheme = graphemes[0] if graphemes else ""

    return PatternNote(
        item_id=item["id"],
        model=PATTERN_MODEL,
        fields=[
            grapheme,
            item.get("ipa", ""),
            front_example,
            all_examples,
            item.get("notes", ""),
            "",  # FrontExampleAudio placeholder
            "",  # AllExamplesAudio placeholder
        ],
    )


def create_letter_case_note(letter: dict) -> LetterCaseNote:
    """Create a LetterCaseNote from an alphabet letter entry."""
    return LetterCaseNote(
        item_id=letter["id"],
        model=LETTER_CASE_MODEL,
        fields=[
            letter.get("upper", ""),
            letter.get("lower", ""),
            letter.get("name", ""),
            "",  # LetterNameAudio placeholder
        ],
    )


def create_visual_confusable_note(confusable: dict) -> VisualConfusableNote:
    """Create a VisualConfusableNote from a confusable entry."""
    return VisualConfusableNote(
        item_id=confusable["id"],
        model=VISUAL_CONFUSABLE_MODEL,
        fields=[
            confusable.get("left", ""),
            confusable.get("right", ""),
            confusable.get("notes", ""),
            confusable.get("hint", ""),
        ],
    )


def create_alphabet_order_note(item: dict) -> AlphabetOrderNote:
    """Create an AlphabetOrderNote from an alphabet order item."""
    return AlphabetOrderNote(
        item_id=item["id"],
        model=ALPHABET_ORDER_MODEL,
        fields=[
            item.get("prompt", ""),
            item.get("answer", ""),
            str(item.get("position", "")),
        ],
    )


# =============================================================================
# Deck Building
# =============================================================================


def build_deck(curriculum: dict, output_path: Path) -> None:
    """
    Build the Anki deck from the curriculum data.

    Args:
        curriculum: The loaded and validated curriculum data.
        output_path: Where to write the .apkg file.
    """
    # Create subdecks
    sounds_deck = genanki.Deck(
        deck_id_for_subdeck(DECK_NAME_SOUNDS),
        DECK_NAME_SOUNDS,
    )
    spellings_deck = genanki.Deck(
        deck_id_for_subdeck(DECK_NAME_SPELLINGS),
        DECK_NAME_SPELLINGS,
    )
    alphabet_case_deck = genanki.Deck(
        deck_id_for_subdeck(DECK_NAME_ALPHABET_CASE),
        DECK_NAME_ALPHABET_CASE,
    )
    alphabet_order_deck = genanki.Deck(
        deck_id_for_subdeck(DECK_NAME_ALPHABET_ORDER),
        DECK_NAME_ALPHABET_ORDER,
    )
    visual_confusables_deck = genanki.Deck(
        deck_id_for_subdeck(DECK_NAME_VISUAL_CONFUSABLES),
        DECK_NAME_VISUAL_CONFUSABLES,
    )

    # Process sound items -> Sounds deck
    sound_items = get_items_by_type(curriculum, "sound")
    for item in sound_items:
        note = create_sound_note(item)
        sounds_deck.add_note(note)

    # Process pattern items -> Spellings deck
    pattern_items = get_items_by_type(curriculum, "pattern")
    for item in pattern_items:
        note = create_pattern_note(item)
        spellings_deck.add_note(note)

    # Process alphabet letters -> Alphabet Case deck
    alphabet = curriculum.get("alphabet", {})
    letters = alphabet.get("letters", [])
    for letter in letters:
        note = create_letter_case_note(letter)
        alphabet_case_deck.add_note(note)

    # Process visual confusables -> Visual Confusables deck
    confusables = alphabet.get("confusables", [])
    for confusable in confusables:
        note = create_visual_confusable_note(confusable)
        visual_confusables_deck.add_note(note)

    # Generate alphabet order items -> Alphabet Order deck
    alphabet_order_items = list(generate_alphabet_order_items(letters, window_size=4))
    for item in alphabet_order_items:
        note = create_alphabet_order_note(item)
        alphabet_order_deck.add_note(note)

    # Create the package with all decks
    all_decks = [
        sounds_deck,
        spellings_deck,
        alphabet_case_deck,
        alphabet_order_deck,
        visual_confusables_deck,
    ]
    package = genanki.Package(all_decks)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write the package
    package.write_to_file(str(output_path))

    # Print summary
    print(f"Deck generated: {output_path}")
    print(f"  Sounds (Core): {len(sound_items)} notes")
    print(f"  Spellings (Graphemes): {len(pattern_items)} notes")
    print(f"  Alphabet Case: {len(letters)} notes")
    print(f"  Alphabet Order: {len(alphabet_order_items)} notes")
    print(f"  Visual Confusables: {len(confusables)} notes")


# =============================================================================
# Main
# =============================================================================


def main():
    """Main entry point."""
    # Parse arguments
    curriculum_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("curriculum.json")
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("output/phonics_deck.apkg")

    # Load curriculum
    try:
        curriculum = load_curriculum(curriculum_path)
    except FileNotFoundError:
        print(f"Error: Curriculum file not found: {curriculum_path}", file=sys.stderr)
        sys.exit(1)
    except CurriculumError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Build deck
    build_deck(curriculum, output_path)


if __name__ == "__main__":
    main()
