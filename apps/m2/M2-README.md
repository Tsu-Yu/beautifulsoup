# Milestone 2 — BeautifulSoup API Exploration & Extension

## Overview
This milestone extends the functionality of BeautifulSoup by:
1. Investigating internal APIs used in Milestone-1 and locating their definitions in the source code (Part 2).  
2. Implementing a new API, **SoupReplacer**, that performs tag replacement *during parsing* (Part 3).  

---

## Part 2 — API Source Code Locations

Below is a list of **all BeautifulSoup APIs** used in Milestone 1 and Milestone 2 (Part 1),  
with their **file locations and line numbers** (from the original `beautifulsoup.zip`).

| API / Class | File Location | Line # | Purpose |
|--------------|---------------|--------|----------|
| **BeautifulSoup** | `bs4/__init__.py` | L133 | Main entry point for parsing HTML/XML into a tree. |
| **Tag.prettify()** | `bs4/element.py` | L2601 | Pretty-prints the entire document or a subtree. |
| **Tag.find_all()** | `bs4/element.py` | L2715 | Finds all tags matching a given name or filter. |
| **Tag.find_parent()** | `bs4/element.py` | L992 | Finds the nearest ancestor tag of a certain type. |
| **Tag.get()** | `bs4/element.py` | L2160 | Retrieves an attribute value by name. |
| **Tag.select()** | `bs4/element.py` | L2799 | Performs CSS-selector-based searches. |
| **Tag.get_text()** | `bs4/element.py` | L524 | Extracts visible text within a tag. |
| **Tag.decompose()** | `bs4/element.py` | L635 | Removes a tag (and its children) from the parse tree. |
| **NavigableString** | `bs4/element.py` | L1274 | Represents raw text inside the tree. |
| **Comment** | `bs4/element.py` | L1472 | Represents an HTML comment node. |
| **SoupStrainer** | `bs4/filter.py` | L313 | Restricts parsing to specific nodes for efficiency. |

### How These Were Located
The following commands were executed to search the BeautifulSoup source:
```bash
grep -Rn "class BeautifulSoup" bs4/
grep -Rn "def prettify" bs4/
grep -Rn "def find_all" bs4/
grep -Rn "class SoupStrainer" bs4/
grep -Rn "class Comment" bs4/
grep -Rn "def find_parent" bs4/
grep -Rn "def get(" bs4/
grep -Rn "def select" bs4/
grep -Rn "def get_text" bs4/
grep -Rn "def decompose" bs4/
grep -Rn "class NavigableString" bs4/
````
Output:
```bash
bs4/__init__.py:133:class BeautifulSoup(Tag):
bs4/element.py:2601:def prettify(
bs4/element.py:2715:def find_all(
bs4/filter.py:313:class SoupStrainer(ElementFilter):
bs4/element.py:1472:class Comment(PreformattedString):
bs4/element.py:992:def find_parent(
bs4/element.py:2160:def get(
bs4/element.py:2799:def select(
bs4/element.py:524:def get_text(
bs4/element.py:635:def decompose(self) -> None:
bs4/element.py:1274:class NavigableString(str, PageElement):
```

### Task-to-API Mapping

| Task           | APIs Used                                                 | Purpose                                        |
| -------------- | --------------------------------------------------------- | ---------------------------------------------- |
| **Task 1**     | `BeautifulSoup`, `prettify()`                             | Pretty-print parsed HTML/XML.                  |
| **Task 2 – 4** | `find_all()`, `get()`, `select()`                         | Find tags, hyperlinks, and elements with `id`. |
| **Task 5**     | `find_parent()`, `get()`                                  | Identify enclosing section/article/div.        |
| **Task 6 – 7** | `find_all()`, `get()`, `get_text()`                       | Modify or add tags/classes.                    |
| **Task 8**     | `find_all()`, `decompose()`, `Comment`, `NavigableString` | Extract readable text.                         |
| **M2 Part 1**  | `SoupStrainer`                                            | Parse only relevant nodes for performance.     |

---

## Part 3 — Implementing `SoupReplacer`

### Objective

Create a new API, **SoupReplacer**, that performs tag replacement **during parsing** (not after).
This avoids a full traversal of the parse tree when modifying tags.

### Implementation Summary

#### New File: `bs4/replacer.py`

```python
class SoupReplacer:
    """Rename tags during parsing: replace every <og_tag> with <alt_tag>."""
    def __init__(self, og_tag: str, alt_tag: str):
        self.og = og_tag
        self.alt = alt_tag

    def maybe(self, name: str) -> str:
        return self.alt if name == self.og else name
```

#### Modified Files

| File                                 | Change                                                                                                                                   |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------- |
| **`bs4/__init__.py`**                | Added `replacer` parameter to `BeautifulSoup.__init__` and stored `self.replacer` before parsing.                                        |
| **`bs4/builder/_htmlparser.py`**     | Added `_map_name()` helper and applied it in `handle_starttag`, `handle_endtag`, and `handle_startendtag` to rename tags during parsing. |
| **`apps/m2/task6.py`**               | Application demonstrating `SoupReplacer` by replacing `<b>` with `<blockquote>`.                                                         |
| **`bs4/tests/test_replacer_api.py`** | New test file verifying that tag replacement occurs correctly during parsing.                                                            |

---

### Example Usage

```python
from bs4 import BeautifulSoup
from bs4.replacer import SoupReplacer

html = "<html><body><b>Bold</b><p>Text <b>Again</b></p></body></html>"
rp = SoupReplacer("b", "blockquote")
soup = BeautifulSoup(html, "html.parser", replacer=rp)
print(soup.prettify())
```

#### Output

```html
<html>
 <body>
  <blockquote>
   Bold
  </blockquote>
  <p>
   Text
   <blockquote>
    Again
   </blockquote>
  </p>
 </body>
</html>
```

---

### Test Cases Summary (`bs4/tests/test_replacer_api.py`)

| Test Name                          | Purpose                                                                 |
| ---------------------------------- | ----------------------------------------------------------------------- |
| `test_replaces_during_parse`       | Confirms all `<b>` tags are replaced by `<blockquote>` during parsing.  |
| `test_with_soupstrainer`           | Ensures `SoupReplacer` works with `SoupStrainer(parse_only=...)`.       |
| `test_no_replacer_does_not_change` | Verifies normal parsing is unaffected when `replacer` is omitted.       |
| `test_custom_tag_pair`             | Tests replacement of arbitrary tag pairs (e.g., `<div>` → `<section>`). |

All tests passed successfully:

```
Ran 4 tests in 0.012s
OK
```

---

### Application Demo (`apps/m2/task6.py`)

Command:

```bash
python3 apps/m2/task6.py samples/sample.html b blockquote
```

Output (`stdout`):

```html
<html>
 <body>
  <blockquote>Hello</blockquote>
  <p>This is a <blockquote>test</blockquote>.</p>
 </body>
</html>
```

---

### Implementation Notes

* `self.replacer` is initialized before `self.builder.initialize_soup(self)` so that builders can access it.
* `_map_name()` in `_htmlparser.py` ensures both start and end tags are replaced consistently.
* Works with any parser that reads `soup.replacer` (currently implemented for `html.parser`).
* Integrates seamlessly with existing APIs like `SoupStrainer`.

