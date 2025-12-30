# Phonics / Phonemic Awareness Anki Deck Generator

Generates a toddler-friendly Anki deck (`.apkg`) for:

- Phonics + phonemic awareness (sounds, common spellings, patterns)
- Advanced minimal pairs (sound discrimination) in an isolated subdeck
- Alphabet practice (uppercase/lowercase association, visual confusables, and alphabet order)

This repo currently contains specs and an implementation plan.

## Specs

- Product + curriculum spec: `PHONETICS_ANKI_SPEC.md`
- Implementation spec (atomic commits, tests, determinism rules): `PHONICS_ANKI_IMPLEMENTATION_SPEC.md`

## Design Requirements (high level)

- Output is **one deck with multiple subdecks**.
- Default pronunciation target is **General American**.
- Regeneration must be deterministic: importing a regenerated deck must **not** create duplicate notes.

## What’s intentionally not in git

Large/generated artifacts are excluded by default:

- `output/` (generated `.apkg`)
- `assets/` (audio/images)
- `cache/` (API generation manifests)

