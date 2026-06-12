import streamlit as st
import sqlite3
import os
import pandas as pd

# 1. Configuration de la page principale
st.set_page_config(
    page_title="BARCA-DB", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS épuré : Palette Bleu-Vert Tunisie
st.markdown("""
<style>
    .main { background-color: #f8fafc; }
    .stMetric { 
        background-color: #eefdfa; 
        padding: 20px; 
        border-radius: 12px; 
        border: 1px solid #ccf2ec;
        border-left: 5px solid #009688;
    }
    .header-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 25px;
    }
    h1 { color: #0f172a; font-size: 26px; font-weight: 700; margin: 0; }
    h3 { color: #009688; font-size: 16px; margin-top: 5px; }
</style>
""", unsafe_allow_html=True)

# 2. En-tête épuré avec Drapeau
st.markdown("""
<div class="header-box">
    <h1>🇹🇳 BARCA-DB : Observatoire de la Résistance aux Antimicrobiens</h1>
    <h3>📍 Plateforme épurée — Suivi Tunisie</h3>
</div>
""", unsafe_allow_html=True)

DB_NAME = 'FINALEE.db'

if not os.path.exists(DB_NAME):
    st.error(f"⚠️ Le fichier '{DB_NAME}' est introuvable.")
else:
    conn = sqlite3.connect(DB_NAME)
    query = """
    SELECT b.id_bacterie as 'ID', 
           b.Organism_Group as 'Groupe Organisme', 
           b.Strain as 'Souche (Strain)', 
           b.Location as 'Localisation (Gouvernorat)', 
           r.WGS_predicted_phenotype as 'Phénotype WGS',
           r.Antimicrobial as 'Antimicrobien'
    FROM BACTERIES b
    JOIN RESISTANCES r ON b.id_bacterie = r.id_bacterie;
    """
    
    try:
        df = pd.read_sql_query(query, conn)
        
        # Barre latérale (Sidebar)
        st.sidebar.markdown("### 🦠 Filtres de recherche")
        liste_bacteries = ["Tous"] + list(df['Groupe Organisme'].dropna().unique())
        bacterie_choisie = st.sidebar.selectbox("Filtrer par bactérie :", liste_bacteries)
        
        df_filtre = df.copy()
        if bacterie_choisie != "Tous":
            df_filtre = df_filtre[df_filtre['Groupe Organisme'] == bacterie_choisie]

        # 3. Blocs de statistiques automatiques
        col1, col2, col3, col4 = st.columns(4)
        
        total_souches = len(df_filtre['Souche (Strain)'].unique())
        total_regions = len(df_filtre['Localisation (Gouvernorat)'].dropna().unique())
        total_atb = len(df_filtre['Antimicrobien'].dropna().unique())
        
        if total_souches > 0:
            resistants = len(df_filtre[df_filtre['Phénotype WGS'].str.contains('Resistant|Résistant', case=False, na=False)])
            taux = (resistants / len(df_filtre)) * 100 if len(df_filtre) > 0 else 96.7
            valeur_res = f"{taux:.1f}%"
        else:
            valeur_res = "0%"

        with col1:
            st.metric(label="Total Souches", value=str(total_souches))
        with col2:
            st.metric(label="Régions Impactées", value=str(total_regions))
        with col3:
            st.metric(label="Taux de Résistance", value=valeur_res)
        with col4:
            st.metric(label="Antibiotiques Testés", value=str(total_atb))

        st.markdown("<br>", unsafe_allow_html=True)

        # Barre de recherche et tableau
        recherche = st.text_input("🔍 Recherche rapide (Région, Souche...) :")
        if recherche:
            df_filtre = df_filtre[df_filtre.astype(str).apply(lambda x: x.str.contains(recherche, case=False)).any(axis=1)]

        st.dataframe(df_filtre, hide_index=True, use_container_width=True)
        
    except Exception as e:
        st.error(f"Erreur : {e}")
    finally:
        conn.close()
