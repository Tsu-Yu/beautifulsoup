# bs4/tests/test_replacer_api.py
import unittest
from bs4 import BeautifulSoup
from bs4.replacer import SoupReplacer

HTML = "<html><body><b>bold</b><p>hi <b>x</b></p></body></html>"

class TestSoupReplacer(unittest.TestCase):
    def test_replaces_during_parse(self):
        rp = SoupReplacer("b", "blockquote")
        soup = BeautifulSoup(HTML, "html.parser", replacer=rp)
        self.assertIsNone(soup.find("b"))
        blocks = soup.find_all("blockquote")
        self.assertEqual(len(blocks), 2)
        self.assertEqual(blocks[0].get_text(), "bold")

    def test_with_soupstrainer(self):
        from bs4 import SoupStrainer
        rp = SoupReplacer("b", "blockquote")
        only_blocks = SoupStrainer("blockquote")
        soup = BeautifulSoup(HTML, "html.parser", replacer=rp, parse_only=only_blocks)
        self.assertEqual([t.name for t in soup.find_all(True)], ["blockquote","blockquote"])

    def test_no_replacer_does_not_change(self):
        """Verify normal parsing is unaffected when no replacer is given."""
        html = "<p><b>bold</b></p>"
        soup = BeautifulSoup(html, "html.parser")  # 沒有 replacer
        self.assertIsNotNone(soup.find("b"))
        self.assertIsNone(soup.find("blockquote"))

    def test_custom_tag_pair(self):
        """Verify arbitrary tag pair replacement works (e.g. div -> section)."""
        html = "<div><div>inner</div></div>"
        rp = SoupReplacer("div", "section")
        soup = BeautifulSoup(html, "html.parser", replacer=rp)
        tags = [t.name for t in soup.find_all(True)]
        self.assertTrue(all(name == "section" for name in tags))


if __name__ == "__main__":
    unittest.main()
