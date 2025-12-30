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
4. Use "Update existing notes" to preserve scheduling on re-import

## Curriculum

Edit `curriculum.json` to modify the deck content. The generator reads this file as the single source of truth.

### Curriculum Structure

```json
{
  "meta": { "dialect": "General American", "version": "v1" },
  "alphabet": {
    "letters": [...],
    "confusables": [...]
  },
  "items": [
    { "id": "sound_ae", "type": "sound", ... },
    { "id": "pattern_sh", "type": "pattern", ... }
  ]
}
```

See `PHONETICS_ANKI_SPEC.md` for detailed curriculum format.

## Specs

- Product + curriculum spec: `PHONETICS_ANKI_SPEC.md`
- Implementation spec (atomic commits, tests, determinism rules): `PHONICS_ANKI_IMPLEMENTATION_SPEC.md`

## Design Requirements

- Output is **one deck with multiple subdecks**.
- Default pronunciation target is **General American**.
- Regeneration must be deterministic: importing a regenerated deck must **not** create duplicate notes.

## What's Intentionally Not in Git

Large/generated artifacts are excluded by default:

- `output/` (generated `.apkg`)
- `assets/` (audio/images)
- `cache/` (API generation manifests)
