from enum import Enum


class PunchTypeRequestEnum(str, Enum):
    IN = "IN"
    OUT = "OUT"
    BREAK_START = "BREAK_START"
    BREAK_END = "BREAK_END"


class TimeAdjustmentTypeRequestEnum(str, Enum):
    ADD_PUNCH = "ADD_PUNCH"
    EDIT_PUNCH = "EDIT_PUNCH"
    JUSTIFY_ABSENCE = "JUSTIFY_ABSENCE"
    REMOVE_PUNCH = "REMOVE_PUNCH"


class TimeAdjustmentDecisionStatusRequestEnum(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class TimeAdjustmentStatusRequestEnum(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    APPLIED = "APPLIED"


class DailyAttendanceStatusRequestEnum(str, Enum):
    OK = "OK"
    INCOMPLETE = "INCOMPLETE"
    PENDING_ADJUSTMENT = "PENDING_ADJUSTMENT"
    NO_POLICY = "NO_POLICY"


class BankHoursSourceRequestEnum(str, Enum):
    DAILY_APURATION = "DAILY_APURATION"
    MANUAL_ADJUST = "MANUAL_ADJUST"
    ADJUSTMENT_REQUEST = "ADJUSTMENT_REQUEST"
