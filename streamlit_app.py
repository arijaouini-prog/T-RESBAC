import streamlit as st
import sqlite3
import os
import pandas as pd

# 1. Configuration moderne de la page web
st.set_page_config(
    page_title="AMR Dashboard Tunisia", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé pour rendre l'interface plus "médicale/scientifique"
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    h1 { color: #004b87; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# 2. Titre principal avec design
st.title("🧬 Plateforme de Suivi des Résistances Bactériennes")
st.subheader("Observatoire de la résistance aux antimicrobiens — Tunisie")
st.markdown("---")

DB_NAME = 'FINALEE.db'

if not os.path.exists(DB_NAME):
    st.error(f"⚠️ Erreur : Le fichier '{DB_NAME}' est introuvable sur GitHub. Veuillez vérifier son emplacement.")
else:
    # Connexion à la base de données
    conn = sqlite3.connect(DB_NAME)
    query = """
    SELECT b.id_bacterie as 'ID', 
           b.Organism_Group as 'Groupe Organisme', 
           b.Strain as 'Souche (Strain)', 
           b.Location as 'Localisation (Gouvernorat)', 
           b.Isolation_source as 'Source d''isolation',
           r.Antimicrobial as 'Antimicrobien', 
           r.Class as 'Classe Antibiotique', 
           r.WGS_predicted_phenotype as 'Phénotype WGS', 
           r.Genetic_background as 'Background Génétique'
    FROM BACTERIES b
    JOIN RESISTANCES r ON b.id_bacterie = r.id_bacterie;
    """
    
    try:
        # Chargement des données fondamentales
        df = pd.read_sql_query(query, conn)
        
        # 3. BARRE LATÉRALE DE FILTRES (Sidebar)
        st.sidebar.header("🎯 Filtres de recherche")
        
        # Filtre par Groupe Organisme (Bactérie)
        liste_bacteries = ["Tous"] + list(df['Groupe Organisme'].unique())
        bacterie_choisie = st.sidebar.selectbox("Filtrer par bactérie :", liste_bacteries)
        
        # Filtre par Localisation (Ville)
        liste_villes = ["Toutes"] + list(df['Localisation (Gouvernorat)'].dropna().unique())
        ville_choisie = st.sidebar.selectbox("Filtrer par région :", liste_villes)
        
        # Filtre par Résistance
        liste_phenotypes = ["Tous"] + list(df['Phénotype WGS'].unique())
        phenotype_choisi = st.sidebar.selectbox("Statut Phénotype :", liste_phenotypes)
        
        # Application dynamique des filtres de la sidebar
        df_filtre = df.copy()
        if bacterie_choisie != "Tous":
            df_filtre = df_filtre[df_filtre['Groupe Organisme'] == bacterie_choisie]
        if ville_choisie != "Toutes":
            df_filtre = df_filtre[df_filtre['Localisation (Gouvernorat)'] == ville_choisie]
        if phenotype_choisi != "Tous":
            df_filtre = df_filtre[df_filtre['Phénotype WGS'] == phenotype_choisi]

        # 4. BLOCS DE STATISTIQUES (Chiffres clés) en haut
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="🦠 Total Souches", value=len(df_filtre['Souche (Strain)'].unique()))
        with col2:
            st.metric(label="📍 Régions impactées", value=len(df_filtre['Localisation (Gouvernorat)'].unique()))
        with col3:
            # Calcul du taux de résistance en %
            total = len(df_filtre)
            if total > 0:
                resistants = len(df_filtre[df_filtre['Phénotype WGS'].str.contains('Resistant', case=False, na=False)])
                taux_resistance = (resistants / total) * 100
                st.metric(label="🚨 Taux de Résistance", value=f"{taux_resistance:.1f}%")
            else:
                st.metric(label="🚨 Taux de Résistance", value="0%")
        with col4:
            st.metric(label="💊 Antibiotiques testés", value=len(df_filtre['Antimicrobien'].unique()))

        st.markdown("<br>", unsafe_allow_html=True)

        # 5. BARRE DE RECHERCHE TEXTUELLE GLOBALE
        recherche = st.text_input("🔍 Recherche rapide (Tapez un gène, un hôpital, une souche...) :")
        if recherche:
            df_filtre = df_filtre[df_filtre.astype(str).apply(lambda x: x.str.contains(recherche, case=False)).any(axis=1)]

        # 6. AFFICHAGE DU TABLEAU ENRICHI
        st.write(f"📊 **Données filtrées :** {len(df_filtre)} lignes trouvées")
        
        # Utilisation de st.dataframe avec configuration avancée des colonnes
        st.dataframe(
            df_filtre,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID": st.column_config.NumberColumn("ID", format="%d"),
                "Phénotype WGS": st.column_config.TextColumn("Phénotype WGS"),
            }
        )
        
    except Exception as e:
        st.error(f"Erreur SQL : {e}")
    finally:
        conn.close()
