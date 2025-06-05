import streamlit as st
import pandas as pd

# Configuration de la page
st.set_page_config(
    page_title="CinéCreuse+",
    page_icon="🎬",
    layout="wide"
)

# Données fictives des films
@st.cache_data
def load_movies():
    movies = [
        {
            "titre": "Les Misérables",
            "genre": "Drame",
            "duree": 158,
            "langue": "Français",
            "note": 4.2,
            "description": "Une adaptation moderne du classique de Victor Hugo",
            "affiche": "🎭"
        },
        {
            "titre": "Amélie",
            "genre": "Romance",
            "duree": 122,
            "langue": "Français",
            "note": 4.5,
            "description": "L'histoire touchante d'une jeune femme parisienne",
            "affiche": "💝"
        },
        {
            "titre": "Intouchables",
            "genre": "Comédie",
            "duree": 112,
            "langue": "Français",
            "note": 4.6,
            "description": "Une amitié improbable entre deux hommes",
            "affiche": "🤝"
        },
        {
            "titre": "La Vie en Rose",
            "genre": "Biographie",
            "duree": 140,
            "langue": "Français",
            "note": 4.1,
            "description": "La vie tumultueuse d'Édith Piaf",
            "affiche": "🌹"
        },
        {
            "titre": "Le Fabuleux Destin d'Amélie Poulain",
            "genre": "Romance",
            "duree": 122,
            "langue": "Français",
            "note": 4.4,
            "description": "Une comédie romantique emblématique",
            "affiche": "🎪"
        },
        {
            "titre": "Asterix et Obelix: Mission Cléopâtre",
            "genre": "Comédie",
            "duree": 107,
            "langue": "Français",
            "note": 3.8,
            "description": "Les aventures des Gaulois en Égypte",
            "affiche": "🏺"
        },
        {
            "titre": "The Matrix",
            "genre": "Science-Fiction",
            "duree": 136,
            "langue": "Anglais",
            "note": 4.3,
            "description": "Un informaticien découvre la vraie nature de la réalité",
            "affiche": "🕶️"
        },
        {
            "titre": "Titanic",
            "genre": "Romance",
            "duree": 195,
            "langue": "Anglais",
            "note": 4.0,
            "description": "Une histoire d'amour tragique à bord du Titanic",
            "affiche": "🚢"
        },
        {
            "titre": "El Laberinto del Fauno",
            "genre": "Fantasy",
            "duree": 118,
            "langue": "Espagnol",
            "note": 4.2,
            "description": "Un conte sombre dans l'Espagne de Franco",
            "affiche": "🧚"
        },
        {
            "titre": "Parasite",
            "genre": "Thriller",
            "duree": 132,
            "langue": "Coréen",
            "note": 4.5,
            "description": "Un thriller social primé aux Oscars",
            "affiche": "🏠"
        }
    ]
    return pd.DataFrame(movies)

# Initialisation des données
movies_df = load_movies()

# En-tête
st.title("🎬 CinéCreuse+")
st.markdown("---")

# Barre de recherche
search_query = st.text_input("🔍 Rechercher un film", placeholder="Tapez le nom d'un film...")

# Sidebar pour les filtres
st.sidebar.header("🎛️ Filtres")

# Filtre par genre
genres = ["Tous"] + sorted(movies_df["genre"].unique().tolist())
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
languages = ["Toutes"] + sorted(movies_df["langue"].unique().tolist())
selected_language = st.sidebar.selectbox("Langue", languages)

# Fonction pour filtrer les films
def filter_movies(df, genre, duration, language, search):
    filtered_df = df.copy()
    
    # Filtre par genre
    if genre != "Tous":
        filtered_df = filtered_df[filtered_df["genre"] == genre]
    
    # Filtre par durée
    if duration == "Court (< 90 min)":
        filtered_df = filtered_df[filtered_df["duree"] < 90]
    elif duration == "Moyen (90-120 min)":
        filtered_df = filtered_df[(filtered_df["duree"] >= 90) & (filtered_df["duree"] <= 120)]
    elif duration == "Long (120-150 min)":
        filtered_df = filtered_df[(filtered_df["duree"] > 120) & (filtered_df["duree"] <= 150)]
    elif duration == "Très long (> 150 min)":
        filtered_df = filtered_df[filtered_df["duree"] > 150]
    
    # Filtre par langue
    if language != "Toutes":
        filtered_df = filtered_df[filtered_df["langue"] == language]
    
    # Filtre par recherche
    if search:
        filtered_df = filtered_df[filtered_df["titre"].str.contains(search, case=False, na=False)]
    
    return filtered_df

# Application des filtres
filtered_movies = filter_movies(movies_df, selected_genre, selected_duration, selected_language, search_query)

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
                        st.markdown(f"### {movie['affiche']} {movie['titre']}")
                        
                        # Informations du film
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Genre:** {movie['genre']}")
                            st.write(f"**Durée:** {movie['duree']} min")
                        with col2:
                            st.write(f"**Langue:** {movie['langue']}")
                            # Affichage de la note avec des étoiles
                            stars = "⭐" * int(movie['note']) + "☆" * (5 - int(movie['note']))
                            st.write(f"**Note:** {movie['note']}/5 {stars}")
                        
                        # Bouton détails
                        if st.button(f"📋 Détails", key=f"details_{movie_idx}"):
                            st.session_state[f"show_details_{movie_idx}"] = True
                        
                        # Affichage des détails si demandé
                        if st.session_state.get(f"show_details_{movie_idx}", False):
                            st.info(f"**Description:** {movie['description']}")
                            if st.button(f"❌ Fermer", key=f"close_{movie_idx}"):
                                st.session_state[f"show_details_{movie_idx}"] = False
                                st.rerun()
                        
                        st.markdown("---")

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
st.sidebar.markdown("### 📊 Statistiques")
st.sidebar.write(f"Total des films: {len(movies_df)}")
st.sidebar.write(f"Films affichés: {len(filtered_movies)}")

# Répartition par genre
genre_counts = movies_df["genre"].value_counts()
st.sidebar.markdown("### 🎭 Genres disponibles")
for genre, count in genre_counts.items():
    st.sidebar.write(f"• {genre}: {count}")
