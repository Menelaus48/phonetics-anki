"""
Minimal pairs note model for the Phonics Anki deck.

Implements AB discrimination cards following the proven pattern from
existing foreign language minimal pairs decks:
- Prompt: "Do you hear ___ or ___?"
- Play one recording
- Reveal the correct choice on the back

Supports 2-way comparisons with optional 3rd distractor.
"""

import genanki

from ids import MODEL_ID_MINIMAL_PAIR, DECK_NAME_MINIMAL_PAIRS, deck_id_for_subdeck, note_guid


# MinimalPairNote: AB discrimination cards
# Fields based on spec:
# - Word1, Recording1, Word1IPA
# - Word2, Recording2, Word2IPA
# - Word3, Recording3, Word3IPA (optional)
# - CompareWord2ToWord3 (flag for extra cards)
# - Notes
MINIMAL_PAIR_MODEL = genanki.Model(
    MODEL_ID_MINIMAL_PAIR,
    "Minimal Pair",
    fields=[
        {"name": "Word1"},
        {"name": "Recording1"},
        {"name": "Word1IPA"},
        {"name": "Word2"},
        {"name": "Recording2"},
        {"name": "Word2IPA"},
        {"name": "Word3"},
        {"name": "Recording3"},
        {"name": "Word3IPA"},
        {"name": "CompareWord2ToWord3"},
        {"name": "Notes"},
    ],
    templates=[
        # Card 1: Play Recording 1, choose between Word 1 and Word 2
        {
            "name": "Word 1 vs Word 2 (hear 1)",
            "qfmt": """
<div class="front">
    <div class="prompt">Do you hear <strong>{{Word1}}</strong> or <strong>{{Word2}}</strong>?</div>
    <div class="audio">{{Recording1}}</div>
    <div class="choices">
        <span class="choice">{{Word1}}</span>
        <span class="choice">{{Word2}}</span>
    </div>
</div>
""",
            "afmt": """
<div class="back">
    <div class="prompt">Do you hear <strong>{{Word1}}</strong> or <strong>{{Word2}}</strong>?</div>
    <div class="audio">{{Recording1}}</div>
    <div class="answer">
        <span class="choice correct">{{Word1}}</span>
        <span class="ipa">{{Word1IPA}}</span>
    </div>
</div>
""",
        },
        # Card 2: Play Recording 2, choose between Word 1 and Word 2
        {
            "name": "Word 1 vs Word 2 (hear 2)",
            "qfmt": """
<div class="front">
    <div class="prompt">Do you hear <strong>{{Word1}}</strong> or <strong>{{Word2}}</strong>?</div>
    <div class="audio">{{Recording2}}</div>
    <div class="choices">
        <span class="choice">{{Word1}}</span>
        <span class="choice">{{Word2}}</span>
    </div>
</div>
""",
            "afmt": """
<div class="back">
    <div class="prompt">Do you hear <strong>{{Word1}}</strong> or <strong>{{Word2}}</strong>?</div>
    <div class="audio">{{Recording2}}</div>
    <div class="answer">
        <span class="choice correct">{{Word2}}</span>
        <span class="ipa">{{Word2IPA}}</span>
    </div>
</div>
""",
        },
        # Card 3: Play Recording 3, choose between Word 1 and Word 3 (only if Word3 present)
        {
            "name": "Word 1 vs Word 3 (hear 3)",
            "qfmt": """
{{#Word3}}
<div class="front">
    <div class="prompt">Do you hear <strong>{{Word1}}</strong> or <strong>{{Word3}}</strong>?</div>
    <div class="audio">{{Recording3}}</div>
    <div class="choices">
        <span class="choice">{{Word1}}</span>
        <span class="choice">{{Word3}}</span>
    </div>
</div>
{{/Word3}}
""",
            "afmt": """
{{#Word3}}
<div class="back">
    <div class="prompt">Do you hear <strong>{{Word1}}</strong> or <strong>{{Word3}}</strong>?</div>
    <div class="audio">{{Recording3}}</div>
    <div class="answer">
        <span class="choice correct">{{Word3}}</span>
        <span class="ipa">{{Word3IPA}}</span>
    </div>
</div>
{{/Word3}}
""",
        },
        # Card 4: Play Recording 1, choose between Word 1 and Word 3 (only if Word3 present)
        {
            "name": "Word 1 vs Word 3 (hear 1)",
            "qfmt": """
{{#Word3}}
<div class="front">
    <div class="prompt">Do you hear <strong>{{Word1}}</strong> or <strong>{{Word3}}</strong>?</div>
    <div class="audio">{{Recording1}}</div>
    <div class="choices">
        <span class="choice">{{Word1}}</span>
        <span class="choice">{{Word3}}</span>
    </div>
</div>
{{/Word3}}
""",
            "afmt": """
{{#Word3}}
<div class="back">
    <div class="prompt">Do you hear <strong>{{Word1}}</strong> or <strong>{{Word3}}</strong>?</div>
    <div class="audio">{{Recording1}}</div>
    <div class="answer">
        <span class="choice correct">{{Word1}}</span>
        <span class="ipa">{{Word1IPA}}</span>
    </div>
</div>
{{/Word3}}
""",
        },
        # Card 5: Play Recording 2, choose between Word 2 and Word 3 (only if CompareWord2ToWord3)
        {
            "name": "Word 2 vs Word 3 (hear 2)",
            "qfmt": """
{{#CompareWord2ToWord3}}
<div class="front">
    <div class="prompt">Do you hear <strong>{{Word2}}</strong> or <strong>{{Word3}}</strong>?</div>
    <div class="audio">{{Recording2}}</div>
    <div class="choices">
        <span class="choice">{{Word2}}</span>
        <span class="choice">{{Word3}}</span>
    </div>
</div>
{{/CompareWord2ToWord3}}
""",
            "afmt": """
{{#CompareWord2ToWord3}}
<div class="back">
    <div class="prompt">Do you hear <strong>{{Word2}}</strong> or <strong>{{Word3}}</strong>?</div>
    <div class="audio">{{Recording2}}</div>
    <div class="answer">
        <span class="choice correct">{{Word2}}</span>
        <span class="ipa">{{Word2IPA}}</span>
    </div>
</div>
{{/CompareWord2ToWord3}}
""",
        },
        # Card 6: Play Recording 3, choose between Word 2 and Word 3 (only if CompareWord2ToWord3)
        {
            "name": "Word 2 vs Word 3 (hear 3)",
            "qfmt": """
{{#CompareWord2ToWord3}}
<div class="front">
    <div class="prompt">Do you hear <strong>{{Word2}}</strong> or <strong>{{Word3}}</strong>?</div>
    <div class="audio">{{Recording3}}</div>
    <div class="choices">
        <span class="choice">{{Word2}}</span>
        <span class="choice">{{Word3}}</span>
    </div>
</div>
{{/CompareWord2ToWord3}}
""",
            "afmt": """
{{#CompareWord2ToWord3}}
<div class="back">
    <div class="prompt">Do you hear <strong>{{Word2}}</strong> or <strong>{{Word3}}</strong>?</div>
    <div class="audio">{{Recording3}}</div>
    <div class="answer">
        <span class="choice correct">{{Word3}}</span>
        <span class="ipa">{{Word3IPA}}</span>
    </div>
</div>
{{/CompareWord2ToWord3}}
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
    margin-bottom: 20px;
}
.audio {
    margin: 20px 0;
}
.choices {
    display: flex;
    justify-content: center;
    gap: 30px;
    margin-top: 20px;
}
.choice {
    font-size: 36px;
    font-weight: bold;
    padding: 20px 40px;
    background-color: white;
    border-radius: 15px;
    color: #333;
}
.answer {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
}
.choice.correct {
    font-size: 48px;
    background-color: #4CAF50;
    color: white;
    padding: 25px 50px;
}
.ipa {
    font-size: 24px;
    font-family: "Lucida Sans Unicode", "DejaVu Sans", sans-serif;
    color: #666;
}
""",
)


class MinimalPairNote(genanki.Note):
    """A note for the Minimal Pair AB discrimination card type."""

    @property
    def guid(self):
        return self._guid

    def __init__(self, item_id: str, **kwargs):
        super().__init__(**kwargs)
        self._guid = note_guid("minimal_pair", item_id)


def create_minimal_pair_note(item: dict) -> MinimalPairNote:
    """
    Create a MinimalPairNote from a curriculum item.

    Expected item structure:
    {
        "id": "minpair_s_vs_sh_sip_ship",
        "type": "minimal_pair_sound",
        "left": {"word": "sip", "ipa": "/sɪp/"},
        "right": {"word": "ship", "ipa": "/ʃɪp/"},
        "third": {"word": "...", "ipa": "..."} (optional),
        "compare_2_to_3": true/false (optional),
        "notes": "..."
    }
    """
    left = item.get("left", {})
    right = item.get("right", {})
    third = item.get("third", {})

    return MinimalPairNote(
        item_id=item["id"],
        model=MINIMAL_PAIR_MODEL,
        fields=[
            left.get("word", ""),
            "",  # Recording1 placeholder
            left.get("ipa", ""),
            right.get("word", ""),
            "",  # Recording2 placeholder
            right.get("ipa", ""),
            third.get("word", ""),
            "",  # Recording3 placeholder
            third.get("ipa", ""),
            "yes" if item.get("compare_2_to_3", False) else "",
            item.get("notes", ""),
        ],
    )


def create_minimal_pairs_deck(curriculum: dict) -> tuple[genanki.Deck, int]:
    """
    Create the minimal pairs deck from curriculum data.

    Args:
        curriculum: The loaded curriculum data.

    Returns:
        Tuple of (deck, note_count).
    """
    deck = genanki.Deck(
        deck_id_for_subdeck(DECK_NAME_MINIMAL_PAIRS),
        DECK_NAME_MINIMAL_PAIRS,
    )

    items = [
        item for item in curriculum.get("items", [])
        if item.get("type") == "minimal_pair_sound"
    ]

    for item in items:
        note = create_minimal_pair_note(item)
        deck.add_note(note)

    return deck, len(items)
