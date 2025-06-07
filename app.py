import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import random
import streamlit.components.v1 as components

# Configuration de la page
st.set_page_config(
    page_title="CinéCreuse+",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Chargement et nettoyage de la base de données réelle
@st.cache_data
def load_movies():
    try:
        # Charger le CSV réel
        df = pd.read_csv('df_main_clean.csv')
        
        # 1. Nettoyer et préparer les données de base
        df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
        df['year'] = df['release_date'].dt.year
        
        # 2. Nettoyer les langues - garder uniquement français et anglais
        df = df[df['original_language'].isin(['fr', 'en'])]
        
        # 3. Nettoyer les genres
        df['genres_x'] = df['genres_x'].astype(str)
        df['genres_x'] = df['genres_x'].str.replace("[", "").str.replace("]", "").str.replace("'", "").str.replace('"', '')
        
        # 4. Colonnes numériques
        df['runtime'] = pd.to_numeric(df['runtime'], errors='coerce')
        df['averageRating'] = pd.to_numeric(df['averageRating'], errors='coerce')
        df['numVotes'] = pd.to_numeric(df['numVotes'], errors='coerce')
        
        # 5. Filtrer les films avec poster_path valide - nettoyage strict
        df = df[df['poster_path'].notna()]  # Éliminer les NaN
        df = df[df['poster_path'] != '']    # Éliminer les chaînes vides
        df = df[df['poster_path'].str.len() > 1]  # Éliminer les chaînes trop courtes
        df = df[df['poster_path'].str.startswith('/')]  # Doit commencer par /
        
        # 6. Construire l'URL complète des affiches TMDB
        df['poster_url'] = 'https://image.tmdb.org/t/p/w500' + df['poster_path']
        
        # 7. Supprimer les doublons basés sur titre, année et durée
        df = df.drop_duplicates(subset=['title_x', 'year', 'runtime'], keep='first')
        
        # 8. Filtrer les films avec des données valides essentielles
        df = df.dropna(subset=['title_x', 'genres_x', 'overview', 'runtime', 'averageRating'])
        df = df[df['runtime'] > 0]
        df = df[df['averageRating'] > 0]
        
        # 9. Conserver uniquement les colonnes utiles
        columns_to_keep = [
            'title_x', 'original_language', 'release_date', 'year', 'genres_x', 
            'overview', 'poster_path', 'poster_url', 'runtime', 'averageRating', 'numVotes'
        ]
        df = df[columns_to_keep]
        
        # 10. Ajouter la description
        df['description'] = df['overview']
        
        return df
        
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {e}")
        return pd.DataFrame()

# Fonction pour obtenir des emojis basés sur le genre
def get_emoji_for_genre(genres):
    if pd.isna(genres):
        return "🎬"
    genres_str = str(genres).lower()
    if 'action' in genres_str:
        return "💥"
    elif 'comedy' in genres_str:
        return "😂"
    elif 'drama' in genres_str:
        return "🎭"
    elif 'horror' in genres_str:
        return "👻"
    elif 'romance' in genres_str:
        return "💕"
    elif 'science fiction' in genres_str or 'sci-fi' in genres_str:
        return "🚀"
    elif 'thriller' in genres_str:
        return "😱"
    elif 'fantasy' in genres_str:
        return "🧚"
    elif 'animation' in genres_str:
        return "🎨"
    elif 'crime' in genres_str:
        return "🔫"
    elif 'war' in genres_str:
        return "⚔️"
    elif 'adventure' in genres_str:
        return "🗺️"
    else:
        return "🎬"

# Génération des horaires
def generate_showtimes():
    base_hours = [14, 16, 18, 20, 22]
    showtimes = []
    for hour in base_hours:
        minutes = random.choice([0, 15, 30, 45])
        time_str = f"{hour:02d}:{minutes:02d}"
        showtimes.append(time_str)
    return showtimes

# Génération des films à venir
def generate_upcoming_movies():
    upcoming = []
    for i in range(5):
        date = datetime.now() + timedelta(days=random.randint(7, 60))
        upcoming.append({
            'title': f"Film à venir {i+1}",
            'date': date.strftime("%d/%m/%Y"),
            'genre': random.choice(['Action', 'Comédie', 'Drame', 'Horreur'])
        })
    return upcoming

# Chargement des utilisateurs (simulation)
def load_users():
    return pd.DataFrame({
        'user_id': range(1, 101),
        'age': np.random.randint(18, 70, 100),
        'genre_pref': np.random.choice(['Action', 'Comédie', 'Drame', 'Horreur', 'Romance'], 100),
        'movies_watched': np.random.randint(1, 50, 100)
    })

# CSS pour cacher les éléments Streamlit
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
df_main = load_movies()

# NAVIGATION
st.sidebar.image("logo_cinecreuse.svg", width=180)
st.sidebar.title("Navigation")

# Options de navigation
pages = [
    "🏠 Accueil", 
    "🎬 Catalogue", 
    "🔍 Recherche", 
    "📺 Programmation TV", 
    "📊 Dashboard Admin", 
    "👥 Gestion Utilisateurs",
    "🎯 Analytique Avancée"
]

page = st.sidebar.selectbox("Aller à", pages)

# ================================
# PAGE ACCUEIL
# ================================
if page == "🏠 Accueil":
    # En-tête avec logo
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("logo_cinecreuse.svg", width=300)
    
    st.markdown("---")
    
    # Section héro
    st.markdown("""
    <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin: 1rem 0;'>
        <h1 style='color: white; font-size: 3rem; margin-bottom: 1rem;'>Bienvenue sur CinéCreuse+</h1>
        <p style='color: white; font-size: 1.2rem; margin-bottom: 0;'>Votre plateforme de streaming premium</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Métriques principales
    if not df_main.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📽️ Films disponibles", len(df_main))
        
        with col2:
            avg_rating = df_main['averageRating'].mean()
            st.metric("⭐ Note moyenne", f"{avg_rating:.1f}/10")
        
        with col3:
            total_runtime = df_main['runtime'].sum()
            total_hours = int(total_runtime / 60)
            st.metric("⏱️ Heures de contenu", f"{total_hours:,}h")
        
        with col4:
            unique_genres = len(df_main['genres_x'].str.split(',').explode().unique())
            st.metric("🎭 Genres disponibles", unique_genres)
    
    st.markdown("---")
    
    # Films populaires en vedette
    st.subheader("À la une cette semaine")
    
    if not df_main.empty:
        # Sélectionner les 6 meilleurs films par note et popularité
        featured_movies = df_main.nlargest(6, 'averageRating')
        
        cols = st.columns(6)
        for idx, (_, movie) in enumerate(featured_movies.iterrows()):
            with cols[idx]:
                if movie['poster_url']:
                    st.image(movie['poster_url'], use_container_width=True)
                else:
                    st.info("🎬 Affiche non disponible")
                
                st.caption(f"**{movie['title_x']}**")
                st.caption(f"⭐ {movie['averageRating']:.1f}/10")
                
                # Bouton pour plus d'infos (simulation)
                if st.button(f"▶️ Regarder", key=f"watch_{idx}"):
                    st.success(f"Lecture de '{movie['title_x']}' démarrée!")

    st.markdown("---")
    
    # Sélections par genre avec carrousel
    st.subheader("Sélections par genre")
    
    if not df_main.empty:
        # Extraire tous les genres uniques
        all_genres = []
        for genres_str in df_main['genres_x'].dropna():
            genres_list = str(genres_str).split(', ')
            all_genres.extend(genres_list)
        
        unique_genres = list(set(all_genres))
        popular_genres = sorted(unique_genres)[:6]  # Prendre les 6 premiers genres
        
        for genre in popular_genres:
            # Filtrer les films de ce genre
            genre_movies = df_main[df_main['genres_x'].str.contains(genre, na=False)]
            
            if len(genre_movies) > 0:
                emoji = get_emoji_for_genre(genre)
                
                # Titre de section aligné à gauche
                st.markdown(f"### {genre}")
                
                # Prendre les 24 meilleurs films de ce genre
                top_genre_movies = genre_movies.nlargest(24, 'averageRating')
                
                # Initialize session state for this genre
                if f"{genre}_page" not in st.session_state:
                    st.session_state[f"{genre}_page"] = 0
                
                movies_per_page = 6
                total_pages = len(top_genre_movies) // movies_per_page
                current_page = st.session_state[f"{genre}_page"]
                
                # Navigation avec boutons sur les côtés alignés au centre
                col_nav1, col_movies, col_nav2 = st.columns([1, 10, 1])
                
                with col_nav1:
                    # Espacement vertical de 60px
                    st.markdown('<div style="height: 60px;"></div>', unsafe_allow_html=True)
                    if current_page > 0:
                        if st.button("◀", key=f"prev_{genre}"):
                            st.session_state[f"{genre}_page"] -= 1
                            st.rerun()
                
                with col_nav2:
                    # Espacement vertical de 60px
                    st.markdown('<div style="height: 60px;"></div>', unsafe_allow_html=True)
                    if current_page < total_pages - 1:
                        if st.button("▶", key=f"next_{genre}"):
                            st.session_state[f"{genre}_page"] += 1
                            st.rerun()
                
                with col_movies:
                    # Afficher les films de la page courante
                    start_idx = current_page * movies_per_page
                    end_idx = min(start_idx + movies_per_page, len(top_genre_movies))
                    page_movies = top_genre_movies.iloc[start_idx:end_idx]
                    
                    cols = st.columns(6)
                    for idx, (_, movie) in enumerate(page_movies.iterrows()):
                        with cols[idx]:
                            if movie['poster_url']:
                                st.image(movie['poster_url'], use_container_width=True)
                            else:
                                st.info("🎬 Affiche non disponible")
                            
                            st.caption(f"**{movie['title_x']}**")
                            st.caption(f"⭐ {movie['averageRating']:.1f}/10")
                
                # Indicateur de page
                st.markdown(f"<div style='text-align: center; color: #666; margin: 10px 0;'>Page {current_page + 1} sur {total_pages}</div>", unsafe_allow_html=True)
                st.markdown("---")

# ================================
# PAGE CATALOGUE
# ================================
elif page == "🎬 Catalogue":
    st.title("🎬 Catalogue complet")
    
    if df_main.empty:
        st.error("Aucun film disponible.")
    else:
        # Filtres
        st.sidebar.subheader("🔍 Filtres")
        
        # Filtre par langue
        languages = df_main['original_language'].unique()
        selected_language = st.sidebar.selectbox("Langue", ['Toutes'] + list(languages))
        
        # Filtre par genre
        all_genres = []
        for genres_str in df_main['genres_x'].dropna():
            genres_list = str(genres_str).split(', ')
            all_genres.extend(genres_list)
        unique_genres = list(set(all_genres))
        selected_genre = st.sidebar.selectbox("Genre", ['Tous'] + sorted(unique_genres))
        
        # Filtre par année
        min_year = int(df_main['year'].min()) if not pd.isna(df_main['year'].min()) else 1900
        max_year = int(df_main['year'].max()) if not pd.isna(df_main['year'].max()) else 2024
        year_range = st.sidebar.slider("Années", min_year, max_year, (min_year, max_year))
        
        # Filtre par note
        rating_range = st.sidebar.slider("Note minimum", 0.0, 10.0, 0.0, 0.1)
        
        # Appliquer les filtres
        filtered_df = df_main.copy()
        
        if selected_language != 'Toutes':
            filtered_df = filtered_df[filtered_df['original_language'] == selected_language]
        
        if selected_genre != 'Tous':
            filtered_df = filtered_df[filtered_df['genres_x'].str.contains(selected_genre, na=False)]
        
        filtered_df = filtered_df[
            (filtered_df['year'] >= year_range[0]) & 
            (filtered_df['year'] <= year_range[1]) &
            (filtered_df['averageRating'] >= rating_range)
        ]
        
        # Affichage des résultats
        st.subheader(f"📊 {len(filtered_df)} films trouvés")
        
        if len(filtered_df) > 0:
            # Tri
            sort_options = {
                'Note (décroissant)': ('averageRating', False),
                'Note (croissant)': ('averageRating', True),
                'Année (récent d\'abord)': ('year', False),
                'Année (ancien d\'abord)': ('year', True),
                'Titre (A-Z)': ('title_x', True),
                'Titre (Z-A)': ('title_x', False)
            }
            
            sort_choice = st.selectbox("Trier par", list(sort_options.keys()))
            sort_column, ascending = sort_options[sort_choice]
            filtered_df = filtered_df.sort_values(sort_column, ascending=ascending)
            
            # Pagination
            movies_per_page = 24
            total_pages = (len(filtered_df) - 1) // movies_per_page + 1
            
            if total_pages > 1:
                page_num = st.selectbox("Page", range(1, total_pages + 1))
                start_idx = (page_num - 1) * movies_per_page
                end_idx = min(start_idx + movies_per_page, len(filtered_df))
                page_movies = filtered_df.iloc[start_idx:end_idx]
            else:
                page_movies = filtered_df
            
            # Affichage en grille
            cols_per_row = 6
            rows = len(page_movies) // cols_per_row + (1 if len(page_movies) % cols_per_row > 0 else 0)
            
            for row in range(rows):
                cols = st.columns(cols_per_row)
                start_idx = row * cols_per_row
                end_idx = min(start_idx + cols_per_row, len(page_movies))
                
                for col_idx, (_, movie) in enumerate(page_movies.iloc[start_idx:end_idx].iterrows()):
                    with cols[col_idx]:
                        if movie['poster_url']:
                            # Affichage avec zoom au clic
                            if st.button("🔍", key=f"zoom_{movie.name}"):
                                st.session_state[f"zoom_movie_{movie.name}"] = not st.session_state.get(f"zoom_movie_{movie.name}", False)
                            
                            if st.session_state.get(f"zoom_movie_{movie.name}", False):
                                # Mode zoom - affichage détaillé
                                st.image(movie['poster_url'], width=300)
                                st.markdown(f"**{movie['title_x']}**")
                                st.markdown(f"📅 {int(movie['year']) if pd.notna(movie['year']) else 'N/A'}")
                                st.markdown(f"⭐ {movie['averageRating']:.1f}/10")
                                st.markdown(f"⏱️ {int(movie['runtime'])}min")
                                st.markdown(f"🎭 {movie['genres_x']}")
                                with st.expander("📝 Description"):
                                    st.write(movie['description'])
                                if st.button("▶️ Regarder maintenant", key=f"play_{movie.name}"):
                                    st.success(f"Lecture de '{movie['title_x']}' démarrée!")
                                if st.button("❌ Fermer", key=f"close_{movie.name}"):
                                    st.session_state[f"zoom_movie_{movie.name}"] = False
                                    st.rerun()
                            else:
                                # Mode normal
                                st.image(movie['poster_url'], use_container_width=True)
                                st.caption(f"**{movie['title_x']}**")
                                st.caption(f"⭐ {movie['averageRating']:.1f}/10")
                        else:
                            st.info("🎬 Affiche non disponible")
                            st.caption(f"**{movie['title_x']}**")

# ================================
# PAGE RECHERCHE
# ================================
elif page == "🔍 Recherche":
    st.title("🔍 Recherche avancée")
    
    # Barre de recherche
    search_query = st.text_input("🔍 Rechercher un film", placeholder="Entrez le titre d'un film...")
    
    if search_query:
        # Recherche dans les titres
        search_results = df_main[
            df_main['title_x'].str.contains(search_query, case=False, na=False)
        ].nlargest(24, 'averageRating')
        
        if len(search_results) > 0:
            st.markdown(f"### 🎬 {len(search_results)} résultat(s) pour '{search_query}'")
            
            # Affichage des résultats
            cols_per_row = 6
            rows = len(search_results) // cols_per_row + (1 if len(search_results) % cols_per_row > 0 else 0)
            
            for row in range(rows):
                cols = st.columns(cols_per_row)
                start_idx = row * cols_per_row
                end_idx = min(start_idx + cols_per_row, len(search_results))
                
                for col_idx, (_, movie) in enumerate(search_results.iloc[start_idx:end_idx].iterrows()):
                    with cols[col_idx]:
                        if movie['poster_url']:
                            st.image(movie['poster_url'], use_container_width=True)
                        else:
                            st.info("🎬 Affiche non disponible")
                        
                        st.caption(f"**{movie['title_x']}**")
                        if pd.notna(movie['year']):
                            st.caption(f"📅 {int(movie['year'])}")
                        st.caption(f"⭐ {movie['averageRating']:.1f}/10")
        else:
            st.warning(f"Aucun film trouvé pour '{search_query}'")
    else:
        st.info("Entrez un titre de film pour commencer votre recherche.")

# ================================
# PAGE PROGRAMMATION TV
# ================================
elif page == "📺 Programmation TV":
    st.title("📺 Programmation TV CinéCreuse+")
    
    # Sélection de la date
    selected_date = st.date_input("📅 Sélectionner une date", datetime.now())
    
    # Génération de la programmation pour la date sélectionnée
    if not df_main.empty:
        # Sélectionner aléatoirement des films pour la programmation
        daily_movies = df_main.sample(min(10, len(df_main))).reset_index(drop=True)
        
        st.subheader(f"Programmation du {selected_date.strftime('%d/%m/%Y')}")
        
        # Créer des créneaux horaires
        time_slots = ["14:00", "16:30", "19:00", "21:30", "00:00"]
        
        for i, (_, movie) in enumerate(daily_movies.head(5).iterrows()):
            time_slot = time_slots[i]
            
            col1, col2, col3 = st.columns([1, 3, 1])
            
            with col1:
                st.markdown(f"### {time_slot}")
                emoji = get_emoji_for_genre(movie['genres_x'])
                st.markdown(f"## {emoji}")
            
            with col2:
                st.markdown(f"**{movie['title_x']}**")
                st.markdown(f"🎭 {movie['genres_x']}")
                st.markdown(f"⏱️ {int(movie['runtime'])}min | ⭐ {movie['averageRating']:.1f}/10")
                
                with st.expander("📝 Synopsis"):
                    st.write(movie['description'])
            
            with col3:
                if movie['poster_url']:
                    st.image(movie['poster_url'], width=150)
                
                if st.button(f"🔔 Rappel", key=f"reminder_{i}"):
                    st.success(f"Rappel programmé pour {movie['title_x']} à {time_slot}")
            
            st.markdown("---")

# ================================
# PAGE DASHBOARD ADMIN
# ================================
elif page == "📊 Dashboard Admin":
    st.title("📊 Dashboard Administrateur")
    
    # Vérification des données
    if df_main.empty:
        st.error("Aucune donnée disponible pour le dashboard.")
    else:
        # KPIs principaux
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📽️ Total Films", len(df_main))
        
        with col2:
            avg_rating = df_main['averageRating'].mean()
            st.metric("⭐ Note Moyenne", f"{avg_rating:.1f}")
        
        with col3:
            total_runtime = df_main['runtime'].sum() / 60  # en heures
            st.metric("⏱️ Heures Totales", f"{total_runtime:,.0f}h")
        
        with col4:
            avg_votes = df_main['numVotes'].mean()
            st.metric("👥 Votes Moyens", f"{avg_votes:,.0f}")
        
        st.markdown("---")
        
        # Graphiques analytiques
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribution des notes
            st.subheader("📊 Distribution des Notes")
            fig_rating = px.histogram(
                df_main, 
                x='averageRating', 
                nbins=20,
                title="Répartition des notes IMDb",
                color_discrete_sequence=['#1f77b4']
            )
            fig_rating.update_layout(
                xaxis_title="Note IMDb",
                yaxis_title="Nombre de films"
            )
            st.plotly_chart(fig_rating, use_container_width=True)
        
        with col2:
            # Films par langue
            st.subheader("🌍 Films par Langue")
            lang_counts = df_main['original_language'].value_counts()
            fig_lang = px.pie(
                values=lang_counts.values, 
                names=lang_counts.index,
                title="Répartition par langue originale"
            )
            st.plotly_chart(fig_lang, use_container_width=True)
        
        # Évolution temporelle
        st.subheader("📈 Films par Année")
        yearly_counts = df_main['year'].value_counts().sort_index()
        fig_yearly = px.line(
            x=yearly_counts.index, 
            y=yearly_counts.values,
            title="Nombre de films par année de sortie"
        )
        fig_yearly.update_layout(
            xaxis_title="Année",
            yaxis_title="Nombre de films"
        )
        st.plotly_chart(fig_yearly, use_container_width=True)
        
        # Top 10 des films les mieux notés
        st.subheader("🏆 Top 10 des Films les Mieux Notés")
        top_movies = df_main.nlargest(10, 'averageRating')
        top_movies.columns = ['Titre', 'Langue', 'Date de sortie', 'Année', 'Genres', 'Description', 'Poster Path', 'Poster URL', 'Durée (min)', 'Note IMDb', 'Nombre de votes', 'Synopsis']
        st.dataframe(
            top_movies[['Titre', 'Année', 'Genres', 'Durée (min)', 'Note IMDb', 'Nombre de votes']],
            use_container_width=True
        )

# ================================
# PAGE GESTION UTILISATEURS
# ================================
elif page == "👥 Gestion Utilisateurs":
    st.title("👥 Gestion des Utilisateurs")
    
    # Simulation de données utilisateurs
    users_df = load_users()
    
    # KPIs utilisateurs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👤 Utilisateurs Actifs", len(users_df))
    
    with col2:
        avg_age = users_df['age'].mean()
        st.metric("📊 Âge Moyen", f"{avg_age:.0f} ans")
    
    with col3:
        avg_movies = users_df['movies_watched'].mean()
        st.metric("🎬 Films/Utilisateur", f"{avg_movies:.1f}")
    
    with col4:
        popular_genre = users_df['genre_pref'].mode()[0]
        st.metric("🎭 Genre Populaire", popular_genre)
    
    st.markdown("---")
    
    # Graphiques utilisateurs
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribution des âges
        st.subheader("📊 Distribution des Âges")
        fig_age = px.histogram(
            users_df, 
            x='age', 
            nbins=15,
            title="Répartition par âge des utilisateurs"
        )
        st.plotly_chart(fig_age, use_container_width=True)
    
    with col2:
        # Préférences de genre
        st.subheader("🎭 Préférences de Genre")
        genre_counts = users_df['genre_pref'].value_counts()
        fig_genre = px.bar(
            x=genre_counts.index, 
            y=genre_counts.values,
            title="Genres préférés des utilisateurs"
        )
        st.plotly_chart(fig_genre, use_container_width=True)
    
    # Tableau des utilisateurs
    st.subheader("📋 Liste des Utilisateurs")
    
    # Filtres pour les utilisateurs
    col1, col2 = st.columns(2)
    with col1:
        age_filter = st.slider("Âge minimum", 18, 70, 18)
    with col2:
        genre_filter = st.selectbox("Genre préféré", ['Tous'] + list(users_df['genre_pref'].unique()))
    
    # Application des filtres
    filtered_users = users_df[users_df['age'] >= age_filter]
    if genre_filter != 'Tous':
        filtered_users = filtered_users[filtered_users['genre_pref'] == genre_filter]
    
    st.dataframe(filtered_users, use_container_width=True)
    
    # Actions en lot
    st.subheader("⚙️ Actions en Lot")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📧 Envoyer Newsletter"):
            st.success(f"Newsletter envoyée à {len(filtered_users)} utilisateurs!")
    
    with col2:
        if st.button("🎁 Offre Spéciale"):
            st.success(f"Offre spéciale envoyée à {len(filtered_users)} utilisateurs!")
    
    with col3:
        if st.button("📊 Rapport Détaillé"):
            st.info("Génération du rapport en cours...")

# ================================
# PAGE ANALYTIQUE AVANCÉE
# ================================
elif page == "🎯 Analytique Avancée":
    st.title("🎯 Analytique Avancée")
    
    if df_main.empty:
        st.error("Aucune donnée disponible pour l'analyse.")
    else:
        # Métriques de performance
        st.subheader("📈 Métriques de Performance")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Films les plus populaires (par nombre de votes)
            most_popular = df_main.nlargest(1, 'numVotes').iloc[0]
            st.metric(
                "🔥 Film le Plus Populaire", 
                most_popular['title_x'],
                f"{most_popular['numVotes']:,.0f} votes"
            )
        
        with col2:
            # Meilleur film (par note)
            best_rated = df_main.nlargest(1, 'averageRating').iloc[0]
            st.metric(
                "⭐ Meilleur Film", 
                best_rated['title_x'],
                f"{best_rated['averageRating']:.1f}/10"
            )
        
        with col3:
            # Film le plus long
            longest_movie = df_main.nlargest(1, 'runtime').iloc[0]
            st.metric(
                "⏱️ Film le Plus Long", 
                longest_movie['title_x'],
                f"{longest_movie['runtime']:.0f} min"
            )
        
        st.markdown("---")
        
        # Analyses détaillées
        col1, col2 = st.columns(2)
        
        with col1:
            # Corrélation durée vs note
            st.subheader("📊 Durée vs Note")
            fig_scatter = px.scatter(
                df_main.sample(min(500, len(df_main))), 
                x='runtime', 
                y='averageRating',
                hover_data=['title_x'],
                title="Relation entre durée et note IMDb"
            )
            fig_scatter.update_layout(
                xaxis_title="Durée (minutes)",
                yaxis_title="Note IMDb"
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        with col2:
            # Box plot des notes par décennie
            st.subheader("📦 Notes par Décennie")
            df_decade = df_main.copy()
            df_decade['decade'] = (df_decade['year'] // 10) * 10
            
            fig_box = px.box(
                df_decade, 
                x='decade', 
                y='averageRating',
                title="Distribution des notes par décennie"
            )
            fig_box.update_layout(
                xaxis_title="Décennie",
                yaxis_title="Note IMDb"
            )
            st.plotly_chart(fig_box, use_container_width=True)
        
        # Analyse des genres
        st.subheader("🎭 Analyse Détaillée des Genres")
        
        # Extraire et analyser les genres
        all_genres = []
        for genres_str in df_main['genres_x'].dropna():
            genres_list = str(genres_str).split(', ')
            all_genres.extend(genres_list)
        
        genre_stats = pd.DataFrame({
            'genre': all_genres
        })
        
        genre_counts = genre_stats['genre'].value_counts().head(10)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top genres par nombre de films
            fig_genre_count = px.bar(
                x=genre_counts.values,
                y=genre_counts.index,
                orientation='h',
                title="Top 10 des genres par nombre de films"
            )
            fig_genre_count.update_layout(
                xaxis_title="Nombre de films",
                yaxis_title="Genre"
            )
            st.plotly_chart(fig_genre_count, use_container_width=True)
        
        with col2:
            # Qualité moyenne par genre
            genre_quality = {}
            for genre in genre_counts.index:
                genre_movies = df_main[df_main['genres_x'].str.contains(genre, na=False)]
                if len(genre_movies) > 0:
                    genre_quality[genre] = genre_movies['averageRating'].mean()
            
            quality_df = pd.DataFrame(list(genre_quality.items()), columns=['Genre', 'Note_Moyenne'])
            quality_df = quality_df.sort_values('Note_Moyenne', ascending=True)
            
            fig_quality = px.bar(
                quality_df,
                x='Note_Moyenne',
                y='Genre',
                orientation='h',
                title="Note moyenne par genre"
            )
            fig_quality.update_layout(
                xaxis_title="Note moyenne IMDb",
                yaxis_title="Genre"
            )
            st.plotly_chart(fig_quality, use_container_width=True)
        
        # Recommandations basées sur les données
        st.subheader("💡 Recommandations Stratégiques")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("""
            **📈 Opportunités de Croissance:**
            - Les films d'action et de comédie sont les plus populaires
            - Focus sur les productions 2000-2020 pour l'engagement
            - Les films de 90-120min ont les meilleures notes
            """)
        
        with col2:
            st.warning("""
            **⚠️ Points d'Attention:**
            - Diversifier le catalogue avec plus de documentaires
            - Améliorer la qualité des films récents (post-2020)
            - Équilibrer le contenu français/anglais
            """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    © 2024 CinéCreuse+ | Votre plateforme de streaming premium
</div>
""", unsafe_allow_html=True)