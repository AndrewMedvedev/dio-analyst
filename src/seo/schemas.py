from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class HeaderAnalysis(BaseModel):
    tag: str = Field(..., description="HTML-тег заголовка")
    text: str = Field(..., description="Текст заголовка")
    contains_keywords: bool = Field(
        ..., description="Содержит ли заголовок целевые ключевые слова"
    )
    issues: list[str] | None = Field(
        default=[], description="Список проблем или замечаний по этому заголовку (если есть)"
    )


class KeywordAnalysis(BaseModel):
    keyword: str = Field(..., description="Ключевое слово или фраза")
    count: int = Field(..., description="Количество вхождений ключевого слова в тексте")
    density: float = Field(..., description="Плотность ключевого слова в процентах (%)")


class LinkAnalysis(BaseModel):
    url: str = Field(..., description="Полный URL ссылки")
    anchor_text: str = Field(..., description="Анкорный текст ссылки (текст, по которому кликают)")
    is_internal: bool = Field(..., description="Является ли ссылка внутренней (на этом же сайте)")
    is_broken: bool | None = Field(
        default=None, description="Битая ли ссылка (True/False/None если не проверяли)"
    )


class ImageAnalysis(BaseModel):
    src: str = Field(..., description="URL или путь к изображению")
    alt_text: str | None = Field(default=None, description="Значение атрибута alt у изображения")
    has_keywords: bool = Field(..., description="Содержит ли alt-текст целевые ключевые слова")
    issues: list[str] | None = Field(
        default=[],
        description="Список проблем с изображением (пустой alt, слишком длинный и т.д.)",
    )


class ReadabilityAnalysis(BaseModel):
    word_count: int = Field(..., description="Общее количество слов в тексте")
    sentence_count: int = Field(..., description="Общее количество предложений")
    paragraphs_count: int = Field(..., description="Общее количество абзацев")
    readability_score: float | None = Field(
        default=None, description="Оценка читаемости (например, Flesch-Kincaid score)"
    )
    issues: list[str] | None = Field(default=[], description="Проблемы с читаемостью текста")


class MetadataAnalysis(BaseModel):
    title: str | None = Field(default=None, description="Содержимое тега <title>")
    description: str | None = Field(default=None, description="Содержимое мета-тега description")
    issues: list[str] | None = Field(
        default=[],
        description="Проблемы с мета-данными (отсутствие, слишком короткий/длинный и т.д.)",
    )


# === НОВЫЙ КЛАСС ===
class StrongSentenceStructureAnalysis(BaseModel):
    strong_constructions: list[str] = Field(
        ...,
        description="Список сильных риторических конструкций, найденных в тексте (параллелизм, триада, риторический вопрос, анафора и т.д.)",  # noqa: E501
    )
    writing_style: str = Field(
        ...,
        description="Определённый стиль письма: продающий, экспертный, эмоциональный, разговорный, повествовательный и др.",  # noqa: E501
    )
    influence_on_reader: str = Field(
        ...,
        description="Как используемые конструкции влияют на читателя (вовлечение, доверие, эмоции, мотивация к действию и т.д.)",  # noqa: E501
    )
    influence_on_seo: str = Field(
        ...,
        description="Влияние стиля и конструкций на SEO (читаемость, время на странице, поведенческие факторы)",  # noqa: E501
    )
    influence_on_conversion: str = Field(
        ...,
        description="Влияние конструкций на конверсию и эффективность текста (продажи, заявки и т.д.)",  # noqa: E501
    )
    examples: list[str] = Field(
        ...,
        description="Конкретные примеры предложений из текста, где используются сильные конструкции",  # noqa: E501
    )
    recommendations: list[str] = Field(
        ..., description="Рекомендации по улучшению или усилению сильных конструкций в тексте"
    )


class SEOAnalysisReport(BaseModel):
    headers: list[HeaderAnalysis] = Field(..., description="Анализ всех заголовков H1–H6")
    keywords: list[KeywordAnalysis] = Field(..., description="Анализ ключевых слов и их плотности")
    links: list[LinkAnalysis] = Field(..., description="Анализ всех ссылок на странице")
    images: list[ImageAnalysis] = Field(..., description="Анализ всех изображений")
    readability: ReadabilityAnalysis = Field(..., description="Анализ читаемости текста")
    metadata: MetadataAnalysis = Field(..., description="Анализ мета-тегов title и description")
    strong_structures: StrongSentenceStructureAnalysis = Field(
        ..., description="Анализ сильных риторических конструкций и стиля текста"
    )
    overall_score: float = Field(..., description="Общая SEO-оценка страницы от 0 до 100")
    recommendations: list[str] = Field(
        ..., description="Общие рекомендации по улучшению SEO страницы"
    )


class CWVMetricSummary(BaseModel):
    category: str | None = Field(
        default=None, description="Категория метрики: Good / Needs Improvement / Poor"
    )
    percentile: float | None = Field(
        default=None, description="Процентиль по сравнению с другими сайтами"
    )
    fast_percent: float | None = Field(
        default=None, description="Процент пользователей с быстрым значением метрики (%)"
    )
    average_percent: float | None = Field(
        default=None, description="Процент пользователей со средним значением метрики (%)"
    )
    slow_percent: float | None = Field(
        default=None, description="Процент пользователей с медленным значением метрики (%)"
    )

    @field_validator(
        "category",
        "percentile",
        "fast_percent",
        "average_percent",
        "slow_percent",
        mode="before",
    )
    @classmethod
    def parse_null_string(cls, v):
        if v == "null":
            return None
        return v


class CWVReport(BaseModel):
    overall_category: str | None = Field(
        default=None, description="Общая категория Core Web Vitals: Good / Average / Poor"
    )
    performance_score: float | None = Field(
        default=None, description="Общий Performance Score (0–100)"
    )
    seo_score: float | None = Field(
        default=None, description="SEO Score на основе Core Web Vitals"
    )
    fcp: CWVMetricSummary | None = Field(default=None, description="First Contentful Paint")
    lcp: CWVMetricSummary | None = Field(default=None, description="Largest Contentful Paint")
    cls: CWVMetricSummary | None = Field(default=None, description="Cumulative Layout Shift")
    ttfb: CWVMetricSummary | None = Field(default=None, description="Time to First Byte")
    inp: CWVMetricSummary | None = Field(default=None, description="Interaction to Next Paint")
    critical_seo_issues: list[dict] | None = Field(
        default=None, description="Критические SEO-проблемы, связанные с Core Web Vitals"
    )
    conclusion: str = Field(..., description="Краткий вывод по Core Web Vitals")
    recommendations: list[str] = Field(
        ..., description="Рекомендации по улучшению Core Web Vitals"
    )


class GenerateAIOContent(BaseModel):
    transformed_content: str = Field(..., description="Переписанный / оптимизированный контент")
    placement_recommendation: str = Field(
        ..., description="Рекомендация, где и как лучше разместить этот текст на странице"
    )


class Problem(BaseModel):
    title: str = Field(..., description="Краткое название проблемы")
    description: str = Field(..., description="Понятное и подробное объяснение сути проблемы")
    severity: str = Field(..., description="Уровень критичности: low | medium | high | critical")
    recommendation: str = Field(..., description="Конкретная рекомендация, как исправить проблему")


class SEOScore(BaseModel):
    score: int = Field(..., ge=0, le=100, description="Общая SEO-оценка сайта от 0 до 100")
    summary: str = Field(..., description="Краткое текстовое пояснение текущей SEO-оценки")


class PerformanceScore(BaseModel):
    score: int = Field(
        ..., ge=0, le=100, description="Общая оценка производительности сайта от 0 до 100"
    )
    lcp: float = Field(..., description="Значение Largest Contentful Paint в миллисекундах")
    fid: float = Field(..., description="Значение First Input Delay в миллисекундах")
    cls: float = Field(..., description="Значение Cumulative Layout Shift (без единиц измерения)")
    summary: str = Field(..., description="Краткое пояснение оценки производительности")


class SiteAnalysisReport(BaseModel):
    overall_summary: str = Field(
        ..., description="Общее резюме состояния сайта одним-двумя абзацами"
    )
    content_analysis: str = Field(..., description="Анализ структуры контента (markdown/HTML)")
    core_web_vitals_analysis: str = Field(
        ..., description="Простыми словами — анализ Core Web Vitals"
    )
    issues: list[Problem] = Field(
        default_factory=list, description="Список всех найденных проблем на сайте"
    )
    recommendations: list[str] = Field(
        default_factory=list, description="Общие рекомендации по улучшению сайта"
    )
    seo: SEOScore = Field(..., description="SEO-оценка сайта")
    performance: PerformanceScore = Field(..., description="Оценка производительности сайта")

    @property
    def to_dict(self) -> dict:
        return {
            "overall_summary": self.overall_summary,
            "content_analysis": self.content_analysis,
            "core_web_vitals_analysis": self.core_web_vitals_analysis,
            "issues": [i.model_dump() for i in self.issues],
            "recommendations": self.recommendations,
            "seo": self.seo.model_dump(),
            "performance": self.performance.model_dump(),
        }


class SpecializationSite(BaseModel):
    specialization: str = Field(
        ...,
        description="Основная специализация сайта (например: 'юридические услуги', 'продажа недвижимости' и т.д.)",  # noqa: E501
    )


class ExpertiseSite(BaseModel):
    main_area: str = Field(..., description="Главная область экспертизы компании")
    key_user_problem: str = Field(
        ..., description="Ключевая проблема, которую решает компания для пользователя"
    )
    benefit_to_the_user: str = Field(
        ..., description="Главное преимущество / польза для пользователя"
    )


class SemanticCore(BaseModel):
    high_frequency: list[str] = Field(..., description="Высокочастотные запросы (ВЧ)")
    medium_frequency: list[str] = Field(..., description="Среднечастотные запросы (СЧ)")
    low_frequency: list[str] = Field(..., description="Низкочастотные запросы (НЧ)")


class Role(StrEnum):
    AI = "assistant"
    USER = "user"


class Chat(BaseModel):
    generation_id: str = Field(..., description="Уникальный идентификатор генерации")
    role: Role = Field(default=Role.USER, description="Роль автора сообщения: assistant или user")
    text: str = Field(..., description="Текст сообщения")


class QueueData(BaseModel):
    urls: list = Field(..., description="Список URL для обработки")
    start_url: str = Field(..., description="Начальный URL сканирования")
    base_url: str = Field(..., description="Базовый домен сайта")
    passed_urls: set = Field(..., description="Множество уже обработанных URL")
    found: bool = Field(..., description="Флаг — найдено ли что-то")
    result: list[dict] = Field(..., description="Результаты обработки")


class GeneratedAlt(BaseModel):
    alt: str = Field(..., description="Сгенерированный alt-текст для изображения")
    url: str = Field(..., description="URL изображения, для которого сгенерирован alt")


class ListGeneratedAlt(BaseModel):
    result: list[GeneratedAlt] = Field(..., description="Список сгенерированных alt-текстов")


class SEOResult(BaseModel):
    model_config = {"from_attributes": True}

    user_id: UUID = Field(..., description="ID пользователя")
    result: dict = Field(..., description="Результат SEO-анализа в виде словаря")
    created_at: datetime = Field(
        default_factory=datetime.now, description="Дата и время создания записи"
    )
