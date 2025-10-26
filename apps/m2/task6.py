# apps/m2/task6.py
import sys
from bs4 import BeautifulSoup
from bs4.replacer import SoupReplacer

def main():
    if len(sys.argv) < 2:
        print("Usage: python apps/m2/task6.py <file.html> [og_tag alt_tag]")
        sys.exit(1)

    path = sys.argv[1]
    og = sys.argv[2] if len(sys.argv) > 2 else "b"
    alt = sys.argv[3] if len(sys.argv) > 3 else "blockquote"

    with open(path, "rb") as f:
        rp = SoupReplacer(og, alt)
        soup = BeautifulSoup(f, "html.parser", replacer=rp)  # 使用 html.parser
    print(soup.prettify())

if __name__ == "__main__":
    main()
