import json
from datetime import UTC, datetime

from ..agents.rag import indexing
from .mocks import mock

m = json.dumps(mock)

result = indexing(
    text=m,
    metadata={
        "tenant_id": "12345678",
        "timestamp": int(datetime.now(UTC).timestamp()),
        "generation_id": "12345678",
    },
)
print(result)
