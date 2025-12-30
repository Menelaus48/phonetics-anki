# Phonics / Phonemic Awareness Anki – Codex Agent Guide

**📖 SSOT Reference:** `CLAUDE.md` (AI project context + critical rules)

This file is a Codex-friendly quickstart for working in this repo without footguns.

---

## 🚨 Guardrails (Non-Negotiable)

### ❌ Never Do This
- Never commit secrets (`.env`, API keys, service account files).
- Never commit large/generated artifacts:
  - `output/` (generated `.apkg`)
  - `assets/` (audio/images)
  - `cache/` (API generation manifests)
- Never use broad staging commands like `git add .` / `git add -A` (easy to accidentally stage big artifacts).
- Never break determinism (stable IDs + GUIDs are mandatory for re-import without duplication).

### ✅ Always Do This
- Create a feature branch: `git checkout -b feature/<short-name>`
- Stage only what you changed: `git add <file>...`
- Follow the atomic commit plan in `PHONICS_ANKI_IMPLEMENTATION_SPEC.md`.
- If a commit is getting big: stop and split it, then update the spec.

---

## Repo Purpose

Generate a **single Anki deck** with multiple subdecks:
- `Phonics::...` (sounds, spellings, patterns)
- `Alphabet::...` (uppercase/lowercase, order)
- `Advanced::...` (minimal pairs; visual confusables)

Defaults:
- Dialect: **General American**
- Minimal pairs: **text on front**
- Alphabet order prompts: **uppercase-only**

---

## Quick Start

- Read specs:
  - `PHONETICS_ANKI_SPEC.md` (what to build)
  - `PHONICS_ANKI_IMPLEMENTATION_SPEC.md` (how to build it in atomic commits)
- Open repo in VS Code:
  - `code -n "/Users/peteralfieri/Projects/phonetics-anki"`

---

## Development Workflow

1. Create branch: `git checkout -b feature/<name>`
2. Implement Commit 1 from the implementation spec
3. Run the smallest relevant verification (tests once they exist)
4. Commit with a conventional message (`docs:`, `feat:`, `test:`)
5. Push branch and open PR

---

## Notes for Agents

- Keep templates simple and robust across Anki desktop/iOS.
- Prefer “text on front” for minimal pairs (mirror existing language decks).
- Alphabet order prompts should be uppercase-only unless explicitly changed in the spec.

