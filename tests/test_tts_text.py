import pytest

from samuel.tts.text import normalize_numbers


@pytest.mark.parametrize(
    "text, expected",
    [
        ("I have 10 cats.", "I have ten cats."),
        ("It costs $3.50.", "It costs three dollars, fifty cents."),
        ("$1 or $0.01", "one dollar or one cent"),
        ("£20", "twenty pounds"),
        (
            "In 1999, 2005 and 1900.",
            "In nineteen ninety-nine, two thousand five and nineteen hundred.",
        ),
        ("Pi is 3.14.", "Pi is three point one four."),
        ("Version 2.0.1", "Version two point zero point one"),
        ("The 21st", "The twenty-first"),
        ("1,234 people", "one thousand two hundred thirty-four people"),
        ("50% off", "fifty percent off"),
        ("$1,000,000.50", "one million dollars, fifty cents"),
        ("£1,234", "one thousand two hundred thirty-four pounds"),
        ("1,2,3", "one,two,three"),
        ("No numbers here.", "No numbers here."),
    ],
)
def test_normalize_numbers(text, expected):
    assert normalize_numbers(text) == expected
