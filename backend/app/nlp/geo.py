from __future__ import annotations


KNOWN_GEOTAGS = {
    "india": "India",
    "taiwan": "Taiwan",
    "pakistan": "Pakistan",
    "maharashtra": "Maharashtra",
    "madhya pradesh": "Madhya Pradesh",
    "rajasthan": "Rajasthan",
    "uttar pradesh": "Uttar Pradesh",
    "bihar": "Bihar",
}


def geotag_text(text: str) -> list[str]:
    lowered = text.lower()
    return [label for needle, label in KNOWN_GEOTAGS.items() if needle in lowered]
