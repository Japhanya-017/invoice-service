from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class InvoiceItemResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    employee_id: int
    employee_name: str
    description: str
    hours: Decimal
    hourly_rate: Decimal
    amount: Decimal


class InvoiceResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    invoice_number: str

    client_id: int
    timesheet_id: int

    invoice_date: date
    due_date: date

    period_start: date
    period_end: date

    subtotal: Decimal
    tax: Decimal
    total: Decimal

    status: str

    created_at: datetime
    updated_at: datetime

    items: list[InvoiceItemResponse] = []


class InvoiceStatusUpdate(BaseModel):
    status: str


class InvoiceStatusResponse(BaseModel):

    id: int
    invoice_number: str
    status: str
    message: str