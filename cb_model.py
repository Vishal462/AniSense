import pandas as pd
import numpy as np
import joblib
import re
import requests
from rapidfuzz import process
import os
import json
from datetime import datetime, timedelta


TRAILER_CACHE_FILE = "trailer_cache.json"
trailer_cache = {}


def load_trailer_cache():
    """Load trailer cache from file"""
    global trailer_cache
    try:
        if os.path.exists(TRAILER_CACHE_FILE):
            with open(TRAILER_CACHE_FILE, 'r', encoding='utf-8') as f:
                trailer_cache = json.load(f)
            print(f"Loaded trailer cache with {len(trailer_cache)} entries")
        else:
            trailer_cache = {}
    except Exception as e:
        print(f"Error loading trailer cache: {e}")
        trailer_cache = {}


def save_trailer_cache():
    """Save trailer cache to file"""
    try:
        with open(TRAILER_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(trailer_cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving trailer cache: {e}")


def get_cached_trailer_id(anilist_id, media_type):
    """Get trailer ID from cache if available and not expired"""
    cache_key = f"{anilist_id}_{media_type}"

    if cache_key in trailer_cache:
        cache_data = trailer_cache[cache_key]
        # Check if cache is still valid (30 days expiry)
        cache_time = datetime.fromisoformat(cache_data['timestamp'])
        if datetime.now() - cache_time < timedelta(days=30):
            return cache_data['trailer_id']
        else:
            # Remove expired cache entry
            del trailer_cache[cache_key]

    return None


def set_cached_trailer_id(anilist_id, media_type, trailer_id):
    """Store trailer ID in cache"""
    cache_key = f"{anilist_id}_{media_type}"
    trailer_cache[cache_key] = {
        'trailer_id': trailer_id,
        'timestamp': datetime.now().isoformat(),
        'media_type': media_type
    }
    # Save cache after each update (or you can batch save)
    save_trailer_cache()


# Load cache when module is imported
load_trailer_cache()


# -----------------------------
# Helper Functions
# -----------------------------
def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r"<[^>]*>", "", text)  # Remove HTML
    text = re.sub(r"\s+", " ", text).strip()  # Remove extra spaces
    if text and not text.endswith(('.', '!', '?')):
        text += '.'
    return text


def safe_list(items):
    if isinstance(items, (list, tuple, set)):
        return [str(x) for x in items if x]
    elif items:
        return [str(items)]
    return []


def format_date(year, month, day, fallback="Ongoing"):
    if pd.isna(year):
        return fallback
    month = int(month) if not pd.isna(month) else 1
    day = int(day) if not pd.isna(day) else 1
    return f"{int(year)}-{month:02d}-{day:02d}"


def format_relations(rel_text):
    """Readable relation text."""
    if not isinstance(rel_text, str) or not rel_text.strip():
        return "No notable related works."
    rel_text = re.sub(r"\s+", " ", rel_text.strip())
    rel_text = re.sub(
        r"(adaptation|sequel|prequel|alternative|side story|spin off|character|summary|other)",
        lambda m: m.group(1).capitalize(),
        rel_text,
    )
    return rel_text


def format_episodes(ep, status):
    """Properly format episodes with releasing status"""
    if ep and ep > 0:
        return f"{int(ep)} Episodes"
    elif status and status.lower() in ["releasing", "ongoing"]:
        return "New episodes releasing"
    elif ep == 0:
        return "New episodes releasing"
    return "N/A"


def format_chapters(chap, status):
    if chap and chap > 0:
        return f"{int(chap)} Chapters"
    elif status and status.lower() in ["releasing", "ongoing"]:
        return "New chapters releasing"
    elif chap == 0:
        return "New chapters releasing"
    return "N/A"


def format_volumes(vol, status):
    """Format volumes with releasing status"""
    if vol and vol > 0:
        return f"{int(vol)} Volumes"
    elif status and status.lower() in ["releasing", "ongoing"]:
        return "New volumes releasing"
    elif vol == 0:
        return "New volumes releasing"
    return "N/A"


def get_trailer_id(anilist_id, media_type):
    """Fetch trailer ID from AniList API with caching"""
    if not anilist_id or pd.isna(anilist_id):
        return None

    # Convert to native Python int
    try:
        media_id = int(anilist_id)
    except (ValueError, TypeError):
        return None

    # Check cache first
    cached_trailer = get_cached_trailer_id(media_id, media_type)
    if cached_trailer is not None:
        print(f"Using cached trailer ID for {media_id}")
        return cached_trailer

    # If not in cache, fetch from API
    query = '''
    query ($id: Int, $type: MediaType) {
        Media (id: $id, type: $type) {
            trailer {
                id
                site
            }
        }
    }
    '''

    variables = {
        'id': media_id,
        'type': media_type.upper() if media_type else 'ANIME'
    }

    url = 'https://graphql.anilist.co'

    try:
        response = requests.post(url, json={'query': query, 'variables': variables}, timeout=5)
        response.raise_for_status()
        data = response.json()

        # Check if we have valid trailer data
        trailer_id = None
        if (data.get('data') and
                data['data'].get('Media') and
                data['data']['Media'].get('trailer') and
                data['data']['Media']['trailer'].get('site') == 'youtube' and
                data['data']['Media']['trailer'].get('id')):
            trailer_id = data['data']['Media']['trailer']['id']

        # Cache the result (even if None to avoid re-fetching failures)
        set_cached_trailer_id(media_id, media_type, trailer_id)

        if trailer_id:
            print(f"Fetched and cached trailer ID for {media_id}: {trailer_id}")
        else:
            print(f"No trailer found for {media_id}, cached None")

        return trailer_id

    except requests.exceptions.Timeout:
        print(f"Timeout fetching trailer for ID {media_id}")
        # Cache None to avoid repeated timeouts
        set_cached_trailer_id(media_id, media_type, None)
    except requests.exceptions.RequestException as e:
        print(f"Request error fetching trailer for ID {media_id}: {e}")
        set_cached_trailer_id(media_id, media_type, None)
    except Exception as e:
        print(f"Unexpected error fetching trailer for ID {media_id}: {e}")
        set_cached_trailer_id(media_id, media_type, None)

    return None

manual_aliases = {
    "aot": "attack on titan",
    "jjk": "jujutsu kaisen",
    "opm": "one punch man",
    "hxh": "hunter x hunter",
    "nrt": "naruto"
}

# -----------------------------
# Load Model Components
# -----------------------------
ANIME_PKL = "data/anime_cb_data_merged.pkl"
SIM_NPY = "data/fused_sim_refined(all-mpnet-base-v2).npy"
TFIDF_JOB = "data/tfidf_vectorizer_merged.joblib"


def load_cb_model():
    anime_df = pd.read_pickle(ANIME_PKL)
    similarity_matrix = np.load(SIM_NPY)
    vectorizer = joblib.load(TFIDF_JOB)
    return anime_df, similarity_matrix, vectorizer

def find_best_match(query, anime_titles):
    match, score, idx = process.extractOne(query, anime_titles)
    return match, score, idx

# -----------------------------
# Fuzzy Match
# -----------------------------

# -----------------------------
# Main Recommendation Function
# -----------------------------
def get_cb_recommendations(anime_name, top_n=10, media_type=None, manga_format=None):
    anime_df, similarity_matrix, _ = load_cb_model()
    df = anime_df.copy()
    df["title_aliases"] = df.apply(lambda row: safe_list([
        row.get("display_title", ""),
        row.get("title_romaji", ""),
        row.get("title_english", ""),
        row.get("title_native", "")
    ]), axis=1)

    df["normalized_aliases"] = df["title_aliases"].apply(
        lambda titles: [t.strip().lower() for t in titles if isinstance(t, str)]
    )

    # Filtering
    if media_type:
        df = df[df["fetched_type"].str.upper() == media_type.upper()]
    if media_type == "MANGA" and manga_format and manga_format.upper() != "ALL":
        df = df[df["format"].str.upper() == manga_format.upper()]
    if df.empty:
        return pd.DataFrame([{"error": "No items match the selected filter."}])

    raw_query = anime_name.strip().lower()
    normalized_query = manual_aliases.get(raw_query, raw_query)

    # Fuzzy match
    alias_map = {}
    for idx, aliases in df["normalized_aliases"].items():
        for title in aliases:
            alias_map[title] = idx
    match, score, _ = find_best_match(normalized_query, list(alias_map.keys()))
    if score < 60:
        return pd.DataFrame([{"error": f"No close match found for '{anime_name}'."}])
    true_idx = alias_map[match]

    # Similarities
    sim_scores = list(enumerate(similarity_matrix[true_idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = [x for x in sim_scores if x[0] in df.index][1: top_n + 20]

    query_genres = set(safe_list(anime_df.loc[true_idx]["genres"]))
    query_tags = set(safe_list(anime_df.loc[true_idx]["tags"]))

    def genre_match_score(idx):
        target_genres = set(safe_list(anime_df.loc[idx]["genres"]))
        return len(query_genres & target_genres)

    def tag_match_score(idx):
        target_tags = set(safe_list(anime_df.loc[idx]["tags"]))
        return len(query_tags & target_tags)

    def combined_score(idx, sim):
        g_score = genre_match_score(idx)
        t_score = tag_match_score(idx)
        return g_score * 0.4 + t_score * 0.2 + sim * 0.4

    genre_filtered = [x for x in sim_scores if genre_match_score(x[0]) > 0]
    genre_top = genre_filtered[:4]
    remaining = [x for x in sim_scores if x not in genre_top]
    remaining = sorted(remaining, key=lambda x: combined_score(x[0], x[1]), reverse=True)
    final_scores = genre_top + remaining[:top_n - len(genre_top)]

    recs = []
    for i, sim in final_scores:
        m = anime_df.loc[i].to_dict()

        # Clean & format
        m["display_title"] = clean_text(m.get("display_title", "N/A"))
        m["title_romaji"] = clean_text(m.get("title_romaji", "N/A"))
        m["title_english"] = clean_text(m.get("title_english", "N/A"))
        m["title_native"] = clean_text(m.get("title_native", "N/A"))

        m["description"] = clean_text(m.get("description", "N/A"))
        m["source"] = clean_text(m.get("source", "N/A"))
        m["status"] = clean_text(m.get("status", "N/A"))
        m["season"] = clean_text(m.get("season", "N/A"))
        m["relations"] = format_relations(clean_text(m.get("relations", "")))
        m["chapters_display"] = format_chapters(m.get("chapters"), m.get("status", "").lower())
        m["volumes_display"] = format_volumes(m.get("volumes"), m.get("status", "").lower())
        m["format"] = clean_text(m.get("format", "N/A"))

        m["studio_links"] = safe_list(m.get("studio_links"))
        m["studios"] = safe_list(m.get("studio"))
        m["similarity_score"] = round(float(sim), 3)

        m["start_date"] = format_date(m.get("start_year"), m.get("start_month"), m.get("start_day"), fallback="N/A")
        m["end_date"] = format_date(m.get("end_year"), m.get("end_month"), m.get("end_day"), fallback="Ongoing")

        m["episodes_display"] = format_episodes(m.get("episodes"), m.get("status").lower())

        m["popularity"] = m.get("popularity") or 0
        m["favourites"] = m.get("favourites") or 0

        m["trailer_thumbnail"] = m.get("trailer_thumbnail") or ""
        m["coverImage"] = m.get("coverImage") or ""
        m["bannerImage"] = m.get("bannerImage") or ""

        # Fetch trailer ID (with caching)
        m["trailer_id"] = get_trailer_id(m.get("id"), m.get("fetched_type"))

        recs.append(m)

    return pd.DataFrame(recs)