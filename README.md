# Phonics / Phonemic Awareness Anki Deck Generator

Generates a toddler-friendly Anki deck (`.apkg`) for:

- Phonics + phonemic awareness (sounds, common spellings, patterns)
- Advanced minimal pairs (sound discrimination) in an isolated subdeck
- Alphabet practice (uppercase/lowercase association, visual confusables, and alphabet order)

## Quick Start

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Install Dependencies

```bash
uv pip install -r requirements.txt
```

### Generate the Deck

```bash
uv run python scripts/create_anki_deck.py
```

Output: `output/phonics_deck.apkg`

### Import into Anki

1. Open Anki
2. File > Import
3. Select `output/phonics_deck.apkg`
4. Use **"Update existing notes when first field matches"** to preserve scheduling

## Subdecks Generated

The generator creates the following subdecks:

| Subdeck | Description |
|---------|-------------|
| `Phonics::1. Sounds (Core)` | Phoneme-first cards (hear sound, see examples) |
| `Phonics::2. Spellings (Graphemes)` | Grapheme-first cards (see spelling, learn sound) |
| `Alphabet::1. Uppercase + Lowercase` | Letter case association (A↔a) |
| `Alphabet::2. Order (What Comes Next?)` | Sequence memorization (A B C D __) |
| `Advanced::Visual Discrimination (Letters)` | Similar letter pairs (b/d, p/q, O/Q) |
| `Advanced::Minimal Pairs (Sound)` | AB discrimination (sip vs ship) |

## Curriculum

Edit `curriculum.json` to modify the deck content. The generator reads this file as the single source of truth.

### Curriculum Structure

```json
{
  "meta": { "dialect": "General American", "version": "v1" },
  "alphabet": {
    "letters": [
      { "id": "letter_a", "upper": "A", "lower": "a", "order": 1 }
    ],
    "confusables": [
      { "id": "confusable_b_d", "left": "b", "right": "d" }
    ]
  },
  "items": [
    {
      "id": "sound_ae",
      "type": "sound",
      "ipa": "/æ/",
      "sound_label": "short a",
      "graphemes": ["a"],
      "examples": [{ "word": "apple" }, { "word": "ant" }]
    },
    {
      "id": "pattern_th_voiceless",
      "type": "pattern",
      "ipa": "/θ/",
      "graphemes": ["th"],
      "examples": [{ "word": "thin" }, { "word": "think" }]
    },
    {
      "id": "minpair_s_vs_sh",
      "type": "minimal_pair_sound",
      "left": { "word": "sip", "ipa": "/sɪp/" },
      "right": { "word": "ship", "ipa": "/ʃɪp/" }
    }
  ]
}
```

See `PHONETICS_ANKI_SPEC.md` for detailed curriculum format.

## Regenerating Without Duplicates

The generator uses **deterministic IDs and GUIDs** so that re-importing an updated deck:
- Updates existing notes (preserving your scheduling/progress)
- Does NOT create duplicate cards

### Safe Workflow for Updates

1. Edit `curriculum.json` (add items, fix typos, etc.)
2. Run the generator:
   ```bash
   uv run python scripts/create_anki_deck.py
   ```
3. Import the new `.apkg` into Anki
4. When prompted, select **"Update existing notes when first field matches"**

### What Gets Preserved

- Your review history and scheduling
- Cards you've suspended
- Tags you've added manually

### What Gets Updated

- Card content (text, IPA, examples)
- Card styling (templates, CSS)
- New cards from new curriculum items

## Optional: Audio Generation

Generate TTS audio for all words using Google Cloud Text-to-Speech:

```bash
# Requires: pip install google-cloud-texttospeech
# Requires: GOOGLE_APPLICATION_CREDENTIALS environment variable

uv run python scripts/generate_audio.py

# Dry run (see what would be generated):
uv run python scripts/generate_audio.py --dry-run
```

Audio files are cached in `assets/audio/` with manifests in `cache/`.

## Optional: Image Generation

Generate illustrations using OpenAI DALL-E (or other providers):

```bash
# Requires: pip install openai requests
# Requires: OPENAI_API_KEY environment variable

uv run python scripts/generate_images.py

# Dry run:
uv run python scripts/generate_images.py --dry-run
```

Images are cached in `assets/images/` with manifests in `cache/`.

## Running Tests

```bash
uv run python -m pytest tests/ -v
```

Tests verify:
- GUID stability (critical for non-duplication)
- Curriculum validation
- Error handling

## Specs

- Product + curriculum spec: `PHONETICS_ANKI_SPEC.md`
- Implementation spec (atomic commits, tests, determinism rules): `PHONICS_ANKI_IMPLEMENTATION_SPEC.md`

## Design Requirements

- Output is **one deck with multiple subdecks**
- Default pronunciation target is **General American**
- Regeneration is **deterministic** (no duplicates on re-import)
- Media generation is **optional** (deck works without audio/images)

## What's Intentionally Not in Git

Large/generated artifacts are excluded by default:

- `output/` (generated `.apkg`)
- `assets/` (audio/images)
- `cache/` (API generation manifests)
