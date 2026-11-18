#!/usr/bin/env python3
"""Lint an investment memo for length, required sections and convergence.

Usage: python3 memo_check.py memo.md [--max-pages 5] [--calc scenarios.json]

--calc takes the JSON from `valuation.py scenarios <input> --json`; the header must then show
the labeled target, fair value today and action price, rounded to the displayed precision (up to 1%).

Page estimate: ~450 English words per dense memo page (tables included); one
English word ~= 1.8 CJK characters. Exit code 1 if any hard check fails.
"""
import json
import re
import sys

REQUIRED = {
    "header line (rating / price / target)": [r"rating|评级", r"target|目标价"],
    "thesis & variant view": [r"variant|consensus|thesis|预期差|共识|核心观点|投资逻辑"],
    "key forces": [r"key forces?|关键力量|核心驱动"],
    "business & competitive position": [r"competit|landscape|moat|竞争|格局|护城河"],
    "core earnings bridge": [r"core (eps|earnings)|gaap\s*(→|->|to)\s*core|核心(eps|盈利|利润)|调整后"],
    "valuation": [r"valuation|估值"],
    "risks": [r"risk|风险"],
    "kill conditions": [r"kill|止损条件|证伪|离场条件"],
    "monitoring / catalysts": [r"monitor|catalyst|watch|跟踪|催化|关注"],
    "sources": [r"source|来源"],
}
FILLER = [
    r"this (report|memo) (aims|seeks|will)", r"it is (important|worth) (to note|noting)", r"in conclusion",
    r"needless to say", r"\bbasically\b", r"\bessentially\b", r"\bactually\b", r"at the end of the day",
    r"本报告旨在", r"值得注意的是", r"综上所述", r"众所周知", r"总的来说",
]


KILL_RX = r"kill condition|止损条件|离场条件|证伪条件|退出条件"
DATE_RX = r"\bby\b|before|within|until|20\d\d|q[1-4]|[1-4]q|fy\s*\d|h[12]\s*['’]?\d|month|quarter|year|截至|之前|前|内|季度|年|月"


def kill_items(text):
    """List items / table rows under the kill-conditions heading or bold label, up to the next heading or label."""
    lines = text.splitlines()
    idx = None
    for i, ln in enumerate(lines):
        if re.search(KILL_RX, ln, re.I) and re.match(r"\s*(#|\*\*|__)", ln):
            idx = i
    if idx is None:
        return None
    items, mode = [], None
    for ln in lines[idx + 1:]:
        st = ln.strip()
        if re.match(r"(#|\*\*[^*]+\*\*\s*[:：]?\s*$)", st) or (st.startswith("**") and items):
            break
        is_list = bool(re.match(r"(?:[-*]|\d+[.)])\s+\S", st))
        is_row = st.startswith("|") and not re.match(r"^\|[-: |]+\|$", st)
        if mode is None and (is_list or is_row):
            mode = "list" if is_list else "table"
        if (mode == "list" and is_list) or (mode == "table" and is_row):
            items.append(st)
        elif st.startswith("|") and mode == "table":
            continue  # separator row
        elif items and (st == "" and mode == "table" or (st and not is_list and not is_row) or (mode == "list" and is_row)):
            break
    if mode == "table" and items:
        items = items[1:]  # drop table header row
    return items


SPLIT_RX = r"stock split|stock dividend|\d+[-‑ ]for[-‑ ]\d+|拆股|送股|分拆"
POST_RX = r"post[- ]split|after the split|split[- ]adjusted|拆股后|送股后|拆分后"


HEADER_FIELDS = (
    ("target", "expected_value", r"\btarget(?: price)?\b|目标价(?:格)?"),
    ("fair value today", "fair_value_today", r"\bfair value(?: today)?\b|(?:当前|今日|当日)?(?:公允|合理|内在)价值"),
    ("action price", "action_price", r"\baction price\b|行动价|买入价|建仓价"),
)


def tie_check(head, calc, fails):
    head = re.sub(r"[*_`]", "", head)
    for label, key, pattern in HEADER_FIELDS:
        if key not in calc or (calc[key] is None and key != "fair_value_today"):
            fails.append(f"Scenarios output lacks {key}.")
            continue
        value = calc[key]
        if value is None:
            continue
        # Optional horizon qualifier belongs to the label, e.g. "Target (3 yr): $120".
        match = re.search(r"(?:" + pattern + r")[ \t]*(?:[(（][^()（）\n|·]*[)）][ \t]*)?"
                          r"[:：=]?[ \t]*(?:≤|<=)?[ \t]*(?:USD|US\$|\$|¥|￥)?[ \t]*"
                          r"(-?\d+(?:,\d{3})*(?:\.\d+)?)(?![\d,.%])", head, re.I)
        if match:
            amount = match[1].replace(",", "")
            decimals = len(amount.partition(".")[2])
            tolerance = min(0.5 * 10 ** -decimals, max(0.005, abs(value) * 0.01))
            if abs(float(amount) - value) <= tolerance + 1e-10:
                continue
        fails.append(f"Header {label} must show its scenarios value ({value:,.2f}).")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    text = open(sys.argv[1], encoding="utf-8").read()
    max_pages = float(sys.argv[sys.argv.index("--max-pages") + 1]) if "--max-pages" in sys.argv else 5.0
    body = re.split(r"\n#+\s*(?:sources|references|来源|资料来源|数据来源|参考)", text, maxsplit=1, flags=re.I)[0]

    cjk = len(re.findall(r"[一-鿿㐀-䶿]", body))
    words = len(re.findall(r"[A-Za-z][A-Za-z'\-]*|\$?\d[\d,.]*%?x?", body))
    equiv = words + cjk / 1.8
    pages = equiv / 450
    lower = text.lower()
    fails, warns = [], []

    if pages > max_pages:
        fails.append(f"Estimated {pages:.1f} pages > {max_pages:.0f}. Cut ~{int(equiv - 450 * max_pages)} word-equivalents (≈{int((equiv - 450 * max_pages) * 1.8)} 字).")
    for name, pats in REQUIRED.items():
        if not all(re.search(p, lower) for p in pats):
            fails.append(f"Missing section/element: {name}")

    items = kill_items(text)
    if items is None:
        fails.append("No kill-conditions heading/label found (e.g. '**Kill conditions**' or '止损条件').")
    else:
        if len(items) < 2:
            fails.append(f"Found {len(items)} kill condition item(s) — need 2–4, one per thesis pillar.")
        for it in items:
            if not re.search(r"\d", it):
                fails.append(f"Kill condition without a number: '{it[:70]}' — make it a measurable threshold.")
            elif not re.search(DATE_RX, it, re.I):
                warns.append(f"Kill condition without a deadline: '{it[:70]}' — add 'by <quarter/date>'.")

    head = "\n".join(text.strip().splitlines()[:6]).lower()
    for label, rx in (("rating", r"rating|评级"), ("target price", r"target|目标价"), ("action price", r"action price|行动价|买入价|建仓价"), ("as-of date", r"as of|截至|\d{4}-\d{2}-\d{2}")):
        if not re.search(rx, head):
            fails.append(f"Header (first lines) lacks {label}.")

    if "--calc" in sys.argv:
        tie_check("\n".join(text.strip().splitlines()[:6]), json.load(open(sys.argv[sys.argv.index("--calc") + 1])), fails)
    if re.search(SPLIT_RX, lower) and re.search(r"pending|effective|announced|将于|生效", lower) and not re.search(POST_RX, head):
        warns.append("A split or stock dividend is mentioned but the header has no post-split values — show pre- and post-split target and action price until it is effective.")

    if not re.search(r"as of|截至|数据日期|\d{4}-\d{2}-\d{2}", lower):
        warns.append("No 'as of' date found — prices and estimates go stale.")
    for f in FILLER:
        for m in re.finditer(f, lower):
            warns.append(f"Filler phrase: '{m.group(0)}' — cut it.")
    for para in re.split(r"\n\s*\n", body):
        if para.lstrip().startswith(("|", "#", "-", "*", ">")):
            continue
        w = len(re.findall(r"[A-Za-z]+", para)) + len(re.findall(r"[一-鿿]", para)) / 1.8
        if w > 130:
            warns.append(f"Paragraph of ~{int(w)} words starting '{para.strip()[:50]}…' — split into bullets or a table.")
    n_tables = len(re.findall(r"^\|[-: |]+\|\s*$", text, re.M))
    if n_tables < 3:
        warns.append(f"Only {n_tables} tables — numbers belong in tables (bridge, valuation, risks, monitoring).")
    if n_tables > 10:
        warns.append(f"{n_tables} tables — too many for 5 pages; merge or move to workpapers.")

    print(f"Length: {words} English words + {cjk} CJK chars ≈ {pages:.1f} pages (limit {max_pages:.0f}); tables: {n_tables}")
    for f in fails:
        print(f"FAIL  {f}")
    for w in warns:
        print(f"WARN  {w}")
    if not fails:
        print("PASS")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
