# beautifulsoup/bs4/tests/test_iterable_soup_m4.py
import unittest

from bs4 import BeautifulSoup
from bs4 import Comment


class TestIterableSoupM4(unittest.TestCase):
    # 1) Basic iteration: iterating over soup should yield the soup object first,
    #    and then traverse the entire tree (all tags and strings reachable from it).
    def test_soup_iterates_entire_tree_and_includes_root(self):
        html = "<div><p>hello</p><p>world</p></div>"
        soup = BeautifulSoup(html, "html.parser")

        nodes = list(soup)

        # 第一個一定是 root soup 本人
        self.assertIs(nodes[0], soup)

        # 所有 <p> tag 都應該出現在 traversal 裡
        p_nodes = [n for n in nodes if getattr(n, "name", None) == "p"]
        self.assertEqual(len(p_nodes), 2)

        # "hello" 和 "world" 文字節點應該也能被走到
        texts = [str(n) for n in nodes if not getattr(n, "name", None)]
        self.assertIn("hello", texts)
        self.assertIn("world", texts)

    # 2) Nested structure: deep descendants should also be visited by iterating soup.
    def test_nested_descendants_are_visited(self):
        html = "<div><ul><li><span>deep</span></li></ul></div>"
        soup = BeautifulSoup(html, "html.parser")

        nodes = list(soup)

        # <span> 這種深層 descendant 也要走到
        span_nodes = [n for n in nodes if getattr(n, "name", None) == "span"]
        self.assertEqual(len(span_nodes), 1)

        # "deep" 這個文字節點也要存在
        texts = [str(n) for n in nodes if not getattr(n, "name", None)]
        self.assertIn("deep", texts)

    # 3) Empty / minimal document: iterating over an empty soup should at least
    #    not crash, and yield the soup itself as the first element.
    def test_empty_document_iteration(self):
        html = ""
        soup = BeautifulSoup(html, "html.parser")

        nodes = list(soup)

        # 只要不噴錯就先算 pass；但我們也要求第一個是 soup
        self.assertGreaterEqual(len(nodes), 1)
        self.assertIs(nodes[0], soup)

    # 4) Tag iteration behavior is unchanged: iterating over a normal Tag
    #    should still iterate over its *immediate* contents (not full subtree),
    #    because element.PageElement.__iter__ returns iter(self.contents).
    def test_tag_iteration_still_yields_direct_children_only(self):
        html = "<div><p>one</p><p>two</p></div>"
        soup = BeautifulSoup(html, "html.parser")
        div = soup.find("div")
        self.assertIsNotNone(div)

        children = list(div)

        # div 底下直接 children 應該只有兩個 <p>
        self.assertEqual(len(children), 2)
        self.assertTrue(all(getattr(c, "name", None) == "p" for c in children))

        # 並不會直接包含文字子節點 "one"/"two"（那些在 <p> 裡面）
        texts = [c for c in children if not getattr(c, "name", None)]
        self.assertEqual(texts, [])

    # 5) Mixed node types (Comment, NavigableString, Tag): ensure that all kinds
    #    of nodes reachable from soup are visited at least once during iteration.
    def test_iteration_sees_mixed_node_types(self):
        html = "<div><!--c--><p>hi<b>there</b></p>tail</div>"
        soup = BeautifulSoup(html, "html.parser")

        nodes = list(soup)

        # 有 comment
        self.assertTrue(any(isinstance(n, Comment) for n in nodes))

        # 有 <b> tag
        b_nodes = [n for n in nodes if getattr(n, "name", None) == "b"]
        self.assertEqual(len(b_nodes), 1)

        # "hi"、"there"、"tail" 這三個文字都要在 traversal 中出現
        texts = [str(n) for n in nodes if not getattr(n, "name", None)]
        self.assertIn("hi", texts)
        self.assertIn("there", texts)
        self.assertIn("tail", texts)


if __name__ == "__main__":
    unittest.main()
