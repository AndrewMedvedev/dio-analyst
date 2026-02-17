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
