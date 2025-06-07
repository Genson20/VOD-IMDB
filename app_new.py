import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# Configuration de la page
st.set_page_config(
    page_title="CinéCreuse+",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_movies():
    """Charge et nettoie les données des films"""
    try:
        # Charger le fichier CSV principal
        df = pd.read_csv('df_main_clean.csv')
        
        # 1. Gestion des valeurs manquantes pour les colonnes critiques
        df['title_x'] = df['title_x'].fillna('Titre non disponible')
        df['genres_x'] = df['genres_x'].fillna('Inconnu')
        df['overview'] = df['overview'].fillna('Aucune description disponible')
        df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
        df['year'] = df['release_date'].dt.year
        
        # 2. Nettoyer les colonnes numériques
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
        df = df.dropna(subset=['title_x', 'genres_x', 'overview', 'runtime', 'averageRating'])
        df = df[df['runtime'] > 0]
        df = df[df['averageRating'] > 0]
        
        # 6. Conserver uniquement les colonnes utiles
        columns_to_keep = [
            'title_x', 'original_language', 'release_date', 'year', 'genres_x', 
            'overview', 'poster_path', 'poster_url', 'runtime', 'averageRating', 'numVotes'
        ]
        df = df[columns_to_keep]
        
        # 7. Ajouter la description
        df['description'] = df['overview']
        
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

# Charger les données
df_main = load_movies()

# Interface utilisateur
st.sidebar.title("🎬 CinéCreuse+")
page = st.sidebar.selectbox("Navigation", [
    "🏠 Accueil", "🎬 Catalogue", "📊 Analytics", "⚙️ Admin"
])

# PAGE ACCUEIL
if page == "🏠 Accueil":
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
elif page == "🎬 Catalogue":
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

# PAGE ANALYTICS
elif page == "📊 Analytics":
    st.title("📊 Analytics & Statistiques")
    
    if df_main.empty:
        st.warning("Aucune donnée disponible pour les analytics.")
    else:
        # Métriques principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📽️ Total Films", len(df_main))
        
        with col2:
            avg_rating = df_main['averageRating'].mean()
            st.metric("⭐ Note Moyenne", f"{avg_rating:.1f}/10")
        
        with col3:
            total_runtime = df_main['runtime'].sum()
            total_hours = int(total_runtime / 60)
            st.metric("⏱️ Heures de Contenu", f"{total_hours:,}h")
        
        with col4:
            unique_genres = len(df_main['genres_x'].str.split(',').explode().unique())
            st.metric("🎭 Genres", unique_genres)
        
        st.markdown("---")
        
        # Graphiques
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribution des notes
            fig_ratings = px.histogram(
                df_main, 
                x='averageRating', 
                bins=20,
                title="Distribution des Notes",
                labels={'averageRating': 'Note Moyenne', 'count': 'Nombre de Films'}
            )
            st.plotly_chart(fig_ratings, use_container_width=True)
        
        with col2:
            # Films par décennie
            df_main['decade'] = (df_main['year'] // 10) * 10
            decade_counts = df_main['decade'].value_counts().sort_index()
            
            fig_decades = px.bar(
                x=decade_counts.index,
                y=decade_counts.values,
                title="Films par Décennie",
                labels={'x': 'Décennie', 'y': 'Nombre de Films'}
            )
            st.plotly_chart(fig_decades, use_container_width=True)

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