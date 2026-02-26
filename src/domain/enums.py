from enum import Enum


class PunchType(str, Enum):
    IN = "IN"
    OUT = "OUT"
    BREAK_START = "BREAK_START"
    BREAK_END = "BREAK_END"


class TimeAdjustmentType(str, Enum):
    ADD_PUNCH = "ADD_PUNCH"
    EDIT_PUNCH = "EDIT_PUNCH"
    JUSTIFY_ABSENCE = "JUSTIFY_ABSENCE"
    REMOVE_PUNCH = "REMOVE_PUNCH"


class TimeAdjustmentStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    APPLIED = "APPLIED"


class DailyAttendanceStatus(str, Enum):
    OK = "OK"
    INCOMPLETE = "INCOMPLETE"
    PENDING_ADJUSTMENT = "PENDING_ADJUSTMENT"
    NO_POLICY = "NO_POLICY"


class BankHoursSource(str, Enum):
    DAILY_APURATION = "DAILY_APURATION"
    MANUAL_ADJUST = "MANUAL_ADJUST"
    ADJUSTMENT_REQUEST = "ADJUSTMENT_REQUEST"
