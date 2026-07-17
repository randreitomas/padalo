from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import create_session_factory
from app.repositories.households import HouseholdRepository
from app.repositories.ledger import (
    BillRepository,
    EnvelopeRepository,
    HouseholdMemberRepository,
    RemittanceRepository,
    TransactionRepository,
)
from app.services.households import HouseholdService
from app.services.ledger import (
    BillService,
    DashboardService,
    EnvelopeService,
    RemittanceService,
    TransactionService,
)


def get_session() -> Generator[Session, None, None]:
    session_factory = create_session_factory()
    if session_factory is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not configured.",
        )

    session = session_factory()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


SessionDependency = Annotated[Session, Depends(get_session)]


def get_household_service(session: SessionDependency) -> HouseholdService:
    return HouseholdService(session, HouseholdRepository(session))


def get_envelope_service(session: SessionDependency) -> EnvelopeService:
    return EnvelopeService(session, HouseholdRepository(session), EnvelopeRepository(session))


def get_transaction_service(session: SessionDependency) -> TransactionService:
    return TransactionService(
        session,
        HouseholdRepository(session),
        EnvelopeRepository(session),
        HouseholdMemberRepository(session),
        TransactionRepository(session),
    )


def get_remittance_service(session: SessionDependency) -> RemittanceService:
    return RemittanceService(
        session,
        HouseholdRepository(session),
        HouseholdMemberRepository(session),
        RemittanceRepository(session),
    )


def get_bill_service(session: SessionDependency) -> BillService:
    return BillService(session, HouseholdRepository(session), BillRepository(session))


def get_dashboard_service(session: SessionDependency) -> DashboardService:
    return DashboardService(
        HouseholdRepository(session),
        EnvelopeRepository(session),
        TransactionRepository(session),
        RemittanceRepository(session),
        BillRepository(session),
    )


HouseholdServiceDependency = Annotated[HouseholdService, Depends(get_household_service)]
EnvelopeServiceDependency = Annotated[EnvelopeService, Depends(get_envelope_service)]
TransactionServiceDependency = Annotated[TransactionService, Depends(get_transaction_service)]
RemittanceServiceDependency = Annotated[RemittanceService, Depends(get_remittance_service)]
BillServiceDependency = Annotated[BillService, Depends(get_bill_service)]
DashboardServiceDependency = Annotated[DashboardService, Depends(get_dashboard_service)]
