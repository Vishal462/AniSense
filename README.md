# AniSense 🎌
Anime & Manga Content-Based Recommendation System

[![Streamlit App](https://img.shields.io/badge/Live-Demo-brightgreen)](https://anisense.streamlit.app/)

---

## 📖 Overview
AniSense is a Streamlit-powered application that recommends anime and manga titles using a **content-based filtering approach**.  
It leverages TF-IDF vectorization and similarity matrices to suggest titles most similar to a user’s query.

---

## 🚀 Features
- 🔍 Search by anime or manga title
- 🎯 Content-based recommendations using TF-IDF + similarity matrix
- 📊 Interactive Streamlit interface
- 🌐 Deployed on Streamlit Cloud: [anisense.streamlit.app](https://anisense.streamlit.app/)

---

## 🛠️ Tech Stack
- **Python 3.13**
- **Streamlit** for UI
- **Pandas / NumPy** for data handling
- **Joblib** for model persistence
- **Scikit-learn** for TF-IDF vectorizer
- **RapidFuzz** for fuzzy matching

---

---

## 📑 Documentation
A detailed report explaining the methodology, dataset, and workflow is available in [`docs/overview.md`](docs/overview.md).  
This README provides a quick summary; see the report for deeper insights.

---

## ▶️ Usage
1. Clone the repo:
   ```bash
   git clone https://github.com/yourusername/anisense.git
   cd anisense
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run locally
   ```bash
   streamlit run Home.py
   ```
   
---

## 📑 Documentation
A detailed report explaining the methodology, dataset, and workflow is available in [`docs/AniSense_report.pdf`](docs/AniSense_report.pdf).  
This README provides a quick summary; see the report for deeper insights.
