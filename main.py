import streamlit as st
import gspread
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Liste de Courses", page_icon="🛒", layout="centered")

# --- CONNEXION SÉCURISÉE À GOOGLE SHEETS ---
@st.cache_resource
def connect_to_sheet():
    """Initialise la connexion à Google Sheets en utilisant les secrets de Streamlit."""
    # Utilise les secrets pour s'authentifier
    sa = gspread.service_account_from_dict(st.secrets["gcp_credentials"])
    # Ouvre la feuille de calcul par son nom
    sh = sa.open("Liste de Courses App") 
    # Sélectionne la première feuille
    worksheet = sh.sheet1
    return worksheet

worksheet = connect_to_sheet()

# --- FONCTIONS DE GESTION DES DONNÉES ---
def charger_donnees():
    """Charge tous les articles depuis la feuille de calcul."""
    records = worksheet.get_all_records()
    # Convertit le "TRUE"/"FALSE" du sheet en booléen Python
    for record in records:
        record['coche'] = (str(record['coche']).upper() == 'TRUE')
    return sorted(records, key=lambda x: x['nom'])

def maj_article(nom_article, est_coche):
    """Met à jour le statut 'coche' d'un article."""
    try:
        cell = worksheet.find(nom_article)
        # Met à jour la cellule dans la colonne B (la 2ème colonne)
        worksheet.update_cell(cell.row, 2, str(est_coche).upper())
    except gspread.exceptions.CellNotFound:
        # Sécurité si l'article a été supprimé entre-temps
        pass

def supprimer_selection():
    """Supprime toutes les lignes dont la case est cochée."""
    all_items = charger_donnees()
    items_to_keep = [item for item in all_items if not item['coche']]
    
    # Vide toute la feuille
    worksheet.clear()
    
    # Réécrit l'en-tête
    worksheet.append_row(["nom", "coche"])
    
    # Réinsère les articles non supprimés
    for item in items_to_keep:
        worksheet.append_row([item['nom'], str(item['coche']).upper()])

def tout_effacer():
    """Supprime tous les articles, ne laissant que l'en-tête."""
    worksheet.clear()
    worksheet.append_row(["nom", "coche"])

# --- INTERFACE UTILISATEUR ---
st.title("🛒 Liste de Courses sur Google Sheet")
st_autorefresh(interval=5000, key="data_refresh")

# --- ACTIONS ---
col1, col2, col3 = st.columns([0.6, 0.2, 0.2])
with col1:
    with st.form(key='form_ajout', clear_on_submit=True):
        nouvel_article = st.text_input("Ajouter un article", label_visibility="collapsed")
        bouton_ajouter = st.form_submit_button(label="➕ Ajouter")
        if bouton_ajouter and nouvel_article:
            worksheet.append_row([nouvel_article.strip().capitalize(), "FALSE"])
            st.rerun()
with col2:
    if st.button("🗑️ Supprimer"):
        supprimer_selection()
        st.rerun()
with col3:
    if st.button("🔄 Vider"):
        tout_effacer()
        st.rerun()

st.markdown("---")

# --- AFFICHAGE DE LA LISTE ---
liste_courses = charger_donnees()
if not liste_courses:
    st.info("Votre liste de courses est vide.")
else:
    for article in liste_courses:
        est_coche = st.checkbox(article['nom'], value=article['coche'], key=article['nom'])
        if est_coche != article['coche']:
            maj_article(article['nom'], est_coche)
            st.rerun()
