from psycopg_pool import ConnectionPool

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from models.paper import Paper
from repository.paper import PaperRepository

class PaperService:
    def __init__(
        self,
        pool: ConnectionPool,
        embeddings_model: GoogleGenerativeAIEmbeddings | None = None
    ) -> None:
        self.repository: PaperRepository = PaperRepository(pool)
        self.embeddings_model = embeddings_model


    def remove_all_papers(self):
        return self.repository.remove_all()


    def add_paper(
        self,
        title: str,
        researcher_id: int,
        year: int | None = None,
        doi: str | None = None,
        language: str | None = None,
        nature: str | None = None,
        country: str | None = None,
        journal: str | None = None,
        issn: str | None = None,
        volume: str | None = None,
        issue: str | None = None,
        first_page: str | None = None,
        last_page: str | None = None,
        title_embeddings: list[float] | None = None,
    ) -> int:
        return self.repository.add(
            title,
            researcher_id,
            year,
            doi,
            language,
            nature,
            country,
            journal,
            issn,
            volume,
            issue,
            first_page,
            last_page,
            title_embeddings,
        )


    def insert_paper(
        self,
        title: str,
        researcher_id: int,
        year: int | None = None,
        doi: str | None = None,
        language: str | None = None,
        nature: str | None = None,
        country: str | None = None,
        journal: str | None = None,
        issn: str | None = None,
        volume: str | None = None,
        issue: str | None = None,
        first_page: str | None = None,
        last_page: str | None = None,
        title_embeddings: list[float] | None = None,
    ) -> int:
        return self.add_paper(
            title,
            researcher_id,
            year,
            doi,
            language,
            nature,
            country,
            journal,
            issn,
            volume,
            issue,
            first_page,
            last_page,
            title_embeddings,
        )


    def get_paper_count(self) -> int:
        return self.repository.count()


    def get_paper_by_title(self, title: str) -> Paper | None:
        return self.repository.get_by_title(title)


    def hybrid_search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[tuple[Paper, float]]:
        if not self.embeddings_model:
            raise ValueError("Embeddings model not configured for PaperService")

        # Generate embedding for the query
        embedding = self.embeddings_model.embed_query(query)
        
        # Call repository search
        return self.repository.search(query, embedding, limit)
    

    def list_all(self, filters: dict[str, object] | None = None) -> list[Paper]:
        return self.repository.list_all(filters)


    def get_by_id(self, paper_id: int) -> Paper | None:
        return self.repository.get_by_id(paper_id)


    def patch(self, paper_id: int, data: dict[str, object]) -> Paper | None:
        return self.repository.patch(paper_id, data)


    def remove_by_id(self, paper_id: int) -> int:
        return self.repository.remove_by_id(paper_id)
    
