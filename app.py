import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="CinéCreuse+",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS pour masquer les éléments Streamlit par défaut
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Chargement des données
@st.cache_data
def load_movies():
    df = pd.read_csv('df_main_clean.csv')
    
    # Nettoyer les données en utilisant les bonnes colonnes
    if 'primaryTitle' in df.columns:
        df['primaryTitle'] = df['primaryTitle'].astype(str)
    if 'original_title' in df.columns:
        df['original_title'] = df['original_title'].astype(str)
    
    # Supprimer les doublons basés sur le titre principal
    if 'primaryTitle' in df.columns:
        df_clean = df.drop_duplicates(subset=['primaryTitle'], keep='first')
    else:
        df_clean = df.drop_duplicates(subset=['title_x'], keep='first')
    
    return df_clean

# Fonction pour générer des emojis selon le genre
def get_emoji_for_genre(genres):
    if pd.isna(genres):
        return "🎬"
    
    genre_emojis = {
        'Action': '💥', 'Adventure': '🗺️', 'Animation': '🎨', 'Biography': '📖',
        'Comedy': '😂', 'Crime': '🔫', 'Documentary': '📹', 'Drama': '🎭',
        'Family': '👨‍👩‍👧‍👦', 'Fantasy': '🧙‍♂️', 'Film-Noir': '🕵️', 'History': '🏛️',
        'Horror': '👻', 'Music': '🎵', 'Musical': '🎼', 'Mystery': '🔍',
        'News': '📰', 'Romance': '💕', 'Sci-Fi': '🚀', 'Sport': '⚽',
        'Thriller': '😱', 'War': '⚔️', 'Western': '🤠'
    }
    
    if isinstance(genres, str):
        for genre, emoji in genre_emojis.items():
            if genre in genres:
                return emoji
    
    return "🎬"

# Chargement des données
df_main = load_movies()

# ================================
# BARRE LATÉRALE
# ================================
with st.sidebar:
    # Logo dans la barre latérale
    logo_sidebar = """
    <div style="text-align: center; margin: 10px 0;">
        <svg width="200" height="80" viewBox="0 0 200 80" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="goldGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" style="stop-color:#FFD700;stop-opacity:1" />
              <stop offset="50%" style="stop-color:#FFA500;stop-opacity:1" />
              <stop offset="100%" style="stop-color:#FF8C00;stop-opacity:1" />
            </linearGradient>
            <linearGradient id="darkGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" style="stop-color:#1a1a1a;stop-opacity:1" />
              <stop offset="100%" style="stop-color:#333333;stop-opacity:1" />
            </linearGradient>
            <filter id="glow">
              <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
              <feMerge> 
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>
          <rect width="200" height="80" rx="10" ry="10" fill="url(#darkGradient)" stroke="#FFD700" stroke-width="1"/>
          <g transform="translate(10, 15)">
            <rect x="0" y="0" width="15" height="50" fill="url(#goldGradient)" rx="2"/>
            <rect x="2" y="5" width="3" height="4" fill="#1a1a1a" rx="0.5"/>
            <rect x="10" y="5" width="3" height="4" fill="#1a1a1a" rx="0.5"/>
            <rect x="2" y="12" width="3" height="4" fill="#1a1a1a" rx="0.5"/>
            <rect x="10" y="12" width="3" height="4" fill="#1a1a1a" rx="0.5"/>
            <rect x="2" y="19" width="3" height="4" fill="#1a1a1a" rx="0.5"/>
            <rect x="10" y="19" width="3" height="4" fill="#1a1a1a" rx="0.5"/>
            <rect x="2" y="26" width="3" height="4" fill="#1a1a1a" rx="0.5"/>
            <rect x="10" y="26" width="3" height="4" fill="#1a1a1a" rx="0.5"/>
            <rect x="2" y="33" width="3" height="4" fill="#1a1a1a" rx="0.5"/>
            <rect x="10" y="33" width="3" height="4" fill="#1a1a1a" rx="0.5"/>
            <rect x="2" y="40" width="3" height="4" fill="#1a1a1a" rx="0.5"/>
            <rect x="10" y="40" width="3" height="4" fill="#1a1a1a" rx="0.5"/>
          </g>
          <text x="35" y="45" font-family="Arial Black, sans-serif" font-size="16" font-weight="bold" fill="url(#goldGradient)" filter="url(#glow)">CinéCreuse+</text>
          <text x="35" y="65" font-family="Arial, sans-serif" font-size="8" fill="#FFD700" opacity="0.7" font-style="italic">Votre plateforme cinéma</text>
        </svg>
    </div>
    """
    
    st.markdown(logo_sidebar, unsafe_allow_html=True)
    st.markdown("---")
    
    # Navigation
    st.markdown("### 🧭 Navigation")
    page = st.radio(
        "",
        ["🏠 Accueil", "🔍 Recherche", "🎬 Films populaires", "📊 Dashboard Admin"],
        key="navigation"
    )

# ================================
# PAGE ACCUEIL
# ================================
if page == "🏠 Accueil":
    # Logo principal de la page d'accueil
    logo_accueil = """
    <div style="display: flex; justify-content: center; margin: 20px 0;">
        <svg width="400" height="150" viewBox="0 0 300 120" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="goldGradientMain" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" style="stop-color:#FFD700;stop-opacity:1" />
              <stop offset="50%" style="stop-color:#FFA500;stop-opacity:1" />
              <stop offset="100%" style="stop-color:#FF8C00;stop-opacity:1" />
            </linearGradient>
            <linearGradient id="darkGradientMain" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" style="stop-color:#1a1a1a;stop-opacity:1" />
              <stop offset="100%" style="stop-color:#333333;stop-opacity:1" />
            </linearGradient>
            <filter id="glowMain">
              <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
              <feMerge> 
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>
          <rect width="300" height="120" rx="15" ry="15" fill="url(#darkGradientMain)" stroke="#FFD700" stroke-width="2"/>
          <g transform="translate(20, 20)">
            <rect x="0" y="0" width="25" height="80" fill="url(#goldGradientMain)" rx="3"/>
            <rect x="3" y="8" width="4" height="6" fill="#1a1a1a" rx="1"/>
            <rect x="18" y="8" width="4" height="6" fill="#1a1a1a" rx="1"/>
            <rect x="3" y="20" width="4" height="6" fill="#1a1a1a" rx="1"/>
            <rect x="18" y="20" width="4" height="6" fill="#1a1a1a" rx="1"/>
            <rect x="3" y="32" width="4" height="6" fill="#1a1a1a" rx="1"/>
            <rect x="18" y="32" width="4" height="6" fill="#1a1a1a" rx="1"/>
            <rect x="3" y="44" width="4" height="6" fill="#1a1a1a" rx="1"/>
            <rect x="18" y="44" width="4" height="6" fill="#1a1a1a" rx="1"/>
            <rect x="3" y="56" width="4" height="6" fill="#1a1a1a" rx="1"/>
            <rect x="18" y="56" width="4" height="6" fill="#1a1a1a" rx="1"/>
            <rect x="3" y="68" width="4" height="6" fill="#1a1a1a" rx="1"/>
            <rect x="18" y="68" width="4" height="6" fill="#1a1a1a" rx="1"/>
          </g>
          <text x="65" y="65" font-family="Arial Black, sans-serif" font-size="26" font-weight="bold" fill="url(#goldGradientMain)" filter="url(#glowMain)">CinéCreuse+</text>
          <g transform="translate(180, 25)">
            <circle cx="15" cy="15" r="20" fill="none" stroke="url(#goldGradientMain)" stroke-width="3"/>
            <line x1="15" y1="5" x2="15" y2="25" stroke="url(#goldGradientMain)" stroke-width="4" stroke-linecap="round"/>
            <line x1="5" y1="15" x2="25" y2="15" stroke="url(#goldGradientMain)" stroke-width="4" stroke-linecap="round"/>
          </g>
          <g fill="url(#goldGradientMain)" opacity="0.8">
            <polygon points="250,25 252,31 258,31 253,35 255,41 250,37 245,41 247,35 242,31 248,31" />
            <polygon points="270,45 271,48 274,48 272,50 273,53 270,51 267,53 268,50 266,48 269,48" />
            <polygon points="260,70 261,73 264,73 262,75 263,78 260,76 257,78 258,75 256,73 259,73" />
          </g>
          <text x="65" y="100" font-family="Arial, sans-serif" font-size="12" fill="#FFD700" opacity="0.7" font-style="italic">Votre plateforme cinéma</text>
        </svg>
    </div>
    """
    
    st.markdown(logo_accueil, unsafe_allow_html=True)
    st.markdown("🎬 Bienvenue sur CinéCreuse+ ! Découvrez notre catalogue de films.")
    st.markdown("---")
    
    # Barre de recherche de films
    st.subheader("🔍 Rechercher un film")
    
    # Champ de recherche
    search_query = st.text_input("Recherche", placeholder="Tapez le nom d'un film...", key="home_search", label_visibility="collapsed")
    
    if search_query:
        # Recherche dans les titres
        search_results = df_main[
            df_main['primaryTitle'].str.contains(search_query, case=False, na=False) |
            df_main['original_title'].str.contains(search_query, case=False, na=False)
        ].nlargest(12, 'averageRating')
        
        if len(search_results) > 0:
            st.markdown(f"### 🎬 Résultats pour '{search_query}'")
            
            # Afficher les résultats en grille 6 par ligne
            num_results = len(search_results)
            num_rows = (num_results - 1) // 6 + 1
            
            for row in range(num_rows):
                cols = st.columns(6)
                start_idx = row * 6
                end_idx = min(start_idx + 6, num_results)
                
                for col_idx, (_, movie) in enumerate(search_results.iloc[start_idx:end_idx].iterrows()):
                    with cols[col_idx]:
                        if 'poster_path' in movie and pd.notna(movie['poster_path']):
                            poster_url = f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"
                            st.image(poster_url, use_container_width=True)
                        else:
                            st.info("🎬 Affiche non disponible")
                        
                        # Titre du film
                        st.caption(f"**{movie['primaryTitle']}**")
                        if 'startYear' in movie and pd.notna(movie['startYear']):
                            st.caption(f"📅 {int(movie['startYear'])}")
                        if 'averageRating' in movie and pd.notna(movie['averageRating']):
                            st.caption(f"⭐ {movie['averageRating']:.1f}/10")
        else:
            st.warning(f"Aucun film trouvé pour '{search_query}'")
    else:
        st.markdown("### 🎭 Films populaires")
        
        # Afficher les films les mieux notés par défaut
        popular_movies = df_main.nlargest(12, 'averageRating')
        
        # Afficher en grille 6 par ligne
        num_movies = len(popular_movies)
        num_rows = (num_movies - 1) // 6 + 1
        
        for row in range(num_rows):
            cols = st.columns(6)
            start_idx = row * 6
            end_idx = min(start_idx + 6, num_movies)
            
            for col_idx, (_, movie) in enumerate(popular_movies.iloc[start_idx:end_idx].iterrows()):
                with cols[col_idx]:
                    if 'poster_path' in movie and pd.notna(movie['poster_path']):
                        poster_url = f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"
                        st.image(poster_url, use_container_width=True)
                    else:
                        st.info("🎬 Affiche non disponible")
                    
                    # Titre du film
                    st.caption(f"**{movie['primaryTitle']}**")
                    if 'startYear' in movie and pd.notna(movie['startYear']):
                        st.caption(f"📅 {int(movie['startYear'])}")
                    if 'averageRating' in movie and pd.notna(movie['averageRating']):
                        st.caption(f"⭐ {movie['averageRating']:.1f}/10")

# ================================
# PAGE RECHERCHE
# ================================
elif page == "🔍 Recherche":
    st.title("🔍 Recherche de films")
    st.markdown("Trouvez vos films préférés dans notre catalogue.")
    st.markdown("---")
    
    # Barre de recherche
    search_query = st.text_input("🔍 Rechercher un film", placeholder="Entrez le titre d'un film...")
    
    if search_query:
        # Recherche dans les titres
        search_results = df_main[
            df_main['primaryTitle'].str.contains(search_query, case=False, na=False) |
            df_main['original_title'].str.contains(search_query, case=False, na=False)
        ].nlargest(24, 'averageRating')
        
        if len(search_results) > 0:
            st.markdown(f"### 🎬 {len(search_results)} résultat(s) pour '{search_query}'")
            
            # Afficher les résultats en grille
            cols_per_row = 6
            num_rows = (len(search_results) - 1) // cols_per_row + 1
            
            for row in range(num_rows):
                cols = st.columns(cols_per_row)
                start_idx = row * cols_per_row
                end_idx = min(start_idx + cols_per_row, len(search_results))
                
                for col_idx, (_, movie) in enumerate(search_results.iloc[start_idx:end_idx].iterrows()):
                    with cols[col_idx]:
                        if 'poster_path' in movie and pd.notna(movie['poster_path']):
                            poster_url = f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"
                            st.image(poster_url, use_container_width=True)
                        else:
                            st.info("🎬 Affiche non disponible")
                        
                        st.caption(f"**{movie['primaryTitle']}**")
                        if 'startYear' in movie and pd.notna(movie['startYear']):
                            st.caption(f"📅 {int(movie['startYear'])}")
                        if 'averageRating' in movie and pd.notna(movie['averageRating']):
                            st.caption(f"⭐ {movie['averageRating']:.1f}/10")
        else:
            st.warning(f"Aucun film trouvé pour '{search_query}'")
    else:
        st.info("Entrez un titre de film pour commencer votre recherche.")

# ================================
# PAGE FILMS POPULAIRES
# ================================
elif page == "🎬 Films populaires":
    st.title("🎬 Films populaires")
    st.markdown("Découvrez les films les mieux notés de notre catalogue.")
    st.markdown("---")
    
    # Sélectionner les films populaires
    popular_movies = df_main.nlargest(30, 'averageRating')
    
    if len(popular_movies) > 0:
        st.markdown(f"### 🏆 Top {len(popular_movies)} films les mieux notés")
        
        # Afficher en grille
        cols_per_row = 6
        num_rows = (len(popular_movies) - 1) // cols_per_row + 1
        
        for row in range(num_rows):
            cols = st.columns(cols_per_row)
            start_idx = row * cols_per_row
            end_idx = min(start_idx + cols_per_row, len(popular_movies))
            
            for col_idx, (_, movie) in enumerate(popular_movies.iloc[start_idx:end_idx].iterrows()):
                with cols[col_idx]:
                    if 'poster_url' in movie and pd.notna(movie['poster_url']):
                        st.image(movie['poster_url'], use_container_width=True)
                    else:
                        st.info("🎬 Affiche non disponible")
                    
                    st.caption(f"**{movie['primaryTitle']}**")
                    if movie['startYear'] and pd.notna(movie['startYear']):
                        st.caption(f"📅 {int(movie['startYear'])}")
                    if movie['averageRating'] and pd.notna(movie['averageRating']):
                        st.caption(f"⭐ {movie['averageRating']:.1f}/10")
                    if 'genres_x' in movie and pd.notna(movie['genres_x']):
                        emoji = get_emoji_for_genre(movie['genres_x'])
                        st.caption(f"{emoji} {movie['genres_x']}")

# ================================
# PAGE DASHBOARD ADMIN
# ================================
elif page == "📊 Dashboard Admin":
    st.title("📊 Dashboard Administrateur")
    st.markdown("Analyse et statistiques de la plateforme CinéCreuse+")
    st.markdown("---")
    
    # Métriques générales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_films = len(df_main)
        st.metric("Films totaux", total_films)
    
    with col2:
        films_with_rating = len(df_main[df_main['averageRating'].notna()])
        st.metric("Films notés", films_with_rating)
    
    with col3:
        avg_rating = df_main['averageRating'].mean()
        st.metric("Note moyenne", f"{avg_rating:.1f}/10")
    
    with col4:
        total_votes = df_main['numVotes'].sum()
        st.metric("Total votes", f"{total_votes:,.0f}")
    
    st.markdown("---")
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Distribution des notes")
        if 'averageRating' in df_main.columns:
            fig_rating = px.histogram(
                df_main[df_main['averageRating'].notna()], 
                x='averageRating',
                title="Répartition des notes des films",
                nbins=20
            )
            st.plotly_chart(fig_rating, use_container_width=True)
    
    with col2:
        st.subheader("📅 Films par décennie")
        if 'startYear' in df_main.columns:
            decade_data = df_main[df_main['startYear'].notna()].copy()
            decade_data['decade'] = (decade_data['startYear'] // 10) * 10
            decade_counts = decade_data['decade'].value_counts().sort_index()
            
            fig_decade = px.bar(
                x=decade_counts.index,
                y=decade_counts.values,
                title="Nombre de films par décennie"
            )
            st.plotly_chart(fig_decade, use_container_width=True)
    
    # Top films
    st.subheader("🏆 Top 10 des films les mieux notés")
    top_movies = df_main.nlargest(10, 'averageRating')[['primaryTitle', 'startYear', 'averageRating', 'numVotes']]
    top_movies.columns = ['Titre', 'Année', 'Note', 'Votes']
    st.dataframe(top_movies, use_container_width=True)