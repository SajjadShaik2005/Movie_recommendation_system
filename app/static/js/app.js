const API_BASE = '/api';
let currentSkip = 0;
const LIMIT = 24;
let isSearching = false;
let currentSearchQuery = "";
let currentUserId = "default_user";

// DOM Elements
const mainGrid = document.getElementById('main-movie-grid');
const searchInput = document.getElementById('search-input');
const loadMoreBtn = document.getElementById('load-more-btn');
const modal = document.getElementById('movie-modal');
const closeModalBtn = document.getElementById('close-modal-btn');
const likedList = document.getElementById('liked-movies-list');
const recsGrid = document.getElementById('personalized-recs');
const refreshRecsBtn = document.getElementById('refresh-recs-btn');
const runEvalBtn = document.getElementById('run-eval-btn');

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    loadMovies();
    loadProfile();
    
    // Event Listeners
    loadMoreBtn.addEventListener('click', () => {
        if (!isSearching) {
            currentSkip += LIMIT;
            loadMovies();
        } else {
            currentSkip += LIMIT;
            searchMovies(currentSearchQuery, true);
        }
    });

    searchInput.addEventListener('input', debounce((e) => {
        const query = e.target.value.trim();
        mainGrid.innerHTML = '';
        currentSkip = 0;
        if (query.length > 0) {
            isSearching = true;
            currentSearchQuery = query;
            searchMovies(query);
        } else {
            isSearching = false;
            currentSearchQuery = "";
            loadMovies();
        }
    }, 500));

    closeModalBtn.addEventListener('click', () => {
        modal.classList.remove('active');
    });

    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('active');
        }
    });
    
    refreshRecsBtn.addEventListener('click', loadPersonalizedRecommendations);
    runEvalBtn.addEventListener('click', runOfflineEvaluation);
});

// API Calls
async function fetchAPI(endpoint, options = {}) {
    try {
        const res = await fetch(`${API_BASE}${endpoint}`, options);
        return await res.json();
    } catch (err) {
        console.error("API Error:", err);
        return null;
    }
}

async function loadMovies() {
    const data = await fetchAPI(`/movies?limit=${LIMIT}&skip=${currentSkip}`);
    if (data && data.movies) {
        renderMovies(data.movies, mainGrid, currentSkip > 0);
        if (data.movies.length < LIMIT) loadMoreBtn.style.display = 'none';
        else loadMoreBtn.style.display = 'inline-block';
    }
}

async function searchMovies(query, append = false) {
    const data = await fetchAPI(`/movies?limit=${LIMIT}&skip=${currentSkip}&query=${encodeURIComponent(query)}`);
    if (data && data.movies) {
        renderMovies(data.movies, mainGrid, append);
        if (data.movies.length < LIMIT) loadMoreBtn.style.display = 'none';
        else loadMoreBtn.style.display = 'inline-block';
    }
}

async function loadProfile() {
    const profile = await fetchAPI(`/profile?user_id=${currentUserId}`);
    if (profile) {
        updateLikedListUI(profile.liked);
        loadPersonalizedRecommendations();
    }
}

async function toggleLike(movieId, isLiked) {
    const endpoint = isLiked ? '/profile/like' : '/profile/dislike';
    const res = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ movie_id: movieId, user_id: currentUserId })
    });
    const data = await res.json();
    if (data.status === 'success') {
        updateLikedListUI(data.profile.liked);
        loadPersonalizedRecommendations();
    }
}

async function loadPersonalizedRecommendations() {
    recsGrid.innerHTML = '<div style="color: var(--text-muted); font-size: 0.9rem;">Computing recommendations...</div>';
    const data = await fetchAPI(`/profile/recommendations?user_id=${currentUserId}&top_n=3`);
    if (data && data.recommendations) {
        recsGrid.innerHTML = '';
        if (data.recommendations.length === 0) {
            recsGrid.innerHTML = '<div style="color: var(--text-muted); font-size: 0.9rem;">Like some movies first!</div>';
            return;
        }
        renderMovies(data.recommendations, recsGrid, false, true);
    }
}

async function runOfflineEvaluation() {
    runEvalBtn.textContent = "Computing metrics...";
    runEvalBtn.disabled = true;
    
    const data = await fetchAPI('/metrics');
    if (data && data.metrics) {
        document.getElementById('metric-precision').textContent = (data.metrics.current_precision * 100).toFixed(1) + "%";
        document.getElementById('metric-recall').textContent = (data.metrics.current_recall * 100).toFixed(1) + "%";
        document.getElementById('metric-improvement').textContent = "+" + data.metrics.improvement_pct.toFixed(1) + "%";
    }
    
    runEvalBtn.textContent = "Run Offline Evaluation";
    runEvalBtn.disabled = false;
}

// Rendering
function renderMovies(movies, container, append = false, isSmall = false) {
    if (!append) container.innerHTML = '';
    
    movies.forEach(movie => {
        const card = document.createElement('div');
        card.className = 'movie-card';
        if (isSmall) card.style.minHeight = '150px';
        
        card.innerHTML = `
            <img src="/api/poster?title=${encodeURIComponent(movie.title)}" alt="${movie.title}" onerror="this.src='https://placehold.co/500x750/1e1e2d/a4b0be?text=${encodeURIComponent(movie.title)}'">
            <div class="overlay">
                <div class="movie-title" style="${isSmall ? 'font-size:0.9rem;' : ''}">${movie.title}</div>
                <div class="movie-meta">
                    <span>${movie.release_date ? movie.release_date.split('-')[0] : 'N/A'}</span>
                    <span><i data-lucide="star" width="12" height="12"></i> ${movie.vote_average.toFixed(1)}</span>
                </div>
            </div>
        `;
        
        card.addEventListener('click', () => openModal(movie.id));
        container.appendChild(card);
    });
    lucide.createIcons();
}

async function openModal(movieId) {
    const movie = await fetchAPI(`/movies/${movieId}`);
    if (!movie) return;

    document.getElementById('modal-poster').src = `/api/poster?title=${encodeURIComponent(movie.title)}`;
    document.getElementById('modal-poster').onerror = function() { this.src = `https://placehold.co/500x750/1e1e2d/a4b0be?text=${encodeURIComponent(movie.title)}`};
    document.getElementById('modal-title').textContent = movie.title;
    document.getElementById('modal-year').textContent = movie.release_date ? movie.release_date.split('-')[0] : '';
    document.getElementById('modal-rating').textContent = movie.vote_average.toFixed(1);
    document.getElementById('modal-overview').textContent = movie.overview || "No overview available.";
    
    const genresContainer = document.getElementById('modal-genres');
    genresContainer.innerHTML = '';
    
    // Parse genres if it's a JSON string (TMDB format)
    let genresList = [];
    try {
        const parsed = JSON.parse(movie.genres.replace(/'/g, '"'));
        genresList = parsed.map(g => g.name);
    } catch(e) {
        // Fallback if it's just a comma separated string
        genresList = movie.genres.split(' ');
    }
    
    genresList.slice(0,4).forEach(genre => {
        if(genre.trim()) {
            const span = document.createElement('span');
            span.className = 'tag';
            span.textContent = genre;
            genresContainer.appendChild(span);
        }
    });

    // Buttons
    const btnLike = document.getElementById('btn-like');
    const btnDislike = document.getElementById('btn-dislike');
    
    // Check if currently liked
    const profile = await fetchAPI(`/profile?user_id=${currentUserId}`);
    let isLiked = profile && profile.liked.includes(movie.id);
    let isDisliked = profile && profile.disliked.includes(movie.id);
    
    btnLike.className = isLiked ? 'btn primary' : 'btn';
    btnDislike.className = isDisliked ? 'btn primary' : 'btn';

    btnLike.onclick = () => {
        toggleLike(movie.id, true);
        btnLike.className = 'btn primary';
        btnDislike.className = 'btn';
    };
    
    btnDislike.onclick = () => {
        toggleLike(movie.id, false);
        btnDislike.className = 'btn primary';
        btnLike.className = 'btn';
    };

    // Fetch Similar Movies
    const similarGrid = document.getElementById('modal-similar-grid');
    similarGrid.innerHTML = '<div style="color: var(--text-muted);">Loading similar movies via AI...</div>';
    
    const similarData = await fetchAPI(`/recommend/${movie.id}?top_n=3`);
    if (similarData && similarData.recommendations) {
        renderMovies(similarData.recommendations, similarGrid, false, true);
    }

    modal.classList.add('active');
}

async function updateLikedListUI(likedIds) {
    likedList.innerHTML = '';
    if (likedIds.length === 0) {
        likedList.innerHTML = '<li>No movies liked yet.</li>';
        return;
    }
    
    for (const id of likedIds.slice(-5).reverse()) { // Show last 5
        const movie = await fetchAPI(`/movies/${id}`);
        if (movie) {
            const li = document.createElement('li');
            li.style.marginBottom = '0.5rem';
            li.style.cursor = 'pointer';
            li.style.whiteSpace = 'nowrap';
            li.style.overflow = 'hidden';
            li.style.textOverflow = 'ellipsis';
            li.innerHTML = `<i data-lucide="check" width="12" height="12" style="color:var(--accent);"></i> ${movie.title}`;
            li.onclick = () => openModal(movie.id);
            likedList.appendChild(li);
        }
    }
    lucide.createIcons();
}

// Utility
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
