"""slugify — unicode-aware slug generation, stdlib only.

Turn arbitrary text into clean, safe slugs for URLs and filenames.

>>> from slugify import slugify
>>> slugify("Crème Brûlée!")
'creme-brulee'
>>> slugify("Straße & Smørrebrød")
'strasse-smorrebrod'
>>> slugify("日本語のテスト", allow_unicode=True)
'日本語のテスト'
"""
from __future__ import annotations

import unicodedata

__version__ = "1.0.0"
__all__ = ["slugify", "__version__"]

# Latin characters that NFKD cannot decompose to ASCII, mapped by hand.
# This is what usually forces a third-party transliteration dependency.
_TRANSLITERATIONS = {
    "æ": "ae", "Æ": "AE",
    "œ": "oe", "Œ": "OE",
    "ø": "o", "Ø": "O",
    "ß": "ss", "ẞ": "SS",
    "ł": "l", "Ł": "L",
    "đ": "d", "Đ": "D",
    "ð": "d", "Ð": "D",
    "þ": "th", "Þ": "TH",
    "ħ": "h", "Ħ": "H",
    "ŋ": "ng", "Ŋ": "NG",
    "ı": "i",
    "ĸ": "k",
}

# Apostrophes/quotes are removed entirely (don't -> dont), never separators.
_QUOTES = "'’‘`´ʼ"

def _is_word_char(ch: str) -> bool:
    """Alphanumerics and Unicode combining marks belong to words.

    Marks matter because lowercasing can create them (e.g. "İ".lower() is
    "i" + U+0307) and Python's \\w does NOT match them — a naive regex
    split would break such words apart. Underscore is a separator here.
    """
    return ch.isalnum() or unicodedata.category(ch).startswith("M")


def _split_words(text: str) -> list:
    words, current = [], []
    for ch in text:
        if _is_word_char(ch):
            current.append(ch)
        elif current:
            words.append("".join(current))
            current = []
    if current:
        words.append("".join(current))
    # a "word" must contain at least one alphanumeric (orphan marks drop)
    return [w for w in words if any(c.isalnum() for c in w)]


def _to_ascii(text: str) -> str:
    """Best-effort ASCII transliteration using NFKD + the hand-made table."""
    text = "".join(_TRANSLITERATIONS.get(ch, ch) for ch in text)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text.encode("ascii", "ignore").decode("ascii")


def slugify(
    text,
    separator="-",
    lowercase=True,
    allow_unicode=False,
    max_length=0,
    stopwords=(),
    replacements=(),
):
    """Convert *text* to a slug.

    separator     string placed between words (default "-"; "" joins words)
    lowercase     lowercase the result (default True)
    allow_unicode keep unicode letters (CJK etc.) instead of ASCII folding
    max_length    truncate at a word boundary to at most this many chars
                  (0 = unlimited; a first word longer than the limit is
                  hard-cut to fit)
    stopwords     words dropped from the slug, case-insensitive
    replacements  iterable of (old, new) string pairs applied before
                  anything else, e.g. [("&", " and ")]
    """
    if not isinstance(text, str):
        raise TypeError(f"slugify() expects str, got {type(text).__name__}")
    if not isinstance(separator, str):
        raise TypeError("separator must be str")
    if max_length < 0:
        raise ValueError("max_length must be >= 0")
    if isinstance(stopwords, str):
        raise TypeError("stopwords must be an iterable of words, not a str")

    for old, new in replacements:
        if old == "":
            raise ValueError("replacement 'old' string must be non-empty")
        text = text.replace(old, new)

    for quote in _QUOTES:
        text = text.replace(quote, "")

    if allow_unicode:
        text = unicodedata.normalize("NFKC", text)
    else:
        text = _to_ascii(text)

    if lowercase:
        text = text.lower()

    words = _split_words(text)

    if stopwords:
        stops = {s.lower() for s in stopwords}
        words = [w for w in words if w.lower() not in stops]

    if not words:
        return ""

    slug = separator.join(words)

    if max_length and len(slug) > max_length:
        kept = []
        for word in words:
            candidate = separator.join(kept + [word])
            if len(candidate) <= max_length:
                kept.append(word)
            else:
                break
        slug = separator.join(kept) if kept else words[0][:max_length]

    return slug
