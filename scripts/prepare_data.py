import os
import pandas as pd
import requests

def prepare_data():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(data_dir, exist_ok=True)
    csv_path = os.path.join(data_dir, "movies.csv")
    
    if os.path.exists(csv_path):
        print("Data already exists!")
        return

    print("Downloading dataset...")
    # Using a reliable github dataset link for TMDB 5000 Movies
    url = "https://raw.githubusercontent.com/Ybi-Foundation/Dataset/main/Movies%20Recommendation.csv"
    
    response = requests.get(url)
    with open(csv_path, "wb") as f:
        f.write(response.content)
        
    print("Processing dataset...")
    # The dataset contains columns: Movie_ID, Movie_Title, Movie_Genre, Movie_Language, Movie_Budget, Movie_Popularity, Movie_Release_Date, Movie_Revenue, Movie_Runtime, Movie_Vote, Movie_Vote_Count, Movie_Homepage, Movie_Keywords, Movie_Overview, Movie_Production_House, Movie_Production_Country, Movie_Spoken_Language, Movie_Tagline, Movie_Cast, Movie_Crew, Movie_Director
    df = pd.read_csv(csv_path)
    
    # Rename for consistency in our app
    df = df.rename(columns={
        "Movie_ID": "id",
        "Movie_Title": "title",
        "Movie_Genre": "genres",
        "Movie_Overview": "overview",
        "Movie_Cast": "cast",
        "Movie_Director": "director",
        "Movie_Popularity": "popularity",
        "Movie_Release_Date": "release_date",
        "Movie_Vote": "vote_average"
    })
    
    # Fill missing values
    df['overview'] = df['overview'].fillna('')
    df['genres'] = df['genres'].fillna('')
    df['cast'] = df['cast'].fillna('')
    df['director'] = df['director'].fillna('')
    
    # Select only required columns
    columns = ["id", "title", "genres", "overview", "cast", "director", "popularity", "release_date", "vote_average"]
    
    # We only need about 1500 movies for good performance and memory constraints on free tiers
    # Let's sort by popularity and take the top 1500
    df = df.sort_values(by="popularity", ascending=False).head(1500).reset_index(drop=True)
    
    # Generate dummy poster paths (using an external service or placehold.co for UI)
    df["poster_path"] = df["id"].apply(lambda x: f"https://image.tmdb.org/t/p/w500/placeholder.jpg") # We will replace this on frontend with real posters if possible, or placeholder
    
    df[columns].to_csv(csv_path, index=False)
    print(f"Prepared {len(df)} movies successfully at {csv_path}!")

if __name__ == "__main__":
    prepare_data()
