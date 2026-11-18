"""Turn figure strings ("9.69M", "$942M", "+13%", "1,530") into numbers.

Anything unclear is refused, never guessed: ranges, approximations ("~", "about"),
inequalities ("<1"), stray words, malformed thousands separators.
"""
import re

from .errors import ParseError

UNITS = ("usd", "usd_per_day", "count", "pct", "ratio", "index", "usd_per_share")

_SUFFIX = {"": 1, "K": 1e3, "M": 1e6, "B": 1e9, "T": 1e12}
_NUM = re.compile(
    r"^(?P<sign>[+\-])?"
    r"(?P<dollar>\$)?"
    r"(?P<num>\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)"
    r"(?P<suffix>[KMBT])?"
    r"(?P<pct>%)?$"
)


def parse_number(text, unit):
    """Parse ``text`` for a figure of ``unit``. pct values come back as fractions (13% -> 0.13)."""
    if unit not in UNITS:
        raise ParseError(f"unknown unit {unit!r}")
    if text is None:
        raise ParseError("empty value")
    raw = str(text).strip().replace("−", "-")
    if not raw:
        raise ParseError("empty value")
    if any(tok in raw for tok in ("~", "<", ">", "–", "—", " to ", "about", "approx")):
        raise ParseError(f"{text!r} is a range, approximation or inequality; store a single exact value")
    m = _NUM.match(raw.replace(" ", ""))
    if not m:
        raise ParseError(f"{text!r} is not a clean number")
    value = float(m.group("num").replace(",", "")) * _SUFFIX[m.group("suffix") or ""]
    if m.group("sign") == "-":
        value = -value
    if unit == "pct":
        if not m.group("pct"):
            raise ParseError(f"{text!r}: pct values must carry a % sign")
        if m.group("dollar") or m.group("suffix"):
            raise ParseError(f"{text!r}: pct value with $ or K/M/B suffix")
        return value / 100.0
    if m.group("pct"):
        raise ParseError(f"{text!r}: % sign on a non-pct unit ({unit})")
    if m.group("dollar") and not unit.startswith("usd"):
        raise ParseError(f"{text!r}: $ sign on a non-dollar unit ({unit})")
    return value
