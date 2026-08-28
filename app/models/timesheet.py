from datetime import datetime, date

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

class Timesheet(Base):
    __tablename__ = "timesheets"

    id: Mapped[int] = mapped_column(Integer,
                                    primary_key= True,
                                    index= True)
    client_id: Mapped[int] = mapped_column(Integer,
                                           nullable= False,
                                           index= True)
    period_start: Mapped[date] = mapped_column(Date, nullable= False)
    period_end: Mapped[date] = mapped_column(Date, nullable= False)

    file_name: Mapped[str] = mapped_column(String(250), nullable= False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(15), nullable= False,
                                        default= "UPLOADED", index= True)
    uploaded_by: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    approved_by: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    entries = relationship("TimesheetEntry", back_populates= "timesheet",
                           cascade= "all, delete-orphan",
                           lazy= "selectin")