"""Offline checks for dated calculator facts bound to local filing extracts."""
from datetime import date
import hashlib
import json
import math
from pathlib import Path
import re
from urllib.parse import urlsplit


def number(value, label):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError(f"{label} must be a finite number")
    return value


def positive(value, label):
    if number(value, label) <= 0:
        raise ValueError(f"{label} must be positive")
    return value


def units(cfg):
    # Legacy examples use millions of currency and millions of shares.
    unit = cfg.get("unit", "USD M")
    if not isinstance(unit, str):
        raise ValueError("unit must be a currency and scale, e.g. USD M")
    unit = unit.replace("_", " ")
    if not re.fullmatch(r"[A-Z]{3} (?:units|K|M|B)", unit):
        raise ValueError("unit must give currency and scale, e.g. USD M")
    currency, scale = unit.split()
    if cfg.get("shares_unit", scale) != scale:
        raise ValueError("shares_unit must match the scale of unit")
    return currency, scale


def numeric_fields(obj, prefix=""):
    if isinstance(obj, dict):
        for key, val in obj.items():
            if not key.startswith("_") and key != "evidence":
                yield from numeric_fields(val, f"{prefix}/{key}")
    elif isinstance(obj, list):
        for i, val in enumerate(obj):
            yield from numeric_fields(val, f"{prefix}/{i}")
    elif isinstance(obj, bool):
        if prefix.rsplit("/", 1)[-1] not in ("has_nci", "apply", "investment", "ipo_catch_up", "mid_year", "margin_grid"):
            raise ValueError(f"{prefix} cannot be a boolean")
    elif type(obj) in (int, float):
        yield prefix, number(obj, prefix)


def expected_unit(path, currency, scale):
    key = path.split("/")[-1]
    expected = None
    if key in ("diluted_shares", "core_diluted_shares", "basic_shares", "shares", "valuation_shares"):
        expected = f"shares_{scale}"
    elif key in ("reported_diluted_eps", "price", "fair_value_today", "value_today", "fundamentals_based_target") or (key == "value" and path.startswith("/scenarios/")):
        expected = f"{currency}/share"
    elif key in ("tax_rate", "nci_fraction", "prob", "pos", "probability", "wacc", "cost_of_equity", "dividend_yield",
                 "terminal_growth", "terminal_roic", "margin_of_safety", "hurdle"):
        expected = "ratio"
    elif path.startswith("/gaap/") or key in ("revenue0", "amount", "pretax", "after_tax",
            "alt_normal_pretax", "normal_pretax", "normal_after_tax", "tax_effect", "gross_tax_effect", "cfo", "capex",
            "sbc", "finance_lease_principal", "net_cash", "other_claims", "investments", "cash", "claims", "excess_customer_advances", "maintenance_capex"):
        expected = f"{currency}_{scale}"
    return expected


def verify(cfg, directory, required=False):
    """Return a portable audit trail, or None for a legacy unaudited input."""
    fields = dict(numeric_fields(cfg))
    if "evidence" not in cfg:
        if required or "as_of" in cfg:
            raise ValueError("evidence manifest required for a dated/audited calculation")
        return None
    if not cfg.get("unit"):
        raise ValueError("dated/audited inputs require an explicit currency and scale in unit")
    root = Path(directory)
    manifest = root / cfg["evidence"]
    data = json.loads(manifest.read_text())
    cutoff = date.fromisoformat(cfg["as_of"])
    start, end = (date.fromisoformat(cfg[key]) for key in ("period_start", "period_end"))
    if start > end or end > cutoff:
        raise ValueError("invalid period or period_end after as_of")
    for key in ("ticker", "period_start", "period_end"):
        if not cfg[key] or data[key] != cfg[key]:
            raise ValueError(f"evidence {key} differs from calculator input")
    currency, scale = units(cfg)
    facts = data["facts"]
    missing = fields.keys() - facts.keys()
    if missing:
        raise ValueError(f"missing evidence for {', '.join(sorted(missing))}")
    documents = data.get("documents", {})
    snapshots = {}
    trail = {}
    for path, value in fields.items():
        fact = facts[path]
        if number(fact["value"], path) != value:
            raise ValueError(f"{path} differs from evidence value")
        if not fact.get("unit") or fact.get("confidence") not in ("high", "medium", "low"):
            raise ValueError(f"{path} needs unit and confidence")
        expected = expected_unit(path, currency, scale)
        if expected and fact["unit"] != expected:
            raise ValueError(f"{path} requires {expected}")
        parts = path.strip("/").split("/")
        if parts[0] in ("adjustments", "revenue_adjustments") and fact.get("event_id") != cfg[parts[0]][int(parts[1])].get("event_id"):
            raise ValueError(f"{path} evidence event_id mismatch")
        kind = fact["evidence_type"]
        if kind == "estimate":
            if (path.startswith("/gaap/") and not path.startswith("/gaap/core_")) or not fact.get("method", "").strip():
                raise ValueError(f"{path} needs a reported fact or documented estimate")
            if date.fromisoformat(fact["estimate_date"]) > cutoff:
                raise ValueError(f"{path} estimate postdates as_of")
            trail[path] = dict(fact)
            continue
        if kind != "reported":
            raise ValueError(f"{path} unknown evidence_type")
        verify_reported(path, value, fact, cfg["ticker"], (start, end, cutoff), documents, snapshots, manifest.parent)
        trail[path] = dict(fact)
    return {"as_of": cutoff.isoformat(), "ticker": cfg["ticker"], "period_start": str(start),
            "period_end": str(end), "documents": documents, "facts": trail}


def verify_reported(path, value, fact, ticker, dates, documents, snapshots, directory):
    start, end, cutoff = dates
    doc_id = fact["document"]
    doc = documents[doc_id]
    filed = date.fromisoformat(doc["filing_date"])
    if doc.get("ticker") != ticker:
        raise ValueError(f"{path} source issuer mismatch")
    if filed > cutoff:
        raise ValueError(f"{path} filing postdates as_of")
    url = urlsplit(doc["source_url"])
    if url.scheme != "https" or not url.hostname or not doc.get("form"):
        raise ValueError(f"{path} needs filing form and HTTPS source_url")
    if doc["form"] not in ("IR", "market"):
        accession = doc["accession"]
        if not re.fullmatch(r"\d{10}-\d{2}-\d{6}", accession):
            raise ValueError(f"{path} invalid SEC accession")
        if url.hostname in ("www.sec.gov", "sec.gov") and accession.replace("-", "") not in url.path.split("/"):
            raise ValueError(f"{path} accession differs from SEC URL")
    if doc_id not in snapshots:
        raw = (directory / doc["snapshot"]).read_bytes()
        if hashlib.sha256(raw).hexdigest() != doc["sha256"]:
            raise ValueError(f"{path} filing snapshot checksum mismatch")
        snapshots[doc_id] = raw.decode().splitlines()
    lines = snapshots[doc_id]
    line_no = fact["line"]
    if type(line_no) != int or not 1 <= line_no <= len(lines):
        raise ValueError(f"{path} invalid source line")
    row = lines[line_no - 1].strip()
    label = fact["source_location"]
    if not label.strip() or not row.startswith(label):
        raise ValueError(f"{path} source row label differs")
    tokens = re.findall(r"\(?-?\d[\d,]*(?:\.\d+)?\)?|[—–]", row[len(label):])
    col = fact["column"]
    if type(col) != int or not 1 <= col <= len(tokens):
        raise ValueError(f"{path} invalid source column")
    fiscal_period = fact.get("fiscal_period", [str(start), str(end)])
    observed_start, observed_end = (date.fromisoformat(v) for v in fiscal_period)
    if observed_start > observed_end or observed_end > filed:
        raise ValueError(f"{path} invalid fact period")
    if path.split("/")[1] in ("gaap", "cash", "adjustments", "revenue_adjustments") and (observed_start, observed_end) != (start, end):
        raise ValueError(f"{path} differs from bridge period")
    if doc["column_periods"].get(str(col)) != fiscal_period:
        raise ValueError(f"{path} source column differs from fiscal period")
    token = tokens[col - 1].replace(",", "").replace("(", "-").replace(")", "")
    observed = 0 if token in ("—", "–") else float(token)
    factor = number(fact.get("factor", 1), "source unit/sign factor")
    if factor not in (1, -1, 1000, -1000, .001, -.001, 1e6, -1e6, 1e-6, -1e-6, .01, -.01, 100, -100):
        raise ValueError(f"{path} unsupported source unit/sign factor")
    if not math.isclose(observed * factor, value, rel_tol=1e-12, abs_tol=1e-12):
        raise ValueError(f"{path} differs from filing row and column")
