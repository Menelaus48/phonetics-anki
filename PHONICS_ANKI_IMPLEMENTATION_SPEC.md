# Phonics / Phonemic Awareness Anki Deck Generator (Implementation Spec)

Build a small, deterministic generator that turns a curated phonics + phonemic awareness curriculum into an Anki `.apkg` deck (with optional audio/image generation), plus several subdecks for alphabet knowledge and advanced minimal-pairs discrimination. This should reuse proven card patterns from Peter’s existing Anki “minimal pairs” decks so the learning flow is familiar and effective. The result should be repeatable: regenerating and re-importing should not create duplicates.

If anything below is underspecified, answer the questions (max 5) and I’ll proceed; otherwise, assumptions are listed and the spec continues.

### Decisions (confirmed)
1. Output packaging: **one deck** with multiple subdecks.
2. Alphabet order prompts: **uppercase only**.
3. Minimal pairs: **text on the front** (mirror existing foreign language minimal pairs decks).
4. Distribution shape: **script-first** for now (we can add a small CLI wrapper later if/when it’s helpful).
5. Letter-name audio: **defer** (keep it configurable later).

### Assumptions (used unless you override)
- Output is a **single `.apkg`** containing multiple subdecks (hierarchical deck names).
- Default pronunciation target is **General American**.
- MVP does **not require** image generation; deck generation must work with missing images and can be run “audio-only” or “no-media” for fast iteration.
- Minimal pairs subdeck uses the same **AB discrimination** card structure as your existing language decks (“Do you hear … or …?”, play audio, reveal correct choice).
- We will not write secrets to disk; API keys/credentials come from environment variables.
- Alphabet order prompts are generated from the uppercase alphabet only (`A`..`Z`).

---

### Metadata
- Status: Draft
- Priority: P0
- Effort: 2–5 days (MVP generator + determinism + minimal tests), +1–3 days for TTS/image integrations
- Owner: Peter (with Codex assistance)
- Blocked By:
  - Google Cloud TTS credentials (optional for MVP)
  - Image generation API access (optional for MVP)
- Unblocks:
  - A usable toddler-friendly deck you can iterate on quickly
- Related docs/specs:
  - `peters-workspace/phonetics-anki/PHONETICS_ANKI_SPEC.md` (curriculum + product spec)
  - `specs/meta/spec-authoring-prompt.md` (spec structure expectations)
- Last updated/version: 2025-12-30 / v1

---

### Current State & Evidence
- This project currently exists as a detailed project/curriculum spec: `peters-workspace/phonetics-anki/PHONETICS_ANKI_SPEC.md`.
- The “Anki best-practice” constraint is known from experience: re-importing regenerated decks must **not** create duplicates; this requires stable deck/model IDs and stable note GUIDs (documented in `peters-workspace/phonetics-anki/PHONETICS_ANKI_SPEC.md`).
- Existing Anki decks (on the same Mac host) contain minimal-pairs note types with an effective AB discrimination pattern:
  - Two options displayed, one audio played, answer reveals the correct choice.
  - Optional third distractor and additional “compare 2 vs 3” cards.
  - These patterns are used across multiple “Minimal Pairs” language subdecks and should be mirrored here for English.

---

### Issue Summary
We need an implementation-ready plan to turn the phonics curriculum into a real, repeatable `.apkg` generator with deterministic imports, plus subdecks for alphabet knowledge and advanced minimal pairs.

---

### Goals (G1, G2, G3...)
- G1: Generate a valid `.apkg` with subdecks and notes from `curriculum.json` in `peters-workspace/phonetics-anki` (no manual Anki editing required).
- G2: Deterministic regeneration: importing a regenerated `.apkg` does **not** duplicate notes (stable IDs + GUIDs).
- G3: Support at least three “tracks” of learning as separate subdecks:
  - Phonics sounds/patterns
  - Alphabet uppercase/lowercase + visual confusables
  - Alphabet order (“what comes next?”)
- G4: Minimal pairs subdeck follows the proven AB discrimination structure (and supports optional third distractor cards).
- G5: Provide a documented, one-command pipeline for “generate deck from curriculum + local assets”, with caching/manifest support for optional TTS/images.

---

### Non-Goals (NG1, NG2...)
- NG1: A web UI or “custom app” learning experience (Anki is the platform; generator is offline).
- NG2: Full pedagogical perfection of the English phoneme inventory (MVP is pragmatic and toddler-focused; we can iterate curriculum later).
- NG3: Guaranteed perfect IPA across dialects (we target General American; other dialects are separate profiles).
- NG4: Shipping this as a public, polished open-source product immediately (first milestone is “works for Peter’s family reliably”).

---

### Systems/Architecture Model

**Core idea:** curriculum drives everything; assets are generated/cached deterministically; deck generation is deterministic.

**Before:**
- Spec-only; no generator; no determinism guarantees.

**After:**
- `curriculum.json` → optional asset generation → `.apkg`

ASCII flow:
```
curriculum.json
  | (validate + normalize)
  v
item list + alphabet list
  |                 \
  |                  \--> generate alphabet order prompts (algorithmic)
  |
  +--> (optional) generate audio/images with cache manifests
  |
  v
genanki builder:
  - stable deck_id/model_ids
  - stable note GUIDs
  - hierarchical subdecks
  |
  v
output/phonics_deck.apkg
```

Failure modes to design for:
- Missing media files → card still renders; audio/image placeholders don’t break import.
- Partially generated media → generator skips or warns; does not crash.
- Curriculum edits → deterministic GUID strategy ensures updates overwrite existing notes rather than duplicating them.

Scalability direction:
- “Scale” here is *content size* (hundreds to a few thousand notes), not throughput. Keep it simple, cache API calls, avoid re-generating unchanged media.

---

### Key Decisions (ADR)

| Decision | Choice | Alternatives Rejected | Why This Won |
|----------|--------|----------------------|--------------|
| Curriculum SSOT | `curriculum.json` (SSOT) with optional CSV export | CSV-only SSOT | JSON better represents nested examples, prompts, and alphabet sections without fragile parsing |
| Output packaging | One `.apkg` with subdecks | One deck per subdeck | One file is easier to import/sync; subdecks preserve isolation |
| Determinism | Stable `deck_id`/`model_id` + stable note GUID per item | “Just regenerate” without stable IDs | Prevents duplicate notes and preserves schedules across re-imports |
| Minimal pairs UX | Reuse AB discrimination pattern from existing decks | New custom UX | It’s already proven in Peter’s study workflow and maps well to phoneme discrimination |
| Alphabet order | Generate algorithmically from alphabet list | Hand-author order cards | Less manual work, fewer errors, easy to adjust window size/difficulty |

---

### Conventions & Standards (if introducing a new pattern)
*(For rationale behind pattern choices, see Key Decisions (ADR) above)*

- Directory SSOT: everything for this project lives under `peters-workspace/phonetics-anki/`.
- SSOT file: `peters-workspace/phonetics-anki/curriculum.json` (NEW).
- Deterministic IDs:
  - Every curriculum item has a stable string `id`.
  - Generator derives Anki note GUID from that `id` (and an explicit namespace per model).
- Media naming:
  - Audio filenames include the stable item id and variant keys (voice + rate): e.g. `audio_word__sound_ae__apple__ga_voice_v1.mp3`
  - Image filenames include word + prompt_version: e.g. `img__apple__style_v1.png`
- Caching/manifests:
  - `cache/audio_manifest.json` and `cache/image_manifest.json` record inputs/params and output filenames/hashes.
  - If an entry exists and the file is present, skip regeneration.
- Avoid randomness:
  - No random example selection; choose deterministic “front example” explicitly in curriculum.

---

### Implementation Plan (Atomic Commits)

'''

## Implementation Workflow

When implementing a spec:

1. **Start implementation** - Begin with Commit 1 (do NOT implement this spec as one monolithic commit)
2. **Complexity check** - If a commit feels too complex:
   - STOP implementation
   - Break down into smaller atomic commits
   - Update the spec with new commits
   - Commit the spec update
   - Continue implementation
3. **Complete commit** - After each atomic commit:
   - Run relevant tests
   - Commit with conventional message
   - Update spec: `☐` → `☑ (abc1234)`
   - Commit spec update
4. **Repeat** until all commits complete
   '''

#### Phase 1: Foundation + Determinism (P0)

**Commit 1: scaffold project directory + docs (45m)** ☑ (d75be75)
```
docs(anki): add phonics anki project scaffold

- Add `peters-workspace/phonetics-anki/` README + minimal run instructions
- Add placeholder `curriculum.json` schema stub
Files:
- peters-workspace/phonetics-anki/README.md (NEW)
- peters-workspace/phonetics-anki/curriculum.json (NEW)
```

**Commit 2: curriculum validation + normalization layer (1–2h)** ☐
```
feat(anki): add curriculum loader and validator

- Implement `load_curriculum()` with schema checks and good error messages
- Normalize fields (e.g., ensure every item has `id`, `type`, examples list)
Files:
- peters-workspace/phonetics-anki/scripts/curriculum.py (NEW)
```

**Commit 3: deterministic ID + GUID strategy (1h)** ☐
```
feat(anki): add deterministic ids for models and notes

- Define stable constants for `deck_id`/`model_id`s
- Implement `note_guid(model_namespace, item_id)` deterministically
Files:
- peters-workspace/phonetics-anki/scripts/ids.py (NEW)
```

**Commit 4: genanki deck builder (sound + pattern notes only) (2h)** ☐
```
feat(anki): generate apkg for sound/pattern subdecks

- Create `SoundNote` and `PatternNote` models
- Generate notes into `Phonics::1. Sounds (Core)` and `Phonics::2. Spellings (Graphemes)`
- Output `output/phonics_deck.apkg`
Files:
- peters-workspace/phonetics-anki/scripts/create_anki_deck.py (NEW)
- peters-workspace/phonetics-anki/output/.gitkeep (NEW)
```

#### Phase 2: Alphabet decks (P0/P1)

**Commit 5: LetterCaseNote + VisualConfusableNote (1–2h)** ☐
```
feat(anki): add alphabet case + confusables subdecks

- Add `Alphabet::1. Uppercase + Lowercase` notes from `alphabet.letters`
- Add `Advanced::Visual Discrimination (Letters)` notes from `alphabet.confusables`
Files:
- peters-workspace/phonetics-anki/scripts/create_anki_deck.py (update)
```

**Commit 6: AlphabetOrderNote generator (“what comes next?”) (1–2h)** ☐
```
feat(anki): add alphabet order subdeck

- Generate `Alphabet::2. Order (What Comes Next?)` notes algorithmically from `alphabet.letters`
- Configurable window size (default 4→next)
Files:
- peters-workspace/phonetics-anki/scripts/alphabet_order.py (NEW)
- peters-workspace/phonetics-anki/scripts/create_anki_deck.py (update)
```

#### Phase 3: Minimal pairs (advanced) (P1)

**Commit 7: MinimalPairNote model + AB discrimination cards (2h)** ☐
```
feat(anki): add minimal pairs note type matching proven pattern

- Implement `MinimalPairNote` fields (Word 1/2, Recording 1/2, optional Word 3)
- Generate multiple cards per note (AB + optional third distractor)
- Place in `Advanced::Minimal Pairs (Sound)`
Files:
- peters-workspace/phonetics-anki/scripts/minimal_pairs.py (NEW)
- peters-workspace/phonetics-anki/scripts/create_anki_deck.py (update)
```

#### Phase 4: Media pipeline (optional integrations) (P2)

**Commit 8: media manifest + local media resolution (1–2h)** ☐
```
feat(anki): add media resolution and caching manifests

- Add a manifest format for generated/known media
- Generator links existing local media without crashing if absent
Files:
- peters-workspace/phonetics-anki/scripts/media.py (NEW)
- peters-workspace/phonetics-anki/cache/.gitkeep (NEW)
```

**Commit 9: Google Cloud TTS batch generator (2h)** ☐
```
feat(anki): generate word audio via google cloud tts

- Generate audio for example words (and optionally letter names)
- Cache outputs in manifest; skip unchanged
Files:
- peters-workspace/phonetics-anki/scripts/generate_audio.py (NEW)
```

**Commit 10: optional image generator integration (2h)** ☐
```
feat(anki): add optional image generation pipeline

- Implement prompt templating and manifest caching
- Keep it optional (deck generation works without it)
Files:
- peters-workspace/phonetics-anki/scripts/generate_images.py (NEW)
```

#### Phase 5: Tests + docs + polish (P0/P1)

**Commit 11: deterministic regeneration smoke test (1–2h)** ☐
```
test(anki): add determinism and schema smoke tests

- Assert GUID stability for a fixed sample curriculum
- Assert deck generation succeeds without media
Files:
- peters-workspace/phonetics-anki/tests/test_determinism.py (NEW)
- peters-workspace/phonetics-anki/tests/test_curriculum_validation.py (NEW)
```

**Commit 12: runbook + “how to iterate safely” docs (45m)** ☐
```
docs(anki): add workflow for regenerating without duplicates

- Document how to update curriculum and re-import
- Document recommended Anki import settings (update existing notes)
Files:
- peters-workspace/phonetics-anki/README.md (update)
```

Commit Summary:
| Phase | Commits | Estimated Time |
|-------|---------|----------------|
| Phase 1 | 1–4 | 5–7h |
| Phase 2 | 5–6 | 3–4h |
| Phase 3 | 7 | 2h |
| Phase 4 | 8–10 | 5–6h |
| Phase 5 | 11–12 | 2–3h |
| **Total** | **12 commits** | **17–22h** |

---

### Priority Ordering (for large specs)
| Priority | Work Item | Effort | Value | Stop Here If... |
|----------|-----------|--------|-------|-----------------|
| P0 | Generate `.apkg` deterministically from curriculum + alphabet | 1–2 days | Highest | You can import and iterate without duplicates |
| P1 | Minimal pairs + better templates | 0.5–1 day | High | You want auditory discrimination training |
| P2 | TTS + image generation | 1–2 days | Medium | You prefer manual/recorded media initially |
| P3 | Style polish + JS highlighting | 0.5 day | Low | AnkiMobile quirks or time constraints |

“Good enough” checkpoint: after Phase 2 (alphabet decks + deterministic `.apkg`), even without TTS/images.

---

### Test Strategy (Comprehensive Coverage)

| Category | Test Cases | Input → Expected Output |
|----------|------------|------------------------|
| **Happy Path** | Generate deck from minimal sample curriculum | Valid `curriculum.json` → `.apkg` created |
| **Error Path** | Missing `id`, unknown `type`, malformed examples | Invalid JSON → validation error with path to field |
| **Edge Cases** | Missing media files, empty examples list | Deck generation succeeds; warnings logged; import works |
| **Regression** | Deterministic GUIDs stable across runs | Same curriculum → identical GUIDs and stable deck/model IDs |

Suggested test location: `peters-workspace/phonetics-anki/tests/`.

---

### Acceptance Criteria (AC1, AC2...)
- AC1: Running the generator produces `peters-workspace/phonetics-anki/output/phonics_deck.apkg`.
- AC2: The `.apkg` imports into Anki without errors.
- AC3: Re-running the generator and importing again does not create duplicate notes (verified by stable GUIDs and “update existing notes” import behavior).
- AC4: Subdecks exist and contain notes:
  - `Phonics::1. Sounds (Core)`
  - `Alphabet::1. Uppercase + Lowercase`
  - `Alphabet::2. Order (What Comes Next?)`
  - `Advanced::Visual Discrimination (Letters)`
- AC5: Minimal pairs model supports AB discrimination with audio fields and generates 2+ cards per note when configured.

CLI verification commands (examples):
- `ls -la peters-workspace/phonetics-anki/output`
- `python peters-workspace/phonetics-anki/scripts/create_anki_deck.py --dry-run`

---

### Definition of Done
- Code Complete: all planned commits merged; generator runs end-to-end.
- Tests Complete: determinism + validation tests pass.
- Documentation Complete: README includes setup + regeneration workflow.
- Verification Complete: imports into Anki on at least one device and basic card preview works.
- Cleanup Complete: no hardcoded secrets, no stray temp artifacts.

---

### Operational Readiness
- Setup:
  - Install dependencies for generator environment (to be defined in README).
  - Provide credentials via environment variables for optional TTS/images.
- Runbook:
  - Update `curriculum.json`
  - Run generator
  - Import `.apkg` into Anki using “update existing notes” behavior

---

### Risks & Mitigations
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Duplicate notes on re-import | Medium | High | Stable IDs + deterministic GUIDs; document import settings |
| TTS pronunciation mismatch | Medium | Medium | Prefer word audio; allow manual recordings; keep dialect consistent |
| Anki template quirks across platforms | Medium | Medium | Keep templates simple; avoid heavy JS; test on iOS if possible |
| Toddler frustration | Medium | High | Separate subdecks; tune new-card limits; keep minimal pairs optional |

---

### Rollback Strategy (for foundation specs)
- Quick disable: don’t import the regenerated `.apkg`; or suspend subdecks in Anki.
- Full revert: regenerate from last known-good curriculum + assets and re-import.

---

### Critical Mistakes to Avoid
- Generating notes without stable GUIDs (will create duplicates on every import).
- Treating “letters” as phonemes in the core phonics curriculum (confusing mappings like `c`).
- Making media generation required for deck generation (slows iteration; increases failure modes).
- Mixing dialect/voice profiles within one deck without intentional versioning (confusing pronunciation).

---

### Cross-References
- `peters-workspace/phonetics-anki/PHONETICS_ANKI_SPEC.md` — curriculum/product direction and subdeck definitions.

---

Top 3 actions to start now:
1. Create a minimal `curriculum.json` with 3–5 sound items + the full alphabet list (A–Z with upper/lower).
2. Implement deterministic `deck_id`/`model_id` + note GUID derivation (the import non-duplication foundation).
3. Build the `.apkg` generator for the core subdecks first (no media dependencies), then iterate.
