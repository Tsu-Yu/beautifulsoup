# Milestone-3

## Goal

Extend the `SoupReplacer` API from Milestone 2 so that tag transformations happen **during parsing**, and are no longer limited to simple renames. The new API supports:

```python
SoupReplacer(name_xformer=None, attrs_xformer=None, xformer=None)
```

where each transformer is a callable receiving a **Tag** node:

* `name_xformer(tag) -> str`
  Return the (possibly new) tag name.

* `attrs_xformer(tag) -> dict`
  Return a full attributes dictionary for the tag.

* `xformer(tag) -> None`
  Arbitrary side effects on the tag (e.g., edit text, remove attrs). No return value.

> Backward compatibility: the M2 constructor `SoupReplacer(og_tag, alt_tag)` is still supported. Mixed usage (pair + keyword transformers at once) raises `ValueError`.

---

## Why M3 (Design Rationale)

### M2 (pair-based) — Pros / Cons

**Pros**

* Tiny, obvious surface area.
* Easy to reason about and test.

**Cons**

* Can only rename one tag to another.
* Cannot modify attributes or contents.
* Encourages out-of-band post-processing (walk the tree after parsing).

### M3 (transformer-based) — Pros / Cons

**Pros**

* Enables **all** common transformations at parse-time:

  * Conditional or global renames.
  * Attribute normalization and injection.
  * In-place content edits (e.g., text, children, cleanup).
* Composable and testable via small lambdas/functions.
* Keeps behavior localized to parsing (no second pass).

**Cons**

* More powerful = more responsibility.
  Poorly written transformers can be non-idempotent or order-sensitive.

### Recommendation

Ship the **M3 API** as the primary interface, while keeping **M2 pair constructor** for smooth migration. Mark the M2 helper `maybe()` as **deprecated**. Provide adapter glue so M2 remains functional, but document M3 as the long-term path.

---

## Public API (M3)

```python
from bs4.replacer import SoupReplacer

# 1) Rename <b> → <blockquote>
b_to_blockquote = SoupReplacer(
    name_xformer=lambda tag: "blockquote" if tag.name == "b" else tag.name
)

# 2) Drop the "class" attribute everywhere
def remove_class(tag):
    if "class" in tag.attrs:
        del tag.attrs["class"]

class_deleter = SoupReplacer(xformer=remove_class)

# 3) Rebuild attributes dict (return a new dict)
def strip_class_and_mark(tag):
    attrs = dict(tag.attrs)
    attrs.pop("class", None)
    attrs["data-x"] = "1"
    return attrs

attrs_mutator = SoupReplacer(attrs_xformer=strip_class_and_mark)
```

> **Order of operations** per tag:
> `name_xformer` → `attrs_xformer` → `xformer`.

---

## Integration Into BeautifulSoup (Parsing-time Execution)

To ensure transformations apply as the tree is built (not after):

1. **Add** a private helper in `BeautifulSoup`:

```python
def _apply_replacer(self, tag) -> None:
    r = getattr(self, "replacer", None)
    if not r:
        return
    if hasattr(r, "transform"):
        r.transform(tag)            # M3 path (name → attrs → node)
        return
    if hasattr(r, "maybe"):         # M2 compatibility
        new_name = r.maybe(tag.name)
        if isinstance(new_name, str) and new_name and new_name != tag.name:
            tag.name = new_name
```

2. **Call it right after a Tag is created** (inside `BeautifulSoup.handle_starttag(...)`), before `pushTag(tag)`.

3. **Call it again just before closing the tag** (inside `BeautifulSoup.handle_endtag(...)`) so `xformer` sees the tag with finalized text/children. When popping, use the actual `currentTag.name` to tolerate rename:

```python
self._apply_replacer(self.currentTag)
name_to_pop = self.currentTag.name  # use new name if renamed
self._popToTag(name_to_pop, nsprefix)
```

4. In the **HTML parser builder** (`bs4/builder/_htmlparser.py`), neutralize any early renaming:

   * `_map_name(name)` should **just return `name`** (do not call `replacer.maybe()` here).
     All transformations happen after the `Tag` exists, via `_apply_replacer`.

This design guarantees:

* Transformers see a real `Tag` (with `.attrs`, `.get()`, children, etc.).
* `xformer` can safely modify final text.
* End-tag pop works even if start-tag was renamed.

---

## Backward Compatibility

* M2 constructor `(og_tag, alt_tag)` is recognized and internally wrapped as a `name_xformer`.
* `SoupReplacer.maybe(tag_name)` still works but **emits `DeprecationWarning`** and is no longer used by the builder.
* If both M2 pair and M3 keyword arguments are passed → `ValueError` to avoid ambiguity.

---

## Testing (6 new tests)

File: `beautifulsoup/bs4/tests/test_replacer_m3.py`

1. **M2 compatibility**: `(og_tag, alt_tag)` still renames `<b>` → `<blockquote>`.
2. **name_xformer**: conditional rename only for `<b>`, pass-through otherwise.
3. **attrs_xformer**: returns a new dict, e.g., remove `class`, add `data-x`.
4. **xformer side effects**: in-place mutation (uppercase text, drop `role` attr).
5. **Conflict guard**: using pair constructor **and** keyword transformers raises `ValueError`.
6. **Order guarantee**: `name_xformer → attrs_xformer → xformer` on the same tag; attrs sees new name; xformer sees both changes and mutates text.

> All tests expect the transformation to happen **during parsing** (i.e., by passing `replacer=...` to the `BeautifulSoup` constructor).

Run:

```bash
python3 -m unittest discover -s bs4/tests -p "test_replacer_m3.py" -v
```

---

## Sample App (Task-7 Reimplementation)

File: `beautifulsoup/apps/m3/task7.py`

**Goal:** During parsing, ensure every `<p>` has `class="test"` (merging with existing classes, not overwriting). Implemented via `attrs_xformer`:

```bash
PYTHONPATH=. python3 apps/m3/task7.py samples/sample.html
# → writes samples/sample.p-test.html
```



---

## Performance & Safety

* **Performance**: negligible overhead for small/medium documents. For large docs, keep transformers cheap and idempotent.
* **Safety**: avoid non-deterministic mutations (e.g., random renames) and infinite loops (don’t create/remove nodes in a way that breaks builder invariants).

---

## Known Limitations / Notes

* If you use multiple tree builders (e.g., `html.parser`, `lxml`), ensure they all **avoid** calling `maybe()` early and rely on the **post-creation hooks** instead. (This README assumes `html.parser` path is fully wired; apply analogous hooks for others if needed.)
* `attrs_xformer` must return a **complete** attribute dict (not a partial diff).
* End-tag name mapping must use the **actual `currentTag.name`** to tolerate renames.

---

## Migration Guidance

* Existing M2 users can keep using `(og_tag, alt_tag)` unchanged.
* Recommend migrating to M3:

  * Replace renames with `name_xformer`.
  * Replace attribute edits with `attrs_xformer`.
  * Move any post-parse cleanups into `xformer` where possible.
* Treat `maybe()` as deprecated (tests may assert a warning).

---