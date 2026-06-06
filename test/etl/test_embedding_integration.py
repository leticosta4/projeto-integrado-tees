import pytest
import os
from flask import Flask
from etl.transformer import Transformer
from etl.models import XMLData, ResearcherData, Paper
from etl.storage import Storage

def test_transformer_generates_embeddings_when_enabled(app: Flask):
    """
    Localized test to verify that the Transformer correctly generates 
    embeddings for paper titles when ENABLE_EMBEDDINGS is True.
    """
    # Create a single mock researcher with one paper
    mock_paper = Paper(
        title="Impact of Artificial Intelligence in Modern Software Engineering",
        year=2026,
        nature="COMPLETO"
    )
    
    mock_data = XMLData(
        filename="test_embedding.xml",
        filehash="test_hash_123",
        researcher_data=ResearcherData(
            full_name="Test Researcher",
            lattes_id="0000000000000000",
            papers=[mock_paper],
            academic_formations=[],
            research_areas=[],
            conference_papers=[],
            advisings=[]
        )
    )

    # Force enable embeddings for this specific test
    # Note: This requires a valid GOOGLE_API_KEY in the environment/settings
    transformer = Transformer(enable_embeddings=True)
    
    transformed_data = transformer.transform([mock_data])
    
    paper = transformed_data[0].researcher_data.papers[0]
    
    # Assertions
    assert paper.title == "Impact of Artificial Intelligence in Modern Software Engineering"
    assert paper.title_embeddings is not None
    assert isinstance(paper.title_embeddings, list)
    assert len(paper.title_embeddings) > 0
    assert all(isinstance(x, float) for x in paper.title_embeddings)

    # Optional: Verify storage actually saves it
    storage = Storage(app)
    storage.store(transformed_data)
    
    paper_service = app.config['PAPER_SERVICE']
    stored_paper = paper_service.get_paper_by_title(paper.title)
    
    assert stored_paper is not None
    assert stored_paper.title_embeddings is not None
    assert len(stored_paper.title_embeddings) == len(paper.title_embeddings)
