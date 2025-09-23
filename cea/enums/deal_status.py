from enum import StrEnum


class DealStatusEnum(StrEnum):
    PENDING = 'PENDING'
    CONFIRMED = 'CONFIRMED'
    REJECTED = 'REJECTED'
