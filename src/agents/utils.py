from langchain.messages import AIMessage

from ..core.depends import yandex_gpt


async def count_tokens_with_ai_message(request: str, result: AIMessage) -> int:
    count_request = yandex_gpt.get_num_tokens(request)
    count_result = yandex_gpt.get_num_tokens(str(result.content))
    return count_request + count_result


async def count_tokens(request: str, result: str) -> int:
    count_request = yandex_gpt.get_num_tokens(request)
    count_result = yandex_gpt.get_num_tokens(result)
    return count_request + count_result


ab_queries = [
    "1с комплексная автоматизация цена",
    "сопровождение 1с архитектор бизнеса",
    "1с:зарплата и управление персоналом",
    "обучение 1с архитектор бизнеса",
    "1с",
    "архитектор бизнеса",
    "1с управление небольшой фирмой",
    "1с бухгалтерия архитектор",
    "внедрение 1с архитектор",
    "1с строительство архитектор",
    "обновление 1с архитектор бизнеса",
    "1с архитектор бизнеса",
    "1с камин архитектор",
    "1с документооборот архитектор",
    "купить 1с у архитектора",
    "отзывы архитектор бизнеса",
    "переход на 1с с архитектором",
    "1с отчетность архитектор",
]

one_bit_queries = [
    "1с документооборот первый бит",
    "внедрение 1с первый бит",
    "обновление 1с первый бит",
    "отзывы о первом бите",
    "1с первый бит",
    "цена 1с бухгалтерия базовая",
    "1с бухгалтерия цена",
    "переход на 1с с первого бита",
    "первый бит",
    "1с отчетность первый бит",
    "аренда 1с в облаке первый бит",
    "купить 1с в первом бите",
    "1с управление торговлей",
    "1с комплексная автоматизация первый бит",
    "курсы 1с первый бит",
    "1с",
    "1с:предприятие",
    "обслуживание 1с первый бит",
]
