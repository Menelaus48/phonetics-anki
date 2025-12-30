#!/usr/bin/env python3
"""
Optional image generator for the Phonics Anki deck.

Generates illustrations for example words using an image generation API.
Uses manifest caching to skip regeneration of unchanged content.

This module is designed to be API-agnostic - it provides the infrastructure
for batch generation with caching, but the actual API call can be swapped
out for different providers (OpenAI DALL-E, Stability AI, etc.).

Usage:
    python scripts/generate_images.py [curriculum.json]

Environment variables:
    OPENAI_API_KEY: API key for OpenAI (if using DALL-E)
    (or configure for your preferred image generation API)

The script runs in dry-run mode if no API is configured.
"""

import os
import sys
from pathlib import Path
from typing import Any, Callable

from curriculum import load_curriculum, CurriculumError
from media import MediaManifest, generate_image_filename, compute_file_hash

# Optional imports for image generation APIs
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    openai = None

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    requests = None


# Default image generation settings
DEFAULT_STYLE_PROMPT = (
    "Simple, high-contrast illustration for a young child. "
    "Kid-friendly, colorful, no text or letters in the image. "
    "Clear subject centered in frame, white or simple background."
)

DEFAULT_IMAGE_CONFIG = {
    "style_version": "v1",
    "size": "512x512",
    "style": DEFAULT_STYLE_PROMPT,
}


def generate_prompt_for_word(word: str, style: str) -> str:
    """
    Generate an image prompt for a word.

    Args:
        word: The word to illustrate.
        style: The style description to append.

    Returns:
        The complete prompt string.
    """
    return f"A {word}. {style}"


def collect_words_for_images(curriculum: dict) -> list[dict]:
    """
    Collect all words that need image generation.

    Args:
        curriculum: The loaded curriculum data.

    Returns:
        List of dicts with 'word' and 'context' fields.
    """
    words = []
    seen = set()

    # Collect example words from sound and pattern items
    for item in curriculum.get("items", []):
        item_type = item.get("type", "")
        item_id = item.get("id", "")

        if item_type in ("sound", "pattern"):
            for example in item.get("examples", []):
                word = example.get("word", "")
                if word and word not in seen:
                    seen.add(word)
                    words.append({
                        "word": word,
                        "context": f"{item_type}:{item_id}",
                    })

        elif item_type == "minimal_pair_sound":
            # Collect words from minimal pairs
            for side in ("left", "right", "third"):
                side_data = item.get(side, {})
                word = side_data.get("word", "")
                if word and word not in seen:
                    seen.add(word)
                    words.append({
                        "word": word,
                        "context": f"minpair:{item_id}:{side}",
                    })

    return words


def generate_image_openai(
    prompt: str,
    output_path: Path,
    size: str = "512x512",
) -> bool:
    """
    Generate an image using OpenAI's DALL-E API.

    Args:
        prompt: The image generation prompt.
        output_path: Where to save the image.
        size: Image size (e.g., "256x256", "512x512", "1024x1024").

    Returns:
        True if successful, False otherwise.
    """
    if not HAS_OPENAI or not HAS_REQUESTS:
        return False

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return False

    try:
        client = openai.OpenAI(api_key=api_key)

        response = client.images.generate(
            model="dall-e-2",
            prompt=prompt,
            size=size,
            n=1,
        )

        image_url = response.data[0].url

        # Download the image
        img_response = requests.get(image_url)
        img_response.raise_for_status()

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save the image
        with open(output_path, "wb") as f:
            f.write(img_response.content)

        return True

    except Exception as e:
        print(f"Error generating image: {e}")
        return False


def generate_images_batch(
    curriculum: dict,
    output_dir: Path,
    manifest: MediaManifest,
    image_config: dict | None = None,
    generator_fn: Callable[[str, Path, str], bool] | None = None,
    dry_run: bool = False,
) -> tuple[int, int, int]:
    """
    Generate images for all words in the curriculum.

    Args:
        curriculum: The loaded curriculum data.
        output_dir: Directory to save image files.
        manifest: The image manifest for caching.
        image_config: Image configuration (style, size, etc.).
        generator_fn: Function to call for image generation.
        dry_run: If True, don't actually generate, just report what would be done.

    Returns:
        Tuple of (generated, skipped, failed) counts.
    """
    image_config = image_config or DEFAULT_IMAGE_CONFIG
    generator_fn = generator_fn or generate_image_openai

    words = collect_words_for_images(curriculum)
    print(f"Found {len(words)} unique words for image generation")

    # Build params for cache comparison
    params_template = {
        "style_version": image_config.get("style_version", "v1"),
        "size": image_config.get("size", "512x512"),
    }

    generated = 0
    skipped = 0
    failed = 0

    for word_info in words:
        word = word_info["word"]
        context = word_info["context"]

        # Generate filename
        filename = generate_image_filename(
            word,
            image_config.get("style_version", "v1"),
        )
        output_path = output_dir / filename

        # Check if regeneration needed
        manifest_key = word
        params = {**params_template, "word": word}

        if not manifest.needs_regeneration(manifest_key, params, output_dir):
            skipped += 1
            continue

        if dry_run:
            print(f"  Would generate: {filename} ({context})")
            generated += 1
            continue

        print(f"  Generating: {filename} ({context})")

        # Generate prompt
        prompt = generate_prompt_for_word(
            word,
            image_config.get("style", DEFAULT_STYLE_PROMPT),
        )

        if generator_fn(prompt, output_path, image_config.get("size", "512x512")):
            # Update manifest
            content_hash = compute_file_hash(output_path)
            manifest.set_entry(manifest_key, filename, params, content_hash)
            generated += 1
        else:
            failed += 1

    return generated, skipped, failed


def check_api_availability() -> tuple[bool, str]:
    """
    Check if an image generation API is available.

    Returns:
        Tuple of (available, message).
    """
    if not HAS_OPENAI:
        return False, "openai package not installed (pip install openai)"

    if not HAS_REQUESTS:
        return False, "requests package not installed (pip install requests)"

    if not os.environ.get("OPENAI_API_KEY"):
        return False, "OPENAI_API_KEY environment variable not set"

    return True, "OpenAI API configured"


def main():
    """Main entry point."""
    # Check for API availability
    api_available, message = check_api_availability()
    if not api_available:
        print(f"Warning: {message}")
        print("Running in dry-run mode.")
        dry_run = True
    else:
        print(f"API status: {message}")
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
    image_dir = project_dir / "assets" / "images"
    cache_dir = project_dir / "cache"

    image_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Load manifest
    manifest = MediaManifest(cache_dir / "image_manifest.json")

    # Generate images
    print(f"Image output directory: {image_dir}")
    if dry_run:
        print("DRY RUN - no files will be generated")

    generated, skipped, failed = generate_images_batch(
        curriculum,
        image_dir,
        manifest,
        dry_run=dry_run,
    )

    # Save manifest
    if not dry_run:
        manifest.save()

    # Print summary
    print()
    print("Image generation complete:")
    print(f"  Generated: {generated}")
    print(f"  Skipped (cached): {skipped}")
    print(f"  Failed: {failed}")


if __name__ == "__main__":
    main()
