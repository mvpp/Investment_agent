#!/usr/bin/env python3
"""List SEC filings and read their text (with grep) — for footnotes XBRL doesn't tag.

Usage:
  python3 filings.py list META --forms 8-K,10-Q,10-K --since 2026-06-30
  python3 filings.py docs META 0001628280-26-066773          # documents in a filing (exhibits)
  python3 filings.py text <document-url> --grep "legal|accru|settlement" --context 400
  python3 filings.py text <document-url> --out q3_10q.txt     # full plain text to a file

`list` (data.sec.gov) works with any User-Agent. `docs`/`text` (www.sec.gov/Archives)
require a contact email: export SEC_USER_AGENT="Your Name your@email.com".
Ticker lookup also needs the email UA; a numeric CIK always works.

Typical uses: the 8-K Ex-99.1 earnings release (management-quantified one-offs),
10-Q/10-K notes (income taxes, legal/contingencies, restructuring, segments, PP&E lives),
and 8-Ks filed AFTER the quarter end (financings, splits, settlements, M&A).
"""
import argparse
import html
import json
import os
import re
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sec_facts import DEFAULT_UA, lookup_cik  # noqa: E402


def ua():
    return os.environ.get("SEC_USER_AGENT", DEFAULT_UA)


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": ua(), "Accept-Encoding": "identity"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        if e.code == 403 and "www.sec.gov" in url:
            sys.exit("403 from www.sec.gov — set SEC_USER_AGENT='Your Name your@email.com' (SEC requires a contact email).")
        raise


def cik_of(x):
    return int(x) if x.isdigit() else lookup_cik(x, ua())[0]


class _Text(HTMLParser):
    BLOCK = {"p", "div", "br", "tr", "li", "h1", "h2", "h3", "h4", "table", "section"}

    def __init__(self):
        super().__init__()
        self.out, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        if tag in self.BLOCK:
            self.out.append("\n")
        if tag in ("td", "th"):
            self.out.append(" | ")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.out.append(data)


def to_text(raw):
    s = raw.decode("utf-8", errors="replace")
    if "<" not in s[:2000]:
        return s
    p = _Text()
    p.feed(s)
    t = html.unescape("".join(p.out)).replace("\xa0", " ")
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"([ \t]*\|[ \t]*)+(?=\S)", " | ", t)
    t = re.sub(r"([ \t]*\|[ \t]*)+\n", "\n", t)
    return re.sub(r"\n\s*\n+", "\n\n", t).strip()


def cmd_list(a):
    cik = cik_of(a.company)
    d = json.loads(get(f"https://data.sec.gov/submissions/CIK{cik:010d}.json"))
    r = d["filings"]["recent"]
    forms = set(a.forms.split(",")) if a.forms else None
    print(f"# {d.get('name')} (CIK {cik})\n")
    print("| Form | Filed | Period | Description | Accession | URL |\n|---|---|---|---|---|---|")
    matches = [i for i in range(len(r["form"]))
               if (not forms or r["form"][i] in forms) and not (a.since and r["filingDate"][i] < a.since)]
    n = 0
    for i in matches:
        acc = r["accessionNumber"][i]
        url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc.replace('-', '')}/{r['primaryDocument'][i]}"
        desc = (r["primaryDocDescription"][i] or "") + (f" items {r['items'][i]}" if r.get("items") and r["items"][i] else "")
        print(f"| {r['form'][i]} | {r['filingDate'][i]} | {r['reportDate'][i]} | {desc} | {acc} | {url} |")
        n += 1
        if n >= a.limit:
            break
    if len(matches) > n:
        print(f"\n⚠ Showing {n} of {len(matches)} matching filings — raise --limit or narrow --forms/--since to see the rest.")
    else:
        print(f"\nAll {n} matching filings shown.")
    if len(r["form"]) and a.since and r["filingDate"][-1] > a.since:
        print("Note: SEC's 'recent' feed (last ~1,000 filings) may not reach back to --since for very active filers.")
    print("8-K item codes: 1.01 material agreement · 2.02 results · 2.03 new debt · 3.02 unregistered equity · 5.02 officer change · 7.01/8.01 other events")


def cmd_docs(a):
    cik = cik_of(a.company)
    acc = a.accession.replace("-", "")
    idx = json.loads(get(f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/index.json"))
    print("| Document | Size | URL |\n|---|---|---|")
    for it in idx["directory"]["item"]:
        name = it["name"]
        if name.endswith((".htm", ".html", ".txt", ".pdf")) and "index" not in name:
            print(f"| {name} | {it.get('size', '')} | https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/{name} |")
    print("\nEarnings releases are usually the exhibit named like *ex99*.htm.")


def cmd_text(a):
    text = to_text(get(a.url))
    if a.out:
        open(a.out, "w", encoding="utf-8").write(text)
        print(f"Wrote {len(text):,} chars to {a.out}")
    if a.grep:
        rx = re.compile(a.grep, re.I)
        last_end = -1
        for m in rx.finditer(text):
            s, e = max(0, m.start() - a.context), min(len(text), m.end() + a.context)
            if s <= last_end:
                continue
            print(f"--- @{m.start():,}\n{text[s:e].strip()}\n")
            last_end = e
    elif not a.out:
        print(text[: a.max_chars])
        if len(text) > a.max_chars:
            print(f"\n[... truncated at {a.max_chars:,} of {len(text):,} chars; use --grep or --out]")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("list")
    p.add_argument("company", help="ticker or CIK")
    p.add_argument("--forms", default="10-K,10-Q,8-K")
    p.add_argument("--since")
    p.add_argument("--limit", type=int, default=60)
    p = sub.add_parser("docs")
    p.add_argument("company")
    p.add_argument("accession")
    p = sub.add_parser("text")
    p.add_argument("url")
    p.add_argument("--grep")
    p.add_argument("--context", type=int, default=300)
    p.add_argument("--out")
    p.add_argument("--max-chars", type=int, default=15000)
    a = ap.parse_args()
    {"list": cmd_list, "docs": cmd_docs, "text": cmd_text}[a.cmd](a)


if __name__ == "__main__":
    main()
