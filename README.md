# slugify

Unicode-aware slug generator — **stdlib only**, library + CLI.

Turns arbitrary text into clean, safe slugs for URLs, filenames, and IDs.
Zero dependencies: the usual reason slug libraries pull in a transliteration
package is a small set of Latin characters (ß, ø, ł, æ, þ…) that Unicode
NFKD cannot decompose — this package maps those by hand instead.

## Install

```bash
pip install .        # from a clone; installs the `slugify` command
```

Or just vendor `slugify/__init__.py` — it is a single stdlib-only file.

## CLI

Real output, run on Python 3.13:

```console
$ slugify "Crème Brûlée & Smørrebrød: A Love Story!"
creme-brulee-smorrebrod-a-love-story

$ slugify -s _ -U "Straße 42, München"
Strasse_42_Munchen

$ slugify -u "東京 2026 Olympics"
東京-2026-olympics

$ slugify -m 20 -w the -w a "The Quick Brown Fox Jumps Over a Lazy Dog"
quick-brown-fox

$ printf "Hello, World!\nĐông Þórður Łódź\ndon't panic\n" | slugify
hello-world
dong-thordur-lodz
dont-panic

$ slugify -r "&= and " "AT&T + Ben & Jerry's"
at-and-t-ben-and-jerrys
```

Flags: `-s/--separator`, `-u/--unicode` (keep CJK etc.), `-U/--no-lowercase`,
`-m/--max-length` (word-boundary truncation), `-w/--stopword` (repeatable),
`-r/--replace OLD=NEW` (repeatable), `--version`. With no arguments it
slugifies each non-empty stdin line (batch mode).

## Library

```python
from slugify import slugify

slugify("Crème Brûlée!")                          # 'creme-brulee'
slugify("Straße")                                 # 'strasse'
slugify("don't stop")                             # 'dont-stop'   (apostrophes vanish)
slugify("foo_bar")                                # 'foo-bar'     (underscore = separator)
slugify("日本語 テスト", allow_unicode=True)        # '日本語-テスト'
slugify("the quick brown fox", max_length=9)      # 'the-quick'   (word boundary)
slugify("Encyclopædia Œuvre", max_length=12)      # 'encyclopaedi' (hard-cut: first word > limit)
slugify("AT&T", replacements=[("&", " and ")])    # 'at-and-t'
slugify("The Quick Fox", stopwords=["the"])       # 'quick-fox'
```

### Semantics worth knowing

- Apostrophes (`' ’ ‘ \` ´ ʼ`) are **removed**, not turned into separators.
- Underscores are separators (`foo_bar` → `foo-bar`).
- `max_length` truncates at word boundaries; only a first word longer than
  the limit is hard-cut. Result never exceeds the limit.
- Unicode combining marks never split words — `slugify("İstanbul",
  allow_unicode=True)` stays one word (`"İ".lower()` produces `i` + a
  combining dot, which a naive `\W` split would break apart).
- Stopword matching is case-insensitive; `stopwords` must not be a bare
  string (raises `TypeError` — a classic silent-bug foot-gun).
- Empty replacement `old` raises `ValueError` (Python's `"".replace` would
  otherwise insert between every character).
- No user input ever reaches a regex or the filesystem; no `eval`/network.

## Tests

64 pytest tests: transliteration, unicode modes, truncation invariants,
error paths, and 11 subprocess CLI tests.

```bash
python3 -m pytest -q
```

## License

MIT © Sentinel Dev Network

---

*Transparency: this tool was designed, implemented, audited, and tested
autonomously by an AI (Sentinel Dev Network build pipeline). Clean-room
implementation — no code copied from existing slug libraries.*
