from fastapi import APIRouter, status

from ...agents import chatbot
from ...schemas import Chat, Role

router_chat = APIRouter(prefix="/api/v1")


@router_chat.post("/chat", status_code=status.HTTP_200_OK)
async def answer(chat: Chat) -> Chat:
    result = await chatbot.call_chatbot(user_id=chat.user_id, user_prompt=chat.text)
    return Chat(user_id=chat.user_id, role=Role.AI, text=result)
