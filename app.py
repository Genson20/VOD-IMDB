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
        
        # 11. Ajouter des emojis pour la compatibilité avec l'interface existante
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
        
        df['affiche'] = df['genres_x'].apply(get_emoji_for_genre)
        
        return df
        
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {e}")
        return pd.DataFrame()

# Fonction pour générer les horaires de séances
@st.cache_data
def generate_showtimes():
    random.seed(42)
    showtimes = {}
    today = datetime.now()
    
    # Horaires disponibles
    time_slots = ["14:00", "17:00", "20:00", "22:00"]
    
    # Pour chaque film actuellement disponible (on prend les 8 premiers)
    current_movies = df_main.head(8)
    
    for _, movie in current_movies.iterrows():
        movie_showtimes = {}
        
        # Générer les horaires pour les 7 prochains jours
        for i in range(7):
            date = today + timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            
            # Chaque film a 2-3 séances par jour
            num_sessions = random.randint(2, 3)
            selected_times = random.sample(time_slots, num_sessions)
            movie_showtimes[date_str] = sorted(selected_times)
        
        showtimes[movie['title_x']] = movie_showtimes
    
    return showtimes

# Fonction pour générer les films à venir
@st.cache_data
def generate_upcoming_movies():
    upcoming = []
    today = datetime.now()
    
    # Créer quelques films fictifs à venir dans les prochaines semaines
    upcoming_titles = [
        {
            "title_x": "Avatar 3: The Seed of Eywa",
            "overview": "Jake Sully et sa famille continuent leur aventure sur Pandora avec de nouveaux défis et des territoires inexplorés.",
            "release_date": today + timedelta(days=15),
            "poster_url": "🌊"
        },
        {
            "title_x": "Mission Impossible 8",
            "overview": "Ethan Hunt revient pour une mission encore plus périlleuse qui le mènera aux quatre coins du globe.",
            "release_date": today + timedelta(days=22),
            "poster_url": "🎯"
        },
        {
            "title_x": "Dune: Partie Trois",
            "overview": "Paul Atreides poursuit son voyage épique à travers l'univers de Dune dans cette conclusion spectaculaire.",
            "release_date": today + timedelta(days=28),
            "poster_url": "🏜️"
        },
        {
            "title_x": "Spider-Man: New Dimensions",
            "overview": "Miles Morales explore de nouvelles dimensions dans cette aventure animée révolutionnaire.",
            "release_date": today + timedelta(days=35),
            "poster_url": "🕷️"
        },
        {
            "title_x": "Fast & Furious 11",
            "overview": "Dom et sa famille reviennent pour une dernière course contre la montre dans cet ultime chapitre.",
            "release_date": today + timedelta(days=42),
            "poster_url": "🏎️"
        }
    ]
    
    return pd.DataFrame(upcoming_titles)

# Base de données fictive des utilisateurs
@st.cache_data
def load_users():
    random.seed(42)  # Pour avoir des données reproductibles
    np.random.seed(42)
    
    users = []
    genres = ["Action", "Comédie", "Drame", "Romance", "Science-Fiction", "Thriller", "Fantasy", "Animation", "Biographie", "Crime"]
    
    # Date de référence : aujourd'hui
    today = datetime.now()
    
    for i in range(500):
        # Date d'inscription (entre 365 jours et aujourd'hui)
        days_ago = random.randint(1, 365)
        date_inscription = today - timedelta(days=days_ago)
        
        # Dernière connexion (entre date inscription et aujourd'hui)
        max_days_since_signup = (today - date_inscription).days
        days_since_last_login = random.randint(0, min(max_days_since_signup, 30))
        derniere_connexion = today - timedelta(days=days_since_last_login)
        
        # Générer des données cohérentes
        nombre_sessions = random.randint(1, 50)
        films_consultes_total = random.randint(5, 200)
        films_favoris = random.randint(0, min(films_consultes_total // 3, 25))
        temps_total_passe = random.randint(30, 1200)  # en minutes
        preferences_genre = random.choice(genres)
        
        users.append({
            "user_id": f"USER_{i+1:04d}",
            "date_inscription": date_inscription,
            "derniere_connexion": derniere_connexion,
            "nombre_sessions": nombre_sessions,
            "films_consultes_total": films_consultes_total,
            "films_favoris": films_favoris,
            "temps_total_passe": temps_total_passe,
            "preferences_genre": preferences_genre
        })
    
    df = pd.DataFrame(users)
    df['date_inscription'] = pd.to_datetime(df['date_inscription'])
    df['derniere_connexion'] = pd.to_datetime(df['derniere_connexion'])
    return df

# Initialisation des données
df_main = load_movies()
df_users = load_users()
showtimes_data = generate_showtimes()
upcoming_movies = generate_upcoming_movies()

# Sidebar Navigation
st.sidebar.title("🎬 CinéCreuse+")
page = st.sidebar.selectbox(
    "Navigation",
    ["🏠 Accueil", "🎯 Recommandations", "🎬 Programme", "👥 Administration", "🧹 Base nettoyée"]
)

# ================================
# PAGE ACCUEIL
# ================================
if page == "🏠 Accueil":
    st.title("🎬 CinéCreuse+")
    st.markdown("🎬 Bienvenue sur CinéCreuse+ ! Découvrez les films à l'affiche classés par genre.")
    st.markdown("---")
    
    # Affichage par genre dynamique
    st.subheader("🎭 Catalogue par genres")
    
    # Extraction des genres uniques
    all_genres = []
    for genres_str in df_main['genres_x'].dropna():
        if isinstance(genres_str, str):
            genres = [g.strip() for g in genres_str.split(',')]
            all_genres.extend(genres)
    
    # Compter les occurrences de chaque genre
    genre_counts = {}
    for genre in all_genres:
        if genre in genre_counts:
            genre_counts[genre] += 1
        else:
            genre_counts[genre] = 1
    
    # Trier par popularité et prendre les top genres
    sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
    top_genres = [genre for genre, count in sorted_genres[:8]]
    
    # Genres prioritaires (assurer qu'ils sont inclus)
    priority_genres = ['Action', 'Drama', 'Comedy', 'Thriller', 'Romance', 'Crime', 'Adventure', 'Animation']
    
    # Créer la liste finale des genres
    final_genres = []
    for genre in priority_genres:
        if genre in [g for g, c in sorted_genres]:
            final_genres.append(genre)
    
    # Ajouter d'autres genres populaires si nécessaire
    for genre in top_genres:
        if genre not in final_genres:
            final_genres.append(genre)
    
    # Limiter à 10 genres maximum
    final_genres = final_genres[:10]
    
    # CSS pour les effets hover
    st.markdown("""
    <style>
    .movie-hover {
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border-radius: 8px;
    }
    .movie-hover:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 25px rgba(229,9,20,0.4);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Afficher chaque section de genre avec navigation horizontale
    for genre in final_genres:
        # Filtrer les films par genre
        genre_movies = df_main[df_main["genres_x"].str.contains(genre, case=False, na=False)]
        
        # Trier par note et prendre les 15 meilleurs
        genre_movies = genre_movies.nlargest(15, 'averageRating')
        
        if len(genre_movies) > 0:
            st.markdown(f"### 🎭 {genre}")
            
            # Interface de pagination pour naviguer dans les 15 films
            if 'current_page' not in st.session_state:
                st.session_state.current_page = {}
            if genre not in st.session_state.current_page:
                st.session_state.current_page[genre] = 0
            
            # Calculer le nombre de pages (6 films par page)
            films_per_page = 6
            total_pages = (len(genre_movies) - 1) // films_per_page + 1
            current_page = st.session_state.current_page[genre]
            
            # Navigation
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                if st.button("⬅️ Précédent", key=f"prev_{genre}", disabled=current_page == 0):
                    st.session_state.current_page[genre] = max(0, current_page - 1)
                    st.rerun()
            with col2:
                st.write(f"Page {current_page + 1} sur {total_pages}")
            with col3:
                if st.button("Suivant ➡️", key=f"next_{genre}", disabled=current_page == total_pages - 1):
                    st.session_state.current_page[genre] = min(total_pages - 1, current_page + 1)
                    st.rerun()
            
            # Afficher les films de la page actuelle
            start_idx = current_page * films_per_page
            end_idx = min(start_idx + films_per_page, len(genre_movies))
            page_movies = genre_movies.iloc[start_idx:end_idx]
            
            # Affichage en colonnes avec effets hover
            cols = st.columns(min(len(page_movies), 6))
            
            for idx, (_, movie) in enumerate(page_movies.iterrows()):
                with cols[idx]:
                    # Container avec effet hover
                    with st.container():
                        # Affiche du film avec classe CSS hover
                        if 'poster_url' in movie and pd.notna(movie['poster_url']):
                            st.markdown(f'<div class="movie-hover">', unsafe_allow_html=True)
                            st.image(movie['poster_url'], width=150, use_container_width=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Titre du film
                        st.markdown(f"**{movie['title_x']}**")
                        
                        # Note
                        st.write(f"⭐ {movie['averageRating']:.1f}/10")
            
            st.markdown("---")
    
    # Section films populaires en fin de page
    st.subheader("🔥 Les plus populaires")
    popular_movies = df_main.nlargest(6, 'numVotes')
    
    cols = st.columns(6)
    for idx, (_, movie) in enumerate(popular_movies.iterrows()):
        with cols[idx]:
            # Afficher l'image TMDB réelle au lieu de l'emoji
            if 'poster_url' in movie and pd.notna(movie['poster_url']):
                st.image(movie['poster_url'], width=100)
            else:
                st.markdown(f"<div style='text-align: center; font-size: 2.5em;'>{movie['affiche']}</div>", 
                          unsafe_allow_html=True)
            st.markdown(f"**{movie['title_x']}**")
            st.write(f"⭐ {movie['averageRating']}/10")
            st.write(f"👥 {movie['numVotes']:,} votes")
    
    # Barre de recherche
    search_query = st.text_input("🔍 Rechercher un film", placeholder="Tapez le nom d'un film...")
    
    # Si une recherche est effectuée, afficher les résultats de recherche
    if search_query:
        st.subheader(f"🔍 Résultats de recherche pour '{search_query}'")
        
        # Filtrer par recherche
        search_results = df_main[df_main["title_x"].str.contains(search_query, case=False, na=False)]
        
        if len(search_results) == 0:
            st.warning("Aucun film trouvé.")
        else:
            # Affichage des résultats en grille
            cols_per_row = 3
            rows = len(search_results) // cols_per_row + (1 if len(search_results) % cols_per_row > 0 else 0)
            
            for row in range(rows):
                cols = st.columns(cols_per_row)
                for col_idx in range(cols_per_row):
                    movie_idx = row * cols_per_row + col_idx
                    if movie_idx < len(search_results):
                        movie = search_results.iloc[movie_idx]
                        
                        with cols[col_idx]:
                            with st.container():
                                st.markdown(f"### {movie['affiche']} {movie['title_x']}")
                                st.write(f"**Genre:** {movie['genres_x']}")
                                st.write(f"**Note:** {movie['averageRating']}/10 ⭐")
                                st.write(f"**Description:** {movie['description']}")
                                st.markdown("---")
    
    else:
        # Affichage style Netflix par genre
        
        # Extraire tous les genres et compter leur fréquence
        all_genres = []
        for genres_str in df_main["genres_x"]:
            if pd.notna(genres_str):
                all_genres.extend(genres_str.split("|"))
        
        # Compter les genres et prendre les 10 plus populaires
        genre_counts = pd.Series(all_genres).value_counts()
        top_genres = genre_counts.head(10).index.tolist()
        
        # Priorité spéciale pour certains genres populaires
        priority_genres = ["Action", "Comédie", "Drame", "Thriller", "Romance", "Science-Fiction"]
        final_genres = []
        
        # Ajouter d'abord les genres prioritaires s'ils existent
        for genre in priority_genres:
            if genre in top_genres:
                final_genres.append(genre)
        
        # Ajouter les autres genres populaires
        for genre in top_genres:
            if genre not in final_genres:
                final_genres.append(genre)
        
        # Limiter à 10 genres maximum
        final_genres = final_genres[:10]
        
        # CSS pour les effets hover
        st.markdown("""
        <style>
        .movie-hover {
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border-radius: 8px;
        }
        .movie-hover:hover {
            transform: scale(1.05);
            box-shadow: 0 8px 25px rgba(229,9,20,0.4);
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Afficher chaque section de genre avec navigation horizontale
        for genre in final_genres:
            # Filtrer les films par genre
            genre_movies = df_main[df_main["genres_x"].str.contains(genre, case=False, na=False)]
            
            # Trier par note et prendre les 15 meilleurs
            genre_movies = genre_movies.nlargest(15, 'averageRating')
            
            if len(genre_movies) > 0:
                st.markdown(f"### 🎭 {genre}")
                
                # Interface de pagination pour naviguer dans les 15 films
                if 'current_page' not in st.session_state:
                    st.session_state.current_page = {}
                if genre not in st.session_state.current_page:
                    st.session_state.current_page[genre] = 0
                
                # Calculer le nombre de pages (6 films par page)
                films_per_page = 6
                total_pages = (len(genre_movies) - 1) // films_per_page + 1
                current_page = st.session_state.current_page[genre]
                
                # Navigation
                col1, col2, col3 = st.columns([1, 2, 1])
                with col1:
                    if st.button("⬅️ Précédent", key=f"prev_{genre}", disabled=current_page == 0):
                        st.session_state.current_page[genre] = max(0, current_page - 1)
                        st.rerun()
                with col2:
                    st.write(f"Page {current_page + 1} sur {total_pages}")
                with col3:
                    if st.button("Suivant ➡️", key=f"next_{genre}", disabled=current_page == total_pages - 1):
                        st.session_state.current_page[genre] = min(total_pages - 1, current_page + 1)
                        st.rerun()
                
                # Afficher les films de la page actuelle
                start_idx = current_page * films_per_page
                end_idx = min(start_idx + films_per_page, len(genre_movies))
                page_movies = genre_movies.iloc[start_idx:end_idx]
                
                # Affichage en colonnes avec effets hover
                cols = st.columns(min(len(page_movies), 6))
                
                for idx, (_, movie) in enumerate(page_movies.iterrows()):
                    with cols[idx]:
                        # Container avec effet hover
                        with st.container():
                            # Affiche du film avec classe CSS hover
                            if 'poster_url' in movie and pd.notna(movie['poster_url']):
                                st.markdown(f'<div class="movie-hover">', unsafe_allow_html=True)
                                st.image(movie['poster_url'], width=150, use_column_width=True)
                                st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Titre du film
                            st.markdown(f"**{movie['title_x']}**")
                            
                            # Note
                            st.write(f"⭐ {movie['averageRating']:.1f}/10")
                
                st.markdown("---")
        
        # Section films populaires en fin de page
        st.subheader("🔥 Les plus populaires")
        popular_movies = df_main.nlargest(6, 'numVotes')
        
        cols = st.columns(6)
        for idx, (_, movie) in enumerate(popular_movies.iterrows()):
            with cols[idx]:
                # Afficher l'image TMDB réelle au lieu de l'emoji
                if 'poster_url' in movie and pd.notna(movie['poster_url']):
                    st.image(movie['poster_url'], width=100)
                else:
                    st.markdown(f"<div style='text-align: center; font-size: 2.5em;'>{movie['affiche']}</div>", 
                              unsafe_allow_html=True)
                st.markdown(f"**{movie['title_x']}**")
                st.write(f"⭐ {movie['averageRating']}/10")
                st.write(f"👥 {movie['numVotes']:,} votes")

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
# PAGE PROGRAMME
# ================================
elif page == "🎬 Programme":
    st.title("🎬 Programme des séances")
    st.markdown("---")
    
    # ========================================
    # SECTION 1: FILMS ACTUELLEMENT À L'AFFICHE
    # ========================================
    st.header("🎭 Films actuellement à l'affiche")
    
    # Filtre par jour
    today = datetime.now()
    date_options = []
    date_labels = []
    
    for i in range(7):
        date = today + timedelta(days=i)
        date_options.append(date.strftime("%Y-%m-%d"))
        if i == 0:
            date_labels.append(f"Aujourd'hui ({date.strftime('%d/%m')})")
        elif i == 1:
            date_labels.append(f"Demain ({date.strftime('%d/%m')})")
        else:
            date_labels.append(date.strftime("%A %d/%m"))
    
    # Sélecteur de jour
    selected_date_index = st.selectbox(
        "Choisir un jour:",
        range(len(date_labels)),
        format_func=lambda x: date_labels[x]
    )
    selected_date = date_options[selected_date_index]
    
    st.subheader(f"📅 Séances du {date_labels[selected_date_index]}")
    
    # Afficher les films actuellement à l'affiche avec leurs horaires
    current_movies = df_main.head(8)  # 8 films à l'affiche
    
    # Affichage en grille de 2 colonnes
    for i in range(0, len(current_movies), 2):
        cols = st.columns(2)
        
        for col_idx, col in enumerate(cols):
            movie_idx = i + col_idx
            if movie_idx < len(current_movies):
                movie = current_movies.iloc[movie_idx]
                
                with col:
                    with st.container():
                        # En-tête du film
                        st.markdown(f"### {movie['affiche']} {movie['title_x']}")
                        
                        # Informations du film
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"**Genre:** {movie['genres_x']}")
                            st.write(f"**Durée:** {movie['runtime']} min")
                            st.write(f"**Note:** {movie['averageRating']}/10 ⭐")
                            st.write(f"**Résumé:** {movie['description']}")
                        
                        with col2:
                            # Affichage de l'affiche (image TMDB réelle)
                            if 'poster_url' in movie and pd.notna(movie['poster_url']):
                                st.image(movie['poster_url'], width=120)
                            else:
                                st.markdown(f"<div style='text-align: center; font-size: 4em;'>{movie['affiche']}</div>", 
                                          unsafe_allow_html=True)
                        
                        # Horaires pour le jour sélectionné
                        if movie['title_x'] in showtimes_data and selected_date in showtimes_data[movie['title_x']]:
                            horaires = showtimes_data[movie['title_x']][selected_date]
                            st.write("**🕐 Horaires:**")
                            
                            # Afficher les horaires en ligne
                            horaires_html = " ".join([f"<span style='background-color: #ff6b6b; color: white; padding: 5px 10px; border-radius: 15px; margin: 2px; display: inline-block;'>{h}</span>" for h in horaires])
                            st.markdown(horaires_html, unsafe_allow_html=True)
                        else:
                            st.write("**🕐 Horaires:** Aucune séance ce jour")
                        
                        st.markdown("---")
    
    st.markdown("---")
    
    # ========================================
    # SECTION 2: FILMS À VENIR
    # ========================================
    st.header("🎟️ Films à venir ce mois")
    
    # Filtre par période
    filter_period = st.selectbox(
        "Filtrer par période:",
        ["Tous les films à venir", "Cette semaine", "Ces 2 prochaines semaines", "Ce mois"]
    )
    
    # Appliquer le filtre
    filtered_upcoming = upcoming_movies.copy()
    
    if filter_period == "Cette semaine":
        week_limit = today + timedelta(days=7)
        filtered_upcoming = filtered_upcoming[filtered_upcoming['release_date'] <= week_limit]
    elif filter_period == "Ces 2 prochaines semaines":
        two_weeks_limit = today + timedelta(days=14)
        filtered_upcoming = filtered_upcoming[filtered_upcoming['release_date'] <= two_weeks_limit]
    elif filter_period == "Ce mois":
        month_limit = today + timedelta(days=30)
        filtered_upcoming = filtered_upcoming[filtered_upcoming['release_date'] <= month_limit]
    
    if len(filtered_upcoming) == 0:
        st.info("Aucun film à venir pour la période sélectionnée.")
    else:
        # Afficher les films à venir
        for _, movie in filtered_upcoming.iterrows():
            with st.container():
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    # Affiche (emoji)
                    st.markdown(f"<div style='text-align: center; font-size: 5em;'>{movie['poster_url']}</div>", 
                              unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"### {movie['title_x']}")
                    
                    # Date de sortie
                    release_date = movie['release_date']
                    days_until_release = (release_date - today).days
                    
                    if days_until_release == 0:
                        date_text = "Sortie aujourd'hui !"
                    elif days_until_release == 1:
                        date_text = "Sortie demain !"
                    else:
                        date_text = f"Sortie dans {days_until_release} jours"
                    
                    st.write(f"**📅 Date de sortie:** {release_date.strftime('%d/%m/%Y')} ({date_text})")
                    st.write(f"**📖 Aperçu:** {movie['overview']}")
                    
                    # Bouton de notification (fictif)
                    if st.button(f"🔔 Me notifier", key=f"notify_{movie['title_x']}"):
                        st.success(f"Vous serez notifié lors de la sortie de '{movie['title_x']}'!")
                
                st.markdown("---")
    
    # Section bonus: Statistiques des séances
    st.markdown("---")
    st.header("📊 Statistiques des séances")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_shows_today = sum(len(showtimes_data[movie][selected_date]) 
                               for movie in showtimes_data 
                               if selected_date in showtimes_data[movie])
        st.metric("🎬 Séances aujourd'hui", total_shows_today)
    
    with col2:
        st.metric("🎭 Films à l'affiche", len(current_movies))
    
    with col3:
        st.metric("🎟️ Films à venir", len(upcoming_movies))

# ================================
# PAGE BASE NETTOYÉE
# ================================
elif page == "🧹 Base nettoyée":
    st.title("🧹 Base de données nettoyée")
    st.markdown("---")
    
    # Afficher les statistiques de nettoyage
    st.subheader("📊 Statistiques après nettoyage")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎬 Films total", len(df_main))
    
    with col2:
        languages_count = df_main['original_language'].nunique()
        st.metric("🌍 Langues", languages_count)
    
    with col3:
        avg_rating = df_main['averageRating'].mean()
        st.metric("⭐ Note moyenne", f"{avg_rating:.1f}/10")
    
    with col4:
        films_with_posters = len(df_main[df_main['poster_url'].notna()])
        st.metric("🖼️ Films avec affiches", films_with_posters)
    
    st.markdown("---")
    
    # Afficher 10 films avec leurs vraies affiches
    st.subheader("🎬 Aperçu - 10 films avec affiches réelles TMDB")
    
    # Prendre les 10 films les mieux notés
    top_10_movies = df_main.nlargest(10, 'averageRating')
    
    # Afficher en grille de 5 colonnes sur 2 rangées
    for row in range(2):
        cols = st.columns(5)
        for col_idx in range(5):
            movie_idx = row * 5 + col_idx
            if movie_idx < len(top_10_movies):
                movie = top_10_movies.iloc[movie_idx]
                
                with cols[col_idx]:
                    # Afficher l'affiche réelle
                    if pd.notna(movie['poster_url']):
                        st.image(movie['poster_url'], width=150)
                    else:
                        st.write("🎬 Pas d'affiche")
                    
                    # Titre
                    st.markdown(f"**{movie['title_x']}**")
                    
                    # Note
                    st.write(f"⭐ {movie['averageRating']}/10")
                    
                    # Genre
                    genre_short = movie['genres_x'][:20] + "..." if len(str(movie['genres_x'])) > 20 else movie['genres_x']
                    st.write(f"🎭 {genre_short}")
                    
                    # Année
                    st.write(f"📅 {movie['year']}")
    
    st.markdown("---")
    
    # Détails techniques du nettoyage
    st.subheader("🔧 Détails du nettoyage effectué")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **✅ Nettoyage réalisé:**
        - Langues ISO valides uniquement
        - Suppression des doublons (titre + année + durée)
        - Films avec affiches TMDB valides seulement
        - URLs d'affiches construites automatiquement
        - Colonnes inutiles supprimées
        """)
    
    with col2:
        st.markdown("""
        **📋 Colonnes conservées:**
        - title_x (titre)
        - original_language (langue)
        - release_date / year (date/année)
        - genres_x (genres)
        - overview/description (résumé)
        - poster_url (URL affiche TMDB)
        - runtime, averageRating, numVotes
        """)
    
    # Exemple d'affiche avec URL
    if len(df_main) > 0:
        sample_movie = df_main.iloc[0]
        st.markdown("---")
        st.subheader("🔗 Exemple d'URL d'affiche générée")
        st.code(sample_movie['poster_url'])
        
        # Afficher quelques échantillons de données
        st.subheader("📋 Échantillon de données nettoyées")
        sample_data = df_main[['title_x', 'genres_x', 'averageRating', 'runtime', 'original_language']].head(5)
        st.dataframe(sample_data, use_container_width=True)

# ================================
# PAGE ADMINISTRATION
# ================================
elif page == "👥 Administration":
    st.title("👥 Tableau de bord Administrateur")
    st.markdown("---")
    
    # ========================================
    # SECTION KPI UTILISATEURS
    # ========================================
    st.header("👥 KPI Utilisateurs")
    
    # Calculs des KPI utilisateurs
    today = datetime.now()
    seven_days_ago = today - timedelta(days=7)
    thirty_days_ago = today - timedelta(days=30)
    
    # KPI principaux utilisateurs
    total_users = len(df_users)
    new_users_7d = len(df_users[df_users['date_inscription'] >= seven_days_ago])
    avg_sessions = df_users['nombre_sessions'].mean()
    avg_time_spent = df_users['temps_total_passe'].mean()
    most_popular_genre = df_users['preferences_genre'].mode().iloc[0]
    active_users_7d = len(df_users[df_users['derniere_connexion'] >= seven_days_ago])
    activity_rate = (active_users_7d / total_users) * 100
    
    # Affichage des KPI utilisateurs en deux colonnes
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Métriques Principales")
        
        st.metric(
            label="👥 Nombre total de clients inscrits",
            value=f"{total_users:,}"
        )
        
        st.metric(
            label="🆕 Nouveaux inscrits (7 derniers jours)",
            value=f"{new_users_7d:,}",
            delta=f"+{new_users_7d} cette semaine"
        )
        
        st.metric(
            label="🔄 Nombre moyen de sessions par utilisateur",
            value=f"{avg_sessions:.1f}"
        )
        
        st.metric(
            label="⏰ Temps moyen passé sur l'app",
            value=f"{avg_time_spent:.0f} min"
        )
    
    with col2:
        st.subheader("📈 Activité & Engagement")
        
        st.metric(
            label="🎭 Genre préféré global",
            value=most_popular_genre
        )
        
        st.metric(
            label="✅ Utilisateurs actifs (7 derniers jours)",
            value=f"{active_users_7d:,}"
        )
        
        st.metric(
            label="📊 Taux d'activité",
            value=f"{activity_rate:.1f}%"
        )
        
        # Statistique supplémentaire
        avg_favorites = df_users['films_favoris'].mean()
        st.metric(
            label="⭐ Films favoris moyens par utilisateur",
            value=f"{avg_favorites:.1f}"
        )
    
    # Graphiques utilisateurs
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📅 Évolution des inscriptions (30 jours)")
        
        # Créer les données pour le graphique d'évolution
        last_30_days = pd.date_range(start=thirty_days_ago, end=today, freq='D')
        daily_signups = []
        
        for day in last_30_days:
            count = len(df_users[df_users['date_inscription'].dt.date == day.date()])
            daily_signups.append(count)
        
        signup_data = pd.DataFrame({
            'Date': last_30_days,
            'Nouvelles inscriptions': daily_signups
        })
        
        # Utiliser bar_chart au lieu de line_chart pour éviter les erreurs
        st.bar_chart(signup_data.set_index('Date'))
    
    with col2:
        st.subheader("🎭 Préférences de genre")
        
        genre_preferences = df_users['preferences_genre'].value_counts()
        
        fig_prefs = px.pie(
            values=genre_preferences.values,
            names=genre_preferences.index,
            title="Préférences de genre des utilisateurs"
        )
        fig_prefs.update_layout(height=400)
        st.plotly_chart(fig_prefs, use_container_width=True)
    
    # Tableau des utilisateurs les plus actifs
    st.subheader("🏆 Top 10 des utilisateurs les plus actifs")
    
    top_users = df_users.nlargest(10, 'nombre_sessions')[
        ['user_id', 'nombre_sessions', 'films_consultes_total', 'temps_total_passe', 'preferences_genre']
    ].round(2)
    top_users.columns = ['ID Utilisateur', 'Sessions', 'Films consultés', 'Temps total (min)', 'Genre préféré']
    st.dataframe(top_users, use_container_width=True)
    
    st.markdown("---")
    
    # ========================================
    # SECTION KPI FILMS
    # ========================================
    st.header("🎬 KPI Films")
    
    # Calcul des KPI films
    total_films = len(df_main)
    avg_rating = df_main['averageRating'].mean()
    avg_runtime = df_main['runtime'].mean()
    pct_french = (df_main['original_language'] == 'fr').sum() / total_films * 100
    
    # Affichage des KPI films en quatre colonnes
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
    
    # Graphiques films
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
    
    # Graphiques films en pleine largeur
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
        # Répartition par langue
        st.subheader("🌍 Répartition par langue")
        language_map = {"fr": "Français", "en": "Anglais", "es": "Espagnol", "ko": "Coréen", "ja": "Japonais"}
        lang_counts = df_main["original_language"].value_counts()
        
        # Créer le graphique avec les noms de langues traduits
        lang_names = [language_map.get(lang, lang) for lang in lang_counts.index]
        
        fig_langs = px.bar(
            x=lang_counts.values,
            y=lang_names,
            orientation='h',
            title="Nombre de films par langue",
            labels={'x': 'Nombre de films', 'y': 'Langue'}
        )
        fig_langs.update_layout(height=500)
        st.plotly_chart(fig_langs, use_container_width=True)
    
    # Tableau des films les mieux notés
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
