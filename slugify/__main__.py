"""slugify CLI — slugify arguments or stdin lines."""
import argparse
import sys

from . import __version__, slugify


def _pair(value):
    if "=" not in value:
        raise argparse.ArgumentTypeError("expected OLD=NEW")
    old, _, new = value.partition("=")
    return (old, new)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="slugify",
        description="Turn text into clean URL/file slugs. Stdlib only.",
    )
    parser.add_argument("text", nargs="*",
                        help="text to slugify (reads stdin lines if omitted)")
    parser.add_argument("-s", "--separator", default="-",
                        help="word separator (default: -)")
    parser.add_argument("-u", "--unicode", action="store_true",
                        help="keep unicode letters (e.g. CJK) instead of ASCII folding")
    parser.add_argument("-U", "--no-lowercase", action="store_true",
                        help="preserve letter case")
    parser.add_argument("-m", "--max-length", type=int, default=0,
                        help="truncate at word boundary to N chars (0 = unlimited)")
    parser.add_argument("-w", "--stopword", action="append", default=[],
                        metavar="WORD", help="drop WORD from slugs (repeatable)")
    parser.add_argument("-r", "--replace", action="append", default=[],
                        type=_pair, metavar="OLD=NEW",
                        help="replacement applied before slugging (repeatable)")
    parser.add_argument("--version", action="version", version=__version__)
    args = parser.parse_args(argv)

    def convert(text):
        return slugify(
            text,
            separator=args.separator,
            lowercase=not args.no_lowercase,
            allow_unicode=args.unicode,
            max_length=args.max_length,
            stopwords=args.stopword,
            replacements=args.replace,
        )

    try:
        if args.text:
            print(convert(" ".join(args.text)))
        else:
            for line in sys.stdin:
                line = line.strip()
                if line:
                    print(convert(line))
    except ValueError as exc:
        print(f"slugify: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
