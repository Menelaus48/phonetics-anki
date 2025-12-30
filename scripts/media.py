"""
Media resolution and caching for the Phonics Anki deck.

Provides a manifest-based system for tracking generated media files
(audio and images) to avoid re-generating unchanged content.

The generator can link existing local media without crashing if files
are absent - missing media is logged as a warning but doesn't block
deck generation.
"""

import hashlib
import json
from pathlib import Path
from typing import Any


class MediaManifest:
    """
    Tracks generated media files with their generation parameters.

    The manifest stores:
    - Input parameters (word, voice settings, prompt version, etc.)
    - Output filename
    - Content hash (for change detection)

    This allows the generator to skip regeneration when inputs haven't changed.
    """

    def __init__(self, manifest_path: Path):
        """
        Initialize the manifest.

        Args:
            manifest_path: Path to the manifest JSON file.
        """
        self.manifest_path = Path(manifest_path)
        self._data: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        """Load the manifest from disk if it exists."""
        if self.manifest_path.exists():
            try:
                with open(self.manifest_path, encoding="utf-8") as f:
                    self._data = json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                print(f"Warning: Could not load manifest {self.manifest_path}: {e}")
                self._data = {}

    def save(self) -> None:
        """Save the manifest to disk."""
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, sort_keys=True)

    def get_entry(self, key: str) -> dict[str, Any] | None:
        """
        Get a manifest entry by key.

        Args:
            key: The unique key for this media item.

        Returns:
            The manifest entry dict, or None if not found.
        """
        return self._data.get(key)

    def set_entry(
        self,
        key: str,
        filename: str,
        params: dict[str, Any],
        content_hash: str | None = None,
    ) -> None:
        """
        Set a manifest entry.

        Args:
            key: The unique key for this media item.
            filename: The output filename.
            params: The generation parameters (for change detection).
            content_hash: Optional hash of the file content.
        """
        self._data[key] = {
            "filename": filename,
            "params": params,
            "content_hash": content_hash,
        }

    def needs_regeneration(
        self,
        key: str,
        params: dict[str, Any],
        media_dir: Path,
    ) -> bool:
        """
        Check if a media item needs to be regenerated.

        Returns True if:
        - No manifest entry exists for this key
        - The parameters have changed
        - The output file doesn't exist

        Args:
            key: The unique key for this media item.
            params: The current generation parameters.
            media_dir: Directory where media files are stored.

        Returns:
            True if regeneration is needed, False otherwise.
        """
        entry = self.get_entry(key)
        if entry is None:
            return True

        # Check if parameters changed
        if entry.get("params") != params:
            return True

        # Check if file exists
        filename = entry.get("filename", "")
        if not filename:
            return True

        file_path = media_dir / filename
        if not file_path.exists():
            return True

        return False


def compute_file_hash(file_path: Path) -> str:
    """
    Compute SHA256 hash of a file.

    Args:
        file_path: Path to the file.

    Returns:
        Hex-encoded SHA256 hash.
    """
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def generate_audio_filename(
    item_id: str,
    word: str,
    voice: str = "default",
    rate: float = 1.0,
) -> str:
    """
    Generate a deterministic filename for an audio file.

    Args:
        item_id: The curriculum item ID.
        word: The word being spoken.
        voice: Voice identifier.
        rate: Speaking rate.

    Returns:
        A deterministic filename.
    """
    # Sanitize word for filename
    safe_word = "".join(c if c.isalnum() else "_" for c in word.lower())
    return f"audio_{item_id}_{safe_word}_{voice}_r{rate:.2f}.mp3"


def generate_image_filename(
    word: str,
    style_version: str = "v1",
) -> str:
    """
    Generate a deterministic filename for an image file.

    Args:
        word: The word being illustrated.
        style_version: Version of the image style prompt.

    Returns:
        A deterministic filename.
    """
    safe_word = "".join(c if c.isalnum() else "_" for c in word.lower())
    return f"img_{safe_word}_{style_version}.png"


class MediaResolver:
    """
    Resolves media references to local files.

    Provides methods to find and link media files for inclusion in the
    Anki deck. Missing files are logged but don't cause errors.
    """

    def __init__(
        self,
        audio_dir: Path,
        image_dir: Path,
        audio_manifest: MediaManifest | None = None,
        image_manifest: MediaManifest | None = None,
    ):
        """
        Initialize the resolver.

        Args:
            audio_dir: Directory containing audio files.
            image_dir: Directory containing image files.
            audio_manifest: Optional manifest for audio files.
            image_manifest: Optional manifest for image files.
        """
        self.audio_dir = Path(audio_dir)
        self.image_dir = Path(image_dir)
        self.audio_manifest = audio_manifest
        self.image_manifest = image_manifest
        self._missing_files: list[str] = []

    def resolve_audio(self, item_id: str, word: str) -> Path | None:
        """
        Find the audio file for a word.

        Args:
            item_id: The curriculum item ID.
            word: The word to find audio for.

        Returns:
            Path to the audio file, or None if not found.
        """
        # Try manifest first
        if self.audio_manifest:
            key = f"{item_id}:{word}"
            entry = self.audio_manifest.get_entry(key)
            if entry:
                path = self.audio_dir / entry["filename"]
                if path.exists():
                    return path

        # Try common filename patterns
        patterns = [
            f"audio_{item_id}_{word.lower()}_*.mp3",
            f"{word.lower()}.mp3",
            f"{item_id}_{word.lower()}.mp3",
        ]

        for pattern in patterns:
            matches = list(self.audio_dir.glob(pattern))
            if matches:
                return matches[0]

        self._missing_files.append(f"audio:{item_id}:{word}")
        return None

    def resolve_image(self, word: str) -> Path | None:
        """
        Find the image file for a word.

        Args:
            word: The word to find an image for.

        Returns:
            Path to the image file, or None if not found.
        """
        # Try manifest first
        if self.image_manifest:
            entry = self.image_manifest.get_entry(word)
            if entry:
                path = self.image_dir / entry["filename"]
                if path.exists():
                    return path

        # Try common filename patterns
        patterns = [
            f"img_{word.lower()}_*.png",
            f"{word.lower()}.png",
            f"{word.lower()}.jpg",
        ]

        for pattern in patterns:
            matches = list(self.image_dir.glob(pattern))
            if matches:
                return matches[0]

        self._missing_files.append(f"image:{word}")
        return None

    def get_missing_files(self) -> list[str]:
        """Get list of files that couldn't be resolved."""
        return self._missing_files.copy()

    def report_missing(self) -> None:
        """Print a summary of missing files."""
        if self._missing_files:
            print(f"\nWarning: {len(self._missing_files)} media files not found:")
            for f in self._missing_files[:10]:
                print(f"  - {f}")
            if len(self._missing_files) > 10:
                print(f"  ... and {len(self._missing_files) - 10} more")


def ensure_cache_dirs(base_dir: Path) -> tuple[Path, Path]:
    """
    Ensure cache directories exist.

    Args:
        base_dir: Base project directory.

    Returns:
        Tuple of (cache_dir, assets_dir).
    """
    cache_dir = base_dir / "cache"
    assets_dir = base_dir / "assets"

    cache_dir.mkdir(parents=True, exist_ok=True)
    (assets_dir / "audio").mkdir(parents=True, exist_ok=True)
    (assets_dir / "images").mkdir(parents=True, exist_ok=True)

    return cache_dir, assets_dir
