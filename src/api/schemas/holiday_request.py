from datetime import date

from pydantic import BaseModel


class HolidayRequest(BaseModel):
    date: date
    name: str
