from langchain.agents import create_agent
from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph

from ..core.depends import yandex_gpt
from ..core.schemas import State
from .tools import tools, wrap_usage_tokens

config: RunnableConfig = {"configurable": {"thread_id": "test_thread_1"}}

agent_orchestrator: CompiledStateGraph = create_agent(
    model=yandex_gpt,
    tools=tools,
    state_schema=State,
    middleware=[wrap_usage_tokens],
)  # type: ignore  # noqa: PGH003
