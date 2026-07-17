from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.exceptions import ConflictError


class ServiceBase:
    def __init__(self, session: Session) -> None:
        self.session = session

    def commit(self) -> None:
        try:
            self.session.commit()
        except IntegrityError as error:
            self.session.rollback()
            raise ConflictError("The request conflicts with an existing record.") from error
        except Exception:
            self.session.rollback()
            raise
