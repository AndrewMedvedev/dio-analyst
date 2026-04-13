import logging
from typing import Any

import jwt

from ...errors import UnauthorizedError
from ...settings import settings

ALGORITHM = "HS256"


logger = logging.getLogger(__name__)


def validate_token(token: str) -> dict[str, Any]:
    """Декодирование токена"""

    try:
        return jwt.decode(
            token, key=settings.secret_key, algorithms=[ALGORITHM], options={"verify_aud": False}
        )
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Token signature expired!") from None
    except jwt.PyJWTError:
        raise UnauthorizedError("Invalid token!") from None
