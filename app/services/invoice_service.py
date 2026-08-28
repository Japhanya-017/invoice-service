import logging
from datetime import date, timedelta
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem
from app.models.timesheet import Timesheet
from app.utils.calculations import (
    calculate_amount,
    calculate_subtotal,
    calculate_total,
)


logger = logging.getLogger(__name__)


VALID_INVOICE_STATUSES = {
    "DRAFT",
    "GENERATED",
    "SENT",
    "OVERDUE",
    "PARTIALLY_PAID",
    "PAID",
    "CANCELLED",
}


def generate_invoice(
    db: Session,
    timesheet_id: int,
    due_days: int = 15,
):
    """
    Generate an invoice from an approved timesheet.
    """

    logger.info(
        "Starting invoice generation | timesheet_id=%s",
        timesheet_id,
    )

    timesheet = (
        db.query(Timesheet)
        .filter(
            Timesheet.id == timesheet_id
        )
        .first()
    )

    if not timesheet:

        logger.warning(
            "Timesheet not found | id=%s",
            timesheet_id,
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timesheet not found.",
        )

    if timesheet.status != "APPROVED":

        logger.warning(
            "Invoice generation rejected | "
            "timesheet_id=%s | status=%s",
            timesheet_id,
            timesheet.status,
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invoice can only be generated "
                "from an approved timesheet."
            ),
        )

    existing_invoice = (
        db.query(Invoice)
        .filter(
            Invoice.timesheet_id == timesheet_id
        )
        .first()
    )

    if existing_invoice:

        logger.warning(
            "Invoice already exists | "
            "timesheet_id=%s | invoice_id=%s",
            timesheet_id,
            existing_invoice.id,
        )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "An invoice already exists "
                "for this timesheet."
            ),
        )

    if not timesheet.entries:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Timesheet has no entries.",
        )

    amounts = []

    for entry in timesheet.entries:

        amount = calculate_amount(
            entry.total_hours,
            entry.hourly_rate,
        )

        entry.amount = amount

        amounts.append(amount)

    subtotal = calculate_subtotal(
        amounts
    )

    # Tax is zero for the current MVP.
    # We can add configurable tax later.
    tax = Decimal("0.00")

    total = calculate_total(
        subtotal,
        tax,
    )

    invoice_date = date.today()

    due_date = (
        invoice_date +
        timedelta(days=due_days)
    )

    invoice = Invoice(
        invoice_number="TEMP",
        client_id=timesheet.client_id,
        timesheet_id=timesheet.id,
        invoice_date=invoice_date,
        due_date=due_date,
        period_start=timesheet.period_start,
        period_end=timesheet.period_end,
        subtotal=subtotal,
        tax=tax,
        total=total,
        status="GENERATED",
    )

    db.add(invoice)

    # Get database-generated invoice ID.
    db.flush()

    invoice.invoice_number = (
        f"INV-{invoice_date.year}-"
        f"{invoice.id:05d}"
    )

    for entry in timesheet.entries:

        invoice_item = InvoiceItem(
            invoice_id=invoice.id,
            employee_id=entry.employee_id,
            employee_name=entry.employee_name,
            description=(
                "Consulting services - "
                f"{timesheet.period_start} "
                f"to {timesheet.period_end}"
            ),
            hours=entry.total_hours,
            hourly_rate=entry.hourly_rate,
            amount=entry.amount,
        )

        db.add(invoice_item)

    timesheet.status = "INVOICED"

    try:

        db.commit()
        db.refresh(invoice)

    except Exception:

        db.rollback()

        logger.exception(
            "Failed to generate invoice | "
            "timesheet_id=%s",
            timesheet_id,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate invoice.",
        )

    logger.info(
        "Invoice generated successfully | "
        "invoice_id=%s | invoice_number=%s | "
        "timesheet_id=%s | total=%s",
        invoice.id,
        invoice.invoice_number,
        timesheet_id,
        invoice.total,
    )

    return invoice


def get_invoices(
    db: Session,
):
    """
    Get all invoices.
    """

    logger.info(
        "Fetching all invoices"
    )

    return (
        db.query(Invoice)
        .order_by(
            Invoice.created_at.desc()
        )
        .all()
    )


def get_invoice(
    db: Session,
    invoice_id: int,
):
    """
    Get one invoice by ID.
    """

    invoice = (
        db.query(Invoice)
        .filter(
            Invoice.id == invoice_id
        )
        .first()
    )

    if not invoice:

        logger.warning(
            "Invoice not found | id=%s",
            invoice_id,
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found.",
        )

    return invoice


def update_invoice_status(
    db: Session,
    invoice_id: int,
    new_status: str,
):
    """
    Update invoice status.

    This is intentionally a controlled status update.
    """

    new_status = new_status.upper().strip()

    if new_status not in VALID_INVOICE_STATUSES:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid invoice status: "
                f"{new_status}"
            ),
        )

    invoice = get_invoice(
        db=db,
        invoice_id=invoice_id,
    )

    current_status = invoice.status

    # Prevent modification of a paid invoice
    # through the normal invoice API.
    if current_status == "PAID":

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "A paid invoice cannot be "
                "manually modified."
            ),
        )

    allowed_transitions = {
        "DRAFT": {
            "GENERATED",
            "CANCELLED",
        },

        "GENERATED": {
            "SENT",
            "CANCELLED",
        },

        "SENT": {
            "OVERDUE",
            "PARTIALLY_PAID",
            "PAID",
            "CANCELLED",
        },

        "OVERDUE": {
            "PARTIALLY_PAID",
            "PAID",
            "CANCELLED",
        },

        "PARTIALLY_PAID": {
            "PAID",
        },

        "CANCELLED": set(),

        "PAID": set(),
    }

    if new_status == current_status:

        return {
            "id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "status": invoice.status,
            "message": (
                "Invoice is already in "
                f"{invoice.status} status."
            ),
        }

    if new_status not in allowed_transitions.get(
        current_status,
        set(),
    ):

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invoice cannot move from "
                f"{current_status} to {new_status}."
            ),
        )

    invoice.status = new_status

    db.commit()
    db.refresh(invoice)

    logger.info(
        "Invoice status updated | "
        "invoice_id=%s | invoice_number=%s | "
        "%s -> %s",
        invoice.id,
        invoice.invoice_number,
        current_status,
        new_status,
    )

    return {
        "id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "status": invoice.status,
        "message": (
            "Invoice status updated successfully."
        ),
    }


def delete_invoice(
    db: Session,
    invoice_id: int,
):
    """
    Delete an invoice.

    Only generated/draft/cancelled invoices can be
    physically deleted.

    Sent/paid invoices should remain for accounting history.
    """

    invoice = get_invoice(
        db=db,
        invoice_id=invoice_id,
    )

    if invoice.status in {
        "SENT",
        "OVERDUE",
        "PARTIALLY_PAID",
        "PAID",
    }:

        logger.warning(
            "Invoice deletion rejected | "
            "invoice_id=%s | status=%s",
            invoice_id,
            invoice.status,
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Sent, overdue, partially paid, or paid "
                "invoices cannot be deleted."
            ),
        )

    invoice_number = invoice.invoice_number

    try:

        db.delete(invoice)

        db.commit()

    except Exception:

        db.rollback()

        logger.exception(
            "Failed to delete invoice | "
            "invoice_id=%s",
            invoice_id,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete invoice.",
        )

    logger.info(
        "Invoice deleted | "
        "invoice_id=%s | invoice_number=%s",
        invoice_id,
        invoice_number,
    )

    return {
        "message": (
            f"Invoice {invoice_number} "
            "deleted successfully."
        )
    }