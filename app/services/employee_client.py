import logging

import httpx
from fastapi import HTTPException, status

from app.core.config import settings


logger = logging.getLogger(__name__)


def get_employee_details(
    employee_id: int,
) -> dict:
    """
    Retrieve employee details from Employee Service.

    Invoice Service does not own Employee data.
    Employee Service remains the source of truth.
    """

    url = (
        f"{settings.EMPLOYEE_SERVICE_URL}"
        f"/employees/{employee_id}"
    )

    logger.info(
        "Requesting employee details | employee_id=%s",
        employee_id,
    )

    try:
        with httpx.Client(
            timeout=10.0
        ) as client:

            response = client.get(url)

    except httpx.TimeoutException:

        logger.error(
            "Employee Service timeout | employee_id=%s",
            employee_id,
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Employee Service request timed out.",
        )

    except httpx.RequestError:

        logger.exception(
            "Employee Service connection failed | employee_id=%s",
            employee_id,
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Employee Service is unavailable.",
        )

    if response.status_code == 404:

        logger.warning(
            "Employee not found | employee_id=%s",
            employee_id,
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Employee {employee_id} "
                "does not exist."
            ),
        )

    if response.status_code != 200:

        logger.error(
            "Employee Service returned unexpected status | "
            "employee_id=%s | status=%s | response=%s",
            employee_id,
            response.status_code,
            response.text,
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Employee Service returned an unexpected response.",
        )

    try:
        employee = response.json()

    except ValueError:

        logger.error(
            "Invalid JSON from Employee Service | "
            "employee_id=%s",
            employee_id,
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Invalid response received from Employee Service.",
        )

    required_fields = {
        "id",
        "first_name",
        "last_name",
        "client_id",
        "hourly_rate",
        "is_active",
    }

    missing_fields = (
        required_fields - employee.keys()
    )

    if missing_fields:

        logger.error(
            "Employee Service response missing fields | "
            "employee_id=%s | missing=%s",
            employee_id,
            missing_fields,
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "Employee Service response is missing "
                "required fields."
            ),
        )

    logger.info(
        "Employee details received | "
        "employee_id=%s | client_id=%s",
        employee_id,
        employee["client_id"],
    )

    return employee