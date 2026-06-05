import pytest
from flask import Flask
from etl.transformer import Transformer
from etl.models import XMLData, ResearcherData, Paper as ETLPaper
from etl.storage import Storage

def test_hybrid_search_functionality(app: Flask):
    """
    Test the RRF hybrid search functionality.
    We'll insert some papers and then search for them.
    """
    paper_service = app.config['PAPER_SERVICE']
    researcher_service = app.config['RESEARCHER_SERVICE']
    
    # 1. Setup: Create a researcher
    # XMLData is needed for ResearcherService.add_researcher
    mock_data = XMLData(
        filename="search_test.xml",
        filehash="search_hash",
        researcher_data=ResearcherData(
            full_name="Search Tester",
            lattes_id="99999999",
            papers=[],
            academic_formations=[],
            research_areas=[],
            conference_papers=[],
            advisings=[]
        )
    )
    researcher_id = researcher_service.add_researcher(mock_data)
    
    # 2. Setup: Create papers with specific titles and embeddings
    # We'll use the actual embedding model to get "real" embeddings for our test papers
    embeddings_model = paper_service.embeddings_model
    
    paper_titles = [
        "Artificial Intelligence in Healthcare",
        "Deep Learning for Image Recognition",
        "Climate Change and its impact on biodiversity",
        "The history of Ancient Rome",
        "Healthcare systems in Brazil"
    ]
    
    for title in paper_titles:
        embedding = embeddings_model.embed_query(title)
        paper_service.add_paper(
            title=title,
            researcher_id=researcher_id,
            title_embeddings=embedding
        )
    
    # 3. Perform Hybrid Search
    # Query that should match "Artificial Intelligence in Healthcare" via keywords
    # and maybe "Healthcare systems in Brazil" via keywords,
    # and "Deep Learning for Image Recognition" via semantic similarity (if AI is related to DL)
    query = "AI in health"
    results = paper_service.hybrid_search(query, limit=5)
    
    # 4. Assertions
    assert len(results) > 0
    
    # The first result should ideally be "Artificial Intelligence in Healthcare"
    # as it has both semantic (AI/Health) and keyword matches (Healthcare/Intelligence)
    top_paper, top_score = results[0]
    assert "Healthcare" in top_paper.title or "AI" in top_paper.title or "Artificial Intelligence" in top_paper.title
    
    print(f"\nQuery: {query}")
    for i, (paper, score) in enumerate(results):
        print(f"Rank {i+1}: {paper.title} (Score: {score:.4f})")
    
    # Verify we have at least 2 results if they are relevant
    assert len(results) >= 2
    
    # Check that scores are descending
    scores = [score for _, score in results]
    assert scores == sorted(scores, reverse=True)
