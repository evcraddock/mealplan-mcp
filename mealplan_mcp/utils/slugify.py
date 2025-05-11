"""
Utility functions for creating URL-friendly slugs from strings.
"""

import re
import unicodedata


def slugify(text: str) -> str:
    """
    Convert a string into a URL-friendly slug.

    Steps:
    1. Convert to lowercase
    2. Remove accents (normalize to ASCII)
    3. Replace spaces and special chars with dashes
    4. Collapse multiple dashes into a single dash
    5. Trim leading/trailing dashes
    6. Truncate to 100 characters max

    Args:
        text: The string to convert to a slug

    Returns:
        A URL-friendly slug
    """
    # Convert to lowercase
    text = text.lower()

    # Convert to ASCII (remove accents)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = "".join(c for c in text if unicodedata.category(c)[0] != "C")

    # Replace non-alphanumeric characters with dash
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)

    # Remove leading/trailing dashes
    text = text.strip("-")

    # Truncate to 100 chars max
    return text[:100]


def suffix_if_exists(slug: str, existing_set: set) -> str:
    """
    Add a numeric suffix to a slug if it already exists in the provided set.

    Args:
        slug: The original slug
        existing_set: A set of existing slugs to check against

    Returns:
        Either the original slug if it doesn't exist in the set,
        or a new slug with a numeric suffix (e.g., "slug-1", "slug-2")
    """
    if slug not in existing_set:
        return slug

    counter = 1
    new_slug = f"{slug}-{counter}"

    while new_slug in existing_set:
        counter += 1
        new_slug = f"{slug}-{counter}"

    return new_slug
