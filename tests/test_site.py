# tests/test_site.py

import html
import itertools
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


def runnable_examples(page: str) -> list[str]:
    blocks = re.findall(r"<pre data-run><code>(.*?)</code></pre>", page, re.DOTALL)
    return [html.unescape(b) for b in blocks]


def test_basics_examples_run_and_print_what_they_claim(capsys):
    # Each data-run example must run offline, and every "# ..." comment right
    # after a print() must match what that print() actually shows.
    page = (ROOT / "site" / "basics.html").read_text()
    examples = runnable_examples(page)
    assert examples, "basics.html has no data-run examples"
    for code in examples:
        lines = code.splitlines()
        claimed = [
            nxt[2:] for line, nxt in itertools.pairwise(lines)
            if line.startswith("print(") and nxt.startswith("# ")
        ]
        exec(compile(code, "basics.html", "exec"), {})  # noqa: S102  our own docs, on purpose
        assert capsys.readouterr().out.splitlines() == claimed


def test_site_pages_link_to_each_other():
    index = (ROOT / "site" / "index.html").read_text()
    basics = (ROOT / "site" / "basics.html").read_text()
    assert 'href="basics.html"' in index
    assert 'href="index.html"' in basics
    for page in (index, basics):
        assert 'href="style.css"' in page
