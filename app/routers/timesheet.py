import logging
from datetime import date

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.timesheet import (TimesheetResponse, TimesheetStatusResponse)

from app.services.timesheet_service import (approve_timesheet, get_timesheet, get_timesheets, reject_timesheet, upload_timesheet)

logger = logging.getLogger(__name__)

router = APIRouter(prefix= "/timesheets", tags=["Timesheets"])

@router.post("/upload", response_model=TimesheetResponse, status_code=status.HTTP_201_CREATED)
def upload_timesheet_file(
    client_id: int = Form(...),
    period_start: date = Form(...),
    period_end: date = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """upload a monthly timesheet"""
    logger.info("Timesheet upload API called |" \
    "client_id=%s | filenamr=%s",
    client_id, file.filename)

    return upload_timesheet(db=db, client_id= client_id, peroid_start= period_start,
                            period_end= period_end, file=file)

@router.get("/", response_model=list[TimesheetResponse])
def list_timesheets(db:Session = Depends(get_db)):
    """Get all timesheets"""
    logger.info("timesheet alist api called")

    return get_timesheets(db=db)

@router.get("/{timesheet_id}", response_model=TimesheetResponse)
def get_timesheet_details(timesheet_id: int,
                          db: Session = Depends(get_db)):
    logger.info("timesheet details API called | id=%s",
                timesheet_id)
    return get_timesheet(db=db, timesheet_id=timesheet_id)

@router.put("/{timesheet_id}/approve", response_model= TimesheetStatusResponse)
def approve_timesheet_file(timesheet_id: int, approved_by: int | None,
                           db: Session = Depends(get_db)):
    """Approve a timesheet"""
    logger.info("Timesheet approve API called |" \
    "id=%s | approved_by=%s",
    timesheet_id, approved_by)

    return approve_timesheet(db=db, timesheet_id=timesheet_id, approved_by=approved_by)

@router.put("/{timesheet_id}/reject", response_model= TimesheetStatusResponse)
def reject_timesheet_file(timesheet_id: int, db:Session = Depends(get_db)):
    """Reject a timesheet"""
    logger.info("Timesheet reject API called | id=%s", timesheet_id)

    return reject_timesheet(db=db, timesheet_id= timesheet_id)


    