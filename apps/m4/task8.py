# beautifulsoup/apps/m4/task8.py
import sys
from pathlib import Path

from bs4 import BeautifulSoup
from bs4 import Comment


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: PYTHONPATH=. python3 apps/m4/task8.py path/to/file.html")
        sys.exit(1)

    html_path = Path(sys.argv[1])
    html = html_path.read_text(encoding="utf-8")

    # client space：establish a BeautifulSoup object
    soup = BeautifulSoup(html, "html.parser")

    # Milestone 4: iterate over all nodes in the soup
    for node in soup:
        if hasattr(node, "name") and node.name is not None:
            print(f"[TAG] <{node.name}>")
        elif isinstance(node, Comment):
            print(f"[COMMENT] {node}")
        else:
            text = str(node).strip()
            if text:
                print(f"[TEXT] {text!r}")


if __name__ == "__main__":
    main()
