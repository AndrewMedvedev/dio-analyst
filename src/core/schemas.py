from enum import Enum

from pydantic import BaseModel, Field


class HeaderAnalysis(BaseModel):
    tag: str  # H1, H2, H3...
    text: str
    contains_keywords: bool
    issues: list[str] | None = []


class KeywordAnalysis(BaseModel):
    keyword: str
    count: int
    density: float  # в процентах


class LinkAnalysis(BaseModel):
    url: str
    anchor_text: str
    is_internal: bool
    is_broken: bool | None = None


class ImageAnalysis(BaseModel):
    src: str
    alt_text: str | None
    has_keywords: bool
    issues: list[str] | None = []


class ReadabilityAnalysis(BaseModel):
    word_count: int
    sentence_count: int
    paragraphs_count: int
    readability_score: float | None = None  # например, Flesch score
    issues: list[str] | None = []


class MetadataAnalysis(BaseModel):
    title: str | None
    description: str | None
    issues: list[str] | None = []


class SEOAnalysisReport(BaseModel):
    headers: list[HeaderAnalysis]
    keywords: list[KeywordAnalysis]
    links: list[LinkAnalysis]
    images: list[ImageAnalysis]
    readability: ReadabilityAnalysis
    metadata: MetadataAnalysis
    overall_score: float | None = None
    recommendations: list[str]


class CWVMetricSummary(BaseModel):
    category: str | None
    percentile: float | None
    fast_percent: float | None
    average_percent: float | None
    slow_percent: float | None


class CWVReport(BaseModel):
    overall_category: str | None
    performance_score: float | None
    seo_score: float | None

    fcp: CWVMetricSummary | None
    lcp: CWVMetricSummary | None
    cls: CWVMetricSummary | None
    ttfb: CWVMetricSummary | None
    inp: CWVMetricSummary | None

    critical_seo_issues: list[dict] | None
    conclusion: str
    recommendations: list[str]


class Problem(BaseModel):
    title: str = Field(..., description="Краткое название проблемы")
    description: str = Field(..., description="Понятное объяснение проблемы")
    severity: str = Field(..., description="Уровень критичности: low | medium | high | critical")
    recommendation: str = Field(..., description="Рекомендация по исправлению")


class SEOScore(BaseModel):
    score: int = Field(..., ge=0, le=100, description="Оценка SEO от 0 до 100")
    summary: str = Field(..., description="Краткое пояснение оценки")


class PerformanceScore(BaseModel):
    score: int = Field(..., ge=0, le=100, description="Оценка производительности от 0 до 100")
    lcp: float | None = Field(None, description="Largest Contentful Paint (сек)")
    fid: float | None = Field(None, description="First Input Delay (мс)")
    cls: float | None = Field(None, description="Cumulative Layout Shift")
    summary: str = Field(..., description="Краткое пояснение оценки производительности")


class SiteAnalysisReport(BaseModel):
    overall_summary: str = Field(..., description="Общее резюме состояния сайта")
    sitemap_analysis: str = Field(..., description="Выводы по sitemap")
    content_analysis: str = Field(..., description="Анализ markdown и HTML структуры")
    core_web_vitals_analysis: str = Field(..., description="Анализ Core Web Vitals простым языком")
    issues: list[Problem] = Field(default_factory=list, description="Список найденных проблем")
    recommendations: list[str] = Field(default_factory=list, description="Общие рекомендации")
    seo: SEOScore
    performance: PerformanceScore


class BusinessModel(str, Enum):
    """Типы бизнес-моделей"""

    B2B = "B2B"
    B2C = "B2C"
    B2G = "B2G"
    HYBRID = "гибридная"
    OTHER = "другая"


class CommunicationTone(str, Enum):
    """Тоны коммуникации"""

    FORMAL = "формальный"
    FRIENDLY = "дружеский"
    EXPERT = "экспертный"
    CASUAL = "непринужденный"
    INSPIRATIONAL = "вдохновляющий"
    OTHER = "другой"


class MainActivity(BaseModel):
    """Раздел: Основная деятельность компании"""

    industry: str = Field(..., description="Отрасль/сфера деятельности компании")
    products_services: list[str] = Field(..., description="Основные продукты или услуги")
    business_model: BusinessModel = Field(..., description="Бизнес-модель компании")


class TargetAudience(BaseModel):
    """Раздел: Целевая аудитория"""

    main_clients: list[str] = Field(..., description="Основные клиенты компании")
    solved_problems: list[str] = Field(
        ..., description="Проблемы клиентов, которые решает компания"
    )


class KeyAdvantages(BaseModel):
    """Раздел: Ключевые преимущества"""

    unique_selling_proposition: str | None = Field(
        None, description="Уникальное торговое предложение (УТП)"
    )
    competitive_advantages: list[str] = Field(..., description="Конкурентные преимущества")


class MissionValues(BaseModel):
    """Раздел: Миссия и ценности"""

    mission: str | None = Field(None, description="Заявленная миссия компании")
    core_values: list[str] = Field(..., description="Основные ценности и принципы работы")


class CommunicationPositioning(BaseModel):
    """Раздел: Тон коммуникации и позиционирование"""

    communication_style: CommunicationTone = Field(..., description="Стиль общения с клиентами")
    communication_style_description: str | None = Field(
        None, description="Детальное описание стиля общения"
    )
    market_positioning: str = Field(..., description="Позиционирование компании на рынке")


class KeyFacts(BaseModel):
    """Раздел: Ключевые факты и цифры"""

    founded_year: int | None = Field(None, description="Год основания компании")
    geography: list[str] = Field(..., description="География присутствия")
    key_metrics: list[str] = Field(..., description="Ключевые метрики и достижения")
    additional_facts: list[str] = Field(default_factory=list, description="Дополнительные факты")


class ProductServiceDetail(BaseModel):
    """Детальное описание продукта или услуги"""

    name: str = Field(..., description="Название продукта/услуги")
    description: str = Field(..., description="Подробное описание")
    price_category: str | None = Field(
        None, description="Ценовая категория (бюджетный, средний, премиум и т.д.)"
    )
    price_range: str | None = Field(None, description="Диапазон цен, если указан")
    delivery_methods: list[str] = Field(
        ..., description="Способы получения/доставки продуктов/услуг"
    )
    features: list[str] = Field(default_factory=list, description="Ключевые характеристики")


class ProductsServicesDetail(BaseModel):
    """Раздел: Товары/услуги детально"""

    products: list[ProductServiceDetail] = Field(..., description="Детальное описание продуктов")
    missing_info: list[str] = Field(
        default_factory=list, description="Информация, которой не хватает в этом разделе"
    )


class MissingInformation(BaseModel):
    """Информация о том, каких данных не хватает в каждом разделе"""

    main_activity: list[str] = Field(default_factory=list)
    target_audience: list[str] = Field(default_factory=list)
    key_advantages: list[str] = Field(default_factory=list)
    mission_values: list[str] = Field(default_factory=list)
    communication_positioning: list[str] = Field(default_factory=list)
    key_facts: list[str] = Field(default_factory=list)
    products_services: list[str] = Field(default_factory=list)


class WebsiteAnalysisResult(BaseModel):
    """Полная Pydantic схема для результата анализа главной страницы сайта"""

    # Основные разделы анализа
    main_activity: MainActivity = Field(..., description="Основная деятельность компании")
    target_audience: TargetAudience = Field(..., description="Целевая аудитория")
    key_advantages: KeyAdvantages = Field(..., description="Ключевые преимущества")
    mission_values: MissionValues = Field(..., description="Миссия и ценности")
    communication_positioning: CommunicationPositioning = Field(
        ..., description="Тон коммуникации и позиционирование"
    )
    key_facts: KeyFacts = Field(..., description="Ключевые факты и цифры")
    products_services_detail: ProductsServicesDetail = Field(
        ..., description="Товары/услуги детально"
    )

    # Информация о пропущенных данных
    missing_info: MissingInformation = Field(
        default_factory=MissingInformation,
        description="Информация, которой не хватает в каждом разделе",
    )

    # Краткое резюме
    summary: str = Field(
        ..., description="Краткое резюме (3-5 предложений) о деятельности компании"
    )

    # Мета-информация
    analysis_date: str | None = Field(None, description="Дата проведения анализа")
    source_url: str | None = Field(None, description="URL проанализированной страницы")


class ExpertiseForm(BaseModel):
    name: str = Field(
        ...,
        description="Название формы демонстрации экспертизы (например, 'профессиональная терминология', 'кейсы')",
    )
    evidence: str = Field(
        ...,
        description="Конкретные примеры или упоминания из текста, подтверждающие наличие этой формы",
    )


class AudienceType(BaseModel):
    type: str = Field(..., description="Тип аудитории: 'новички', 'специалисты', 'руководители'")
    justification: str = Field(
        ..., description="Обоснование отнесения к этому типу на основе текста"
    )


class UniquenessAspect(BaseModel):
    aspect: str = Field(
        ...,
        description="Аспект уникальности (например, 'авторский взгляд', 'нестандартные решения')",
    )
    description: str = Field(..., description="Описание проявления этого аспекта в тексте")


class AnalysisResult(BaseModel):
    subject_area: str = Field(
        ..., description="Предметная область экспертизы (IT, медицина, финансы и т. д.)"
    )
    knowledge_depth: str = Field(
        ...,
        description="Оценка глубины знаний: 'поверхностное упоминание', 'базовый уровень', 'продвинутый уровень'",
    )
    expertise_forms: list[ExpertiseForm] = Field(
        default_factory=list,
        description="Список форм демонстрации экспертизы с примерами из текста",
    )
    target_audience: list[AudienceType] = Field(
        default_factory=list, description="Целевая аудитория и обоснование выбора"
    )
    practical_value: list[str] = Field(
        default_factory=list,
        description="Конкретные выгоды для пользователя (готовые решения, инструкции, чек‑листы и т. п.)",
    )
    uniqueness_aspects: list[UniquenessAspect] = Field(
        default_factory=list, description="Аспекты уникальности подхода с описанием их проявления"
    )
    communication_tone: str = Field(
        ...,
        description="Тон коммуникации: 'авторитетно', 'наставнически', 'коллаборативно', 'нейтрально'",
    )
    notes: str | None = Field(
        None, description="Дополнительные замечания, если какие‑то аспекты не отражены в тексте"
    )

    class Config:
        extra = "forbid"  # Запрещает поля, не описанные в схеме
        validate_assignment = True  # Включает валидацию при присваивании значений
