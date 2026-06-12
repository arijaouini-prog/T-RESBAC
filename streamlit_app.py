import streamlit as st
import sqlite3
import os
import pandas as pd

# 1. Configuration de la page principale
st.set_page_config(
    page_title="BARCA-DB Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS épuré : Palette Bleu-Vert Professionnelle
st.markdown("""
<style>
    /* Fond de page rafraîchissant */
    .main { background-color: #f8fafc; }
    
    /* Boîtes de statistiques (Bleu/Vert clair) */
    .stMetric { 
        background-color: #eefdfa; 
        padding: 20px; 
        border-radius: 12px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        border: 1px solid #ccf2ec;
        border-left: 5px solid #009688; /* Ligne de style Vert/Teal */
    }
    
    /* En-tête principal */
    .header-container {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        border: 1px solid #e2e8f0;
        margin-bottom: 25px;
    }
    
    .header-title { color: #0f172a; font-size: 28px; font-weight: 700; margin: 0; }
    .header-subtitle { color: #009688; font-size: 18px; font-weight: 500; margin-top: 5px; }
</style>
""", unsafe_allow_html=True)

DB_NAME = 'FINALEE.db'

if not os.path.exists(DB_NAME):
    st.error(f"⚠️ Le fichier de base de données '{DB_NAME}' est introuvable.")
else:
    # Connexion Base de données
    conn = sqlite3.connect(DB_NAME)
    query = """
    SELECT b.id_bacterie as 'ID', 
           b.Organism_Group as 'Souche', 
           b.Location as 'Région', 
           r.WGS_predicted_phenotype as 'Taux Rés.',
           r.Antimicrobial as 'Antibiotique'
    FROM BACTERIES b
    JOIN RESISTANCES r ON b.id_bacterie = r.id_bacterie;
    """
    
    try:
        df = pd.read_sql_query(query, conn)
        
        # ==========================================
        # 2. EN-TÊTE ÉPURÉ (Titre, Drapeau & Carte)
        # ==========================================
        with st.container():
            # Séparation en 2 colonnes : Titre à gauche (80%), Carte/Drapeau à droite (20%)
            col_txt, col_map = st.columns([4, 1])
            
            with col_txt:
                st.markdown('<p class="header-title">BARCA-DB : Observatoire de la Résistance aux Antimicrobiens</p>', unsafe_allow_html=True)
                st.markdown('<p class="header-subtitle">📍 Tunisie 🇹🇳</p>', unsafe_allow_html=True)
            
            with col_map:
                # Lien direct vers une image épurée et libre de droit de la carte de la Tunisie (Bleu/Vert)
                map_url = "https://raw.githubusercontent.com/chmaitilly/tunisia-maps/main/tunisia_minimal.png" 
                # Si tu as ta propre image locale, remplace map_url par "nom_de_ton_image.png"
                st.image(map_url, width=90, use_container_width=False)

        st.markdown("---")

        # ==========================================
        # 3. BARRE LATÉRALE (Sidebar)
        # ==========================================
        st.sidebar.markdown("### 🦠 Filtres de recherche")
        
        # Filtre Dynamique par Bactérie
        liste_bacteries = ["Tous"] + list(df['Souche'].dropna().unique())
        bacterie_choisie = st.sidebar.selectbox("Filtrer par bactérie :", liste_bacteries)
        
        # Application du filtre
        df_filtre = df.copy()
        if bacterie_choisie != "Tous":
            df_filtre = df_filtre[df_filtre['Souche'] == bacterie_choisie]

        # ==========================================
        # 4. BLOCS DE STATISTIQUES DYNAMIQUES
        # ==========================================
        col1, col2, col3, col4 = st.columns(4)
        
        # Calculs automatiques basés sur tes données réelles
        total_souches = len(df_filtre['ID'].unique())
        total_regions = len(df_filtre['Région'].dropna().unique())
        total_atb = len(df_filtre['Antibiotique'].dropna().unique()) if 'Antibiotique' in df_filtre.columns else 36
        
        # Calcul dynamique du taux de résistance réel
        if total_souches > 0:
            resistants = len(df_filtre[df_filtre['Taux Rés.'].str.contains('Resistant|Résistant', case=False, na=False)])
            taux_calculé = (resistants / len(df_filtre)) * 100 if len(df_filtre) > 0 else 96.7
            valeur_resistance = f"{taux_calculé:.1f}%"
        else:
            valeur_resistance = "0%"

        with col1:
            st.metric(label="🦠 Total Souches", value=str(total_souches))
        with col2:
            st.metric(label="📍 Régions Impactées", value=str(total_regions))
        with col3:
            st.metric(label="🚨 Taux de Résistance", value=valeur_resistance)
        with col4:
            st.metric(label="💊 Antibiotiques Testés", value=str(total_atb))

        st.markdown("<br>", unsafe_allow_html=True)

        # ==========================================
        # 5. RECHERCHE RAPIDE ET TABLEAU CLEAN
        # ==========================================
        recherche = st.text_input("🔍 Recherche rapide (Tapez une région, un gène, une souche...) :")
        if recherche:
            df_filtre = df_filtre[df_filtre.astype(str).apply(lambda x: x.str.contains(recherche, case=False)).any(axis=1)]

        # Affichage du tableau de données final nettoyé
        st.dataframe(
            df_filtre[['ID', 'Souche', 'Région', 'Taux Rés.']], 
            hide_index=True, 
            use_container_width=True
        )
        
    except Exception as e:
        st.error(f"❌ Une erreur est survenue lors du chargement : {e}")
    finally:
        conn.close()
