# bs4/replacer.py
import warnings
class SoupReplacer:
    # M2 version
    # def __init__(self, og_tag, alt_tag):
    #     self.og_tag = og_tag
    #     self.alt_tag = alt_tag

    # def maybe(self, tag_name: str) -> str:
    #     return self.alt_tag if tag_name == self.og_tag else tag_name

    # M3 + M2 version
    def __init__(self, *args, name_xformer=None, attrs_xformer=None, xformer=None):
        if len(args) == 2 and not any([name_xformer, attrs_xformer, xformer]):
            og, alt = args
            self._name_x = lambda tag, _og=og, _alt=alt: _alt if tag.name == _og else tag.name
            self._attrs_x = None
            self._node_x = None
            self._legacy = (og, alt)
        elif len(args) == 0:
            self._name_x = name_xformer
            self._attrs_x = attrs_xformer
            self._node_x = xformer
            self._legacy = None
        else:
            raise ValueError("Use (og_tag, alt_tag) OR keyword xformers, not both.")

    def maybe(self, tag_name: str) -> str:
        warnings.warn("maybe() is deprecated; use name_xformer instead.", DeprecationWarning)
        if not self._name_x:
            return tag_name
        class _Tmp: 
            def __init__(self, name): self.name = name; self.attrs = {}
        return self._name_x(_Tmp(tag_name))

    def transform(self, tag) -> None:
        if self._name_x:
            new_name = self._name_x(tag)
            if isinstance(new_name, str) and new_name and new_name != tag.name:
                tag.name = new_name
        if self._attrs_x:
            new_attrs = self._attrs_x(tag)
            if isinstance(new_attrs, dict):
                tag.attrs = new_attrs
        if self._node_x:
            self._node_x(tag)