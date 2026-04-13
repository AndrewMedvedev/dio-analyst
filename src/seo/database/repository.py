from typing import Any
from uuid import UUID

from sqlalchemy import insert, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from ..schemas import SEOResult
from .base import Base


class SEOResultOrm(Base):
    __tablename__ = "seo_result"
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), unique=False, nullable=True)
    result: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)


class UserSEORepository:
    model = SEOResultOrm
    schema = SEOResult

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, entity: SEOResult) -> None:
        stmt = insert(self.model).values(**entity.model_dump())
        await self.session.execute(stmt)
        await self.session.flush()
        await self.session.commit()

    async def read_paginated(self, user_id: UUID, limit: int, page: int) -> list:
        offset = (page - 1) * limit
        stmt = select(self.model).where(self.model.user_id == user_id).offset(offset).limit(limit)
        results = await self.session.execute(stmt)
        models = results.scalars().all()
        return [self.schema.model_validate(model) for model in models]
