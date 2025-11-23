# beautifulsoup/bs4/tests/test_replacer_m3.py
import unittest
import warnings

from bs4 import BeautifulSoup
from bs4.replacer import SoupReplacer


class TestSoupReplacerM3(unittest.TestCase):
    # 1) Backward compatibility: M2-style pair (og_tag, alt_tag) still works.
    #    <b> turns into <blockquote> while other tags remain unchanged.
    def test_m2_pair_constructor_kept(self):
        html = "<div><b>bold</b><i>italic</i></div>"
        replacer = SoupReplacer("b", "blockquote")
        soup = BeautifulSoup(html, "html.parser", replacer=replacer)
        out = soup.prettify()

        self.assertIn("<blockquote>", out)
        self.assertIn("</blockquote>", out)
        self.assertIn("<i>", out)  # unrelated tags untouched
        self.assertIn("</i>", out)
        self.assertNotIn("<b>", out)  # original tag should be renamed

    # 2) name_xformer: conditional renaming using M3 API.
    #    Only rename <b> to <blockquote>; all other names pass through unchanged.
    def test_name_xformer_renames_conditionally(self):
        html = "<div><b>bold</b><u>under</u></div>"
        replacer = SoupReplacer(name_xformer=lambda tag: "blockquote" if tag.name == "b" else tag.name)
        soup = BeautifulSoup(html, "html.parser", replacer=replacer)
        out = soup.prettify()

        self.assertIn("<blockquote>", out)
        self.assertIn("</blockquote>", out)
        self.assertIn("<u>", out)             # should not be renamed
        self.assertNotIn("<b>", out)

    # 3) attrs_xformer: rewrite attributes by returning a brand-new dict.
    #    Remove "class" and add a data-* marker.
    def test_attrs_xformer_rewrites_attributes(self):
        html = '<p class="x y" id="pid">text</p>'
        def strip_class_and_mark(tag):
            attrs = dict(tag.attrs)           # start from current attrs
            attrs.pop("class", None)          # remove class if present
            attrs["data-x"] = "1"             # add a new attribute
            return attrs

        replacer = SoupReplacer(attrs_xformer=strip_class_and_mark)
        soup = BeautifulSoup(html, "html.parser", replacer=replacer)
        p = soup.find("p")

        self.assertIsNotNone(p)
        self.assertNotIn("class", p.attrs)    # class removed
        self.assertIn("id", p.attrs)          # id preserved
        self.assertEqual(p.attrs.get("data-x"), "1")

    # 4) xformer (side effects): mutate the node in-place without returning anything.
    #    Here we uppercase the text and drop a specific attribute if present.
    def test_node_xformer_side_effects(self):
        html = '<span role="note">hello</span>'
        def mutate(tag):
            if tag.name == "span" and tag.string:
                tag.string.replace_with(tag.string.upper())
            tag.attrs.pop("role", None)  # side-effect: remove "role"

        replacer = SoupReplacer(xformer=mutate)
        soup = BeautifulSoup(html, "html.parser", replacer=replacer)
        span = soup.find("span")

        self.assertEqual(span.text, "HELLO")
        self.assertNotIn("role", span.attrs)

    # 5) Conflict protection: supplying both (og_tag, alt_tag) AND keyword transformers
    #    should raise ValueError to avoid ambiguous semantics.
    def test_conflicting_constructors_raise(self):
        with self.assertRaises(ValueError):
            SoupReplacer("b", "blockquote", name_xformer=lambda tag: tag.name)

    # 6) Transformation order guarantee: name_xformer -> attrs_xformer -> xformer.
    #    We verify that:
    #       - name_xformer renames <b> to <blockquote>
    #       - attrs_xformer sees the NEW name and writes an attribute based on it
    #       - xformer sees both new name and attrs and appends a suffix to the text
    def test_transformation_order_name_then_attrs_then_node(self):
        html = "<div><b id='x'>bold</b></div>"
        order_log = []

        # Only log when operating on the target node (id='x')
        def nx(tag):
            if tag.get("id") == "x":
                order_log.append(f"nx:{tag.name}")
            if tag.name == "b":
                return "blockquote"
            return tag.name

        def ax(tag):
            if tag.get("id") == "x":
                order_log.append(f"ax:{tag.name}")
            new_attrs = dict(tag.attrs)
            new_attrs["data-seen-name"] = tag.name
            return new_attrs

        def xx(tag):
            if tag.get("id") == "x":
                order_log.append(f"xx:{tag.name}:{tag.attrs.get('data-seen-name')}")
            if tag.name == "blockquote" and tag.string:
                tag.string.replace_with(tag.string + " (x)")

        replacer = SoupReplacer(name_xformer=nx, attrs_xformer=ax, xformer=xx)
        soup = BeautifulSoup(html, "html.parser", replacer=replacer)
        out = soup.prettify()

        # Structural assertions (unchanged)
        self.assertIn("<blockquote", out)                 # renamed
        self.assertIn('data-seen-name="blockquote"', out) # attrs_xformer ran after rename
        self.assertIn("bold (x)", out)                    # xformer ran last and mutated text

        # Now order assertions are insulated from <div> transforms
        self.assertEqual(order_log[:3], ["nx:b", "ax:blockquote", "xx:blockquote:blockquote"])


if __name__ == "__main__":
    unittest.main()
