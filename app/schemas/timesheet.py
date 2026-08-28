from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class TimesheetEntryResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    employee_name: str
    regular_hours: Decimal
    overtime_hours: Decimal
    total_hours: Decimal
    hourly_rate: Decimal
    amount: Decimal


class TimesheetResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: int
    period_start: date
    period_end: date
    file_name: str
    status: str
    uploaded_by: int | None
    approved_by: int | None
    uploaded_at: datetime
    approved_at: datetime | None
    entries: list[TimesheetEntryResponse] = []


class TimesheetStatusResponse(BaseModel):

    id: int
    status: str
    message: str