from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, PositiveInt


class InvitationCreate(BaseModel):
    """Отправка приглашения"""

    email: EmailStr = Field(..., description="Email пользователя")


class InvitationResponse(BaseModel):
    """Схема ответа отправленного приглашения"""

    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    expires_at: datetime
    is_used: bool


class TokenType(StrEnum):
    """Типы токенов"""

    ACCESS = "access"
    REFRESH = "refresh"


class Token(BaseModel):
    """Схема 'access' токена"""

    access_token: str
    token_type: str = Field("Bearer", frozen=True)
    expires_at: PositiveInt = Field(..., description="Время истечения токена в формате timestamp")


class TokensPair(BaseModel):
    """Пара токенов 'access' и 'refresh'"""

    access_token: str
    refresh_token: str
    token_type: str = Field(default="Bearer", frozen=True)
    expires_at: PositiveInt = Field(
        ..., description="Время истечения access токена в формате timestamp"
    )


class UserCreateForm(BaseModel):
    """Форма для создания пользователя"""

    username: str | None = Field(
        None, description="Никнейм пользователя", examples=["ivan_ivanov"]
    )
    full_name: str | None = Field(
        None, max_length=150, description="ФИО", examples=["Иванов Иван Иванович"]
    )
    password: str = Field(..., description="Пароль, который придумал пользователь")


class UserResponse(BaseModel):
    """Модель для API ответа с данными о пользователе"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    full_name: str | None = None
    is_active: bool = True
    created_at: datetime
