import logging
from typing import Any, Generic, Type, TypeAlias, TypeVar

from pydantic import BaseModel
from sqlalchemy import (
    ColumnElement,
    Delete,
    Result,
    Row,
    Update,
    delete,
    func,
    select,
    text,
    update,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute, QueryableAttribute

from cea.db.errors import (
    RepositoryError,
    RepositoryIntegrityConflictError,
)
from cea.db.models.base import Base

_logger = logging.getLogger(__name__)

CreateDataSchema: TypeAlias = BaseModel
ModelType = TypeVar('ModelType', bound=Base)


class BaseRepository(Generic[ModelType]):
    """Async base repository with basic methods."""

    def __init__(self, model: Type[ModelType]) -> None:
        """Repository with basic methods"""

        self.model = model

    async def create(
        self, session: AsyncSession, data: CreateDataSchema
    ) -> ModelType:
        """
        Accepts a Pydantic model, creates a new record in a database
        and catches integrity errors.


        Args:
            session (AsyncSession): SQLAlchemy asynchronous session.
            data (DataSchema): Pydantic data model.

            Raises:
                RepositoryIntegrityConflictError: If SQLAlchemy model
                conflicts with existing data for creation.
                RepositoryError: If an unknown error occurs while
                    creation.

        Returns:
            ModelType: SQLAlchemy model
        """

        try:
            instance = self.model(**data.model_dump())
            session.add(instance)
            await session.commit()

            return instance
        except IntegrityError:
            integrity_msg: str = (
                f'{self.model.__tablename__} conflicts with existing data'
            )
            _logger.error(integrity_msg)
            raise RepositoryIntegrityConflictError(integrity_msg)
        except Exception as e:
            error_msg: str = f'Unknown exception occurred: {e}'
            _logger.error(error_msg)
            raise RepositoryError(error_msg) from e

    async def _read(
        self,
        session: AsyncSession,
        *,
        entities: list[QueryableAttribute] | None = None,
        where: (
            ColumnElement[bool] | tuple[ColumnElement[bool], ...] | None
        ) = None,
        order_by: InstrumentedAttribute | ColumnElement | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> Result[Any]:
        """
        Find (filtering by `where`) records in db.

        Args:
            session (AsyncSession): SQLAlchemy asynchronous session.
            entities (list[InstrumentedAttribute] | None): Columns
                to query.
            where (
                ColumnElement[bool]
                | tuple[ColumnElement[bool], ...]
                | None,
            ): Where SQL expressions. Defaults to `None`.
            order_by (InstrumentedAttribute | ColumnElement | None):
                `Order by` expression. Defaults to `None`.
            offset (int | None): How many rows to select. Defaults
                to `None`.
            limit (int | None): How many rows to skip. Defaults
                to `None`.

        Returns:
            Result[Any]: Query result.
        """

        statement = select(*entities) if entities else select(self.model)

        if where is not None:
            statement = (
                statement.where(*where)
                if isinstance(where, tuple)
                else statement.where(where)
            )
        if order_by is not None:
            statement = statement.order_by(order_by)
        if offset is not None:
            statement = statement.offset(offset)
        if limit is not None:
            statement = statement.limit(limit)

        return await session.execute(statement)

    async def update_by_id(
        self,
        session: AsyncSession,
        instance_id: int,
        *,
        is_commit: bool = True,
        returning: Type[ModelType] | list[InstrumentedAttribute] | None = None,
        **value_kwargs: Any,
    ) -> Row[Any] | None:
        """
        Update existing data in a table by ID.

        Args:
            session (AsyncSession): SQLAlchemy asynchronous session.
            instance_id (list[InstrumentedAttribute] | None): ID to
                update.
            is_commit (
                ColumnElement[bool]
                | tuple[ColumnElement[bool], ...]
                | None,
            ): Whether to commit or not. Defaults to `True`.
            returning (
                Type[ModelType]
                | list[InstrumentedAttribute]
                | None
            ): `Returning` expression. Defaults to `None`.
            value_kwargs (Any): Data values to update.

        Returns:
            Result[Any] | None: Query result.
        """

        statement = (
            update(self.model)
            .where(self.model.id == instance_id)  # type: ignore
            .values(**value_kwargs)
        )
        if returning:
            return await self._apply_and_execute_returning(
                session, statement, is_commit=is_commit, returning=returning
            )

        await session.execute(statement)
        if is_commit:
            await session.commit()

        return None

    async def delete_by_id(
        self,
        session: AsyncSession,
        instance_id: int,
        is_commit: bool = True,
        returning: Type[ModelType] | list[InstrumentedAttribute] | None = None,
    ) -> Row[Any] | None:
        """
        Delete existing data in a table by ID.

        Args:
            session (AsyncSession): SQLAlchemy asynchronous session.
            instance_id (list[InstrumentedAttribute] | None): ID to
                delete.
            is_commit (
                ColumnElement[bool]
                | tuple[ColumnElement[bool], ...]
                | None,
            ): Whether to commit or not. Defaults to `True`.
            returning (
                Type[ModelType]
                | list[InstrumentedAttribute]
                | None
            ): `Returning` expression. Defaults to `None`.

        Returns:
            Result[Any] | None: Query result.
        """

        statement = delete(self.model).where(self.model.id == instance_id)  # type: ignore
        if returning:
            return await self._apply_and_execute_returning(
                session, statement, is_commit=is_commit, returning=returning
            )

        await session.execute(statement)
        if is_commit:
            await session.commit()

        return None

    @staticmethod
    async def _apply_and_execute_returning(
        session: AsyncSession,
        statement: Delete | Update,
        *,
        is_commit: bool = True,
        returning: Type[ModelType] | list[InstrumentedAttribute],
    ) -> Row | None:
        if isinstance(returning, list):
            result = await session.execute(statement.returning(*returning))
        else:
            result = await session.execute(statement.returning(returning))
        if is_commit:
            await session.commit()

        return result.first()

    async def count(
        self,
        session: AsyncSession,
        column: InstrumentedAttribute | None = None,
        where: (
            ColumnElement[bool] | tuple[ColumnElement[bool], ...] | None
        ) = None,
    ) -> int | None:
        """
        Returns the number of rows.

        Args:
            session (AsyncSession): SQLAlchemy asynchronous session.
            column (InstrumentedAttribute): Column to count.
            where (
                ColumnElement[bool]
                | tuple[ColumnElement[bool], ...]
                | None,
            ): Where SQL expressions. Defaults to `None`.

        Returns:
            int: The number of rows.
        """

        statement = select(
            func.count(column if column else text('*'))
        ).select_from(self.model)

        if where:
            statement = (
                statement.where(*where)
                if isinstance(where, tuple)
                else statement.where(where)
            )

        return await session.scalar(statement)
