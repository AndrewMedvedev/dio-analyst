from fastapi import APIRouter, status

from ...agents import chatbot
from ...schemas import Chat, Role
from ..dependencies import CurrentUserDep

router_chat = APIRouter()


@router_chat.post("/chat", status_code=status.HTTP_200_OK)
async def answer(chat: Chat, current_user: CurrentUserDep) -> Chat:
    result = await chatbot.call_chatbot(
        user_id=current_user.user_id, user_prompt=chat.text, generation_id=chat.generation_id
    )
    return Chat(role=Role.AI, text=result, generation_id=chat.generation_id)
