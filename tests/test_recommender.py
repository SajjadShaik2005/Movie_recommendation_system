import pytest
import os
import pandas as pd
from app.engine.recommender import RecommendationEngine
from app.engine.user_profile import UserProfileManager
from app.engine.evaluator import Evaluator

@pytest.fixture
def test_data_path():
    # We will use the actual dataset if it exists, otherwise skip tests that need it
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "movies.csv")
    return data_path

def test_engine_initialization(test_data_path):
    if not os.path.exists(test_data_path):
        pytest.skip("Data not prepared yet.")
        
    engine = RecommendationEngine(test_data_path)
    assert engine.movies_df is not None
    assert engine.similarity_matrix is not None
    assert len(engine.movies_df) > 0

def test_get_similar_movies(test_data_path):
    if not os.path.exists(test_data_path):
        pytest.skip("Data not prepared yet.")
        
    engine = RecommendationEngine(test_data_path)
    # Get ID of first movie
    movie_id = int(engine.movies_df.iloc[0]['id'])
    
    recs = engine.get_similar_movies(movie_id, top_n=5)
    assert len(recs) == 5
    # Ensure the movie itself is not in recommendations
    assert all(r['id'] != movie_id for r in recs)

def test_user_profile(test_data_path):
    if not os.path.exists(test_data_path):
        pytest.skip("Data not prepared yet.")
        
    engine = RecommendationEngine(test_data_path)
    manager = UserProfileManager(engine)
    
    movie_id = int(engine.movies_df.iloc[0]['id'])
    
    # Test liking
    profile = manager.add_like(movie_id, "user1")
    assert movie_id in profile["liked"]
    
    # Test personalized recs
    recs = manager.get_personalized_recommendations("user1", top_n=5)
    assert len(recs) == 5
    assert all(r['id'] != movie_id for r in recs)

def test_evaluator(test_data_path):
    if not os.path.exists(test_data_path):
        pytest.skip("Data not prepared yet.")
        
    engine = RecommendationEngine(test_data_path)
    evaluator = Evaluator(engine)
    
    metrics = evaluator.evaluate_precision_recall_at_k(k=5, sample_size=5)
    assert "current_precision" in metrics
    assert "current_recall" in metrics
