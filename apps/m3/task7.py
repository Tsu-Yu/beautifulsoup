# beautifulsoup/apps/m3/task7_m3.py
# Re-implements Milestone-1 task-7 using the new SoupReplacer API.
# During parsing, we ensure every <p> tag has class="test" (merged, not overwritten).

import argparse
import sys
import pathlib
from typing import List, Union

from bs4 import BeautifulSoup
from bs4.replacer import SoupReplacer


def pick_parser(suffix: str, override: str) -> str:
    """Choose a parser. If override is 'auto', pick XML for .xml, HTML otherwise."""
    if override != "auto":
        return override
    return "lxml-xml" if suffix == ".xml" else "lxml"


def default_out_path(in_path: pathlib.Path) -> pathlib.Path:
    """Default output path: <name>.p-test<ext>"""
    return in_path.with_name(f"{in_path.stem}.p-test{in_path.suffix}")


def ensure_test_class_attrs(tag) -> dict:
    """
    attrs_xformer for SoupReplacer:
    - If the tag name is (case-insensitive) 'p', ensure its class contains 'test'.
    - Merge with existing classes without dropping any.
    - Return a full new attributes dict as required by attrs_xformer.
    """
    attrs = dict(tag.attrs)  # copy current attributes

    # Only target <p> tags (case-insensitive to handle XML with 'P')
    if tag.name.lower() != "p":
        return attrs

    existing = attrs.get("class")

    # BeautifulSoup may represent class as list (HTML) or string (XML).
    # Normalize to a list of strings, merge, and write back as list.
    def to_tokens(x: Union[str, List[str], None]) -> List[str]:
        if x is None:
            return []
        if isinstance(x, list):
            return [t for t in x if isinstance(t, str)]
        # string: split on whitespace
        return [t for t in x.split() if t]

    tokens = to_tokens(existing)
    if "test" not in tokens:
        tokens.append("test")

    attrs["class"] = tokens
    return attrs


def main():
    parser = argparse.ArgumentParser(
        description='Add/merge class="test" for all <p> tags using SoupReplacer (M3).'
    )
    parser.add_argument("input", help="Path to HTML/XML file")
    parser.add_argument("-o", "--output",
                        help="Output file (default: <name>.p-test<ext>)")
    parser.add_argument("--parser",
                        default="auto",
                        choices=["auto", "lxml", "html.parser", "xml", "lxml-xml"],
                        help="Parser to use (default: auto by file extension)")
    args = parser.parse_args()

    in_path = pathlib.Path(args.input)
    if not in_path.is_file():
        print(f"ERROR: file not found: {in_path}", file=sys.stderr)
        sys.exit(2)

    out_path = pathlib.Path(args.output) if args.output else default_out_path(in_path)
    feature = pick_parser(in_path.suffix.lower(), args.parser)

    text = in_path.read_text(encoding="utf-8", errors="ignore")

    # ★ NEW (M3): build a replacer that rewrites attributes during parsing
    replacer = SoupReplacer(attrs_xformer=ensure_test_class_attrs)

    # Pass replacer=... into BeautifulSoup so transforms happen while parsing
    soup = BeautifulSoup(text, features=feature, replacer=replacer)

    # Output
    is_xml = feature in ("xml", "lxml-xml")
    out_path.write_text(soup.prettify(), encoding="utf-8")
    print(f"Wrote modified {'XML' if is_xml else 'HTML'} to {out_path}")


if __name__ == "__main__":
    # Keep large documents safe on deep trees
    sys.setrecursionlimit(10000)
    main()
