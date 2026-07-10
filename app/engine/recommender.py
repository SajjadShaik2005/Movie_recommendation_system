import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class RecommendationEngine:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.movies_df = None
        self.similarity_matrix = None
        self._load_and_prepare_data()
        self._compute_similarities()

    def _load_and_prepare_data(self):
        print(f"Loading data from {self.data_path}...")
        self.movies_df = pd.read_csv(self.data_path)
        
        # Ensure correct types and fill NaNs
        for col in ['genres', 'cast', 'director', 'overview']:
            self.movies_df[col] = self.movies_df[col].fillna('').astype(str)
            
        # Create a combined cast and director feature for CountVectorizer
        # We give more weight to director by repeating it
        self.movies_df['cast_director'] = self.movies_df['cast'] + " " + self.movies_df['director'] + " " + self.movies_df['director']

        # Process genres (replace hyphens and spaces to make them unique tokens if needed, though they are usually comma-separated)
        self.movies_df['genres_processed'] = self.movies_df['genres'].apply(lambda x: x.replace(',', ' ').replace('-', ''))

    def _compute_similarities(self):
        print("Computing similarity matrices...")
        
        # 1. Genre Similarity (Weight: 0.35)
        # Using CountVectorizer since genres are discrete categories
        genre_vectorizer = CountVectorizer()
        genre_matrix = genre_vectorizer.fit_transform(self.movies_df['genres_processed'])
        genre_sim = cosine_similarity(genre_matrix, genre_matrix)
        
        # 2. Cast & Director Similarity (Weight: 0.25)
        cast_vectorizer = CountVectorizer(stop_words='english')
        cast_matrix = cast_vectorizer.fit_transform(self.movies_df['cast_director'])
        cast_sim = cosine_similarity(cast_matrix, cast_matrix)
        
        # 3. Overview NLP Similarity (Weight: 0.40)
        # Using TF-IDF to penalize common words and highlight unique descriptive words
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(self.movies_df['overview'])
        overview_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
        
        # Blended Similarity Matrix
        self.similarity_matrix = (0.35 * genre_sim) + (0.25 * cast_sim) + (0.40 * overview_sim)
        
        print("Similarity matrices computed successfully!")

    def get_similar_movies(self, movie_id: int, top_n: int = 10, exclude_ids: list = None) -> list:
        if exclude_ids is None:
            exclude_ids = []
            
        # Find the index of the movie
        idx_series = self.movies_df.index[self.movies_df['id'] == movie_id]
        if len(idx_series) == 0:
            return []
        
        idx = idx_series[0]
        
        # Get similarity scores for this movie
        sim_scores = list(enumerate(self.similarity_matrix[idx]))
        
        # Sort movies based on similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Filter out the movie itself and any excluded ids
        exclude_indices = [idx]
        if exclude_ids:
            exclude_indices.extend(self.movies_df.index[self.movies_df['id'].isin(exclude_ids)].tolist())
            
        movie_indices = [i[0] for i in sim_scores if i[0] not in exclude_indices]
        
        # Return top N
        top_indices = movie_indices[:top_n]
        top_movies = self.movies_df.iloc[top_indices].to_dict('records')
        
        return top_movies
        
    def get_movie_by_id(self, movie_id: int):
        movie = self.movies_df[self.movies_df['id'] == movie_id]
        if not movie.empty:
            return movie.iloc[0].to_dict()
        return None

    def get_all_movies(self, limit: int = 50, skip: int = 0, query: str = None):
        df = self.movies_df
        if query:
            df = df[df['title'].str.contains(query, case=False, na=False) | df['genres'].str.contains(query, case=False, na=False)]
        
        total = len(df)
        movies = df.iloc[skip:skip+limit].to_dict('records')
        return {"total": total, "movies": movies}
