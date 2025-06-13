import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import joblib
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

# Configuration de la page
st.set_page_config(
    page_title="CinéCreuse+",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def load_knn_model():
    """Charge le modèle KNN pour les recommandations"""
    try:
        model = joblib.load('attached_assets/knn_model_1749778773406.joblib')
        return model
    except Exception as e:
        st.error(f"Erreur lors du chargement du modèle KNN: {e}")
        return None

@st.cache_data
def prepare_features_for_knn(df):
    """Prépare les features pour le modèle KNN"""
    try:
        # Créer des features numériques pour le modèle
        features_df = df.copy()
        
        # Encodage des genres (one-hot encoding simplifié)
        all_genres = set()
        for genres in df['genres_x'].str.split(','):
            if isinstance(genres, list):
                all_genres.update([g.strip() for g in genres])
        
        # Créer des colonnes binaires pour chaque genre
        for genre in all_genres:
            if genre and genre != 'nan':
                features_df[f'genre_{genre}'] = df['genres_x'].str.contains(genre, na=False).astype(int)
        
        # Features numériques
        numeric_features = ['averageRating', 'runtime', 'year', 'numVotes']
        
        # Combiner toutes les features
        feature_columns = numeric_features + [col for col in features_df.columns if col.startswith('genre_')]
        features_matrix = features_df[feature_columns].fillna(0)
        
        return features_matrix, feature_columns
    except Exception as e:
        st.error(f"Erreur lors de la préparation des features: {e}")
        return None, None

def get_knn_recommendations(movie_title, df, model, n_recommendations=5):
    """Obtient des recommandations basées sur le modèle KNN"""
    try:
        # Préparer les features
        features_matrix, feature_columns = prepare_features_for_knn(df)
        if features_matrix is None or model is None:
            return []
        
        # Trouver l'index du film
        movie_idx = df[df['title_x'] == movie_title].index
        if len(movie_idx) == 0:
            return []
        
        movie_idx = movie_idx[0]
        
        # Obtenir les features du film
        movie_features = features_matrix.iloc[movie_idx:movie_idx+1]
        
        # Utiliser le modèle KNN pour trouver des films similaires
        distances, indices = model.kneighbors(movie_features, n_neighbors=n_recommendations+1)
        
        # Exclure le film lui-même et retourner les recommandations
        recommended_indices = indices[0][1:]
        recommended_movies = df.iloc[recommended_indices]
        
        return recommended_movies.to_dict('records')
    except Exception as e:
        st.error(f"Erreur lors de la génération des recommandations: {e}")
        return []

@st.cache_data
def load_movies():
    """Charge et nettoie les données des films"""
    try:
        # Charger le nouveau fichier CSV
        df = pd.read_csv('attached_assets/df_main_cleaned_1749777540074.csv')
        
        # 1. Mapper les colonnes vers les noms attendus par l'application
        if 'title' in df.columns and 'title_x' not in df.columns:
            df['title_x'] = df['title']
        if 'genres' in df.columns and 'genres_x' not in df.columns:
            df['genres_x'] = df['genres']
        if 'overview' in df.columns and 'description' not in df.columns:
            df['description'] = df['overview']
        
        # 2. Gestion des valeurs manquantes pour les colonnes critiques
        df['title_x'] = df['title_x'].fillna('Titre non disponible')
        df['genres_x'] = df['genres_x'].fillna('Inconnu')
        if 'description' in df.columns:
            df['description'] = df['description'].fillna('Aucune description disponible')
        elif 'overview' in df.columns:
            df['description'] = df['overview'].fillna('Aucune description disponible')
        
        df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
        df['year'] = df['release_date'].dt.year
        
        # 3. Nettoyer les colonnes numériques
        numeric_columns = ['runtime', 'averageRating', 'numVotes']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                df[col] = df[col].fillna(0)
        
        # 3. Créer l'URL du poster si elle n'existe pas
        if 'poster_url' not in df.columns:
            base_url = "https://image.tmdb.org/t/p/w500"
            df['poster_url'] = df['poster_path'].apply(
                lambda x: f"{base_url}{x}" if pd.notna(x) and str(x).startswith('/') else None
            )
        
        # 4. Nettoyer les genres (enlever les crochets et guillemets)
        df['genres_x'] = df['genres_x'].astype(str)
        df['genres_x'] = df['genres_x'].str.replace(r'[\[\]\'"]', '', regex=True)
        df['genres_x'] = df['genres_x'].str.replace(r'\s+', ' ', regex=True)
        
        # 5. Filtrer les données
        df = df.drop_duplicates(subset=['title_x', 'release_date'], keep='first')
        df = df.dropna(subset=['title_x', 'genres_x', 'runtime', 'averageRating'])
        df = df[df['runtime'] > 0]
        df = df[df['averageRating'] > 0]
        
        # 6. Conserver uniquement les colonnes utiles disponibles
        available_columns = df.columns.tolist()
        columns_to_keep = []
        for col in ['title_x', 'original_language', 'release_date', 'year', 'genres_x', 
                   'description', 'poster_path', 'poster_url', 'runtime', 'averageRating', 'numVotes']:
            if col in available_columns:
                columns_to_keep.append(col)
        
        df = df[columns_to_keep]
        
        return df
        
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {e}")
        return pd.DataFrame()

def create_poster_with_play_button(poster_url, title, unique_id):
    """Crée le HTML pour une affiche avec bouton play au survol"""
    return f'''
    <style>
    .poster-{unique_id} {{
        position: relative;
        transition: transform 0.3s ease, box-shadow 0.3s ease, filter 0.3s ease;
        cursor: pointer;
        border-radius: 8px;
        overflow: hidden;
        display: block;
    }}
    .poster-{unique_id}:hover {{
        transform: scale(1.25);
        box-shadow: 0 20px 50px rgba(0,0,0,0.9);
        filter: brightness(1.2) contrast(1.1);
        z-index: 100;
    }}
    .poster-{unique_id} img {{
        width: 100%;
        height: auto;
        border-radius: 8px;
        display: block;
    }}
    .play-button-{unique_id} {{
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: rgba(255, 255, 255, 0.9);
        border: none;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        font-size: 24px;
        cursor: pointer;
        opacity: 0;
        transition: opacity 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #333;
    }}
    .poster-{unique_id}:hover .play-button-{unique_id} {{
        opacity: 1;
    }}
    </style>
    <div class="poster-{unique_id}">
        <img src="{poster_url}" alt="{title}" style="width: 180px; border-radius: 8px;">
        <div class="play-button-{unique_id}">▶</div>
    </div>
    '''

# Ajouter le CSS global pour les boutons de navigation
def add_navigation_button_styles():
    """Ajoute les styles CSS pour les boutons de navigation"""
    st.markdown("""
    <style>
    /* Styles pour les boutons de navigation de la sidebar */
    section[data-testid="stSidebar"] .stButton > button {
        background: rgba(40, 44, 52, 0.8) !important;
        color: #e8e8e8 !important;
        border: 1px solid rgba(80, 80, 80, 0.3) !important;
        border-radius: 8px !important;
        width: 100% !important;
        min-height: 60px !important;
        height: auto !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        text-align: center !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        line-height: 1.3 !important;
        padding: 12px 8px !important;
        margin-bottom: 8px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        overflow-wrap: break-word !important;
        hyphens: auto !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(60, 64, 72, 0.9) !important;
        border-color: rgba(120, 120, 120, 0.5) !important;
        color: #ffffff !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3) !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button:disabled {
        background: rgba(25, 28, 35, 0.9) !important;
        color: #a0a0a0 !important;
        border-color: rgba(60, 60, 60, 0.4) !important;
        transform: none !important;
        box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.3) !important;
        cursor: not-allowed !important;
    }
    
    /* Styles pour les boutons de navigation des carrousels dans le contenu principal */
    .main .stButton > button {
        background: rgba(0, 0, 0, 0.6) !important;
        color: white !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 50% !important;
        width: 50px !important;
        height: 50px !important;
        font-size: 20px !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
        backdrop-filter: blur(5px) !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
    }
    
    .main .stButton > button:hover {
        background: rgba(255, 255, 255, 0.9) !important;
        color: #333 !important;
        border-color: #fff !important;
        transform: scale(1.1) !important;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4) !important;
    }
    
    .main .stButton > button:active {
        transform: scale(0.95) !important;
    }
    
    /* Animation pour les boutons */
    .stButton > button:focus {
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.3) !important;
    }
    
    /* Espacement de la sidebar */
    section[data-testid="stSidebar"] {
        padding-top: 1rem !important;
    }
    
    /* Largeur optimisée pour la sidebar */
    section[data-testid="stSidebar"] .block-container {
        padding: 1rem 1rem 10rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Charger les données
df_main = load_movies()

# Appliquer les styles pour les boutons de navigation
add_navigation_button_styles()

# Interface utilisateur avec navigation par boutons
st.sidebar.title("CinéCreuse+")

# Initialiser la page par défaut si elle n'existe pas
if 'page' not in st.session_state:
    st.session_state['page'] = 'Accueil'

# Liste des pages
pages = ['Accueil', 'Catalogue', 'Recommandation', 'Votre cinéma', 'Admin stats']

# Créer les boutons de navigation
for page_name in pages:
    # Vérifier si c'est la page active
    is_active = st.session_state['page'] == page_name
    
    # Bouton avec état visuel différent selon l'activité
    if st.sidebar.button(
        page_name, 
        key=f"nav_{page_name}",
        disabled=is_active,
        use_container_width=True
    ):
        st.session_state['page'] = page_name
        st.rerun()

# Récupérer la page active
page = st.session_state['page']

# PAGE ACCUEIL
if page == "Accueil":
    # En-tête avec logo
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("logo_cinecreuse.svg", width=300)
    
    st.markdown("---")
    
    # Films populaires en vedette avec carrousel
    st.subheader("À la une cette semaine")
    
    if not df_main.empty:
        # Sélectionner les 18 meilleurs films par note et popularité
        featured_movies = df_main.nlargest(18, 'averageRating')
        
        # Système de pagination : 6 films par page, 3 pages maximum
        movies_per_page = 6
        total_pages = 3
        
        # État de pagination pour cette section
        if "featured_page" not in st.session_state:
            st.session_state["featured_page"] = 0
        
        current_page = st.session_state["featured_page"]
        
        # Navigation avec boutons alignés dynamiquement
        start_idx = current_page * movies_per_page
        end_idx = min(start_idx + movies_per_page, len(featured_movies))
        page_movies = featured_movies.iloc[start_idx:end_idx]
        
        if current_page > 0:
            # Mode normal avec boutons des deux côtés
            col_nav1, col_movies, col_nav2 = st.columns([1, 10, 1])
            
            with col_nav1:
                # Espacement vertical de 60px
                st.markdown('<div style="height: 60px;"></div>', unsafe_allow_html=True)
                if st.button("◀", key="prev_featured"):
                    st.session_state["featured_page"] -= 1
                    st.rerun()
            
            with col_nav2:
                # Espacement vertical de 60px
                st.markdown('<div style="height: 60px;"></div>', unsafe_allow_html=True)
                if current_page < total_pages - 1:
                    if st.button("▶", key="next_featured"):
                        st.session_state["featured_page"] += 1
                        st.rerun()
            
            with col_movies:
                # Afficher films avec colonnes centrées
                cols = st.columns(6)
                for idx, (_, movie) in enumerate(page_movies.iterrows()):
                    with cols[idx]:
                        if movie['poster_url']:
                            unique_id = f"featured_{current_page}_{idx}_{hash(movie['poster_url']) % 10000}"
                            poster_html = create_poster_with_play_button(movie['poster_url'], movie['title_x'], unique_id)
                            st.markdown(poster_html, unsafe_allow_html=True)
                        else:
                            st.markdown('<div style="height: 270px; width: 180px; background: #333; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; margin: 0 auto;">🎬</div>', unsafe_allow_html=True)
                        st.caption(f"**{movie['title_x']}**")
                        st.caption(f"⭐ {movie['averageRating']:.1f}/10")
        else:
            # Mode première page - alignement à gauche
            col_movies, col_nav2 = st.columns([10, 1])
            
            with col_nav2:
                # Espacement vertical de 60px
                st.markdown('<div style="height: 60px;"></div>', unsafe_allow_html=True)
                if current_page < total_pages - 1:
                    if st.button("▶", key="next_featured"):
                        st.session_state["featured_page"] += 1
                        st.rerun()
            
            with col_movies:
                # Afficher films alignés à gauche
                cols = st.columns(6)
                for idx, (_, movie) in enumerate(page_movies.iterrows()):
                    with cols[idx]:
                        if movie['poster_url']:
                            unique_id = f"featured_{current_page}_{idx}_{hash(movie['poster_url']) % 10000}"
                            poster_html = create_poster_with_play_button(movie['poster_url'], movie['title_x'], unique_id)
                            st.markdown(poster_html, unsafe_allow_html=True)
                        else:
                            st.markdown('<div style="height: 270px; width: 180px; background: #333; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; margin: 0 auto;">🎬</div>', unsafe_allow_html=True)
                        st.caption(f"**{movie['title_x']}**")
                        st.caption(f"⭐ {movie['averageRating']:.1f}/10")

    st.markdown("---")
    
    # Sélections par genre
    genres_dict = {
        "Action": "Action",
        "Comédie": "Comedy", 
        "Drame": "Drama",
        "Horreur": "Horror",
        "Romance": "Romance",
        "Thriller": "Thriller",
        "Aventure": "Adventure",
        "Science-Fiction": "Sci-Fi"
    }
    
    for genre_title, genre in genres_dict.items():
        # Filtrer les films par genre
        genre_movies = df_main[df_main['genres_x'].str.contains(genre, case=False, na=False)]
        
        if not genre_movies.empty:
            # Sélectionner les 18 meilleurs films du genre
            top_genre_movies = genre_movies.nlargest(18, 'averageRating')
            
            st.subheader(genre_title)
            
            # Système de pagination : 6 films par page, 3 pages maximum
            movies_per_page = 6
            total_pages = 3
            
            # État de pagination pour cette section
            genre_key = f"{genre}_page"
            if genre_key not in st.session_state:
                st.session_state[genre_key] = 0
            
            current_page = st.session_state[genre_key]
            
            # Navigation avec boutons alignés dynamiquement
            start_idx = current_page * movies_per_page
            end_idx = min(start_idx + movies_per_page, len(top_genre_movies))
            page_movies = top_genre_movies.iloc[start_idx:end_idx]
            
            if current_page > 0:
                # Mode normal avec boutons des deux côtés
                col_nav1, col_movies, col_nav2 = st.columns([1, 10, 1])
                
                with col_nav1:
                    # Espacement vertical de 60px
                    st.markdown('<div style="height: 60px;"></div>', unsafe_allow_html=True)
                    if st.button("◀", key=f"prev_{genre}"):
                        st.session_state[genre_key] -= 1
                        st.rerun()
                
                with col_nav2:
                    # Espacement vertical de 60px
                    st.markdown('<div style="height: 60px;"></div>', unsafe_allow_html=True)
                    if current_page < total_pages - 1 and len(top_genre_movies) > (current_page + 1) * movies_per_page:
                        if st.button("▶", key=f"next_{genre}"):
                            st.session_state[genre_key] += 1
                            st.rerun()
                
                with col_movies:
                    # Afficher films avec colonnes centrées
                    cols = st.columns(6)
                    for idx, (_, movie) in enumerate(page_movies.iterrows()):
                        with cols[idx]:
                            if 'poster_url' in movie and pd.notna(movie['poster_url']):
                                unique_id = f"{genre}_{current_page}_{idx}_{hash(movie['poster_url']) % 10000}"
                                poster_html = create_poster_with_play_button(movie['poster_url'], movie['title_x'], unique_id)
                                st.markdown(poster_html, unsafe_allow_html=True)
                            else:
                                st.markdown('<div style="height: 270px; width: 180px; background: #333; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; margin: 0 auto;">🎬</div>', unsafe_allow_html=True)
                            st.caption(f"**{movie['title_x']}**")
                            st.caption(f"⭐ {movie['averageRating']:.1f}/10")
            else:
                # Mode première page - alignement à gauche
                col_movies, col_nav2 = st.columns([10, 1])
                
                with col_nav2:
                    # Espacement vertical de 60px
                    st.markdown('<div style="height: 60px;"></div>', unsafe_allow_html=True)
                    if current_page < total_pages - 1 and len(top_genre_movies) > (current_page + 1) * movies_per_page:
                        if st.button("▶", key=f"next_{genre}"):
                            st.session_state[genre_key] += 1
                            st.rerun()
                
                with col_movies:
                    # Afficher films alignés à gauche
                    cols = st.columns(6)
                    for idx, (_, movie) in enumerate(page_movies.iterrows()):
                        with cols[idx]:
                            if 'poster_url' in movie and pd.notna(movie['poster_url']):
                                unique_id = f"{genre}_{current_page}_{idx}_{hash(movie['poster_url']) % 10000}"
                                poster_html = create_poster_with_play_button(movie['poster_url'], movie['title_x'], unique_id)
                                st.markdown(poster_html, unsafe_allow_html=True)
                            else:
                                st.markdown('<div style="height: 270px; width: 180px; background: #333; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; margin: 0 auto;">🎬</div>', unsafe_allow_html=True)
                            st.caption(f"**{movie['title_x']}**")
                            st.caption(f"⭐ {movie['averageRating']:.1f}/10")
            
            st.markdown("---")
    
    # Section "Les plus populaires" avec carrousel
    st.subheader("Les plus populaires")
    
    if not df_main.empty:
        # Sélectionner les 18 films les plus populaires par note
        popular_movies = df_main.nlargest(18, 'averageRating')
        
        # Système de pagination : 6 films par page, 3 pages maximum
        movies_per_page = 6
        total_pages = 3
        
        # État de pagination pour cette section
        if "popular_page" not in st.session_state:
            st.session_state["popular_page"] = 0
        
        current_page = st.session_state["popular_page"]
        
        # Navigation avec boutons alignés dynamiquement
        start_idx = current_page * movies_per_page
        end_idx = min(start_idx + movies_per_page, len(popular_movies))
        page_movies = popular_movies.iloc[start_idx:end_idx]
        
        if current_page > 0:
            # Mode normal avec boutons des deux côtés
            col_nav1, col_movies, col_nav2 = st.columns([1, 10, 1])
            
            with col_nav1:
                # Espacement vertical de 60px
                st.markdown('<div style="height: 60px;"></div>', unsafe_allow_html=True)
                if st.button("◀", key="prev_popular"):
                    st.session_state["popular_page"] -= 1
                    st.rerun()
            
            with col_nav2:
                # Espacement vertical de 60px
                st.markdown('<div style="height: 60px;"></div>', unsafe_allow_html=True)
                if current_page < total_pages - 1 and len(popular_movies) > (current_page + 1) * movies_per_page:
                    if st.button("▶", key="next_popular"):
                        st.session_state["popular_page"] += 1
                        st.rerun()
            
            with col_movies:
                # Afficher films avec colonnes centrées
                cols = st.columns(6)
                for idx, (_, movie) in enumerate(page_movies.iterrows()):
                    with cols[idx]:
                        if 'poster_url' in movie and pd.notna(movie['poster_url']):
                            unique_id = f"popular_{current_page}_{idx}_{hash(movie['poster_url']) % 10000}"
                            poster_html = create_poster_with_play_button(movie['poster_url'], movie['title_x'], unique_id)
                            st.markdown(poster_html, unsafe_allow_html=True)
                        else:
                            st.markdown('<div style="height: 270px; width: 180px; background: #333; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; margin: 0 auto;">🎬</div>', unsafe_allow_html=True)
                        st.caption(f"**{movie['title_x']}**")
                        st.caption(f"⭐ {movie['averageRating']:.1f}/10")
        else:
            # Mode première page - alignement à gauche
            col_movies, col_nav2 = st.columns([10, 1])
            
            with col_nav2:
                # Espacement vertical de 60px
                st.markdown('<div style="height: 60px;"></div>', unsafe_allow_html=True)
                if current_page < total_pages - 1 and len(popular_movies) > (current_page + 1) * movies_per_page:
                    if st.button("▶", key="next_popular"):
                        st.session_state["popular_page"] += 1
                        st.rerun()
            
            with col_movies:
                # Afficher films alignés à gauche
                cols = st.columns(6)
                for idx, (_, movie) in enumerate(page_movies.iterrows()):
                    with cols[idx]:
                        if 'poster_url' in movie and pd.notna(movie['poster_url']):
                            unique_id = f"popular_{current_page}_{idx}_{hash(movie['poster_url']) % 10000}"
                            poster_html = create_poster_with_play_button(movie['poster_url'], movie['title_x'], unique_id)
                            st.markdown(poster_html, unsafe_allow_html=True)
                        else:
                            st.markdown('<div style="height: 270px; width: 180px; background: #333; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; margin: 0 auto;">🎬</div>', unsafe_allow_html=True)
                        st.caption(f"**{movie['title_x']}**")
                        st.caption(f"⭐ {movie['averageRating']:.1f}/10")
        
        st.markdown("---")

# PAGE CATALOGUE
elif page == "Catalogue":
    st.title("🎬 Catalogue complet")
    
    if df_main.empty:
        st.warning("Aucune donnée disponible.")
    else:
        # Filtres
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Filtre par genre
            all_genres = []
            for genres_str in df_main['genres_x'].dropna():
                if isinstance(genres_str, str):
                    genres_list = [g.strip() for g in genres_str.split(',')]
                    all_genres.extend(genres_list)
            
            unique_genres = sorted(list(set(all_genres)))
            selected_genre = st.selectbox("Filtrer par genre", ["Tous"] + unique_genres)
        
        with col2:
            # Filtre par année
            years = sorted(df_main['year'].dropna().unique(), reverse=True)
            selected_year = st.selectbox("Filtrer par année", ["Toutes"] + [str(int(y)) for y in years if y > 1900])
        
        with col3:
            # Tri
            sort_options = {
                "Note (décroissant)": ("averageRating", False),
                "Note (croissant)": ("averageRating", True),
                "Année (récent)": ("year", False),
                "Année (ancien)": ("year", True),
                "Titre (A-Z)": ("title_x", True),
                "Titre (Z-A)": ("title_x", False)
            }
            selected_sort = st.selectbox("Trier par", list(sort_options.keys()))
        
        # Appliquer les filtres
        filtered_df = df_main.copy()
        
        if selected_genre != "Tous":
            filtered_df = filtered_df[filtered_df['genres_x'].str.contains(selected_genre, case=False, na=False)]
        
        if selected_year != "Toutes":
            filtered_df = filtered_df[filtered_df['year'] == int(selected_year)]
        
        # Appliquer le tri
        sort_column, ascending = sort_options[selected_sort]
        filtered_df = filtered_df.sort_values(sort_column, ascending=ascending)
        
        st.write(f"**{len(filtered_df)} films trouvés**")
        
        # Affichage en grille
        if not filtered_df.empty:
            movies_per_row = 6
            rows = len(filtered_df) // movies_per_row + (1 if len(filtered_df) % movies_per_row > 0 else 0)
            
            for row in range(rows):
                cols = st.columns(movies_per_row)
                start_idx = row * movies_per_row
                end_idx = min(start_idx + movies_per_row, len(filtered_df))
                
                for col_idx, movie_idx in enumerate(range(start_idx, end_idx)):
                    movie = filtered_df.iloc[movie_idx]
                    with cols[col_idx]:
                        if movie['poster_url']:
                            unique_id = f"catalog_{row}_{col_idx}_{hash(movie['poster_url']) % 10000}"
                            poster_html = create_poster_with_play_button(movie['poster_url'], movie['title_x'], unique_id)
                            st.markdown(poster_html, unsafe_allow_html=True)
                        else:
                            st.markdown('<div style="height: 270px; width: 180px; background: #333; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; margin: 0 auto;">🎬</div>', unsafe_allow_html=True)
                        
                        st.caption(f"**{movie['title_x']}**")
                        st.caption(f"⭐ {movie['averageRating']:.1f}/10 • {movie['year']}")

# PAGE RECOMMANDATION
elif page == "Recommandation":
    st.title("🎯 Recommandations personnalisées par IA")
    
    # Charger le modèle KNN
    knn_model = load_knn_model()
    
    if df_main.empty:
        st.warning("Aucune donnée disponible pour les recommandations.")
    elif knn_model is None:
        st.error("Le modèle de recommandation n'est pas disponible.")
    else:
        st.markdown("### Trouvez des films similaires à vos préférences")
        
        # Interface de sélection de film
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Sélecteur de film
            movie_titles = sorted(df_main['title_x'].tolist())
            selected_movie = st.selectbox(
                "Choisissez un film que vous avez aimé :",
                movie_titles,
                index=0
            )
        
        with col2:
            num_recommendations = st.slider(
                "Nombre de recommandations :",
                min_value=3,
                max_value=12,
                value=6
            )
        
        if st.button("🔍 Obtenir des recommandations", type="primary"):
            with st.spinner("Analyse en cours avec l'IA..."):
                # Obtenir les recommandations avec le modèle KNN
                recommendations = get_knn_recommendations(
                    selected_movie, 
                    df_main, 
                    knn_model, 
                    num_recommendations
                )
                
                if recommendations:
                    st.success(f"Voici {len(recommendations)} films recommandés basés sur **{selected_movie}** :")
                    
                    # Afficher le film sélectionné
                    st.markdown("---")
                    st.subheader("Film de référence")
                    selected_movie_data = df_main[df_main['title_x'] == selected_movie].iloc[0]
                    
                    ref_col1, ref_col2 = st.columns([1, 3])
                    with ref_col1:
                        if pd.notna(selected_movie_data['poster_url']):
                            st.image(selected_movie_data['poster_url'], width=150)
                        else:
                            st.markdown('<div style="height: 200px; width: 150px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white;">🎬</div>', unsafe_allow_html=True)
                    
                    with ref_col2:
                        st.markdown(f"**{selected_movie_data['title_x']}**")
                        st.markdown(f"**Note :** ⭐ {selected_movie_data['averageRating']:.1f}/10")
                        st.markdown(f"**Année :** {int(selected_movie_data['year'])}")
                        st.markdown(f"**Genres :** {selected_movie_data['genres_x']}")
                        st.markdown(f"**Durée :** {int(selected_movie_data['runtime'])} min")
                        if 'description' in selected_movie_data and pd.notna(selected_movie_data['description']):
                            st.markdown(f"**Synopsis :** {selected_movie_data['description'][:200]}...")
                    
                    # Afficher les recommandations
                    st.markdown("---")
                    st.subheader("Films similaires recommandés")
                    
                    # Organiser en grille
                    cols_per_row = 3
                    for i in range(0, len(recommendations), cols_per_row):
                        cols = st.columns(cols_per_row)
                        for j, movie in enumerate(recommendations[i:i+cols_per_row]):
                            with cols[j]:
                                # Card style pour chaque recommandation
                                with st.container():
                                    if pd.notna(movie['poster_url']):
                                        st.image(movie['poster_url'], width=200)
                                    else:
                                        st.markdown('<div style="height: 270px; width: 180px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; margin: 0 auto;">🎬</div>', unsafe_allow_html=True)
                                    
                                    st.markdown(f"**{movie['title_x']}**")
                                    st.markdown(f"⭐ {movie['averageRating']:.1f}/10 • {int(movie['year'])}")
                                    st.markdown(f"🎭 {movie['genres_x']}")
                                    st.markdown(f"⏱️ {int(movie['runtime'])} min")
                                    
                                    if 'description' in movie and pd.notna(movie['description']):
                                        with st.expander("📖 Synopsis"):
                                            st.write(movie['description'])
                else:
                    st.warning("Aucune recommandation trouvée pour ce film.")
        
        st.markdown("---")
        
        # Section films les mieux notés
        st.subheader("🌟 Films les mieux notés du catalogue")
        top_movies = df_main.nlargest(8, 'averageRating')
        
        if not top_movies.empty:
            cols = st.columns(4)
            for idx, (_, movie) in enumerate(top_movies.iterrows()):
                if idx >= 8:
                    break
                col_idx = idx % 4
                with cols[col_idx]:
                    if pd.notna(movie['poster_url']):
                        unique_id = f"top_{idx}_{hash(movie['poster_url']) % 10000}"
                        poster_html = create_poster_with_play_button(movie['poster_url'], movie['title_x'], unique_id)
                        st.markdown(poster_html, unsafe_allow_html=True)
                    else:
                        st.markdown('<div style="height: 270px; width: 180px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; margin: 0 auto;">🎬</div>', unsafe_allow_html=True)
                    st.caption(f"**{movie['title_x']}**")
                    st.caption(f"⭐ {movie['averageRating']:.1f}/10")
        
        # Information sur le modèle
        st.markdown("---")
        with st.expander("ℹ️ À propos du système de recommandation"):
            st.markdown("""
            **Comment ça marche ?**
            
            Notre système utilise un modèle d'intelligence artificielle (K-Nearest Neighbors) qui analyse :
            - Les notes et popularité des films
            - Les genres et catégories
            - L'année de sortie
            - La durée des films
            
            L'algorithme trouve les films les plus similaires en analysant ces caractéristiques et vous propose des recommandations personnalisées basées sur vos goûts.
            """)

# PAGE VOTRE CINÉMA
elif page == "Votre cinéma":
    st.title("Votre cinéma local")
    
    # Informations sur le cinéma
    cinema_col1, cinema_col2 = st.columns([3, 1])
    
    with cinema_col1:
        st.subheader("Cinéma CinéCreuse")
        st.write("📍 **Adresse:** 123 Rue du Cinéma, Creuse, France")
        st.write("📞 **Téléphone:** +33 5 55 XX XX XX")
        st.write("🕐 **Horaires:** Lundi-Dimanche 14h00-23h00")
    
    with cinema_col2:
        st.metric("Places disponibles", "245", "12")
        st.metric("Films à l'affiche", "12", "2")
    
    st.markdown("---")
    
    # Vérifier d'abord si les données sont disponibles
    if not df_main.empty:
        # Programmation sur 7 jours
        st.subheader("Programmation sur 7 jours")
        
        from datetime import datetime, timedelta
        import random
        
        # Générer les 7 prochains jours
        today = datetime.now()
        week_days = []
        for i in range(7):
            day = today + timedelta(days=i)
            week_days.append({
                'date': day,
                'day_name': day.strftime('%A'),
                'day_num': day.strftime('%d'),
                'month': day.strftime('%b')
            })
        
        # Sélecteur de jour
        selected_day_index = st.selectbox(
            "Choisir un jour:",
            range(7),
            format_func=lambda x: f"{week_days[x]['day_name']} {week_days[x]['day_num']} {week_days[x]['month']}"
        )
        
        selected_day = week_days[selected_day_index]
        
        # Rotation des films selon le jour pour varier la programmation
        random.seed(selected_day_index)  # Seed fixe pour cohérence
        available_movies = df_main.sample(min(8, len(df_main))).reset_index(drop=True)
        
        st.markdown(f"### Films du {selected_day['day_name']} {selected_day['day_num']} {selected_day['month']}")
        
        # Horaires variables selon le jour
        base_times = ["14:30", "17:00", "19:30", "22:00"]
        if selected_day_index == 5 or selected_day_index == 6:  # Weekend
            showtimes = ["10:30", "13:00", "15:30", "18:00", "20:30", "23:00"]
        else:
            showtimes = base_times
        
        # Affichage en grille
        movies_per_row = 4
        for i in range(0, len(available_movies), movies_per_row):
            movie_cols = st.columns(movies_per_row)
            
            for j, col in enumerate(movie_cols):
                if i + j < len(available_movies):
                    movie = available_movies.iloc[i + j]
                    
                    with col:
                        # Poster du film
                        if movie['poster_url']:
                            poster_html = create_poster_with_play_button(
                                movie['poster_url'], 
                                movie['title_x'], 
                                f"cinema_{i+j}"
                            )
                            st.markdown(poster_html, unsafe_allow_html=True)
                        else:
                            st.markdown(
                                '<div style="height: 200px; width: 100%; background: #333; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; margin-bottom: 10px;">🎬</div>', 
                                unsafe_allow_html=True
                            )
                        
                        # Informations du film
                        st.markdown(f"**{movie['title_x'][:25]}{'...' if len(movie['title_x']) > 25 else ''}**")
                        st.caption(f"⭐ {movie['averageRating']:.1f}/10 • {movie['runtime']}min")
                        st.caption(f"{movie['genres_x'][:20]}{'...' if len(str(movie['genres_x'])) > 20 else ''}")
                        
                        # Horaires pour ce film (2-3 séances par film)
                        movie_times = random.sample(showtimes, min(3, len(showtimes)))
                        movie_times.sort()
                        
                        st.markdown("**Séances:**")
                        times_text = " • ".join([f"**{time}**" for time in movie_times])
                        st.markdown(times_text)
                        
                        # Bouton de réservation
                        if st.button(f"Réserver", key=f"book_{selected_day_index}_{i+j}"):
                            st.success(f"Réservation pour {movie['title_x']}")
        
        st.markdown("---")
        
        # Section informations pratiques
        st.subheader("Informations pratiques")
        
        info_col1, info_col2 = st.columns(2)
        
        with info_col1:
            st.markdown("""
            **Tarifs:**
            - Plein tarif: 9,50€
            - Étudiant: 7,50€ 
            - Enfant (-12 ans): 6,50€
            - Séance matinale: 6,00€
            """)
        
        with info_col2:
            st.markdown("""
            **Services:**
            - Billetterie en ligne
            - Parking gratuit
            - Accessibilité PMR
            - Climatisation
            """)
    else:
        st.warning("Aucun film disponible pour le moment.")

# PAGE ADMIN STATS
elif page == "Admin stats":
    st.title("📊 Dashboard Analytics - CinéCreuse+")
    
    if df_main.empty:
        st.warning("Aucune donnée disponible pour les analytics.")
    else:
        import random
        import numpy as np
        from datetime import datetime, timedelta
        
        # === KPI FILMS ===
        st.subheader("🎬 KPI Films & Catalogue")
        
        # Métriques principales films
        films_col1, films_col2, films_col3, films_col4, films_col5 = st.columns(5)
        
        with films_col1:
            total_films = len(df_main)
            st.metric("Films au catalogue", total_films, "12")
        
        with films_col2:
            avg_rating = df_main['averageRating'].mean()
            st.metric("Note moyenne", f"{avg_rating:.1f}/10", "0.2")
        
        with films_col3:
            total_runtime = df_main['runtime'].sum()
            total_hours = int(total_runtime / 60)
            st.metric("Heures de contenu", f"{total_hours:,}h", "156h")
        
        with films_col4:
            high_rated = len(df_main[df_main['averageRating'] >= 7.5])
            high_rated_pct = (high_rated / total_films) * 100
            st.metric("Films bien notés", f"{high_rated_pct:.0f}%", "3%")
        
        with films_col5:
            recent_films = len(df_main[df_main['year'] >= 2020])
            st.metric("Films récents (2020+)", recent_films, "8")
        
        # Métriques secondaires films
        films_sub_col1, films_sub_col2, films_sub_col3, films_sub_col4 = st.columns(4)
        
        with films_sub_col1:
            unique_genres = len(df_main['genres_x'].str.split(',').explode().unique())
            st.metric("Genres disponibles", unique_genres)
        
        with films_sub_col2:
            avg_runtime = df_main['runtime'].mean()
            st.metric("Durée moyenne", f"{avg_runtime:.0f}min")
        
        with films_sub_col3:
            blockbusters = len(df_main[df_main['runtime'] >= 150])
            st.metric("Films > 2h30", blockbusters)
        
        with films_sub_col4:
            short_films = len(df_main[df_main['runtime'] <= 90])
            st.metric("Films < 1h30", short_films)
        
        st.markdown("---")
        
        # === KPI UTILISATEURS (Simulés) ===
        st.subheader("👥 KPI Utilisateurs & Engagement")
        
        # Simuler des données utilisateurs réalistes
        total_users = 2847
        active_users_month = 1923
        active_users_week = 1205
        active_users_today = 287
        
        # Métriques principales utilisateurs
        users_col1, users_col2, users_col3, users_col4, users_col5 = st.columns(5)
        
        with users_col1:
            st.metric("Utilisateurs total", f"{total_users:,}", "156")
        
        with users_col2:
            monthly_retention = (active_users_month / total_users) * 100
            st.metric("Actifs ce mois", f"{active_users_month:,}", f"{monthly_retention:.0f}%")
        
        with users_col3:
            weekly_retention = (active_users_week / total_users) * 100
            st.metric("Actifs cette semaine", f"{active_users_week:,}", f"{weekly_retention:.0f}%")
        
        with users_col4:
            st.metric("Actifs aujourd'hui", active_users_today, "23")
        
        with users_col5:
            avg_session = random.randint(8, 15)
            st.metric("Session moyenne", f"{avg_session}min", "2min")
        
        # Métriques engagement
        engage_col1, engage_col2, engage_col3, engage_col4 = st.columns(4)
        
        with engage_col1:
            films_viewed_today = random.randint(156, 203)
            st.metric("Films vus aujourd'hui", films_viewed_today, "12")
        
        with engage_col2:
            bounce_rate = random.randint(25, 35)
            st.metric("Taux de rebond", f"{bounce_rate}%", "-3%")
        
        with engage_col3:
            avg_films_per_user = random.randint(3, 7)
            st.metric("Films/utilisateur", f"{avg_films_per_user:.1f}", "0.4")
        
        with engage_col4:
            conversion_rate = random.randint(12, 18)
            st.metric("Taux conversion", f"{conversion_rate}%", "2%")
        
        st.markdown("---")
        
        # === GRAPHIQUES ANALYTICS ===
        st.subheader("📈 Analytics Détaillées")
        
        graph_col1, graph_col2 = st.columns(2)
        
        with graph_col1:
            # Top genres par popularité (simulé avec données réelles)
            genres_split = df_main['genres_x'].str.split(',').explode().str.strip()
            top_genres = genres_split.value_counts().head(8)
            
            fig_genres = px.bar(
                x=top_genres.values,
                y=top_genres.index,
                orientation='h',
                title="Top Genres les Plus Populaires",
                labels={'x': 'Nombre de Films', 'y': 'Genre'},
                color=top_genres.values,
                color_continuous_scale='viridis'
            )
            fig_genres.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_genres, use_container_width=True)
        
        with graph_col2:
            # Évolution audience (données simulées)
            dates = [(datetime.now() - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(30, 0, -1)]
            audience_data = [random.randint(180, 320) for _ in range(30)]
            
            # Ajouter une tendance croissante
            for i in range(1, len(audience_data)):
                audience_data[i] = max(150, audience_data[i-1] + random.randint(-20, 25))
            
            fig_audience = px.line(
                x=dates,
                y=audience_data,
                title="Évolution Audience Quotidienne (30j)",
                labels={'x': 'Date', 'y': 'Utilisateurs Actifs'}
            )
            fig_audience.update_traces(line_color='#ff6b6b', line_width=3)
            fig_audience.update_layout(height=400)
            st.plotly_chart(fig_audience, use_container_width=True)
        
        # Deuxième ligne de graphiques
        graph2_col1, graph2_col2 = st.columns(2)
        
        with graph2_col1:
            # Distribution des notes avec plus de détails
            fig_ratings = px.histogram(
                df_main, 
                x='averageRating', 
                nbins=20,
                title="Distribution Qualité du Catalogue",
                labels={'averageRating': 'Note IMDB', 'count': 'Nombre de Films'},
                color_discrete_sequence=['#4ecdc4']
            )
            fig_ratings.add_vline(x=avg_rating, line_dash="dash", line_color="red", 
                                annotation_text=f"Moyenne: {avg_rating:.1f}")
            st.plotly_chart(fig_ratings, use_container_width=True)
        
        with graph2_col2:
            # Répartition par décennie avec tendances
            df_main['decade'] = (df_main['year'] // 10) * 10
            decade_counts = df_main['decade'].value_counts().sort_index()
            
            fig_decades = px.bar(
                x=decade_counts.index,
                y=decade_counts.values,
                title="Répartition Catalogue par Époque",
                labels={'x': 'Décennie', 'y': 'Nombre de Films'},
                color=decade_counts.values,
                color_continuous_scale='plasma'
            )
            st.plotly_chart(fig_decades, use_container_width=True)
        
        st.markdown("---")
        
        # === TABLEAU DE BORD OPÉRATIONNEL ===
        st.subheader("⚡ Tableau de Bord Opérationnel")
        
        ops_col1, ops_col2, ops_col3 = st.columns(3)
        
        with ops_col1:
            st.markdown("**🎯 Objectifs du Mois**")
            st.progress(0.73, text="Nouveaux utilisateurs: 73%")
            st.progress(0.45, text="Films ajoutés: 45%")
            st.progress(0.89, text="Satisfaction client: 89%")
        
        with ops_col2:
            st.markdown("**📊 Performance Technique**")
            st.metric("Temps de chargement", "1.2s", "-0.3s")
            st.metric("Uptime serveur", "99.8%", "0.1%")
            st.metric("Erreurs API", "0.02%", "-0.01%")
        
        with ops_col3:
            st.markdown("**💰 Indicateurs Business**")
            st.metric("Revenus mensuels", "€12,847", "€1,203")
            st.metric("Coût par acquisition", "€8.40", "-€1.20")
            st.metric("LTV moyenne", "€47.50", "€3.20")
        
        # Top films performants
        st.markdown("---")
        st.subheader("🏆 Top Films Performance")
        
        top_films = df_main.nlargest(10, 'averageRating')[['title_x', 'averageRating', 'year', 'genres_x', 'runtime']]
        top_films.columns = ['Titre', 'Note', 'Année', 'Genre', 'Durée (min)']
        st.dataframe(top_films, use_container_width=True, hide_index=True)

# PAGE ADMIN
elif page == "⚙️ Admin":
    st.title("⚙️ Administration")
    
    # Informations système
    st.subheader("📊 Informations Système")
    
    if not df_main.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Nombre total de films:** {len(df_main)}")
            st.info(f"**Colonnes disponibles:** {len(df_main.columns)}")
            st.info(f"**Taille mémoire:** {df_main.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        with col2:
            st.info(f"**Films avec posters:** {df_main['poster_url'].notna().sum()}")
            st.info(f"**Année la plus ancienne:** {int(df_main['year'].min())}")
            st.info(f"**Année la plus récente:** {int(df_main['year'].max())}")
    
    st.markdown("---")
    
    # Actions d'administration
    st.subheader("🔧 Actions")
    
    if st.button("🔄 Recharger les données"):
        st.cache_data.clear()
        st.rerun()
    
    if st.button("📥 Exporter les données"):
        csv = df_main.to_csv(index=False)
        st.download_button(
            label="Télécharger CSV",
            data=csv,
            file_name=f"cinecreuse_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )