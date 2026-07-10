Movie Recommendation System
A simple AI movie recommendation web app built with FastAPI. It recommends similar movies, lets users like or dislike movies, and shows personalized recommendations.
Live Demo
Visit the deployed app here:
https://movie-recommendation-system-sbjp.onrender.com
Note: This is hosted on Render's free plan, so the first visit may take 50 seconds or more if the service was sleeping.
Features
Browse movies
Search movies
Get similar movie recommendations
Like and dislike movies
Get personalized recommendations
View basic recommendation metrics
Works without a movie poster API key
API Key Note
This project does not require an API key to run.
If no TMDB API key is added, the app uses placeholder poster images instead of real movie posters. The recommendation system still works normally.
If you want real posters later, create a free TMDB API key and add it as:
TMDB_API_KEY=your_api_key_here
Tech Stack
Python
FastAPI
Pandas
NumPy
Scikit-learn
HTML, CSS, JavaScript
Render for deployment
Run Locally
Clone the project:
git clone https://github.com/SajjadShaik2005/Movie_recommendation_system.git
cd Movie_recommendation_system
Create and activate a virtual environment:
python -m venv .venv
.venv\Scripts\activate
Install dependencies:
pip install -r requirements.txt
Start the app:
uvicorn app.main:app --host 0.0.0.0 --port 8000
Open in your browser:
http://localhost:8000
Deploy On Render
Use these settings on Render:
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
No environment variables are required unless you want real TMDB movie posters.
Project Structure
app/
  main.py
  core/
  engine/
  static/
data/
  movies.csv
scripts/
tests/
requirements.txt
Dockerfile
run.py
