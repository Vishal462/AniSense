import streamlit as st
import re
from cb_model import get_cb_recommendations
from urllib.parse import quote
# -----------------------------
# Helper functions
# -----------------------------
def format_description(desc: str) -> str:
    if not desc or not isinstance(desc, str):
        return "No description available."
    desc = " ".join(desc.strip().split())
    if not desc:
        return "No description available."
    desc = desc[0].upper() + desc[1:]
    if desc and desc[-1] not in ".!?":
         desc += "."
    sentences = []
    current = ""
    words = desc.split()
    for i, word in enumerate(words):
        current += word + " "
        next_word = words[i + 1] if i < len(words) - 1 else ""
        if (word.endswith(('.', '!', '?')) or
             (next_word and next_word[0].isupper() and len(current.split()) > 8)):
             sentence = current.strip()
             if sentence and not sentence[-1] in '.!?':
                 sentence += '.'
             sentences.append(sentence)
             current = ""

    if current.strip():
        last_sentence = current.strip()
        if not last_sentence[-1] in '.!?':
            last_sentence += '.'
        sentences.append(last_sentence)

    formatted_desc = " ".join(sentences)
    formatted_desc = re.sub(r'\s+([.,!?])', r'\1', formatted_desc)  # Remove space before punctuation
    formatted_desc = re.sub(r'([.,!?])([A-Za-z])', r'\1 \2', formatted_desc)  # Add space after punctuation
    formatted_desc = re.sub(r'\s+', ' ', formatted_desc)  # Remove extra spaces
    return formatted_desc


def format_title(title: str) -> str:
    """Convert title to proper case while preserving acronyms and special words."""
    if not title or not isinstance(title, str):
        return "N/A"
    # Remove trailing period and strip whitespace
    title = title.strip().rstrip('.')
    # Common anime/manga words that should stay capitalized
    special_words = {'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X'}
    words = title.split()
    formatted_words = []
    for i, word in enumerate(words):
        if word.upper() in special_words or (len(word) > 1 and word.isupper()):
            # Preserve acronyms and Roman numerals
            formatted_words.append(word)
        else:
            # Capitalize first letter, lowercase the rest
            formatted_words.append(word[0].upper() + word[1:].lower())
    return ' '.join(formatted_words)

# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(page_title="AniSense", layout="wide",page_icon="naruto.jpg")
st.markdown("""
<div class="main-header">
    <h1 style='margin:0; color:white; font-size:2.5rem; font-weight:700;'>AniSense : An Anime and Manga Recommender</h1>
    <p style='margin:0; color:rgba(255,255,255,0.8); font-size:1.1rem; margin-top:10px;'>
        Discover your next favorite anime or manga with AI-powered recommendations
    </p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Streaming Platforms
# -----------------------------
platforms = [
    {"name": "Netflix", "icon": "https://img.icons8.com/color/96/netflix.png", "url": "https://www.netflix.com/"},
    {"name": "Crunchyroll", "icon": "https://img.icons8.com/color/96/crunchyroll.png", "url": "https://www.crunchyroll.com/"},
    {"name": "Amazon Prime", "icon": "https://img.icons8.com/color/96/amazon-prime-video.png", "url": "https://www.primevideo.com/"},
    {"name": "Hulu", "icon": "https://img.icons8.com/color/96/hulu.png", "url": "https://www.hulu.com/"},
    {"name": "Hoopla", "icon": "https://img.icons8.com/color/96/hoopla.png", "url": "https://www.hoopladigital.com/"},
    {"name": "iQIYI", "icon": "https://img.icons8.com/color/96/iqiyi.png", "url": "https://www.iq.com/"},
    {"name": "Bilibili TV", "icon": "https://img.icons8.com/color/96/bilibili.png", "url": "https://www.bilibili.tv/"},

]

st.markdown("### Platforms to Watch Anime:")
cols = st.columns(len(platforms))
for idx, p in enumerate(platforms):
    with cols[idx]:
        st.markdown(
            f"<div style='text-align:center; margin-bottom:10px;'>"
            f"<a href='{p['url']}' target='_blank' style='text-decoration:none;'>"
            f"<img src='{p['icon']}' style='width:53px; height:53px; border-radius:12px; transition: transform 0.3s; margin-bottom:5px;' "
            f"onmouseover=\"this.style.transform='scale(1.2)'\" onmouseout=\"this.style.transform='scale(1.0)'\">"
            f"<br><span style='font-size:0.90rem; color:#282828;font-weight:600'>{p['name']}</span>"
            f"</a></div>",
            unsafe_allow_html=True
        )
# Add this after the platforms section
st.markdown("### YouTube Channels:")
youtube_channels = [
    {"name": "Crunchyroll Collection", "url": "https://www.youtube.com/c/CrunchyrollCollection"},
    {"name": "TOHO Animation", "url": "https://www.youtube.com/@TOHOanimation"},
    {"name": "Muse Asia", "url": "https://www.youtube.com/c/MuseAsia"},
    {"name": "Ani-One", "url": "https://www.youtube.com/c/AniOneAsia"}
]
yt_cols = st.columns(len(youtube_channels))
for idx, channel in enumerate(youtube_channels):
    with yt_cols[idx]:
        st.markdown(
            f"<div style='text-align:center; margin-bottom:10px;'>"
            f"<a href='{channel['url']}' target='_blank' style='text-decoration:none;'>"
            f"<img src='https://img.icons8.com/color/96/youtube-play.png' style='width:53px; height:53px; border-radius:8px; transition: transform 0.3s; margin-bottom:5px;' "
            f"onmouseover=\"this.style.transform='scale(1.15)'\" onmouseout=\"this.style.transform='scale(1.0)'\">"
            f"<br><span style='font-size:0.90rem; color:#282828;font-weight:600'>{channel['name']}</span>"
            f"</a></div>",
            unsafe_allow_html=True
        )


st.markdown("---")

# -----------------------------
# CSS for Styling
# -----------------------------
st.markdown("""
<style>
/* Force style updates */
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* Global Styles */
body { 
    background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
    color: #ffffff;
    font-family: 'Inter', 'Segoe UI', sans-serif;
    line-height: 1.6;
}

/* Header Styling */
.main-header {
    background: linear-gradient(135deg, #ff4c60 0%, #ff6b7a 100%);
    padding: 2rem;
    border-radius: 20px;
    margin-bottom: 2rem;
    text-align: center;
    box-shadow: 0 10px 30px rgba(255, 76, 96, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Enhanced Card Styling */
.card {
    border-radius: 20px;
    padding: 22px 18px;
    margin-bottom: 25px;
    transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    color: #ffffff;
    font-family: 'Inter', sans-serif;
    position: relative;
    overflow: hidden;
    background: linear-gradient(160deg, #1b1b2f 0%, #141420 100%);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
    line-height: 1.5;
}

.card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 15px 35px rgba(255,255,255,0.15);
}

/* NEW BORDER COLORS - Purple & Green Theme */
.card-anime {
    border: 2px solid #FFD700;
    background: linear-gradient(160deg, #1b1b2f 0%, #2d1b3d 100%);
}

.card-manga {
    border: 2px solid #00FF7F;
    background: linear-gradient(160deg, #1b2f1b 0%, #142814 100%);
}

.card img.cover {
    width: 100%;
    height: 300px;
    object-fit: cover;
    border-radius: 12px;
    transition: transform 0.3s ease;
    margin-bottom: 13px;
}

.card:hover img.cover {
    transform: scale(1.05);
}

/* Improved Title Styling */
.card h3 {
    margin: 18px 0 16px 0 !important;
    font-size: 1.35rem !important;
    font-weight: 700 !important;
    line-height: 1.3 !important;
    text-align: center;
    padding: 0 10px;
    font-family: 'Poppins', sans-serif;
    letter-spacing: 0.2px;
}

.card h3 a {
    color: #ffffff !important;
    text-decoration: none !important;
    transition: all 0.3s ease;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.card h3 a:hover {
    color: #ff6b7a !important;
    text-decoration: none !important;
}

/* FIXED GENRE BADGES - Better wrapping and spacing */
.genre-container {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 6px;
    margin: 16px 0 20px 0;
    padding: 0 5px;
    min-height: 40px;
    align-items: center;
}

.badge {
    background: linear-gradient(135deg, #ff6b7a, #ff4c60);
    color: white;
    border-radius: 16px;
    padding: 6px 12px;
    font-size: 0.63rem;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(255, 107, 122, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.25);
    font-family: 'Inter', sans-serif;
    letter-spacing: 0.2px;
    text-transform: uppercase;
    white-space: nowrap;
    flex-shrink: 0;
    max-width: 120px;
    overflow: hidden;
    text-overflow: ellipsis;
}

.badge:hover { 
    transform: translateY(-2px) scale(1.05);
    box-shadow: 0 4px 12px rgba(255, 107, 122, 0.5);
    background: linear-gradient(135deg, #ff7b88, #ff5c70);
}

/* IMPROVED TAGS STYLING */
.tags-container {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 16px 0;
    padding: 16px;
    background: rgba(40, 40, 60, 0.7);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.15);
    justify-content: center;
}

.tag-item {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 6px 12px;
    border-radius: 16px;
    font-size: 0.75rem;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.2);
    font-family: 'Inter', sans-serif;
    letter-spacing: 0.1px;
    white-space: nowrap;
}

.tag-item:hover {
    transform: translateY(-2px) scale(1.05);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.5);
    background: linear-gradient(135deg, #738ae6, #855fb0);
}

/* Improved Meta Data Styling */
.meta-container {
    margin-top: 16px;
    padding: 16px;
    background: rgba(35, 35, 55, 0.7);
    border-radius: 12px;
    border-left: 4px solid #ff6b7a;
    backdrop-filter: blur(10px);
}

.meta-block {
    font-size: 0.95rem;
    margin: 7px 0;
    color: #f5f5f5;
    padding: 4px 0;
    line-height: 1.5;
    transition: all 0.3s ease;
    font-family: 'Inter', sans-serif;
    letter-spacing: 0.05px;
}

.meta-block:hover {
    color: #ffffff;
    transform: translateX(3px);
}

.meta-block b {
    color: #00d4ff;
    font-weight: 700;
    font-size: 0.95rem;
}

.studio-link { 
    color: #2ecc71; 
    text-decoration: none; 
    font-weight: 600;
    transition: all 0.3s ease;
    font-family: 'Inter', sans-serif;
}

.studio-link:hover { 
    color: #27ae60; 
    text-decoration: underline;
    transform: translateX(2px);
}

/* Description & Expander */
.desc {
    font-size: 0.92rem;
    color: #e8e8e8;
    font-family: 'Inter', sans-serif;
    line-height: 1.7;
    text-align: left;
    padding: 18px;
    background: rgba(35, 35, 45, 0.8);
    border-radius: 12px;
    border-left: 4px solid #ff6b7a;
    margin: 16px 0;
    max-height: 300px;
    overflow-y: auto;
    backdrop-filter: blur(10px);
    letter-spacing: 0.1px;
}

.desc::-webkit-scrollbar {
    width: 6px;
}

.desc::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
}

.desc::-webkit-scrollbar-thumb {
    background: #ff6b7a;
    border-radius: 3px;
}

.desc::-webkit-scrollbar-thumb:hover {
    background: #ff8a95;
}

/* Relation Link */
.relation-text {
    font-size: 0.88rem;
    color: #e0e0e0;
    margin-top: 20px;
    text-align: center;
    font-family: 'Inter', sans-serif;
}

.relation-toggle {
    color: #ffffff;
    cursor: pointer;
    font-weight: 700;
    text-decoration: none;
    display: inline-block;
    padding: 10px 20px;
    background: linear-gradient(135deg, #ff4c60, #ff7685);
    border-radius: 10px;
    border: none;
    transition: all 0.3s;
    box-shadow: 0 4px 12px rgba(255, 76, 96, 0.4);
    text-align: center;
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    letter-spacing: 0.3px;
}

.relation-toggle:hover {
    color: #ffffff;
    background: linear-gradient(135deg, #ff6b7a, #ff8a95);
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(255, 76, 96, 0.6);
    text-decoration: none;
}

/* Expander header */
.streamlit-expanderHeader {
    background: rgba(70, 70, 90, 0.9) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    padding: 14px 18px !important;
    transition: all 0.3s ease !important;
    font-family: 'Inter', sans-serif;
}

.streamlit-expanderHeader:hover {
    background: rgba(80, 80, 100, 0.9) !important;
    color: #ffffff !important;
    border-color: rgba(255, 255, 255, 0.3) !important;
    transform: translateY(-2px);
}

/* Button Styling */
.stButton button {
    background: linear-gradient(135deg, #ff4c60 0%, #ff2e4a 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 20px !important;
    padding: 18px 45px !important;
    font-weight: 900 !important;
    font-size: 1.4rem !important;
    transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
    box-shadow: 0 12px 35px rgba(255, 76, 96, 0.8) !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    margin-top: 30px !important;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    position: relative;
    overflow: hidden;
    font-family: 'Inter', sans-serif;
}

.stButton button:hover {
    transform: translateY(-6px) scale(1.04) !important;
    box-shadow: 0 18px 40px rgba(255, 76, 96, 1) !important;
    background: linear-gradient(135deg, #ff5c70 0%, #ff3e5a 100%) !important;
}

/* Custom scrollbar for entire app */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #ff6b7a, #ff4c60);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #ff7b88, #ff5c70);
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Form Inputs
# -----------------------------
with st.form("search_form"):
    query = st.text_input("Enter an anime/manga title:",placeholder="e.g., Naruto, Attack on Titan, One Piece...")
    media_type = st.selectbox("Media Type", ["ANIME", "MANGA"])
    top_n = st.slider("Number of recommendations:", 5, 30, 15)
    submitted = st.form_submit_button("Generate Recommendations")

# -----------------------------
# Display Results
# -----------------------------
if submitted and query:
    with st.spinner("Fetching recommendations..."):
        recs = get_cb_recommendations(query, top_n=top_n, media_type=media_type)

    if "error" in recs.columns:
        st.warning(recs.iloc[0]["error"])
    else:
        st.success(f"Top {len(recs)} recommendations for '{query}':")
        cols_per_row = 4

        for i in range(0, len(recs), cols_per_row):
            row_cols = st.columns(cols_per_row)
            for j, col in enumerate(row_cols):
                if i + j >= len(recs):
                    continue
                item = recs.iloc[i + j]
                card_class = "card-anime" if item["fetched_type"].upper() == "ANIME" else "card-manga"

                genres_html = " ".join([f"<span class='badge'>{g.title()}</span>" for g in (item['genres'].split(',') if item['genres'] else [])])
                studios = item.get("studios", [])
                studio_links = item.get("studio_links", [])
                if studio_links:
                    studio_html = " | ".join([f"<a href='{link}' target='_blank' class='studio-link'>{studio}</a>"
                                              for studio, link in zip(item.get("studios", []), studio_links)])
                else:
                    studio_html = "N/A"

                # Remove all the relations preview logic and just keep this:
                relations_link = (f'<div class="relation-text" style="text-align: center; margin-top: 10px;">'
                                  f'<a href="https://anilist.co/{item["fetched_type"].lower()}/{item.get("id", "")}/relations" target="_blank" class="relation-toggle">View All Details →</a></div>')


                # Dynamic metadata (anime vs manga)
                if item["fetched_type"].upper() == "ANIME":
                    start_date = f"{item['start_date']}" if item[
                        'start_date'] else "Unknown"
                    end_date = f"{item['end_date']}" if item[
                        'end_date'] else "Still airing"
                    meta_html = f"""
                        <div class='meta-block'><b>Type / Format:</b> {item['fetched_type'].title()} / {item['format'].title()}</div>
                        <div class='meta-block'><b>Episodes:</b> {item.get('episodes_display')}</div>
                        <div class='meta-block'><b>Duration:</b> {item['duration']} min</div>
                        <div class='meta-block'><b>Studio:</b> {studio_html}</div>
                        <div class='meta-block'><b>Season:</b> {item['season'].title()}</div>
                        <div class='meta-block'><b>Country:</b> {item['country'].upper()}</div>
                        <div class='meta-block'><b>Score:</b> {item['averageScore'] / 10:.1f}/10</div>
                        <div class='meta-block'><b>Dates:</b> {start_date} → {end_date}</div>
                        <div class='meta-block'><b>Popularity:</b> {item['popularity']} | <b>Favourites:</b> {item['favourites']}</div>
                        <div class='meta-block'><b>Source / Status:</b> {item['source'].title()} / {item['status'].title()}</div>
                        <div class='meta-block'><b>Similarity:</b> {item['similarity_score']}</div>
                    """
                else:
                    start_date = f"{item['start_date']}" if item[
                        'start_date'] else "Unknown"
                    end_date = f"{item['end_date']}" if item[
                        'end_date'] else "Still publishing"
                    meta_html = f"""
                        <div class='meta-block'><b>Type / Format:</b> {item['fetched_type'].title()} / {item['format'].title()}</div>
                        <div class='meta-block'><b>Chapters:</b> {item.get('chapters_display')}</div>
                        <div class='meta-block'><b>Volumes:</b> {item.get('volumes_display')}</div>
                        <div class='meta-block'><b>Country:</b> {item['country'].upper()}</div>
                        <div class='meta-block'><b>Score:</b> {item['averageScore'] / 10:.1f}/10</div>
                        <div class='meta-block'><b>Dates:</b> {start_date} → {end_date}</div>
                        <div class='meta-block'><b>Popularity:</b> {item['popularity']} | <b>Favourites:</b> {item['favourites']}</div>
                        <div class='meta-block'><b>Source / Status:</b> {item['source'].title()} / {item['status'].title()}</div>
                        <div class='meta-block'><b>Similarity:</b> {item['similarity_score']}</div>
                    """

                with col:
                    # Display the card
                    st.markdown(f"""
                    <div class='card {card_class}'>
                        <img class='cover' src="{item['coverImage']}" alt="cover">
                        <h3 style='margin:10px 0;'>
                           <a href='https://anilist.co/{item["fetched_type"].lower()}/{item.get("id", "")}' target='_blank' style='color:#ffffff; text-decoration:none;'>
                                {item['display_title'].title().rstrip('.')}
                            </a>
                        </h3>
                        {genres_html}
                        <div style='margin-top:8px;'>{meta_html}</div>
                        {relations_link}
                    </div>
                    """, unsafe_allow_html=True)

                    with st.expander("Description"):
                        alt_titles = []
                        if item.get('title_romaji') and item['title_romaji'] != item['display_title']:
                            alt_titles.append(f"Romaji: {format_title(item['title_romaji'].rstrip('.'))}")
                        if item.get('title_english') and item['title_english'] != item['display_title']:
                            alt_titles.append(f"English: {format_title(item['title_english'].rstrip('.'))}")
                        if item.get('title_native') and item['title_native'] != item['display_title']:
                            alt_titles.append(f"Native: {format_title(item['title_native'].rstrip('.'))}")
                        if alt_titles:
                            st.markdown(f"**Alternative Titles:** {', '.join(alt_titles)}")
                        if item.get('tags'):
                            tags_list = [tag.strip() for tag in item['tags'].split(' ') if tag.strip()]
                            if tags_list:
                                limited_tags = tags_list[:10]  # Show more tags
                                tags_html = " ".join([
                                    f"<span style='background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 6px 14px; border-radius: 20px; font-size: 0.75rem; margin: 2px 6px 4px 0; display: inline-block; border: 1px solid rgba(255,255,255,0.3); box-shadow: 0 3px 10px rgba(102, 126, 234, 0.4); transition: all 0.3s ease; font-weight: 600; cursor: pointer;' onmouseover=\"this.style.transform='translateY(-3px) scale(1.05)'; this.style.boxShadow='0 6px 15px rgba(102, 126, 234, 0.6)'\" onmouseout=\"this.style.transform='translateY(0) scale(1)'; this.style.boxShadow='0 3px 10px rgba(102, 126, 234, 0.4)'\">{tag.title()}</span>"
                                    for tag in limited_tags])
                                st.markdown(f"""
                                <div style='margin: 4px 0; padding: 16px; background: rgba(30, 30, 46, 0.8); border-radius: 15px; border-left: 4px solid #667eea;'>
                                    <div style='font-weight: 700; color: #00d4ff; margin-bottom: 8px; font-size: 1rem;'>Popular Tags:</div>
                                    <div style='line-height: 1.8;'>{tags_html}</div>
                                </div>
                                """, unsafe_allow_html=True)
                        banner_bg = f"""
                            <div style='
                                position: relative;
                                border-radius: 10px;
                                overflow: hidden;
                                margin-bottom: 10px;
                                max-height: 400px;
                            '>
                                {f'<img src="{item["bannerImage"]}" style="width:100%; height:200px; object-fit:cover; opacity:0.3; filter:blur(1px);" alt="banner">' if item.get("bannerImage") else ''}
                                <div style='
                                    position: absolute;
                                    top: 0;
                                    left: 0;
                                    right: 0;
                                    bottom: 0;
                                    padding: 20px;
                                    background: rgba(0, 0, 0, 0.7);
                                    overflow-y: auto;
                                '>
                                    <div class='desc'>{format_description(item.get('description', ''))}</div>
                                </div>
                            </div>
                            """
                        st.markdown(banner_bg, unsafe_allow_html=True)

                    trailer_url = ""
                    trailer_id = item.get('trailer_id')
                    if trailer_id:
                        trailer_url = f"https://www.youtube.com/watch?v={trailer_id}"
                    else:
                        search_query = f"{item['display_title']} official trailer"
                        trailer_url = f"https://www.youtube.com/results?search_query={quote(search_query)}"
                    if item["trailer_thumbnail"]:
                        st.markdown(
                            f"""
                            <div style='text-align: center; margin: 20px 0;'>
                                <a href='{trailer_url}' target='_blank' style='text-decoration: none; display: block;'>
                                    <div style='position: relative; border-radius: 12px; overflow: hidden; box-shadow: 0 8px 25px rgba(0,0,0,0.4); transition: all 0.3s ease;' 
                                         onmouseover="this.style.transform='scale(1.03)'; this.style.boxShadow='0 12px 35px rgba(255,107,122,0.3)'" 
                                         onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='0 8px 25px rgba(0,0,0,0.4)'">
                                        <img src='{item["trailer_thumbnail"]}' 
                                             style='width:100%; height:auto; border-radius:12px; display:block;'
                                             alt='Trailer Thumbnail'>
                                        <div style='position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: rgba(255,107,122,0.9); border-radius: 50%; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center;'>
                                            <svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" fill="white" viewBox="0 0 24 24">
                                                <path d="M8 5v14l11-7z"/>
                                            </svg>
                                        </div>
                                    </div>
                                </a>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(f"""
                            <a href='{trailer_url}' target='_blank'>
                                <div style='
                                    width:100%; 
                                    height:180px; 
                                    border-radius:12px; 
                                    background: linear-gradient(135deg, #ff4c60, #1b1b2f);
                                    display:flex; 
                                    align-items:center; 
                                    justify-content:center; 
                                    flex-direction:column;
                                    color:#ffffff; 
                                    font-weight:bold; 
                                    font-size:1rem;
                                    transition: transform 0.3s;
                                    box-shadow: 0 4px 14px rgba(0,0,0,0.3);
                                    margin-top: 20px;
                                ' onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1.0)'">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="46" height="46" fill="white" viewBox="0 0 24 24">
                                        <path d="M3 22V2l18 10-18 10z"/>
                                    </svg>
                                    <span style='margin-top:8px;'>Trailer Thumbnail Not Available</span>
                                </div>
                            </a>
                        """, unsafe_allow_html=True)

# -----------------------------
# Footer
# -----------------------------

st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 1.5rem;'>
    <div style='display: flex; align-items: center; justify-content: center; gap: 15px;'>
        <img src='https://i.postimg.cc/QN0y1wf8/gojo.jpg' 
             style='width: 50px; height: 50px; border-radius: 50%; object-fit: cover; border: 2px solid #00d4ff; box-shadow: 0 4px 15px rgba(0, 212, 255, 0.4);'
             alt='Gojo Satoru'>
        <div>
            <p style='color: #888; font-size: 0.9rem; margin: 0; font-weight: 600;'>
                Powered by AniList API
            </p>
            <p style='color: #666; font-size: 0.8rem; margin: 5px 0 0 0;'>
                Made for anime fans • 域を展開
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
