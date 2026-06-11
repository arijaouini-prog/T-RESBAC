import streamlit as st
import sqlite3
import os
import pandas as pd

# Configuration de la page web
st.set_page_config(page_title="Suivi AMR Tunisia", layout="wide")

st.title("🦠 Suivi des Résistances Bactériennes (Tunisia)")
st.write("Données chargées en direct depuis la base de données SQLite.")

DB_NAME = 'FINALEE.db'

if not os.path.exists(DB_NAME):
    st.error(f"Erreur : Le fichier '{DB_NAME}' est introuvable sur GitHub. Vérifie son nom.")
else:
    # Connexion et lecture de la base SQLite
    conn = sqlite3.connect(DB_NAME)
    query = """
    SELECT b.id_bacterie as 'ID', 
           b.Organism_Group as 'Groupe Organisme', 
           b.Strain as 'Souche (Strain)', 
           b.Location as 'Localisation', 
           b.Isolation_source as 'Source d''isolation',
           r.Antimicrobial as 'Antimicrobien', 
           r.Class as 'Classe', 
           r.WGS_predicted_phenotype as 'Phénotype WGS', 
           r.Genetic_background as 'Background Génétique'
    FROM BACTERIES b
    JOIN RESISTANCES r ON b.id_bacterie = r.id_bacterie;
    """
    
    try:
        # Récupération des données dans un tableau
        df = pd.read_sql_query(query, conn)
        
        # Ajout d'une barre de recherche interactive
        recherche = st.text_input("🔍 Rechercher une bactérie, un antibiotique, une localisation...")
        if recherche:
            df = df[df.astype(str).apply(lambda x: x.str.contains(recherche, case=False)).any(axis=1)]
            
        # Affichage du tableau dynamique sur le site
        st.dataframe(df, use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.error(f"Erreur lors de la lecture des tables SQL : {e}. Vérifie que tu as bien exécuté et enregistré le script SQL dans ton fichier.")
    finally:
        conn.close()
