from collections.abc import Generator

from fastapi import Request

from infra.database_manager import DatabaseManagerConnection


def get_database_manager(
    request: Request,
) -> Generator[DatabaseManagerConnection, None, None]:
    _ = request
    db_manager = DatabaseManagerConnection()
    yield db_manager
    db_manager.close_session()
