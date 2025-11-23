# Milestone 4

## 1. Where I implemented iteration

I made the `BeautifulSoup` object itself iterable by adding `__iter__` to the `BeautifulSoup` class:

- **File:** `bs4/__init__.py`  
- **Class:** `BeautifulSoup`  
- **Change:** added

```python
class BeautifulSoup(Tag):
    ...
    def __iter__(self):
        """
        Iterate over the entire parse tree starting from this BeautifulSoup
        object, yielding one node at a time.

        Implementation uses an explicit stack (DFS) so we never collect all
        nodes into a list at once, as required by the assignment.
        """
        from .element import Tag

        stack = [self]
        while stack:
            node = stack.pop()
            yield node

            if isinstance(node, Tag):
                # Reverse so that children are visited in document order.
                for child in reversed(node.contents):
                    stack.append(child)
````

This iterator:

* Yields the **soup object itself first**, then all nodes in a depth-first traversal.
* Uses a **stack** and `yield` to produce one node at a time.
* **Does not** build an intermediate list of all nodes (it respects the “no list of nodes” requirement).
* Does **not** change `Tag.__iter__` in `element.py`, so iterating over a normal tag still only iterates over its direct contents.

---

## 2. Where I wrote the tests

I added 5 unit tests dedicated to Milestone 4:

* **File:** `bs4/tests/test_iterable_soup_m4.py`
* **Test class:** `TestIterableSoupM4`

The tests cover:

1. **Full-tree iteration and root presence**

   * HTML with two `<p>` tags.
   * Verifies that `list(soup)[0]` is the soup object itself, both `<p>` tags appear in the traversal, and the text nodes `"hello"` and `"world"` are visited.

2. **Nested descendants**

   * HTML like `<div><ul><li><span>deep</span></li></ul></div>`.
   * Checks that a deeply nested `<span>` and its text `"deep"` are both visited when iterating over `soup`.

3. **Empty document behavior**

   * HTML is an empty string.
   * Confirms that iterating over the soup does not crash, and the first element in `list(soup)` is still the soup object.

4. **Tag iteration remains unchanged**

   * HTML `<div><p>one</p><p>two</p></div>`.
   * Iterates over the `<div>` tag directly and confirms:

     * It only yields the **two direct `<p>` children**.
     * It does **not** directly yield `"one"` / `"two"` text nodes (those are inside the `<p>` tags).
   * This verifies that the existing `PageElement.__iter__` behavior (iterating `contents`) is preserved, and only `BeautifulSoup` has the new full-tree iterator.

5. **Mixed node types (Tag / Comment / text)**

   * HTML like `<div><!--c--><p>hi<b>there</b></p>tail</div>`.
   * Checks that:

     * At least one `Comment` node is seen.
     * A `<b>` tag is present in the traversal.
     * Text nodes `"hi"`, `"there"`, and `"tail"` are all visited.

---

## 3. How I ran my tests

From the repository root, I ran the unit tests using `unittest`:

```bash
python3 -m unittest discover -s bs4/tests -p "test_iterable_soup_m4.py" -v
```

This executes all 5 test cases in `TestIterableSoupM4` and verifies:

* The soup iterator walks the entire tree without building a list internally.
* Existing `Tag` iteration semantics are preserved.
* Mixed node types (tags, comments, and text) are correctly handled.

All tests passed successfully.

---

## 4. Application program (`task8.py`)

To demonstrate the iterable `BeautifulSoup` in a real program, I implemented:

* **File:** `apps/m4/task8.py`

```python
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

    # client space: establish a BeautifulSoup object
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
```

This program:

* Reads an HTML file from the command line.
* Builds a `BeautifulSoup` object.
* Iterates over **all nodes** in `soup` using the new iterator.
* Prints:

  * `[TAG] <tagname>` for tag nodes.
  * `[COMMENT] ...` for comments.
  * `[TEXT] '...text...'` for non-empty text nodes.

### Example run and result

Command (run from the project root):

```bash
PYTHONPATH=. python3 apps/m4/task8.py samples/sample.html
```

Output (ignoring the optional `soupsieve` warning):

```text
[TAG] <[document]>
[TAG] <html>
[TAG] <body>
[TAG] <b>
[TEXT] 'Hello'
[TAG] <p>
[TEXT] 'This is a'
[TAG] <b>
[TEXT] 'test'
[TEXT] '.'
```

This confirms that:

* The soup object and all tags are visited in depth-first order.
* Text nodes at different depths (`"Hello"`, `"This is a"`, `"test"`, `"."`) are all yielded by the iterator.
* The program is using the new iterable `BeautifulSoup` API exactly as required in Milestone 4.



