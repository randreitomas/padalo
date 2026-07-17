from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Annotated

from fastapi import APIRouter, Query, Response, status

from app.api.dependencies import (
    BillServiceDependency,
    DashboardServiceDependency,
    EnvelopeServiceDependency,
    RemittanceServiceDependency,
    TransactionServiceDependency,
)
from app.api.routers.common import PaginationDependency
from app.schemas.bills import BillCreate, BillRead, BillStatus, BillUpdate
from app.schemas.common import PaginatedResponse
from app.schemas.dashboard import DashboardSummaryRead
from app.schemas.envelopes import EnvelopeCreate, EnvelopeRead, EnvelopeUpdate
from app.schemas.remittances import RemittanceCreate, RemittanceRead, RemittanceUpdate
from app.schemas.transactions import TransactionCreate, TransactionRead, TransactionUpdate

router = APIRouter(prefix="/api/v1/households/{household_id}")


@router.get("/envelopes", response_model=PaginatedResponse[EnvelopeRead], tags=["envelopes"])
def list_envelopes(
    household_id: uuid.UUID,
    pagination: PaginationDependency,
    service: EnvelopeServiceDependency,
) -> dict:
    return {
        "items": service.list(household_id, limit=pagination.limit, offset=pagination.offset),
        "limit": pagination.limit,
        "offset": pagination.offset,
    }


@router.post(
    "/envelopes",
    response_model=EnvelopeRead,
    status_code=status.HTTP_201_CREATED,
    tags=["envelopes"],
)
def create_envelope(
    household_id: uuid.UUID, payload: EnvelopeCreate, service: EnvelopeServiceDependency
) -> object:
    return service.create(household_id, payload)


@router.get("/envelopes/{envelope_id}", response_model=EnvelopeRead, tags=["envelopes"])
def get_envelope(
    household_id: uuid.UUID, envelope_id: uuid.UUID, service: EnvelopeServiceDependency
) -> object:
    return service.get(household_id, envelope_id)


@router.patch("/envelopes/{envelope_id}", response_model=EnvelopeRead, tags=["envelopes"])
def update_envelope(
    household_id: uuid.UUID,
    envelope_id: uuid.UUID,
    payload: EnvelopeUpdate,
    service: EnvelopeServiceDependency,
) -> object:
    return service.update(household_id, envelope_id, payload)


@router.delete(
    "/envelopes/{envelope_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    tags=["envelopes"],
)
def delete_envelope(
    household_id: uuid.UUID, envelope_id: uuid.UUID, service: EnvelopeServiceDependency
) -> Response:
    service.delete(household_id, envelope_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/transactions",
    response_model=PaginatedResponse[TransactionRead],
    tags=["transactions"],
)
def list_transactions(
    household_id: uuid.UUID,
    pagination: PaginationDependency,
    service: TransactionServiceDependency,
    envelope_id: uuid.UUID | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> dict:
    return {
        "items": service.list(
            household_id,
            limit=pagination.limit,
            offset=pagination.offset,
            envelope_id=envelope_id,
            start_date=start_date,
            end_date=end_date,
        ),
        "limit": pagination.limit,
        "offset": pagination.offset,
    }


@router.post(
    "/transactions",
    response_model=TransactionRead,
    status_code=status.HTTP_201_CREATED,
    tags=["transactions"],
)
def create_transaction(
    household_id: uuid.UUID, payload: TransactionCreate, service: TransactionServiceDependency
) -> object:
    return service.create(household_id, payload)


@router.get("/transactions/{transaction_id}", response_model=TransactionRead, tags=["transactions"])
def get_transaction(
    household_id: uuid.UUID, transaction_id: uuid.UUID, service: TransactionServiceDependency
) -> object:
    return service.get(household_id, transaction_id)


@router.patch(
    "/transactions/{transaction_id}",
    response_model=TransactionRead,
    tags=["transactions"],
)
def update_transaction(
    household_id: uuid.UUID,
    transaction_id: uuid.UUID,
    payload: TransactionUpdate,
    service: TransactionServiceDependency,
) -> object:
    return service.update(household_id, transaction_id, payload)


@router.delete(
    "/transactions/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    tags=["transactions"],
)
def delete_transaction(
    household_id: uuid.UUID,
    transaction_id: uuid.UUID,
    service: TransactionServiceDependency,
) -> Response:
    service.delete(household_id, transaction_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/remittances", response_model=PaginatedResponse[RemittanceRead], tags=["remittances"])
def list_remittances(
    household_id: uuid.UUID,
    pagination: PaginationDependency,
    service: RemittanceServiceDependency,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
) -> dict:
    return {
        "items": service.list(
            household_id,
            limit=pagination.limit,
            offset=pagination.offset,
            start_at=start_at,
            end_at=end_at,
        ),
        "limit": pagination.limit,
        "offset": pagination.offset,
    }


@router.post(
    "/remittances",
    response_model=RemittanceRead,
    status_code=status.HTTP_201_CREATED,
    tags=["remittances"],
)
def create_remittance(
    household_id: uuid.UUID, payload: RemittanceCreate, service: RemittanceServiceDependency
) -> object:
    return service.create(household_id, payload)


@router.get("/remittances/{remittance_id}", response_model=RemittanceRead, tags=["remittances"])
def get_remittance(
    household_id: uuid.UUID, remittance_id: uuid.UUID, service: RemittanceServiceDependency
) -> object:
    return service.get(household_id, remittance_id)


@router.patch("/remittances/{remittance_id}", response_model=RemittanceRead, tags=["remittances"])
def update_remittance(
    household_id: uuid.UUID,
    remittance_id: uuid.UUID,
    payload: RemittanceUpdate,
    service: RemittanceServiceDependency,
) -> object:
    return service.update(household_id, remittance_id, payload)


@router.delete(
    "/remittances/{remittance_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    tags=["remittances"],
)
def delete_remittance(
    household_id: uuid.UUID, remittance_id: uuid.UUID, service: RemittanceServiceDependency
) -> Response:
    service.delete(household_id, remittance_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/bills", response_model=PaginatedResponse[BillRead], tags=["bills"])
def list_bills(
    household_id: uuid.UUID,
    pagination: PaginationDependency,
    service: BillServiceDependency,
    status_filter: Annotated[BillStatus | None, Query(alias="status")] = None,
    due_from: date | None = None,
    due_to: date | None = None,
) -> dict:
    return {
        "items": service.list(
            household_id,
            limit=pagination.limit,
            offset=pagination.offset,
            status=status_filter.value if status_filter is not None else None,
            due_from=due_from,
            due_to=due_to,
        ),
        "limit": pagination.limit,
        "offset": pagination.offset,
    }


@router.post(
    "/bills",
    response_model=BillRead,
    status_code=status.HTTP_201_CREATED,
    tags=["bills"],
)
def create_bill(
    household_id: uuid.UUID, payload: BillCreate, service: BillServiceDependency
) -> object:
    return service.create(household_id, payload)


@router.get("/bills/{bill_id}", response_model=BillRead, tags=["bills"])
def get_bill(household_id: uuid.UUID, bill_id: uuid.UUID, service: BillServiceDependency) -> object:
    return service.get(household_id, bill_id)


@router.patch("/bills/{bill_id}", response_model=BillRead, tags=["bills"])
def update_bill(
    household_id: uuid.UUID,
    bill_id: uuid.UUID,
    payload: BillUpdate,
    service: BillServiceDependency,
) -> object:
    return service.update(household_id, bill_id, payload)


@router.delete(
    "/bills/{bill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    tags=["bills"],
)
def delete_bill(
    household_id: uuid.UUID, bill_id: uuid.UUID, service: BillServiceDependency
) -> Response:
    service.delete(household_id, bill_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/dashboard/summary", response_model=DashboardSummaryRead, tags=["dashboard"])
def get_dashboard_summary(
    household_id: uuid.UUID,
    service: DashboardServiceDependency,
    due_within_days: int = Query(default=14, ge=1, le=90),
) -> dict:
    return service.summary(household_id, due_within_days=due_within_days)
