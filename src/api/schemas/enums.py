from enum import Enum


class PunchTypeRequestEnum(str, Enum):
    IN = "IN"
    OUT = "OUT"


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


class WorkWeekDayRequestEnum(str, Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


class UfRequestEnum(str, Enum):
    AC = "AC"
    AL = "AL"
    AP = "AP"
    AM = "AM"
    BA = "BA"
    CE = "CE"
    DF = "DF"
    ES = "ES"
    GO = "GO"
    MA = "MA"
    MT = "MT"
    MS = "MS"
    MG = "MG"
    PA = "PA"
    PB = "PB"
    PR = "PR"
    PE = "PE"
    PI = "PI"
    RJ = "RJ"
    RN = "RN"
    RS = "RS"
    RO = "RO"
    RR = "RR"
    SC = "SC"
    SP = "SP"
    SE = "SE"
    TO = "TO"
