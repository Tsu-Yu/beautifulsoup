# apps/m2/task3.py
import argparse, sys, pathlib
from bs4 import BeautifulSoup, SoupStrainer

def pick_parser(suffix: str, override: str) -> str:
    if override != "auto":
        return override
    return "lxml-xml" if suffix == ".xml" else "lxml"

def main():
    p = argparse.ArgumentParser(description="Task3 (M2): print every tag using SoupStrainer.")
    p.add_argument("input", help="Path to HTML/XML file")
    p.add_argument("--parser", default="auto",
                   choices=["auto", "lxml", "html.parser", "xml", "lxml-xml"])
    args = p.parse_args()

    in_path = pathlib.Path(args.input)
    if not in_path.is_file():
        print(f"ERROR: file not found: {in_path}", file=sys.stderr)
        sys.exit(2)

    parser = pick_parser(in_path.suffix.lower(), args.parser)
    text = in_path.read_text(encoding="utf-8", errors="ignore")

    # only parse every tag
    strainer = SoupStrainer(True)
    soup = BeautifulSoup(text, features=parser, parse_only=strainer)

    for tag in soup.find_all(True):
        print(tag.name)

if __name__ == "__main__":
    sys.setrecursionlimit(10000)
    main()
