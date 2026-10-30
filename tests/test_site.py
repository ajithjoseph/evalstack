# tests/test_site.py

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def python_block(text: str) -> str:
    """The first code block that imports evalstack, whitespace-trimmed."""
    for block in re.findall(r"```python\n(.*?)```|<code>(.*?)</code>", text, re.DOTALL):
        code = html.unescape(block[0] or block[1]).strip()
        if code.startswith("from evalstack"):
            return code
    raise AssertionError("no evalstack code block found")


def test_site_quick_start_matches_readme():
    readme = (ROOT / "README.md").read_text()
    site = (ROOT / "site" / "index.html").read_text()
    assert python_block(site) == python_block(readme)
