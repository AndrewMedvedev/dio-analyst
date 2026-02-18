import logging
import time
from collections.abc import Callable
from functools import wraps
from typing import Any

from langchain.agents import AgentState
from langchain.agents.middleware import after_model
from langchain.tools import ToolRuntime, tool
from langchain_core.messages import AIMessage
from langgraph.runtime import Runtime
from langgraph.types import Command

from ..core.schemas import State
from .aio_agent.agent import agent_aio
from .importer_agent import agent_importer
from .seo_agent.agent import agent_seo

logger = logging.getLogger(__name__)
RESULT_PREVIEW_CHARS = 300


def log_tool_call(tool_name: str | None = None):
    """Декоратор для логирования вызовов инструментов"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            tool_id = tool_name or func.__name__
            start_time = time.time()
            logger.info(
                "🛠️ TOOL CALL START: %s",
                tool_id,
                extra={
                    "tool": tool_id,
                    "input_args": args,
                    "input_kwargs": kwargs,
                    "timestamp": start_time,
                },
            )
            try:
                result = func(*args, **kwargs)
                execution_time = round(time.time() - start_time, 2)
                result_preview = (
                    str(result)[:RESULT_PREVIEW_CHARS] + "..."
                    if len(str(result)) > RESULT_PREVIEW_CHARS
                    else str(result)
                )
                logger.info(
                    "✅ TOOL CALL SUCCESS: %s (%s s)",
                    tool_id,
                    execution_time,
                    extra={
                        "tool": tool_id,
                        "execution_time": execution_time,
                        "result_preview": result_preview,
                        "result_type": type(result).__name__,
                        "result_length": len(str(result)) if hasattr(result, "__len__") else None,
                    },
                )
            except Exception as e:
                execution_time = round(time.time() - start_time, 2)
                logger.exception(
                    "❌ TOOL CALL FAILED: %s (%s s)",
                    tool_id,
                    execution_time,
                    extra={
                        "tool": tool_id,
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "execution_time": execution_time,
                    },
                )
                raise
            else:
                return result

        return wrapper

    return decorator


@after_model()
async def wrap_usage_tokens(
    state: AgentState[State],
    runtime: Runtime[ToolRuntime],  # noqa: ARG001
) -> Command[Any] | None:
    total = 0

    messages = state.get("messages", [])

    for msg in messages:
        if isinstance(msg, AIMessage) and msg.usage_metadata:
            total += msg.usage_metadata.get("total_tokens", 0)

    if total == 0:
        return None

    prev = state.get("total_tokens", 0)
    return Command(update={"total_tokens": prev + total})


@tool("call_importer_agent", parse_docstring=True)
@log_tool_call("call_importer_agent")
async def call_importer_agent(runtime: ToolRuntime, url: str) -> dict:  # noqa: ARG001
    """
    Вызывает агент импортера для получения структуры сайта и его страниц.

    Асинхронно выполняет обход указанного веб-сайта, строит его карту (site map),
    извлекает ключевые страницы на основе приоритетных ключевых слов и получает
    их HTML и Markdown содержимое.

    Args:
        runtime: Экземпляр ToolRuntime для выполнения операции.
        url: URL-адрес веб-сайта для анализа.

    Returns:
        Словарь с результатами работы агента импортера:
        {
            "importer_result": {
                "url": str - URL-адрес веб-сайта для анализа,
                "max_result": int - количество страниц для анализа,
                "site_map": TreeNode - корневой узел дерева сайта,
                "pages": list[HttpUrl] - список извлеченных ключевых страниц,
                "markdown": list[dict] - список словарей с URL и markdown-содержимым,
                "html": list[dict] - список словарей с URL и HTML-содержимым
            }
        }

    """
    call_agent = await agent_importer.ainvoke({"url": url, "max_result": 3})  # type: ignore  # noqa: PGH003
    return {"importer_result": call_agent}


@tool("call_aio_agent", parse_docstring=True)
@log_tool_call("call_aio_agent")
async def call_aio_agent(
    runtime: ToolRuntime,
    url: str,
    markdown: list[dict],
    html: list[dict],
) -> dict:
    """
    Запускает агента для комплексного AI-анализа контента веб-сайта.

    Асинхронно выполняет многоэтапный анализ указанного URL-адреса:
    1. Генерирует AI-контент на основе markdown-версий страниц
    2. Извлекает и анализирует JSON-LD структурированные данные или генерирует JSON-LD
    3. Анализирует robots.txt файл
    4. Обрабатывает llms.txt файл для получения структурированной информации о сайте или генерирует llms.txt

    Args:
        runtime: Экземпляр ToolRuntime для выполнения операции.
        url: URL-адрес веб-сайта для комплексного AI-анализа.
        markdown: markdown контент страниц с url.
        html: html разметка страниц с url.
    Returns:
        Словарь с результатами работы агента AI-анализа:
        {
            "aio_result": {
                "url": str - URL-адрес веб-сайта для анализа,
                "markdown": list[dict] - markdown контент страниц с url,
                "html": list[dict] - html разметка страниц с url,
                "new_content": list[dict] - список сгенерированного AI-контента для каждой страницы,
                "jsons_ld": list[dict] - список проанализированных и сгенерированных JSON-LD данных,
                "robots_txt": str - проанализированное содержимое robots.txt,
                "llms_txt": str - проанализированное содержимое llms.txt,
                "total_tokens": int - общее количество токенов, использованных при анализе
            }
        }
    """  # noqa: E501
    call_agent = await agent_aio.ainvoke(
        {"url": url, "markdown": markdown, "html": html}  # type: ignore  # noqa: PGH003
    )  # type: ignore  # noqa: PGH003
    return {"aio_result": call_agent}


@tool("call_seo_agent", parse_docstring=True)
@log_tool_call("call_seo_agent")
async def call_seo_agent(
    runtime: ToolRuntime,
    url: str,
    markdown: list[dict],
    html: list[dict],
) -> dict:
    """
    Запускает агента SEO-аудита для комплексного анализа веб-сайта.

    Асинхронно выполняет многоэтапный анализ указанного веб-сайта:
    1. Анализирует разметку и структуру HTML-страниц
    2. Оценивает Core Web Vitals (основные веб-показатели)
    3. Формирует итоговый отчет с рекомендациями по SEO-оптимизации

    Args:
        runtime: Экземпляр ToolRuntime для выполнения операции.
        url: URL-адрес веб-сайта для проведения SEO-аудита.
        markdown: markdown контент страниц с url.
        html: html разметка страниц с url.

    Returns:
        Словарь с результатами SEO-аудита:
        {
            "seo_result": {
                "url": str - URL-адрес проанализированного сайта,
                "markdown": list[dict] - список словарей с URL и markdown-содержимым,
                "html": list[dict] - список словарей с URL и HTML-содержимым,
                "analyze_md": list[dict] - результаты анализа markdown-контента,
                "seo_issue": list[dict] - выявленные SEO-проблемы по страницам,
                "cwv": dict - отчет по Core Web Vitals,
                "result": SiteAnalysisReport - итоговый структурированный отчет,
                "total_tokens": int - общее количество токенов, использованных при анализе
            }
        }
    """
    call_agent = await agent_seo.ainvoke({"url": url, "markdown": markdown, "html": html})  # type: ignore  # noqa: PGH003
    return {"seo_result": call_agent}


@tool("save_state", parse_docstring=True)  # type: ignore  # noqa: PGH003
@log_tool_call("save_state")
async def save_state(  # noqa: PLR0913
    runtime: ToolRuntime,  # noqa: ARG001
    request: str,
    importer_result: dict,
    aio_result: dict,
    seo_result: dict,
    total_tokens: int,
    total_money: float,
) -> Command:
    """Сохраняет текущее состояние обработки запроса.

    Инструмент предназначен для сохранения промежуточных результатов и параметров
    обработки запроса. Формирует команду обновления состояния с переданными
    данными, которая затем может быть выполнена для сохранения состояния.

    Args:
        runtime: Экземпляр ToolRuntime для выполнения инструмента.
        request: Исходный текст запроса пользователя.
        importer_result: Результат работы инструмента импорта данных.
        aio_result: Результат работы AI-ассистента (AIO).
        seo_result: Результат SEO-обработки.
        total_tokens: Общее количество потраченных токенов.
        total_money: Общая сумма затраченных средств.

    Returns:
        Command: Команда с данными для обновления состояния, содержащая
                все переданные параметры в поле update.
    """
    return Command(
        update={
            "request": request,
            "importer_result": importer_result,
            "aio_result": aio_result,
            "seo_result": seo_result,
            "total_tokens": total_tokens,
            "total_money": total_money,
        }
    )


tools = [call_importer_agent, call_aio_agent, call_seo_agent, save_state]
