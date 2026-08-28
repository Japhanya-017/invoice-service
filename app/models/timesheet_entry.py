from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TimesheetEntry(Base):
    __tablename__ = "timesheet_entries"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    timesheet_id: Mapped[int] = mapped_column(
        ForeignKey("timesheets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    employee_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    employee_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    regular_hours: Mapped[Decimal] = mapped_column(
        Numeric(8, 2),
        nullable=False,
        default=0,
    )

    overtime_hours: Mapped[Decimal] = mapped_column(
        Numeric(8, 2),
        nullable=False,
        default=0,
    )

    total_hours: Mapped[Decimal] = mapped_column(
        Numeric(8, 2),
        nullable=False,
    )

    hourly_rate: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    timesheet = relationship(
        "Timesheet",
        back_populates="entries",
    )