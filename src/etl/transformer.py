from collections.abc import Callable, Hashable, Iterable
from datetime import datetime

from etl.models import (
    AcademicFormation,
    Advising,
    ConferencePaper,
    Paper,
    ResearchArea,
    XMLData,
)
from settings import Settings
from langchain_google_genai import GoogleGenerativeAIEmbeddings


class Transformer:
    def __init__(self, enable_embeddings: bool | None = None) -> None:
        if enable_embeddings is None:
            try:
                self.enable_embeddings = Settings().ENABLE_EMBEDDINGS
            except Exception:
                self.enable_embeddings = False
        else:
            self.enable_embeddings = enable_embeddings

        if self.enable_embeddings:
            settings = Settings()
            self.embeddings_model: GoogleGenerativeAIEmbeddings | None = GoogleGenerativeAIEmbeddings(
                model=settings.EMBEDDING_MODEL,
                api_key=settings.GOOGLE_API_KEY,
                output_dimensionality=settings.DIMENSIONS,
            )
        else:
            self.embeddings_model = None

    def transform(self, data: list[XMLData]) -> list[XMLData]:
        transformed_data = [self.transform_xml_data(item) for item in data]

        if self.enable_embeddings and self.embeddings_model:
            self._embed_titles(transformed_data)

        return transformed_data

    def _embed_titles(self, data: list[XMLData]) -> None:
        papers_to_embed: list[Paper] = []
        for item in data:
            papers_to_embed.extend(item.researcher_data.papers)

        if not papers_to_embed:
            return

        titles = [paper.title for paper in papers_to_embed]
        # Embed in batches to avoid hitting rate limits or just for efficiency
        # Google Generative AI embeddings usually handle lists
        try:
            assert self.embeddings_model is not None
            embeddings = self.embeddings_model.embed_documents(titles)
            for paper, embedding in zip(papers_to_embed, embeddings):
                paper.title_embeddings = embedding
        except Exception as e:
            print(f"[ERROR] Failed to embed titles: {e}")

    def transform_xml_data(self, item: XMLData) -> XMLData:
        researcher = item.researcher_data

        researcher.full_name = normalize_text(researcher.full_name) or ""
        researcher.lattes_id = normalize_text(researcher.lattes_id) or ""
        researcher.citation_name = normalize_text(researcher.citation_name)
        researcher.orcid = normalize_orcid(researcher.orcid)
        researcher.nationality = normalize_text(researcher.nationality)
        researcher.birth_country = normalize_text(researcher.birth_country)
        researcher.birth_state = normalize_upper(researcher.birth_state)
        researcher.update_date = normalize_lattes_date(researcher.update_date)

        researcher.papers = deduplicate(
            [self.transform_paper(paper) for paper in researcher.papers],
            paper_key,
        )
        researcher.academic_formations = deduplicate(
            [
                self.transform_academic_formation(formation)
                for formation in researcher.academic_formations
            ],
            academic_formation_key,
        )
        researcher.research_areas = deduplicate(
            [self.transform_research_area(area) for area in researcher.research_areas],
            research_area_key,
        )
        researcher.conference_papers = deduplicate(
            [
                self.transform_conference_paper(conference_paper)
                for conference_paper in researcher.conference_papers
            ],
            conference_paper_key,
        )
        researcher.advisings = deduplicate(
            [self.transform_advising(advising) for advising in researcher.advisings],
            advising_key,
        )

        return item

    def transform_paper(self, paper: Paper) -> Paper:
        paper.title = normalize_title(paper.title) or ""
        paper.year = normalize_year(paper.year)
        paper.doi = normalize_doi(paper.doi)
        paper.language = normalize_text(paper.language)
        paper.nature = normalize_upper(paper.nature)
        paper.country = normalize_text(paper.country)
        paper.journal = normalize_text(paper.journal)
        paper.issn = normalize_digits(paper.issn)
        paper.volume = normalize_text(paper.volume)
        paper.issue = normalize_text(paper.issue)
        paper.first_page = normalize_page(paper.first_page)
        paper.last_page = normalize_page(paper.last_page)
        return paper

    def transform_academic_formation(
        self,
        formation: AcademicFormation,
    ) -> AcademicFormation:
        formation.level = normalize_underscore(formation.level) or ""
        formation.institution = normalize_text(formation.institution)
        formation.course = normalize_text(formation.course)
        formation.status = normalize_upper(formation.status)
        formation.start_year = normalize_year(formation.start_year)
        formation.end_year = normalize_year(formation.end_year)
        formation.thesis_title = normalize_title(formation.thesis_title)
        formation.advisor = normalize_text(formation.advisor)
        formation.funding_agency = normalize_text(formation.funding_agency)
        return formation

    def transform_research_area(self, area: ResearchArea) -> ResearchArea:
        area.major_area = normalize_underscore(area.major_area)
        area.area = normalize_text(area.area)
        area.sub_area = normalize_text(area.sub_area)
        area.specialty = normalize_text(area.specialty)
        return area

    def transform_conference_paper(
        self,
        conference_paper: ConferencePaper,
    ) -> ConferencePaper:
        conference_paper.title = normalize_title(conference_paper.title) or ""
        conference_paper.year = normalize_year(conference_paper.year)
        conference_paper.nature = normalize_upper(conference_paper.nature)
        conference_paper.country = normalize_text(conference_paper.country)
        conference_paper.language = normalize_text(conference_paper.language)
        conference_paper.doi = normalize_doi(conference_paper.doi)
        conference_paper.event_name = normalize_text(conference_paper.event_name)
        conference_paper.event_city = normalize_text(conference_paper.event_city)
        conference_paper.event_year = normalize_year(conference_paper.event_year)
        conference_paper.event_classification = normalize_upper(
            conference_paper.event_classification
        )
        conference_paper.proceedings_title = normalize_text(
            conference_paper.proceedings_title
        )
        conference_paper.isbn = normalize_digits(conference_paper.isbn)
        conference_paper.first_page = normalize_page(conference_paper.first_page)
        conference_paper.last_page = normalize_page(conference_paper.last_page)
        return conference_paper

    def transform_advising(self, advising: Advising) -> Advising:
        advising.level = normalize_underscore(advising.level) or ""
        advising.title = normalize_title(advising.title) or ""
        advising.year = normalize_year(advising.year)
        advising.advisee_name = normalize_text(advising.advisee_name)
        advising.advising_type = normalize_underscore(advising.advising_type)
        advising.institution = normalize_text(advising.institution)
        advising.course = normalize_text(advising.course)
        advising.country = normalize_text(advising.country)
        advising.funding_agency = normalize_text(advising.funding_agency)
        return advising


def normalize_text(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = " ".join(value.strip().split())
    return normalized or None


def normalize_title(value: str | None) -> str | None:
    return normalize_text(value)


def normalize_upper(value: str | None) -> str | None:
    value = normalize_text(value)
    return value.upper() if value else None


def normalize_underscore(value: str | None) -> str | None:
    value = normalize_text(value)
    return value.replace("_", " ") if value else None


def normalize_digits(value: str | None) -> str | None:
    value = normalize_text(value)
    if value is None:
        return None

    digits = "".join(character for character in value if character.isdigit())
    return digits or None


def normalize_page(value: str | None) -> str | None:
    value = normalize_text(value)
    if value is None:
        return None

    prefixes = ("p.", "P.", "pag.", "Pag.", "pagina", "Pagina")
    for prefix in prefixes:
        if value.startswith(prefix):
            value = value[len(prefix):].strip()

    return value or None


def normalize_year(value: int | str | None) -> int | None:
    if value is None:
        return None

    try:
        year = int(str(value).strip())
    except ValueError:
        return None

    if 1000 <= year <= 9999:
        return year

    return None


def normalize_doi(value: str | None) -> str | None:
    value = normalize_text(value)
    if value is None:
        return None

    value = value.lower()
    prefixes = (
        "https://doi.org/",
        "http://doi.org/",
        "https://dx.doi.org/",
        "http://dx.doi.org/",
        "doi:",
    )

    for prefix in prefixes:
        if value.startswith(prefix):
            value = value[len(prefix):]
            break

    return value.strip() or None


def normalize_orcid(value: str | None) -> str | None:
    value = normalize_text(value)
    if value is None:
        return None

    value = value.replace("https://orcid.org/", "")
    value = value.replace("http://orcid.org/", "")
    return value or None


def normalize_lattes_date(value: str | None) -> str | None:
    value = normalize_text(value)
    if value is None:
        return None

    for date_format in ("%d%m%Y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, date_format).date().isoformat()
        except ValueError:
            continue

    return value


def deduplicate[T](
    items: Iterable[T],
    key_factory: Callable[[T], Hashable],
) -> list[T]:
    seen: set[Hashable] = set()
    deduplicated: list[T] = []

    for item in items:
        key = key_factory(item)
        if key in seen:
            continue

        seen.add(key)
        deduplicated.append(item)

    return deduplicated


def normalized_key(value: str | None) -> str | None:
    value = normalize_text(value)
    return value.lower() if value else None


def paper_key(paper: Paper) -> tuple[str, str | int | None, int | None]:
    if paper.doi:
        return ("doi", paper.doi, None)

    return ("title_year", normalized_key(paper.title), paper.year)


def academic_formation_key(
    formation: AcademicFormation,
) -> tuple[str | int | None, ...]:
    return (
        normalized_key(formation.level),
        normalized_key(formation.institution),
        normalized_key(formation.course),
        formation.start_year,
        formation.end_year,
    )


def research_area_key(area: ResearchArea) -> tuple[str | None, ...]:
    return (
        normalized_key(area.major_area),
        normalized_key(area.area),
        normalized_key(area.sub_area),
        normalized_key(area.specialty),
    )


def conference_paper_key(
    conference_paper: ConferencePaper,
) -> tuple[str, str | int | None, int | None]:
    if conference_paper.doi:
        return ("doi", conference_paper.doi, None)

    return (
        "title_year",
        normalized_key(conference_paper.title),
        conference_paper.year,
    )


def advising_key(advising: Advising) -> tuple[str | int | None, ...]:
    return (
        normalized_key(advising.title),
        advising.year,
        normalized_key(advising.advisee_name),
    )
