# Phonics & Phonemic Awareness Anki Deck - Project Specification

**Project:** Open-source early literacy deck generator for personal use (age ~2.5+)
**Status:** Draft
**Last Updated:** 2025-12-30

> Note: This project was originally scoped as “phonetics”, but the actual goal is **phonics + phonemic awareness**
> (sound ↔ spelling patterns, and auditory discrimination). This spec uses that terminology throughout.

---

## 1. Overview

Build a **phonics / phonemic awareness Anki deck generator** that:
- Starts with manually-curated curriculum data (phonemes, graphemes, spelling patterns, minimal pairs)
- Auto-generates audio assets via TTS API
- Auto-generates image assets via image generation (optional; can be replaced with curated images)
- Creates Anki cards programmatically using `genanki`
- Outputs an `.apkg` file ready to import and sync across devices

**Core insight:** Leverage Anki's spaced repetition + existing sync infrastructure instead of rebuilding a custom app.

### Target Dialect / Accent

Pick one target accent to avoid “correct but confusing” variants.

- **Default:** General American (GA)
- **If you want another dialect later:** treat it as a new voice/profile and regenerate assets deterministically (don’t mix within one deck).

---

## 2. Goals

### Primary
- [ ] Create a clear curriculum (sounds + common spellings + patterns)
- [ ] Automate asset generation (audio + images)
- [ ] Generate Anki deck that syncs across devices (iPhone, iPad, Mac)
- [ ] Parent-friendly iteration: regenerate without duplicates, without losing scheduling

### Secondary
- [ ] Reusable script—others can fork and customize for different languages
- [ ] Explore existing Anki phonetics decks for curriculum inspiration
- [ ] Document asset generation process so it's reproducible

---

## 3. Curriculum (MVP Scope)

### Definitions (quick)

- **Phoneme:** a contrastive speech sound (e.g., /p/ vs /b/, /θ/ vs /ð/).
- **Grapheme:** a written unit that represents a sound (e.g., `sh`, `th`, `ck`, `igh`).
- **Phonics:** mapping between sounds and spellings (graphemes).
- **Phonemic awareness:** ability to hear/manipulate sounds (blending, segmenting, discrimination).
- **Minimal pair:** two items that differ by one sound feature (e.g., *thin* /θɪn/ vs *then* /ðɛn/).

### Design choice: what is a “card”?

This deck supports two related card families:

1. **Sound cards (phoneme-first):** “Hear a sound → pick/recognize examples.”
2. **Spelling-pattern cards (grapheme-first):** “See `sh` → hear /ʃ/ → see examples.”

For toddlers, “sound cards” tend to be the best starting point; spelling-pattern cards can be phased in later.

### Deck / Subdeck Layout

Keep “skills” separated into subdecks so you can enable/disable without deleting content.

Suggested structure (Anki uses `::` as the deck hierarchy separator):

- `Phonics::1. Sounds (Core)`
- `Phonics::2. Spellings (Graphemes)`
- `Phonics::3. Patterns (Chunks/Rimes)`
- `Advanced::Minimal Pairs (Sound)`
- `Advanced::Visual Discrimination (Letters)`
- `Alphabet::1. Uppercase + Lowercase`
- `Alphabet::2. Order (What Comes Next?)`

The “Alphabet” decks are intentionally separate from “Phonics”: letter-name and letter-order practice is useful,
but it’s a different learning objective than sound/spelling mapping.

### Phase 1 (MVP): Core Sounds (phonemes)

**Count target:** ~25–35 notes (enough coverage, still toddler-manageable)

Important change vs the original draft: we do **not** treat letters like `c` or `y` as “sounds”.
Instead we teach **phonemes**, and later teach common spellings for those phonemes.

Example (illustrative, not final):

| Phoneme | Example Words | Notes |
|---|---|---|
| /æ/ | apple, ant, alligator | “short a” |
| /b/ | ball, bat, boy |  |
| /k/ | cat, kite, cup | later: `c`, `k`, `ck` spellings |
| /s/ | sun, sock, seal | later: `s`, `c` (as in *city*) |

**Vowels (GA, short forms):** /æ/ /ɛ/ /ɪ/ /ɑ/ /ʌ/ (toddler labels: short a/e/i/o/u)

**Consonants:** choose a practical starter set (stops, nasals, common fricatives), then expand.
Avoid “rare” early items if they add confusion (e.g., /ʒ/).

### Phase 2: Common Spellings (digraphs and frequent grapheme patterns)

This phase teaches **grapheme → phoneme** mappings. Some introduce “new” phonemes for kids (/ʃ/),
others are “alternate spellings” of already-known phonemes (`ph` → /f/).

**Count target:** ~15–25 notes

| Grapheme | Phoneme | Example Words | Notes |
|---|---|---|---|
| `sh` | /ʃ/ | ship, shell, shy |  |
| `ch` | /tʃ/ | chat, chair, child |  |
| `th` | /θ/ | thin, think, thumb | voiceless “th” |
| `th` | /ð/ | the, this, that | voiced “th” |
| `ng` | /ŋ/ | ring, sing, wing |  |
| `ck` | /k/ | duck, sock, back | alternate spelling of /k/ |
| `qu` | /kw/ | queen, quit, quick | consonant cluster (treat as pattern) |
| `wh` | /w/ | what, when, whale | GA default /w/ (optional /hw/ subdeck) |
| `ph` | /f/ | phone, photo, dolphin | alternate spelling of /f/ |

Also include vowel patterns only when you’re ready (they balloon scope quickly): `ee` /i/, `ai` /eɪ/, `oa` /oʊ/, etc.

### Phase 3: Rimes / Larger Patterns (trigraphs and common chunks)

These aren’t “pure phonemes” so much as helpful spelling chunks (great for blending later).

**Count target:** ~10–20 notes

| Pattern | Sound (approx) | Examples | Notes |
|---|---|---|---|
| `igh` | /aɪ/ | light, night, fight | long i |
| `ing` | /ɪŋ/ | ring, sing, thing | chunk; overlaps with /ŋ/ |
| `tion` | /ʃən/ | station, motion, lotion | optional/later |

### Phase 4 (Advanced): Minimal Pairs (isolated subdeck)

Minimal pairs are powerful but can be frustrating if introduced too early. Put them in a separate subdeck so
they can be enabled only when the learner is ready.

Two flavors:

1. **Phonetic minimal pairs (sound contrasts):** /θ/ vs /ð/, /p/ vs /b/, /s/ vs /ʃ/, etc.
2. **Orthographic / visual minimal pairs (letter-shape discrimination):** `b` vs `d`, `p` vs `q`, `O` vs `Q`, etc.

For a toddler, the “visual discrimination” deck is a different cognitive skill than phoneme discrimination,
so it should be explicitly labeled and separated.

### Alphabet Track (optional, but recommended)

This is “bonus practice” that can run in parallel with phonics:

1. **Uppercase/lowercase association:** recognize that `A` and `a` are the “same letter”.
2. **Visual confusables:** extra reps on shapes that are easy to confuse (`O` vs `Q`, `b` vs `d`, etc.).
3. **Alphabet order memorization (“what comes next?”):** build the internal sequence A→B→C… (useful later for indexing,
   spelling, and basic school routines).

These should be separate subdecks so you can dial intensity up/down depending on attention and frustration level.

---

## 4. Asset Generation Strategy

### 4.1 Audio Assets

**Source:** Google Cloud Text-to-Speech API

**Recommendation:** prioritize **example word audio** first. Isolated-phoneme audio is much trickier for TTS.

**Approach:**
1. Generate audio for each example word (high reliability)
2. Optionally generate a “sound” clip using SSML phoneme features (if supported and validated)
3. Optional: parent recordings for encouragement (recorded audio will always beat TTS for warmth)

**Batch script:**
```python
# Pseudocode
for phoneme in curriculum:
    # Prefer word audio first; sound audio may be optional.
    for word in phoneme['example_words']:
        audio_word = tts_api(word)
    save_audio_files(phoneme['id'])
```

**Audio hygiene (important):**
- Normalize loudness to a consistent target, trim leading/trailing silence.
- Choose one voice + speaking rate for the whole deck (per dialect).
- Deterministic filenames (so re-runs overwrite the same media instead of duplicating it).

### 4.2 Image Assets

**Source:** image generation (e.g., DALL-E 3) or curated image set
**Approach:**
1. Generate one illustration per example word
2. Write prompts with a stable “style block” for consistency (“simple, high-contrast, kid-friendly, no text”)
3. Batch generate 60-80 images

**Batch workflow:**
```python
# Pseudocode
for phoneme in curriculum:
    for word in phoneme['example_words']:
        prompt = generate_prompt(word, age=2.5, style="v1")
        image = image_api(prompt)
        save_image(f"{word}.png")
```

**Image hygiene (important):**
- Avoid text in images (“no letters, no words”) to keep focus on the concept.
- Use consistent aspect ratio and size so cards don’t jump visually.
- Cache by `(word, prompt_version, model)` to avoid re-paying for unchanged prompts.

### 4.3 Video Assets (Optional, Phase 2)

**For now:** Skip. Audio + static images sufficient for MVP.
**Later if desired:** Simple Canvas animations or Blender-generated letter formation videos.

---

## 5. Data Structure

### 5.1 Source of Truth: JSON (recommended) + optional CSV export

Use JSON as SSOT because lists and nested structures matter (multiple graphemes, multiple examples, per-example prompts).
CSV can still be a convenient editing surface, but it’s best treated as an export/import format.

**File:** `curriculum.json` (SSOT), optional `curriculum.csv` (view/edit)

**CSV Format (example):**
```csv
item_id,item_type,ipa,graphemes,front_example,example_words,notes
sound_ae,sound,/æ/,"a",apple,"apple,ant,alligator",short 'a' sound
pattern_sh,pattern,/ʃ/,"sh",ship,"ship,shell,shy",digraph pattern
pattern_th_voiceless,pattern,/θ/,"th",thin,"thin,think,thumb",voiceless th
pattern_th_voiced,pattern,/ð/,"th",the,"the,this,that",voiced th
```

**JSON Format (example):**
```json
{
  "meta": {
    "dialect": "General American",
    "version": "v1",
    "default_voice": {
      "provider": "google-cloud-tts",
      "voice_name": "TBD",
      "speaking_rate": 0.95,
      "pitch": 0
    }
  },
  "alphabet": {
    "include_alphabet_decks": true,
    "letters": [
      { "id": "letter_a", "upper": "A", "lower": "a", "name": "A", "order": 1 },
      { "id": "letter_b", "upper": "B", "lower": "b", "name": "B", "order": 2 }
    ],
    "confusables": [
      { "id": "confusable_o_q", "type": "visual_pair", "left": "O", "right": "Q", "notes": "round vs tail" },
      { "id": "confusable_b_d", "type": "visual_pair", "left": "b", "right": "d", "notes": "mirror" }
    ]
  },
  "items": [
    {
      "id": "sound_ae",
      "type": "sound",
      "ipa": "/æ/",
      "sound_label": "short a",
      "graphemes": ["a"],
      "examples": [
        { "word": "apple" },
        { "word": "ant" },
        { "word": "alligator" }
      ],
      "notes": "short 'a' sound"
    },
    {
      "id": "pattern_th_voiceless",
      "type": "pattern",
      "ipa": "/θ/",
      "graphemes": ["th"],
      "examples": [
        { "word": "thin" },
        { "word": "think" },
        { "word": "thumb" }
      ],
      "notes": "voiceless th"
    },
    {
      "id": "minpair_s_vs_sh_sip_ship",
      "type": "minimal_pair_sound",
      "contrast_id": "s_vs_sh",
      "left": { "word": "sip", "ipa": "/sɪp/" },
      "right": { "word": "ship", "ipa": "/ʃɪp/" },
      "notes": "imageable, great early contrast"
    }
  ]
}
```

**Benefits:**
- Version-controllable
- Human-readable
- Script reads it to generate everything

---

## 6. Anki Card Structure

### 6.1 Models / Note Types

Use separate note types (models) to keep templates simple:

1. **SoundNote** (phoneme-first)
2. **PatternNote** (grapheme-first)
3. **MinimalPairNote** (advanced, separate subdeck; sound discrimination)
4. **LetterCaseNote** (alphabet: uppercase/lowercase association)
5. **VisualConfusableNote** (alphabet: orthographic minimal pairs / confusables)
6. **AlphabetOrderNote** (alphabet: “what comes next?” sequencing)

### 6.2 Minimal Pair Design (based on your existing successful decks)

You already have minimal-pairs decks across multiple foreign languages that implement a very effective pattern:

- Prompt: “Do you hear ___ or ___?”
- Play one recording
- Reveal the correct choice on the back
- Optionally include a 3rd distractor and extra discrimination cards

For this project, reuse that proven design so the English minimal-pairs subdeck behaves similarly.

**Recommended `MinimalPairNote` fields (2-way + optional 3rd distractor):**

- `Sort Field` (optional; used to control card ordering)
- `Word 1`, `Recording 1`, `Word 1 IPA`, `Word 1 English/Picture`
- `Word 2`, `Recording 2`, `Word 2 IPA`, `Word 2 English/Picture`
- Optional: `Word 3`, `Recording 3`, `Word 3 IPA`, `Word 3 English/Picture`
- Optional: `Compare Word 2 to Word 3?` (simple switch to enable extra cards)

**Recommended cards generated from one note (mirrors your deck behavior):**

- Card 1: play `Recording 1`, show `Word 1` vs `Word 2` options, answer reveals `Word 1`
- Card 2: play `Recording 2`, show `Word 1` vs `Word 2` options, answer reveals `Word 2`
- Optional if `Word 3` present:
  - Card 3: play `Recording 3`, show `Word 1` vs `Word 3`, answer reveals `Word 3`
  - Card 4: play `Recording 1`, show `Word 1` vs `Word 3`, answer reveals `Word 1`
  - Optional “compare 2 vs 3” if the flag is enabled:
    - Card 5: play `Recording 2`, show `Word 2` vs `Word 3`, answer reveals `Word 2`
    - Card 6: play `Recording 3`, show `Word 2` vs `Word 3`, answer reveals `Word 3`

For toddler use, you can keep written words minimal (or even hide the text on the front and rely on pictures),
but keep the *structure* identical.

### 6.3 Core Card Template (Sound/Pattern Notes)

**Front:**
```
[SOUND BUTTON: Play /æ/ sound]

[IMAGE: apple illustration]

Example: apple
```

**Back:**
```
Sound: /æ/ (short 'a')
Orthography: 'a'

Examples:
- apple
- ant
- alligator

[AUDIO: all three words pronounced]
```

**Anki Features:**
- Audio auto-plays on card reveal (optional, configurable)
- Images embedded inline
- Clickable sound buttons
- Spaced repetition algorithm handles when kid sees each card

### 6.4 Alphabet Card Types (Upper/Lower, Confusables, Order)

These decks are “letter knowledge”, not phonics. Keep them separate and simple.

**LetterCaseNote (uppercase/lowercase association):**

- Fields: `Upper`, `Lower`, optional `Letter Name Audio`, optional `Keyword Image` (e.g., “A is for apple” image)
- Cards:
  - “What’s the lowercase of `A`?”
  - “What’s the uppercase of `a`?”

**VisualConfusableNote (orthographic minimal pairs / confusables):**

- Fields: `Left`, `Right`, optional `Notes`, optional `Hint` (e.g., “Q has a tail”)
- Cards:
  - “Which one is `Q`?” (show both, answer highlights correct)
  - “Which one is `O`?” (reverse)

**AlphabetOrderNote (“what comes next?”):**

Two reasonable implementations:

1. Store notes explicitly (one note per prompt), or
2. Generate notes algorithmically from the alphabet list.

For simplicity and correctness, generate algorithmically from `alphabet.letters`:

- Example front: `A  B  C  D  __`
- Answer: `E`
- Optional reverse: “What comes before `E`?” (later)

This reproduces the kind of alphabet-order memorization practice you described using in your own language study.

### 6.5 Regeneration Without Duplicates (critical)

To support “parent-friendly iteration”, the generator must be deterministic:

- Stable `deck_id` and `model_id` (constants in code)
- Stable note GUID per item:
  - `SoundNote` GUID derived from `item.id`
  - `PatternNote` GUID derived from `item.id`
  - `MinimalPairNote` GUID derived from `item.id` (or `(contrast_id, left_word, right_word)` if you don’t store ids)
  - `LetterCaseNote` GUID derived from `letter.id`
  - `VisualConfusableNote` GUID derived from `confusable.id`
  - `AlphabetOrderNote` GUID derived from `(order_index, window_size, direction)` or similar

This allows you to re-import an updated `.apkg` without creating duplicate notes.

---

## 7. Technical Architecture

### 7.1 Tech Stack

| Component | Technology |
|-----------|-----------|
| **Curriculum Definition** | JSON (SSOT) + optional CSV |
| **Asset Generation** | Python 3.12+ |
| **TTS API** | Google Cloud Text-to-Speech |
| **Image Generation** | Optional (e.g., DALL-E 3); or curated images |
| **Anki Card Generation** | `genanki` Python library |
| **Version Control** | Git (this repo) |
| **Output** | `.apkg` Anki deck file |

### 7.2 Directory Structure

```
peters-workspace/
└── phonetics-anki/
    ├── PHONETICS_ANKI_SPEC.md          (this file)
    ├── PHONICS_ANKI_IMPLEMENTATION_SPEC.md
    ├── curriculum.json                 (source of truth)
    ├── curriculum.csv                  (optional export/edit surface)
    ├── scripts/
    │   ├── generate_audio.py           (TTS API calls)
    │   ├── generate_images.py          (optional image generation batch)
    │   ├── create_anki_deck.py         (genanki card creation)
    │   └── pipeline.py                 (orchestrates all steps)
    ├── assets/
    │   ├── audio/
    │   │   ├── sounds/                 (individual phoneme sounds)
    │   │   └── words/                  (word pronunciations)
    │   └── images/
    │       └── *.png                   (object illustrations)
    ├── cache/
    │   ├── audio_manifest.json          (what was generated, params, hashes)
    │   └── image_manifest.json          (what was generated, params, hashes)
    ├── output/
    │   └── phonics_deck.apkg           (generated Anki deck)
    └── README.md                       (how to use the scripts)
```

Note: keep `.apkg` generation idempotent; cache manifests prevent re-paying APIs on re-run.

---

## 8. Implementation Plan

### Phase 1: MVP Foundation (Priority 1)
- [ ] Define `curriculum.json` (Phase 1 sound items only)
- [ ] Define `alphabet.letters` and enable `Alphabet::*` subdecks (optional early win)
- [ ] Write `generate_audio.py` (TTS API integration)
- [ ] Write `generate_images.py` (optional image batch generation)
- [ ] Write `create_anki_deck.py` (genanki card generation)
- [ ] Implement deterministic deck/model IDs + note GUIDs
- [ ] Test with 5 items end-to-end (import twice, verify no duplicates)
- [ ] Generate full deck for all 25 base phonemes

**Effort:** ~20-40 hours (depends on asset generation + iteration)

### Phase 2: Polish & Iteration (Priority 2)
- [ ] Add Phase 2 grapheme patterns (`sh`, `ch`, `th` voiced/voiceless, etc.)
- [ ] Refine audio quality (volume, speed, pronunciation)
- [ ] Refine image quality (style consistency, clarity)
- [ ] Add parent voice recordings for encouragement
- [ ] Test on actual devices (AnkiDroid, iOS, Mac)

**Effort:** ~20-30 hours

### Phase 3: Rimes & Scaling (Priority 3)
- [ ] Add Phase 3 rime/pattern items (`igh`, `ing`, etc.)
- [ ] Document asset generation process
- [ ] Make scripts reusable for other languages

**Effort:** ~10-15 hours

### Phase 4: Minimal Pairs (Priority 4, advanced)
- [ ] Define minimal-pairs subdeck and note model
- [ ] Add phonetic minimal pairs (/θ/ vs /ð/, /p/ vs /b/, etc.)
- [ ] Add optional visual-discrimination “orthographic confusables” deck (`b/d/p/q`, `O/Q`, etc.)
- [ ] Add `Alphabet::2. Order (What Comes Next?)` generator cards

---

## 9. Success Criteria

### Functional
- [ ] Script auto-generates all assets (no manual image editing)
- [ ] Anki deck imports without errors
- [ ] Cards display audio + images correctly
- [ ] Deck syncs across 3+ devices (phone, tablet, computer)
- [ ] Re-importing a regenerated `.apkg` does not duplicate notes

### Content
- [ ] All Phase 1 phonemes covered (with toddler-friendly labels)
- [ ] Each phoneme has 3-5 example words
- [ ] Audio quality acceptable for 2.5yo
- [ ] Images clearly illustrate concepts
- [ ] Alphabet subdecks work (upper/lower, confusables, order) without frustration

### Operational
- [ ] Script is repeatable (can regenerate deck anytime)
- [ ] Curriculum data is editable (JSON SSOT, optional CSV)
- [ ] Asset generation cost < $30 total

---

## 10. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| TTS pronunciation quality | Low—kids learn from it | Test voice settings; use fast/clear preset |
| Isolated phoneme TTS unreliable | Medium—can teach wrong sound | Prefer word audio; validate SSML phoneme; allow recorded audio |
| Image quality inconsistent | Medium—affects learning | Stable style prompt; regenerate; allow curated images |
| Anki card syntax errors | High—deck won't import | Test genanki with 1 card first |
| API rate limits | Medium—slow generation | Implement batch queueing; cache results |
| Audio file size bloat | Medium—slower syncing | Compress MP3; use low-bitrate settings |
| Duplicate notes on re-import | High—deck becomes unusable | Deterministic IDs + stable GUIDs |

---

## 11. Open Questions

1. **Sequencing:** follow a known order (OG/Montessori) vs frequency-based vs “what kid is seeing in books”?
2. **Audio profile:** which voice, speaking rate, and whether to include a “pause then repeat” pattern for clarity?
3. **Images:** consistent cartoon style vs photos vs curated icons?
4. **Minimal pairs:** when to introduce phoneme discrimination vs visual discrimination?
5. **Alphabet order:** do we want strict A→Z memorization early, or treat it as “nice to have” with light daily exposure?

---

## 12. Next Steps

1. **Finalize Phase 1 sound list** (phonemes + example words + toddler labels)
2. **Choose dialect + voice profile** (General American baseline)
3. **Write script scaffold** (`pipeline.py` + deterministic IDs)
4. **Test with 3–5 items end-to-end** (import twice; verify no duplicates)
5. **Iterate on asset quality**
6. **Generate full MVP deck**
7. **Test on actual devices**

---

## Appendix: References

### Mentava Insights (For Inspiration)
- Uses 44 sounds (English language)
- Includes digraphs (sh, ch, th, ph, ng, etc.)
- Teaches blending after sound recognition
- Emphasizes consistency + daily practice

### Anki Documentation
- [genanki GitHub](https://github.com/kerrickstaley/genanki)
- [Anki Card Template Syntax](https://docs.ankiweb.net/templates/fields.html)
- [Anki Media Files](https://docs.ankiweb.net/media.html)

### Phonetics Resources
- IPA (International Phonetic Alphabet) for consistent notation
- Common digraphs in English
- Common trigraphs in English

---

**Document Status:** Ready for review and curriculum finalization.
