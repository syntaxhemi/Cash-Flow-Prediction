from enum import StrEnum


class CounterpartyType(StrEnum):
    CUSTOMER = 'customer'
    SUPPLIER = 'supplier'
    LENDER = 'lender'
    OTHER = 'other'
