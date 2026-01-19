# AniSense 🎌: Hybrid Anime & Manga Recommendation System

AniSense is a high-performance, hybrid recommendation system designed to provide personalized discovery across the anime and manga domains. By leveraging real-time data and a multi-modal similarity fusion architecture, it delivers contextually aware suggestions that surpass traditional rule-based or static systems.

**Live Demo:** [Run AniSense here](https://anisense.streamlit.app/)

---

## Key Features
- **Hybrid Multi-Modal Fusion:** Combines semantic, lexical, numeric, and categorical similarities into a unified ranking score.
- **Real-Time Data Pipeline:** Dynamically fetches and processes metadata for **8,000+ titles** (4,000 anime and 4,000 manga) via the **AniList GraphQL API**.
- **Cross-Medium Navigation:** Intelligently links adaptations, sequels, and spin-offs between anime and manga formats.
- **Query Robustness:** Features fuzzy alias resolution and manual substitution (e.g., "JJK" → "Jujutsu Kaisen") for intuitive search.
- **Recency-Aware Boosting:** Prioritizes contemporary and ongoing works to ensure temporal relevance.

## Technical Architecture

The core engine utilizes a **Multi-Modal Similarity Fusion** layer with the following weighted components:

| Component | Methodology | Weight | Purpose |
| :--- | :--- | :--- | :--- |
| **Semantic** | `all-mpnet-base-v2` Transformer Embeddings | 40% | Deep contextual & thematic understanding |
| **Categorical** | One-Hot Encoding (Format, Season, Country) | 40% | Alignment of structural metadata |
| **Numeric** | Min-Max Scaled Features (Score, Popularity) | 10% | Alignment of quantitative metrics |
| **Lexical** | TF-IDF Vectorization (Max 5,000 features) | 5% | Surface-level textual overlap |
| **Temporal** | Recency-Aware Weighting | 5% | Boosting new/ongoing content |

### Tech Stack
- **Models:** Sentence-Transformers (`all-mpnet-base-v2`), Scikit-learn (TF-IDF, MinMax).
- **Data:** AniList GraphQL API, Pandas, NumPy.
- **Interface:** Streamlit with Netflix-inspired card layouts and interactive filtering.
- **Performance:** Sub-second retrieval latency for cached queries.

## Performance Metrics
*Values recorded on a mid-range GPU system*:
- **Dataset Size:** ~8,000 integrated titles.
- **Semantic Vectorization:** ~179.5s for total corpus embedding.
- **Matrix Fusion Time:** ~3.6s (includes temporal adjustments).
- **Query Latency:** **< 5 seconds** for Top-N retrieval and UI rendering.

## Installation & Usage

### 1. Clone the repository
```bash
git clone [https://github.com/yourusername/anisense.git](https://github.com/yourusername/anisense.git)
cd anisense
```
### 2. Install dependencies
```bash
pip install -r requirements.txt
```
### 3. Run locally
```bash
streamlit run project.py
```
## Documentation
The implementation details and experimental results are based on the research report:

**"AniSense: An Anime and Manga Recommendation System" by Vishal Agarwal.**

[Download AniSense Technical Report](docs/AniSense_report.pdf)
