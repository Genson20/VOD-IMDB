import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="CinéCreuse+",
    page_icon="🎬",
    layout="wide"
)

# Base de données fictive enrichie pour le dashboard KPI
@st.cache_data
def load_movies():
    movies = [
        {
            "title_x": "Les Misérables",
            "genres_x": "Drame",
            "runtime": 158,
            "original_language": "fr",
            "averageRating": 8.4,
            "numVotes": 125000,
            "release_date": "2012-12-25",
            "description": "Une adaptation moderne du classique de Victor Hugo",
            "affiche": "🎭"
        },
        {
            "title_x": "Amélie",
            "genres_x": "Romance|Comédie",
            "runtime": 122,
            "original_language": "fr",
            "averageRating": 9.0,
            "numVotes": 180000,
            "release_date": "2001-04-25",
            "description": "L'histoire touchante d'une jeune femme parisienne",
            "affiche": "💝"
        },
        {
            "title_x": "Intouchables",
            "genres_x": "Comédie|Drame",
            "runtime": 112,
            "original_language": "fr",
            "averageRating": 9.2,
            "numVotes": 250000,
            "release_date": "2011-11-02",
            "description": "Une amitié improbable entre deux hommes",
            "affiche": "🤝"
        },
        {
            "title_x": "La Vie en Rose",
            "genres_x": "Biographie|Drame",
            "runtime": 140,
            "original_language": "fr",
            "averageRating": 8.2,
            "numVotes": 95000,
            "release_date": "2007-06-08",
            "description": "La vie tumultueuse d'Édith Piaf",
            "affiche": "🌹"
        },
        {
            "title_x": "Le Fabuleux Destin d'Amélie Poulain",
            "genres_x": "Romance|Comédie",
            "runtime": 122,
            "original_language": "fr",
            "averageRating": 8.8,
            "numVotes": 200000,
            "release_date": "2001-04-25",
            "description": "Une comédie romantique emblématique",
            "affiche": "🎪"
        },
        {
            "title_x": "Asterix et Obelix: Mission Cléopâtre",
            "genres_x": "Comédie|Aventure",
            "runtime": 107,
            "original_language": "fr",
            "averageRating": 7.6,
            "numVotes": 85000,
            "release_date": "2002-01-30",
            "description": "Les aventures des Gaulois en Égypte",
            "affiche": "🏺"
        },
        {
            "title_x": "The Matrix",
            "genres_x": "Science-Fiction|Action",
            "runtime": 136,
            "original_language": "en",
            "averageRating": 8.7,
            "numVotes": 1500000,
            "release_date": "1999-03-31",
            "description": "Un informaticien découvre la vraie nature de la réalité",
            "affiche": "🕶️"
        },
        {
            "title_x": "Titanic",
            "genres_x": "Romance|Drame",
            "runtime": 195,
            "original_language": "en",
            "averageRating": 8.0,
            "numVotes": 1200000,
            "release_date": "1997-12-19",
            "description": "Une histoire d'amour tragique à bord du Titanic",
            "affiche": "🚢"
        },
        {
            "title_x": "El Laberinto del Fauno",
            "genres_x": "Fantasy|Drame",
            "runtime": 118,
            "original_language": "es",
            "averageRating": 8.4,
            "numVotes": 220000,
            "release_date": "2006-10-11",
            "description": "Un conte sombre dans l'Espagne de Franco",
            "affiche": "🧚"
        },
        {
            "title_x": "Parasite",
            "genres_x": "Thriller|Comédie",
            "runtime": 132,
            "original_language": "ko",
            "averageRating": 9.5,
            "numVotes": 350000,
            "release_date": "2019-05-30",
            "description": "Un thriller social primé aux Oscars",
            "affiche": "🏠"
        },
        {
            "title_x": "Pulp Fiction",
            "genres_x": "Crime|Drame",
            "runtime": 154,
            "original_language": "en",
            "averageRating": 8.9,
            "numVotes": 1800000,
            "release_date": "1994-10-14",
            "description": "Des histoires entrelacées dans le Los Angeles criminel",
            "affiche": "🔫"
        },
        {
            "title_x": "Spirited Away",
            "genres_x": "Animation|Fantasy",
            "runtime": 125,
            "original_language": "ja",
            "averageRating": 9.3,
            "numVotes": 650000,
            "release_date": "2001-07-20",
            "description": "Une jeune fille dans un monde d'esprits",
            "affiche": "👻"
        },
        {
            "title_x": "Inception",
            "genres_x": "Science-Fiction|Thriller",
            "runtime": 148,
            "original_language": "en",
            "averageRating": 8.8,
            "numVotes": 2200000,
            "release_date": "2010-07-16",
            "description": "L'art de pénétrer dans les rêves",
            "affiche": "🌀"
        },
        {
            "title_x": "The Godfather",
            "genres_x": "Crime|Drame",
            "runtime": 175,
            "original_language": "en",
            "averageRating": 9.2,
            "numVotes": 1700000,
            "release_date": "1972-03-24",
            "description": "La saga d'une famille mafieuse",
            "affiche": "👑"
        },
        {
            "title_x": "Seven Samurai",
            "genres_x": "Action|Drame",
            "runtime": 207,
            "original_language": "ja",
            "averageRating": 9.0,
            "numVotes": 330000,
            "release_date": "1954-04-26",
            "description": "Sept samouraïs défendent un village",
            "affiche": "⚔️"
        }
    ]
    df = pd.DataFrame(movies)
    df['release_date'] = pd.to_datetime(df['release_date'])
    df['year'] = df['release_date'].dt.year
    return df

# Initialisation des données
df_main = load_movies()

# Sidebar Navigation
st.sidebar.title("🎬 CinéCreuse+")
page = st.sidebar.selectbox(
    "Navigation",
    ["🏠 Accueil", "🎯 Recommandations", "📊 KPI Dashboard"]
)

# ================================
# PAGE ACCUEIL
# ================================
if page == "🏠 Accueil":
    st.title("🎬 CinéCreuse+")
    st.markdown("---")
    
    # Barre de recherche
    search_query = st.text_input("🔍 Rechercher un film", placeholder="Tapez le nom d'un film...")
    
    # Filtres dans la sidebar
    st.sidebar.header("🎛️ Filtres")
    
    # Extraire les genres uniques
    all_genres = set()
    for genres_str in df_main["genres_x"]:
        if pd.notna(genres_str):
            all_genres.update(genres_str.split("|"))
    genres = ["Tous"] + sorted(list(all_genres))
    selected_genre = st.sidebar.selectbox("Genre", genres)
    
    # Filtre par durée
    duration_ranges = [
        "Toutes durées",
        "Court (< 90 min)",
        "Moyen (90-120 min)",
        "Long (120-150 min)",
        "Très long (> 150 min)"
    ]
    selected_duration = st.sidebar.selectbox("Durée", duration_ranges)
    
    # Filtre par langue
    language_map = {"fr": "Français", "en": "Anglais", "es": "Espagnol", "ko": "Coréen", "ja": "Japonais"}
    languages = ["Toutes"] + [language_map.get(lang, lang) for lang in sorted(df_main["original_language"].unique())]
    selected_language = st.sidebar.selectbox("Langue", languages)
    
    # Fonction pour filtrer les films
    def filter_movies(df, genre, duration, language, search):
        filtered_df = df.copy()
        
        # Filtre par genre
        if genre != "Tous":
            filtered_df = filtered_df[filtered_df["genres_x"].str.contains(genre, case=False, na=False)]
        
        # Filtre par durée
        if duration == "Court (< 90 min)":
            filtered_df = filtered_df[filtered_df["runtime"] < 90]
        elif duration == "Moyen (90-120 min)":
            filtered_df = filtered_df[(filtered_df["runtime"] >= 90) & (filtered_df["runtime"] <= 120)]
        elif duration == "Long (120-150 min)":
            filtered_df = filtered_df[(filtered_df["runtime"] > 120) & (filtered_df["runtime"] <= 150)]
        elif duration == "Très long (> 150 min)":
            filtered_df = filtered_df[filtered_df["runtime"] > 150]
        
        # Filtre par langue
        if language != "Toutes":
            reverse_map = {v: k for k, v in language_map.items()}
            lang_code = reverse_map.get(language, language)
            filtered_df = filtered_df[filtered_df["original_language"] == lang_code]
        
        # Filtre par recherche
        if search:
            filtered_df = filtered_df[filtered_df["title_x"].str.contains(search, case=False, na=False)]
        
        return filtered_df
    
    # Application des filtres
    filtered_movies = filter_movies(df_main, selected_genre, selected_duration, selected_language, search_query)
    
    # Affichage du nombre de résultats
    st.subheader(f"📽️ Films disponibles ({len(filtered_movies)} résultat{'s' if len(filtered_movies) > 1 else ''})")
    
    if len(filtered_movies) == 0:
        st.warning("Aucun film ne correspond à vos critères de recherche.")
    else:
        # Affichage des films en grille
        cols_per_row = 3
        rows = len(filtered_movies) // cols_per_row + (1 if len(filtered_movies) % cols_per_row > 0 else 0)
        
        for row in range(rows):
            cols = st.columns(cols_per_row)
            for col_idx in range(cols_per_row):
                movie_idx = row * cols_per_row + col_idx
                if movie_idx < len(filtered_movies):
                    movie = filtered_movies.iloc[movie_idx]
                    
                    with cols[col_idx]:
                        # Carte du film
                        with st.container():
                            st.markdown(f"### {movie['affiche']} {movie['title_x']}")
                            
                            # Informations du film
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Genre:** {movie['genres_x']}")
                                st.write(f"**Durée:** {movie['runtime']} min")
                            with col2:
                                lang_display = language_map.get(movie['original_language'], movie['original_language'])
                                st.write(f"**Langue:** {lang_display}")
                                stars = "⭐" * int(movie['averageRating']) + "☆" * (10 - int(movie['averageRating']))
                                st.write(f"**Note:** {movie['averageRating']}/10")
                            
                            # Bouton détails
                            if st.button(f"📋 Détails", key=f"details_{movie_idx}"):
                                st.session_state[f"show_details_{movie_idx}"] = True
                            
                            # Affichage des détails si demandé
                            if st.session_state.get(f"show_details_{movie_idx}", False):
                                st.info(f"**Description:** {movie['description']}")
                                st.write(f"**Votes:** {movie['numVotes']:,}")
                                st.write(f"**Année:** {movie['year']}")
                                if st.button(f"❌ Fermer", key=f"close_{movie_idx}"):
                                    st.session_state[f"show_details_{movie_idx}"] = False
                                    st.rerun()
                            
                            st.markdown("---")

# ================================
# PAGE RECOMMANDATIONS
# ================================
elif page == "🎯 Recommandations":
    st.title("🎯 Système de Recommandations")
    st.markdown("---")
    
    st.info("🚧 Cette section sera développée avec un système de machine learning pour recommander des films basés sur vos préférences.")
    
    # Recommandations simples basées sur les notes
    st.subheader("🏆 Films les mieux notés")
    top_movies = df_main.nlargest(5, 'averageRating')[['title_x', 'averageRating', 'genres_x', 'runtime']]
    st.dataframe(top_movies, use_container_width=True)

# ================================
# PAGE KPI DASHBOARD
# ================================
elif page == "📊 KPI Dashboard":
    st.title("🎬 Tableau de bord - KPI CinéCreuse+")
    st.markdown("---")
    
    # Calcul des KPI
    total_films = len(df_main)
    avg_rating = df_main['averageRating'].mean()
    avg_runtime = df_main['runtime'].mean()
    pct_french = (df_main['original_language'] == 'fr').sum() / total_films * 100
    
    # Affichage des KPI en cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🎥 Nombre total de films",
            value=f"{total_films:,}"
        )
    
    with col2:
        st.metric(
            label="⭐ Moyenne des notes",
            value=f"{avg_rating:.1f}/10"
        )
    
    with col3:
        st.metric(
            label="⏱️ Durée moyenne",
            value=f"{avg_runtime:.0f} min"
        )
    
    with col4:
        st.metric(
            label="🇫🇷 % Films français",
            value=f"{pct_french:.1f}%"
        )
    
    st.markdown("---")
    
    # Section des visualisations
    col1, col2 = st.columns(2)
    
    with col1:
        # Histogramme des notes
        st.subheader("📊 Distribution des notes")
        fig_ratings = px.histogram(
            df_main, 
            x='averageRating', 
            nbins=20,
            title="Répartition des notes (1-10)",
            labels={'averageRating': 'Note moyenne', 'count': 'Nombre de films'}
        )
        fig_ratings.update_layout(height=400)
        st.plotly_chart(fig_ratings, use_container_width=True)
    
    with col2:
        # Histogramme des durées
        st.subheader("⏱️ Distribution des durées")
        fig_runtime = px.histogram(
            df_main, 
            x='runtime',
            nbins=15,
            title="Répartition des durées",
            labels={'runtime': 'Durée (minutes)', 'count': 'Nombre de films'}
        )
        fig_runtime.update_layout(height=400)
        st.plotly_chart(fig_runtime, use_container_width=True)
    
    # Graphiques en pleine largeur
    col1, col2 = st.columns(2)
    
    with col1:
        # Nombre de films par genre
        st.subheader("🎭 Films par genre")
        # Extraire tous les genres
        all_genres = []
        for genres_str in df_main["genres_x"]:
            if pd.notna(genres_str):
                all_genres.extend(genres_str.split("|"))
        
        genre_counts = pd.Series(all_genres).value_counts()
        
        fig_genres = px.bar(
            x=genre_counts.values,
            y=genre_counts.index,
            orientation='h',
            title="Nombre de films par genre",
            labels={'x': 'Nombre de films', 'y': 'Genre'}
        )
        fig_genres.update_layout(height=500)
        st.plotly_chart(fig_genres, use_container_width=True)
    
    with col2:
        # Répartition par année
        st.subheader("📅 Films par année")
        year_counts = df_main['year'].value_counts().sort_index()
        
        fig_years = px.line(
            x=year_counts.index,
            y=year_counts.values,
            title="Évolution du nombre de films par année",
            labels={'x': 'Année', 'y': 'Nombre de films'}
        )
        fig_years.update_layout(height=500)
        st.plotly_chart(fig_years, use_container_width=True)
    
    st.markdown("---")
    
    # Tableau interactif des top films
    st.subheader("🏆 Top 10 des films les mieux notés")
    top_films = df_main.nlargest(10, 'averageRating')[['title_x', 'averageRating', 'runtime', 'numVotes']].round(2)
    top_films.columns = ['Titre', 'Note moyenne', 'Durée (min)', 'Nombre de votes']
    st.dataframe(top_films, use_container_width=True)

# Pied de page
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray; padding: 20px;'>"
    "Propulsé par CinéCreuse+"
    "</div>",
    unsafe_allow_html=True
)

# Sidebar avec informations supplémentaires
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Statistiques générales")
st.sidebar.write(f"Total des films: {len(df_main)}")

# Répartition par langue dans la sidebar
lang_counts = df_main["original_language"].value_counts()
st.sidebar.markdown("### 🌍 Langues disponibles")
language_map = {"fr": "Français", "en": "Anglais", "es": "Espagnol", "ko": "Coréen", "ja": "Japonais"}
for lang, count in lang_counts.items():
    lang_display = language_map.get(str(lang), str(lang))
    st.sidebar.write(f"• {lang_display}: {count}")
