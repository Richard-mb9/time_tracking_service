from dataclasses import dataclass
from datetime import date


@dataclass
class HolidayDTO:
    date: date
    name: str
