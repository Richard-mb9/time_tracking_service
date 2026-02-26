from sqlalchemy import Column, Date, Integer, Table, Text

from domain import BankHoursLedger

from . import mapper_registry

bank_hours_ledger = Table(
    "bank_hours_ledger",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("tenant_id", Integer, nullable=False, index=True),
    Column("employee_id", Integer, nullable=False, index=True),
    Column("matricula", Text, nullable=False, index=True),
    Column("event_date", Date, nullable=False),
    Column("minutes_delta", Integer, nullable=False),
    Column("source", Text, nullable=False),
    Column("reference_id", Integer, nullable=True),
)

mapper_registry.map_imperatively(BankHoursLedger, bank_hours_ledger)
