import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.invoice import (
    InvoiceResponse,
    InvoiceStatusResponse,
    InvoiceStatusUpdate,
)
from app.services.invoice_service import (
    delete_invoice,
    generate_invoice,
    get_invoice,
    get_invoices,
    update_invoice_status,
)


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/invoices",
    tags=["Invoices"],
)


@router.post(
    "/generate/{timesheet_id}",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_invoice(
    timesheet_id: int,
    db: Session = Depends(get_db),
):
    """
    Generate an invoice from an approved timesheet.
    """

    logger.info(
        "Generate invoice request | timesheet_id=%s",
        timesheet_id,
    )

    return generate_invoice(
        db=db,
        timesheet_id=timesheet_id,
    )


@router.get(
    "/",
    response_model=list[InvoiceResponse],
)
def list_invoices(
    db: Session = Depends(get_db),
):
    """
    Get all invoices.
    """

    logger.info(
        "List invoices request"
    )

    return get_invoices(
        db=db,
    )


@router.get(
    "/{invoice_id}",
    response_model=InvoiceResponse,
)
def get_invoice_details(
    invoice_id: int,
    db: Session = Depends(get_db),
):
    """
    Get invoice details.
    """

    logger.info(
        "Get invoice request | invoice_id=%s",
        invoice_id,
    )

    return get_invoice(
        db=db,
        invoice_id=invoice_id,
    )


@router.put(
    "/{invoice_id}/status",
    response_model=InvoiceStatusResponse,
)
def update_status(
    invoice_id: int,
    payload: InvoiceStatusUpdate,
    db: Session = Depends(get_db),
):
    """
    Update invoice status.
    """

    logger.info(
        "Update invoice status request | "
        "invoice_id=%s | status=%s",
        invoice_id,
        payload.status,
    )

    return update_invoice_status(
        db=db,
        invoice_id=invoice_id,
        new_status=payload.status,
    )


@router.delete(
    "/{invoice_id}",
)
def remove_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
):
    """
    Delete an invoice.
    """

    logger.info(
        "Delete invoice request | invoice_id=%s",
        invoice_id,
    )

    return delete_invoice(
        db=db,
        invoice_id=invoice_id,
    )