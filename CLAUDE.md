# Phonics / Phonemic Awareness Anki – Claude Reference

_AI-focused project context (standalone repo) – Last updated: 2025-12-30T19:31:58Z_

This repo generates a **single Anki deck (`.apkg`) with multiple subdecks** for:
- Phonics + phonemic awareness (sounds, common spellings, patterns)
- Advanced minimal pairs (sound discrimination)
- Alphabet practice (uppercase/lowercase association, visual confusables, alphabet order “what comes next?”)

SSOT specs:
- Product + curriculum spec: `PHONETICS_ANKI_SPEC.md`
- Implementation spec (atomic commits + tests + determinism rules): `PHONICS_ANKI_IMPLEMENTATION_SPEC.md`

---

## 🚨 Critical Rules

### ❌ Never Do This
- Never commit secrets: no `.env`, API keys, service account JSON, etc.
- Never commit generated artifacts (excluded by `.gitignore`):
  - `output/` (generated `.apkg`)
  - `assets/` (audio/images)
  - `cache/` (API generation manifests)
- Never “wing it” on determinism: if note GUIDs are not stable, imports will duplicate and the deck becomes unusable.

### ✅ Always Do This
- Use feature branches: `git checkout -b feature/<name>`
- Stage explicitly: `git add <file>...` (avoid accidentally staging large assets)
- Keep changes small and reviewable; follow the atomic-commit plan in `PHONICS_ANKI_IMPLEMENTATION_SPEC.md`.

---

## Project Decisions (Locked In)

- Output packaging: **one deck** with multiple subdecks.
- Default dialect: **General American**.
- Minimal pairs: **text on the front**, mirroring existing foreign-language minimal pairs decks.
- Alphabet order prompts: **uppercase-only**.
- Letter-name audio: **deferred** (keep it configurable later).

---

## Implementation Notes (What Matters Most)

### Deterministic Regeneration

The generator must use:
- stable `deck_id` / `model_id` constants
- stable per-note GUID derived from curriculum IDs (and a per-model namespace)

Goal: regenerating and importing again should **update existing notes** rather than creating duplicates, preserving scheduling.

### Minimal Pairs Model (AB Discrimination)

Reuse the proven UX pattern:
- Prompt: “Do you hear ___ or ___?”
- Play one audio (Word 1 or Word 2)
- Reveal: “You heard: ___” on back
- Optional third distractor and extra compare cards (advanced mode)

### Alphabet Tracks

Keep alphabet work separate from phonics work (different skill):
- `Alphabet::1. Uppercase + Lowercase`
- `Alphabet::2. Order (What Comes Next?)` (uppercase-only)
- `Advanced::Visual Discrimination (Letters)` (confusables like `O/Q`, `b/d/p/q`)

---

## Local Workflow (Expected)

This repo is currently spec-first. As code lands, keep commands stable and documented in `README.md`.

Expected end-state commands (subject to implementation):
- Generate deck: `python scripts/create_anki_deck.py`
- (Optional) Generate audio: `python scripts/generate_audio.py`
- Run tests: `python -m pytest`

---

## Coding Standards

- Prefer boring Python: minimal dependencies, clear error messages, deterministic behavior.
- No random defaults in curriculum processing.
- Do not add complex template JS unless needed; keep Anki templates robust across devices.

