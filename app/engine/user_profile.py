import numpy as np
from app.engine.recommender import RecommendationEngine

class UserProfileManager:
    def __init__(self, recommender: RecommendationEngine):
        self.recommender = recommender
        # In-memory store for demo purposes: { user_id: { "liked": [movie_ids], "disliked": [movie_ids] } }
        self.profiles = {}

    def get_profile(self, user_id: str = "default"):
        if user_id not in self.profiles:
            self.profiles[user_id] = {"liked": [], "disliked": []}
        return self.profiles[user_id]

    def add_like(self, movie_id: int, user_id: str = "default"):
        profile = self.get_profile(user_id)
        if movie_id not in profile["liked"]:
            profile["liked"].append(movie_id)
        if movie_id in profile["disliked"]:
            profile["disliked"].remove(movie_id)
        return profile

    def add_dislike(self, movie_id: int, user_id: str = "default"):
        profile = self.get_profile(user_id)
        if movie_id not in profile["disliked"]:
            profile["disliked"].append(movie_id)
        if movie_id in profile["liked"]:
            profile["liked"].remove(movie_id)
        return profile

    def remove_preference(self, movie_id: int, user_id: str = "default"):
        profile = self.get_profile(user_id)
        if movie_id in profile["liked"]:
            profile["liked"].remove(movie_id)
        if movie_id in profile["disliked"]:
            profile["disliked"].remove(movie_id)
        return profile

    def get_personalized_recommendations(self, user_id: str = "default", top_n: int = 10):
        profile = self.get_profile(user_id)
        liked_ids = profile["liked"]
        
        if not liked_ids:
            # Return popular movies if no profile
            return self.recommender.get_all_movies(limit=top_n)['movies']
            
        # Get indices of liked movies
        liked_indices = self.recommender.movies_df.index[self.recommender.movies_df['id'].isin(liked_ids)].tolist()
        
        # Aggregate the similarity vectors of liked movies
        # We take the mean of the similarity vectors for all liked movies
        sim_matrix = self.recommender.similarity_matrix
        aggregated_sim = np.mean(sim_matrix[liked_indices], axis=0)
        
        # Get scores and sort
        sim_scores = list(enumerate(aggregated_sim))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Filter out movies the user has already liked or disliked
        exclude_ids = set(liked_ids + profile["disliked"])
        exclude_indices = self.recommender.movies_df.index[self.recommender.movies_df['id'].isin(exclude_ids)].tolist()
        
        movie_indices = [i[0] for i in sim_scores if i[0] not in exclude_indices]
        
        top_indices = movie_indices[:top_n]
        top_movies = self.recommender.movies_df.iloc[top_indices].to_dict('records')
        
        return top_movies
