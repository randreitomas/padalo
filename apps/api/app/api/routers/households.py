from __future__ import annotations

import uuid

from fastapi import APIRouter, Response, status

from app.api.dependencies import HouseholdServiceDependency
from app.api.routers.common import PaginationDependency
from app.schemas.common import PaginatedResponse
from app.schemas.households import HouseholdCreate, HouseholdRead, HouseholdUpdate

router = APIRouter(prefix="/api/v1/households", tags=["households"])


@router.get("", response_model=PaginatedResponse[HouseholdRead], summary="List households")
def list_households(
    pagination: PaginationDependency,
    service: HouseholdServiceDependency,
) -> dict:
    return {
        "items": service.list(limit=pagination.limit, offset=pagination.offset),
        "limit": pagination.limit,
        "offset": pagination.offset,
    }


@router.post(
    "",
    response_model=HouseholdRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a household",
)
def create_household(payload: HouseholdCreate, service: HouseholdServiceDependency) -> object:
    return service.create(payload)


@router.get("/{household_id}", response_model=HouseholdRead, summary="Get a household")
def get_household(household_id: uuid.UUID, service: HouseholdServiceDependency) -> object:
    return service.get(household_id)


@router.patch("/{household_id}", response_model=HouseholdRead, summary="Update a household")
def update_household(
    household_id: uuid.UUID,
    payload: HouseholdUpdate,
    service: HouseholdServiceDependency,
) -> object:
    return service.update(household_id, payload)


@router.delete(
    "/{household_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Soft-delete a household",
)
def delete_household(household_id: uuid.UUID, service: HouseholdServiceDependency) -> Response:
    service.delete(household_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
