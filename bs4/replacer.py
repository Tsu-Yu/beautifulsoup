# bs4/replacer.py
class SoupReplacer:
    """Simple tag replacer used by BeautifulSoup to rename tags during parsing."""

    def __init__(self, og_tag, alt_tag):
        self.og_tag = og_tag
        self.alt_tag = alt_tag

    def maybe(self, tag_name: str) -> str:
        return self.alt_tag if tag_name == self.og_tag else tag_name
