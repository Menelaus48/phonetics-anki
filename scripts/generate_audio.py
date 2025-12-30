#!/usr/bin/env python3
"""
Google Cloud TTS audio generator for the Phonics Anki deck.

Generates audio for example words (and optionally letter names) using
Google Cloud Text-to-Speech API. Uses manifest caching to skip
regeneration of unchanged content.

Usage:
    python scripts/generate_audio.py [curriculum.json]

Environment variables:
    GOOGLE_APPLICATION_CREDENTIALS: Path to service account JSON file
    (or use default application credentials)

Requires:
    pip install google-cloud-texttospeech
"""

import os
import sys
from pathlib import Path
from typing import Any

from curriculum import load_curriculum, CurriculumError
from media import MediaManifest, generate_audio_filename, compute_file_hash

# Optional import - allows running without google-cloud-texttospeech installed
try:
    from google.cloud import texttospeech
    HAS_TTS = True
except ImportError:
    HAS_TTS = False
    texttospeech = None


# Default voice settings for General American
DEFAULT_VOICE_CONFIG = {
    "language_code": "en-US",
    "name": "en-US-Neural2-D",  # Male neural voice
    "ssml_gender": "MALE",
}

DEFAULT_AUDIO_CONFIG = {
    "audio_encoding": "MP3",
    "speaking_rate": 0.95,  # Slightly slower for toddlers
    "pitch": 0.0,
}


def get_tts_client() -> Any:
    """
    Get a Text-to-Speech client.

    Returns:
        The TTS client, or None if not available.
    """
    if not HAS_TTS:
        return None

    try:
        return texttospeech.TextToSpeechClient()
    except Exception as e:
        print(f"Warning: Could not create TTS client: {e}")
        return None


def synthesize_speech(
    client: Any,
    text: str,
    output_path: Path,
    voice_config: dict | None = None,
    audio_config: dict | None = None,
) -> bool:
    """
    Synthesize speech for a text string.

    Args:
        client: The TTS client.
        text: The text to synthesize.
        output_path: Where to save the audio file.
        voice_config: Voice configuration (language, name, gender).
        audio_config: Audio configuration (encoding, rate, pitch).

    Returns:
        True if successful, False otherwise.
    """
    if client is None:
        return False

    voice_config = voice_config or DEFAULT_VOICE_CONFIG
    audio_config = audio_config or DEFAULT_AUDIO_CONFIG

    try:
        synthesis_input = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(
            language_code=voice_config["language_code"],
            name=voice_config.get("name"),
            ssml_gender=getattr(
                texttospeech.SsmlVoiceGender,
                voice_config.get("ssml_gender", "NEUTRAL"),
            ),
        )

        audio = texttospeech.AudioConfig(
            audio_encoding=getattr(
                texttospeech.AudioEncoding,
                audio_config.get("audio_encoding", "MP3"),
            ),
            speaking_rate=audio_config.get("speaking_rate", 1.0),
            pitch=audio_config.get("pitch", 0.0),
        )

        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio,
        )

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write the audio file
        with open(output_path, "wb") as f:
            f.write(response.audio_content)

        return True

    except Exception as e:
        print(f"Error synthesizing '{text}': {e}")
        return False


def collect_words_to_generate(curriculum: dict) -> list[dict]:
    """
    Collect all words that need audio generation.

    Args:
        curriculum: The loaded curriculum data.

    Returns:
        List of dicts with 'item_id', 'word', and 'context' fields.
    """
    words = []

    # Collect example words from sound and pattern items
    for item in curriculum.get("items", []):
        item_type = item.get("type", "")
        item_id = item.get("id", "")

        if item_type in ("sound", "pattern"):
            for example in item.get("examples", []):
                word = example.get("word", "")
                if word:
                    words.append({
                        "item_id": item_id,
                        "word": word,
                        "context": f"{item_type}:{item_id}",
                    })

        elif item_type == "minimal_pair_sound":
            # Collect words from minimal pairs
            for side in ("left", "right", "third"):
                side_data = item.get(side, {})
                word = side_data.get("word", "")
                if word:
                    words.append({
                        "item_id": item_id,
                        "word": word,
                        "context": f"minpair:{item_id}:{side}",
                    })

    return words


def generate_audio_batch(
    curriculum: dict,
    output_dir: Path,
    manifest: MediaManifest,
    voice_config: dict | None = None,
    audio_config: dict | None = None,
    dry_run: bool = False,
) -> tuple[int, int, int]:
    """
    Generate audio for all words in the curriculum.

    Args:
        curriculum: The loaded curriculum data.
        output_dir: Directory to save audio files.
        manifest: The audio manifest for caching.
        voice_config: Voice configuration.
        audio_config: Audio configuration.
        dry_run: If True, don't actually generate, just report what would be done.

    Returns:
        Tuple of (generated, skipped, failed) counts.
    """
    voice_config = voice_config or DEFAULT_VOICE_CONFIG
    audio_config = audio_config or DEFAULT_AUDIO_CONFIG

    words = collect_words_to_generate(curriculum)
    print(f"Found {len(words)} words to process")

    # Build params for cache comparison
    params_template = {
        "voice": voice_config,
        "audio": audio_config,
    }

    generated = 0
    skipped = 0
    failed = 0

    client = None if dry_run else get_tts_client()

    for word_info in words:
        item_id = word_info["item_id"]
        word = word_info["word"]
        context = word_info["context"]

        # Generate filename
        filename = generate_audio_filename(
            item_id,
            word,
            voice_config.get("name", "default"),
            audio_config.get("speaking_rate", 1.0),
        )
        output_path = output_dir / filename

        # Check if regeneration needed
        manifest_key = f"{item_id}:{word}"
        params = {**params_template, "word": word}

        if not manifest.needs_regeneration(manifest_key, params, output_dir):
            skipped += 1
            continue

        if dry_run:
            print(f"  Would generate: {filename} ({context})")
            generated += 1
            continue

        print(f"  Generating: {filename} ({context})")

        if client is None:
            print("    Skipped (no TTS client)")
            failed += 1
            continue

        if synthesize_speech(client, word, output_path, voice_config, audio_config):
            # Update manifest
            content_hash = compute_file_hash(output_path)
            manifest.set_entry(manifest_key, filename, params, content_hash)
            generated += 1
        else:
            failed += 1

    return generated, skipped, failed


def main():
    """Main entry point."""
    # Check for TTS availability
    if not HAS_TTS:
        print("Warning: google-cloud-texttospeech not installed.")
        print("Install with: pip install google-cloud-texttospeech")
        print("Running in dry-run mode.")
        dry_run = True
    else:
        dry_run = "--dry-run" in sys.argv

    # Parse arguments
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    curriculum_path = Path(args[0]) if args else Path("curriculum.json")

    # Load curriculum
    try:
        curriculum = load_curriculum(curriculum_path)
    except FileNotFoundError:
        print(f"Error: Curriculum file not found: {curriculum_path}", file=sys.stderr)
        sys.exit(1)
    except CurriculumError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Setup paths
    project_dir = Path(__file__).parent.parent
    audio_dir = project_dir / "assets" / "audio"
    cache_dir = project_dir / "cache"

    audio_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Load manifest
    manifest = MediaManifest(cache_dir / "audio_manifest.json")

    # Generate audio
    print(f"Audio output directory: {audio_dir}")
    if dry_run:
        print("DRY RUN - no files will be generated")

    generated, skipped, failed = generate_audio_batch(
        curriculum,
        audio_dir,
        manifest,
        dry_run=dry_run,
    )

    # Save manifest
    if not dry_run:
        manifest.save()

    # Print summary
    print()
    print("Audio generation complete:")
    print(f"  Generated: {generated}")
    print(f"  Skipped (cached): {skipped}")
    print(f"  Failed: {failed}")


if __name__ == "__main__":
    main()
