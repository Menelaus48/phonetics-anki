"""
Alphabet order note generator for the Phonics Anki deck.

Generates "What comes next?" cards algorithmically from the alphabet list.
Example: A B C D __ -> E

Per spec, prompts use uppercase letters only.
"""

from typing import Iterator


def generate_alphabet_order_items(
    letters: list[dict],
    window_size: int = 4,
) -> Iterator[dict]:
    """
    Generate alphabet order items for "what comes next?" cards.

    Args:
        letters: List of letter dicts from curriculum, sorted by 'order'.
        window_size: Number of letters to show before the blank (default 4).

    Yields:
        Dicts with 'id', 'prompt', 'answer', and 'position' fields.

    Example:
        With window_size=4, generates items like:
        - prompt: "A  B  C  D  __", answer: "E", position: 5
        - prompt: "B  C  D  E  __", answer: "F", position: 6
        ...
    """
    # Sort letters by order to ensure correct sequence
    sorted_letters = sorted(letters, key=lambda x: x.get("order", 0))

    # We can only generate items starting from position (window_size + 1)
    # because we need 'window_size' letters before the blank
    for i in range(window_size, len(sorted_letters)):
        # Get the window of letters before this position
        window = sorted_letters[i - window_size : i]
        answer_letter = sorted_letters[i]

        # Build the prompt using uppercase letters
        prompt_letters = [letter.get("upper", "") for letter in window]
        prompt = "  ".join(prompt_letters) + "  __"

        # The answer is the uppercase letter at position i
        answer = answer_letter.get("upper", "")

        # Create a stable ID based on position
        item_id = f"alphabet_order_{answer_letter.get('order', i + 1)}"

        yield {
            "id": item_id,
            "prompt": prompt,
            "answer": answer,
            "position": answer_letter.get("order", i + 1),
        }
