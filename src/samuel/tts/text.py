"""Spell out numbers before text goes to the TTS model, so that it doesn't have
to guess how to read "10" or "$3.50".

Adapted from the number expansion in Keith Ito's Tacotron ``english_cleaners``
(github.com/keithito/tacotron, text/numbers.py, MIT licence).
"""

import re

import inflect

_inflect = inflect.engine()

_comma_number_re = re.compile(r"\b([0-9]{1,3}(?:,[0-9]{3})+)\b")
_decimal_point_re = re.compile(r"(?<=[0-9])\.([0-9]+)")
_pounds_re = re.compile(r"£([0-9.,]*[0-9]+)")
_dollars_re = re.compile(r"\$([0-9.,]*[0-9]+)")
_percent_re = re.compile(r"([0-9])\s*%")
_ordinal_re = re.compile(r"[0-9]+(st|nd|rd|th)\b")
_number_re = re.compile(r"[0-9]+")


def _words(num: int | str, **kwargs) -> str:
    # inflect separates thousands with commas, which the model would read as pauses.
    return _inflect.number_to_words(num, **kwargs).replace(",", "")


def _expand_dollars(m: re.Match) -> str:
    parts = m.group(1).replace(",", "").split(".")
    if len(parts) > 2:
        return m.group(1) + " dollars"  # Unexpected format
    dollars = int(parts[0]) if parts[0] else 0
    cents = int(parts[1]) if len(parts) > 1 and parts[1] else 0
    dollar_unit = "dollar" if dollars == 1 else "dollars"
    cent_unit = "cent" if cents == 1 else "cents"
    if dollars and cents:
        return f"{dollars} {dollar_unit}, {cents} {cent_unit}"
    if cents:
        return f"{cents} {cent_unit}"
    return f"{dollars} {dollar_unit}"


def _expand_decimal_point(m: re.Match) -> str:
    # "3.14" -> "3 point 1 4": the digits after the point are read one by one.
    return f" point {' '.join(m.group(1))}"


def _expand_number(m: re.Match) -> str:
    num = int(m.group(0))
    # Numbers in this range are most often years: "1999" -> "nineteen ninety-nine".
    if 1000 < num < 3000:
        if num == 2000:
            return "two thousand"
        if 2000 < num < 2010:
            return "two thousand " + _words(num % 100)
        if num % 100 == 0:
            return _words(num // 100) + " hundred"
        return _words(num, andword="", zero="oh", group=2)
    return _words(num, andword="")


def normalize_numbers(text: str) -> str:
    """Spell out the numbers, amounts of money, percentages and ordinals in ``text``."""
    text = _pounds_re.sub(r"\1 pounds", text)
    text = _dollars_re.sub(_expand_dollars, text)
    # Not _expand_number: with thousands separators, it isn't a year.
    text = _comma_number_re.sub(
        lambda m: _words(m.group(1).replace(",", ""), andword=""), text
    )
    text = _percent_re.sub(r"\1 percent", text)
    text = _decimal_point_re.sub(_expand_decimal_point, text)
    text = _ordinal_re.sub(lambda m: _words(m.group(0)), text)
    text = _number_re.sub(_expand_number, text)
    return text
