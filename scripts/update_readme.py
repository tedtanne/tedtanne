"""Refresh the writing lists in README.md from tedtanner.org (WordPress REST API).

Rewrites only the text between the <!-- recent:start/end --> and
<!-- snakebytes:start/end --> markers. Run daily by .github/workflows/refresh.yml.
"""
import html
import json
import re
import urllib.request
from datetime import datetime

SITE = "https://www.tedtanner.org"
UA = {"User-Agent": "tedtanne-profile-readme/1.0 (+https://github.com/tedtanne)"}


def fetch(path):
    req = urllib.request.Request(SITE + path, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def title(p):
    return html.unescape(re.sub(r"<[^>]+>", "", p["title"]["rendered"])).strip()


def month(p):
    return datetime.fromisoformat(p["date"]).strftime("%B %Y")


def line(p):
    t = title(p).replace("[", "\\[").replace("]", "\\]")
    return f"- [{t}]({p['link']}) <sub>{month(p)}</sub>"


def splice(text, name, body):
    pat = re.compile(rf"(<!-- {name}:start -->\n).*?(\n<!-- {name}:end -->)", re.S)
    return pat.sub(lambda m: m.group(1) + body + m.group(2), text)


def main():
    latest = fetch("/wp-json/wp/v2/posts?per_page=15&_fields=title,link,date")
    found = fetch("/wp-json/wp/v2/posts?search=SnakeByte&per_page=100&_fields=title,link,date")
    snakes = [p for p in found if title(p).lower().startswith("snakebyte")]
    recent = [p for p in latest if not title(p).lower().startswith("snakebyte")][:5]

    readme = open("README.md", encoding="utf-8").read()
    readme = splice(readme, "recent", "\n".join(line(p) for p in recent))
    readme = splice(readme, "snakebytes", "\n".join(line(p) for p in snakes[:5]))
    open("README.md", "w", encoding="utf-8").write(readme)


if __name__ == "__main__":
    main()
