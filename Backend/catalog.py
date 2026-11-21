"""Suggested values for the treatment form. The columns are free text, so these are only suggestions."""
from typing import Tuple

ACTIONS: Tuple[str, ...] = (
    "root canal treatment",
    "dental filling",
    "teeth whitening",
    "tooth decay treatment",
    "dental implant",
)

COMPLAINTS: Tuple[str, ...] = (
    "annual inspection",
    "general inspection",
    "inspection after treatmen",  # the spelling of the existing rows is kept, so statistics keep matching
    "toothache",
)

COMPLAINT_LABELS = {"inspection after treatmen": "inspection after treatment"}


def complaint_label(value: str) -> str:
    return COMPLAINT_LABELS.get(value, value)
