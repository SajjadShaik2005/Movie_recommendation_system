import os
import requests
import urllib.parse
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel

from app.core.config import settings
from app.engine.recommender import RecommendationEngine
from app.engine.user_profile import UserProfileManager
from app.engine.evaluator import Evaluator

# Initialize global engine instances
recommender = None
user_profile_manager = None
evaluator = None

app = FastAPI(title="AI Movie Recommendation System")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    global recommender, user_profile_manager, evaluator
    print("Initializing Recommendation Engine...")
    
    # If the data file doesn't exist, we run the prepare_data script
    if not os.path.exists(settings.data_path):
        import subprocess
        script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "scripts", "prepare_data.py")
        subprocess.run(["python", script_path])
        
    recommender = RecommendationEngine(settings.data_path)
    user_profile_manager = UserProfileManager(recommender)
    evaluator = Evaluator(recommender)
    print("Recommendation Engine Ready!")

# --- API Endpoints ---

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Engine is running."}

@app.get("/api/movies")
def get_movies(limit: int = 50, skip: int = 0, query: Optional[str] = None):
    return recommender.get_all_movies(limit=limit, skip=skip, query=query)

@app.get("/api/movies/{movie_id}")
def get_movie(movie_id: int):
    movie = recommender.get_movie_by_id(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

@app.get("/api/recommend/{movie_id}")
def get_item_recommendations(movie_id: int, top_n: int = 10):
    recs = recommender.get_similar_movies(movie_id, top_n=top_n)
    return {"recommendations": recs}

# Poster Cache to avoid hammering the TMDB API
poster_cache = {}

@app.get("/api/poster")
def get_poster(title: str):
    if title in poster_cache:
        return RedirectResponse(poster_cache[title])
        
    fallback_url = f"https://placehold.co/500x750/1e1e2d/a4b0be?text={urllib.parse.quote(title)}"
    
    if not settings.tmdb_api_key:
        return RedirectResponse(fallback_url)
        
    try:
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={settings.tmdb_api_key}&query={urllib.parse.quote(title)}"
        res = requests.get(search_url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if data.get("results") and len(data["results"]) > 0:
                path = data["results"][0].get("poster_path")
                if path:
                    poster_url = f"https://image.tmdb.org/t/p/w500{path}"
                    poster_cache[title] = poster_url
                    return RedirectResponse(poster_url)
    except Exception as e:
        print(f"Error fetching poster for {title}: {e}")
        
    # Cache fallback to avoid retrying failed lookups
    poster_cache[title] = fallback_url
    return RedirectResponse(fallback_url)

class ProfileAction(BaseModel):
    movie_id: int
    user_id: str = "default"

@app.post("/api/profile/like")
def like_movie(action: ProfileAction):
    profile = user_profile_manager.add_like(action.movie_id, action.user_id)
    return {"status": "success", "profile": profile}

@app.post("/api/profile/dislike")
def dislike_movie(action: ProfileAction):
    profile = user_profile_manager.add_dislike(action.movie_id, action.user_id)
    return {"status": "success", "profile": profile}

@app.get("/api/profile/recommendations")
def get_personalized_recommendations(user_id: str = "default", top_n: int = 10):
    recs = user_profile_manager.get_personalized_recommendations(user_id=user_id, top_n=top_n)
    return {"recommendations": recs}

@app.get("/api/profile")
def get_profile(user_id: str = "default"):
    return user_profile_manager.get_profile(user_id)

@app.get("/api/metrics")
def get_metrics():
    metrics = evaluator.evaluate_precision_recall_at_k(k=10, sample_size=50)
    return {"metrics": metrics}

# Mount static files
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(static_dir, exist_ok=True)
os.makedirs(os.path.join(static_dir, "css"), exist_ok=True)
os.makedirs(os.path.join(static_dir, "js"), exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def serve_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse(status_code=404, content={"message": "Index file not found."})
