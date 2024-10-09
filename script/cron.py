from typing import Union
from datetime import datetime


class AnyValue:
    def __str__(self):
        return "*"
    
    def is_match(self, value: int):
        return True


class MultipleValue:
    def __init__(self, n: int):
        self.n = n

    def __str__(self):
        return f"*/{self.n}"
    
    def is_match(self, value: int):
        return value % self.n == 0

class SpecificValue:
    def __init__(self, value: int):
        self.value = value

    def __str__(self):
        return str(self.value)
    
    def is_match(self, value: int):
        return value == self.value
    
CronElement = Union[AnyValue, MultipleValue, SpecificValue]

class CronSetting:
    def __init__(
        self,
        month: CronElement,
        day: CronElement,
        hour: CronElement,
        minute: CronElement,
    ):
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute

    def __str__(self):
        return f"{self.minute} {self.hour} {self.day} {self.month}"

    def is_match(self, dt: datetime):
        return any(
            [
                self.minute.is_match(dt.minute),
                self.hour.is_match(dt.hour),
                self.day.is_match(dt.day),
                self.month.is_match(dt.month),
            ]
        )
    
    @classmethod
    def from_str(cls, s: str) -> "CronSetting":
        elements = s.split()
        return cls(
            month=cls._parse_element(elements[3]),
            day=cls._parse_element(elements[2]),
            hour=cls._parse_element(elements[1]),
            minute=cls._parse_element(elements[0]),
        )
    
    @staticmethod
    def _parse_element(s: str) -> CronElement:
        if s == "*":
            return AnyValue()
        if s.startswith("*/"):
            return MultipleValue(int(s[2:]))
        return SpecificValue(int(s))